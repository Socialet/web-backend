import aiofiles
import os
from fastapi import status
from typing import List
from bson import ObjectId
from cloudinary.uploader import destroy
import cloudinary.uploader as uploader
from app.db.connect import users, channels
from app.utils.image_processing import convert_size_mb, delete_uploaded_media
from app.models.main import ErrorResponseModel
from app.config import get_logger

logger = get_logger()

async def create_channel(user_id: str, channel_name:str, channel_obj: dict):
    
    channel = await channels.find_one({"user_id": user_id})
    if channel != None:
        # do not insert as a new channel
        channel_updated = await channels.update_one({"user_id": user_id}, {'$set':{channel_name: channel_obj}})
        return channel_updated
        
    channel_inserted = await channels.insert_one({"user_id": user_id, channel_name: channel_obj})
    updated_user = await users.update_one({"_id": ObjectId(user_id)}, {'$set': {"channel_id": channel_inserted.inserted_id}})
    
    return channel_inserted

# gets channel details if channel exists


async def get_channel_details(user_id: str):
    
    channel = await channels.find_one({"user_id": user_id})
    if channel == None:
        return None
    return channel

# media handler for POST NOW Tweets
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
                await delete_uploaded_media(file_path=file_path)
                return ErrorResponseModel(
                    error="Image Size Too Large",
                    code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    message="Image Size is Too Large for Twitter Support. Please upload image with size upto 5MB only."
                )
            else:
                res = api.upload_media(filename=file_path)
                # handling Twitter API Error
                if res == None:
                    await delete_uploaded_media(file_path=file_path)
                    return ErrorResponseModel(
                        error="Something Went Wrong While Uploading Image.",
                        code=status.HTTP_400_BAD_REQUEST,
                        message="Something Went Wrong While Uploading Image to Twitter."
                    )
                media_ids.append(res)

        # if media is GIF
        elif extension == "gif":
            if file_size > 15:
                await delete_uploaded_media(file_path=file_path)
                return ErrorResponseModel(
                    error="GIF Size Too Large",
                    code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    message="GIF Size is Too Large for Twitter Support. Please upload GIF with size upto 15MB only."
                )
            else:
                res = api.upload_media(filename=file_path)
                # handling Twitter API Error
                if res == None:
                    await delete_uploaded_media(file_path=file_path)
                    return ErrorResponseModel(
                        error="Something Went Wrong While Uploading GIF.",
                        code=status.HTTP_400_BAD_REQUEST,
                        message="Something Went Wrong While Uploading GIF to Twitter."
                    )
                media_ids.append(res)
        # if media is Video
        else:
            if file_size > 512:
                await delete_uploaded_media(file_path=file_path)
                return ErrorResponseModel(
                    error="Video Size Too Large",
                    code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    message="Video Size is Too Large for Twitter Support. Please upload Video with size upto 512MB only."
                )
            else:
                res = api.upload_media(filename=file_path)
                # handling Twitter API Error
                if res == None:
                    await delete_uploaded_media(file_path=file_path)
                    return ErrorResponseModel(
                        error="Something Went Wrong While Uploading Video.",
                        code=status.HTTP_400_BAD_REQUEST,
                        message="Something Went Wrong While Uploading Video to Twitter."
                    )
                media_ids.append(res)

        # delete uploaded file
        await delete_uploaded_media(file_path=file_path)
    return media_ids

# media handler for Scheduled Tweets
async def scheduled_media_handler(files) -> List:
    
    media_uploads = []
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

        content = await media.read()
        # if video use upload_large
        if extension in ("webp","mp4","mov"):
            uploaded_file= uploader.upload_large(content)
        else:
            uploaded_file= uploader.upload(content)

        file_size=convert_size_mb(uploaded_file["bytes"])
        # if media is image
        if extension in ("jpg", "jpeg", "png"):
            # image size greater than 5 MB not supported by Twitter
            if file_size > 5:
                try:
                    destroy(uploaded_file['public_id'])
                except Exception as e:
                    logger.error(f"Something went wrong: {str(e)}")
                return ErrorResponseModel(
                    error="Image Size Too Large",
                    code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    message="Image Size is Too Large for Twitter Support. Please upload image with size upto 5MB only."
                )
            else:
                media_uploads.append(uploaded_file['url'])

        # if media is GIF
        elif extension == "gif":
            if file_size > 15:
                try:
                    destroy(uploaded_file['public_id'])
                except Exception as e:
                    logger.error(f"Something went wrong: {str(e)}")
                return ErrorResponseModel(
                    error="GIF Size Too Large",
                    code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    message="GIF Size is Too Large for Twitter Support. Please upload GIF with size upto 15MB only."
                )
            else:
                media_uploads.append(uploaded_file['url'])

        # if media is Video
        else:
            if file_size > 512:
                try:
                    destroy(uploaded_file['public_id'])
                except Exception as e:
                    logger.error(f"Something went wrong: {str(e)}")
                return ErrorResponseModel(
                    error="Video Size Too Large",
                    code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    message="Video Size is Too Large for Twitter Support. Please upload Video with size upto 512MB only."
                )
            else:
                media_uploads.append(uploaded_file['url'])

    return media_uploads
