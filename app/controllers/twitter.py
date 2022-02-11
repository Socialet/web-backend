import aiofiles
import os
from fastapi import status
from typing import List
from app.db.connect import users, channels, profiles
from app.utils.image_processing import convert_size_mb
from app.models.main import ErrorResponseModel
from fastapi.encoders import jsonable_encoder
from bson import ObjectId


async def create_channel(user_id: str, twitterOAuth: dict):
    channel = await channels.find_one({"user_id": user_id})
    if channel != None:
        # do not insert as a new channel
        return None
    channel_inserted = await channels.insert_one({"user_id": user_id, "twitter": twitterOAuth})
    updated_user = await users.update_one({"_id": ObjectId(user_id)}, {'$set': {"channel_id": channel_inserted.inserted_id}})
    return channel_inserted

# gets channel details if channel exists


async def get_channel_details(user_id: str):
    channel = await channels.find_one({"user_id": user_id})
    if channel == None:
        return None
    return channel


async def media_handler(files, api) -> List:
    media_ids = []
    for media in files:
        extension = media.filename.split(".")[-1]
        supported = extension in (
            "jpg", "jpeg", "png", "gif", "webp", "mp4", "mov")
        if not supported:
            return ErrorResponseModel(
                error="Media Type Not Supported",
                code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                message="This File Format is unsupported by Twitter."
            )

        # convert file size to MB for checks
        file_size = 0
        file_path = os.path.join(os.getcwd(), f'uploads\{media.filename}')

        if not os.path.exists(os.path.join(os.getcwd(), f'uploads')):
            os.makedirs(os.path.join(os.getcwd(), f'uploads'))

        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await media.read()
            await out_file.write(content)
            file_size = convert_size_mb(len(content))

        # if media is image
        if extension in ("jpg", "jpeg", "png"):
            # image size greater than 5 MB not supported by Twitter
            if file_size > 5:
                return ErrorResponseModel(
                    error="Image Size Too Large",
                    code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    message="Image Size is Too Large for Twitter Support. Please upload image with size upto 5MB only."
                )
            else:
                res = api.upload_media(filename=file_path)
                # handling Twitter API Error
                if res == None:
                    return ErrorResponseModel(
                        error="Something Went Wrong While Uploading Image.",
                        code=status.HTTP_400_BAD_REQUEST,
                        message="Something Went Wrong While Uploading Image to Twitter."
                    )
                media_ids.append(res)

        # if media is GIF
        elif extension == "gif":
            if file_size > 15:
                return ErrorResponseModel(
                    error="GIF Size Too Large",
                    code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    message="GIF Size is Too Large for Twitter Support. Please upload GIF with size upto 15MB only."
                )
            else:
                res = api.upload_media(filename=file_path)
                # handling Twitter API Error
                if res == None:
                    return ErrorResponseModel(
                        error="Something Went Wrong While Uploading GIF.",
                        code=status.HTTP_400_BAD_REQUEST,
                        message="Something Went Wrong While Uploading GIF to Twitter."
                    )
                media_ids.append(res)
        # if media is Video
        else:
            if file_size > 512:
                return ErrorResponseModel(
                    error="Video Size Too Large",
                    code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    message="Video Size is Too Large for Twitter Support. Please upload Video with size upto 512MB only."
                )
            else:
                res = api.upload_media(filename=file_path)
                # handling Twitter API Error
                if res == None:
                    return ErrorResponseModel(
                        error="Something Went Wrong While Uploading Video.",
                        code=status.HTTP_400_BAD_REQUEST,
                        message="Something Went Wrong While Uploading Video to Twitter."
                    )
                media_ids.append(res)

        # delete uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print("The file does not exist")
    return media_ids


async def profile_add_on_new_user_registration(survey_data):
    print(survey_data)
    data = jsonable_encoder(survey_data)
    profile_inserted = await profiles.insert_one({"user_id": data['user_id'], "surveyData": data})
    print(profile_inserted)
    ref_id_added_to_user = await users.update_one({"_id": ObjectId(data['user_id'])}, {"$set": {"profile_id": profile_inserted.inserted_id}})
    return profile_inserted
