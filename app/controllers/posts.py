import os
import requests
import aiofiles
from fastapi.encoders import jsonable_encoder
from typing import List
from app.services.api.twitterAPI import TwitterAPI
from app.db.connect import posts
from app.controllers.twitter import get_channel_details, delete_uploaded_media


async def scheduled_post_media_uploader(files, api) -> List:
    media_ids = []
    for media in files:
        fileURL = media
        filename = fileURL.split('/')[-1]
        file_path = os.path.join(os.getcwd(), f'uploads\{filename}')
        
        request = requests.get(media, stream=True)


        if request.status_code == 200:

            if not os.path.exists(os.path.join(os.getcwd(), f'uploads')):
                os.makedirs(os.path.join(os.getcwd(), f'uploads'))

            async with aiofiles.open(file_path, 'wb') as media:
                for chunk in request:
                    await media.write(chunk)
        else:
            print("Unable to download image")
            return False
    
        res = api.upload_media(filename=file_path)
        # handling Twitter API Error        
        if res == None:
            return False
        await delete_uploaded_media(file_path=file_path)
        media_ids.append(res)

    return media_ids

# saves scheduled posts to Database
async def post_saver(scheduled_post: dict):
    data = jsonable_encoder(scheduled_post)
    post_inserted = await posts.insert_one(data)
    post_created = await posts.find_one({"_id": post_inserted.inserted_id})
    return post_created

async def get_scheduled_posts(user_id: str):
    posts_list = [document async for document in posts.find({}) if document['user_id']==user_id]
    print(posts_list)
    if posts_list == None:
        return None
    return posts_list

async def post_scheduled_tweet(post):
    channel = await get_channel_details(user_id=post['user_id'])

    if channel == None:
        return False

    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])

    media_response = None
    if post['files'] != None:
        media_response = await scheduled_post_media_uploader(files=post['files'], api=api)
        # check if response is a dictionary returned by ErrorResponseModel
        if media_response==False:
            # Error returned
            return False

    tweet = api.create_tweet(post['text'], media_response)
    if tweet == None:
        return False

    # post has been published successfully
    return True