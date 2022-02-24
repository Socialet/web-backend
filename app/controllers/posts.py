import os
import requests
import aiofiles
from datetime import datetime
from dateutil import parser,tz
from fastapi.encoders import jsonable_encoder
from typing import List
from bson import ObjectId
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
    if post['isReply']:
        tweet = api.reply_tweet(post['text'], media_response, post['replyTweetId'])
    else:
        tweet = api.create_tweet(post['text'], media_response)
    
    if tweet == None:
        return False

    # post has been published successfully
    return True

async def get_scheduled_posts(user_id: str):
    posts_list = [document async for document in posts.find({}) if document['user_id']==user_id]
    if posts_list == None:
        return None
    return posts_list

async def remove_scheduled_post(post_id:str):
    delete_result = await posts.delete_one({"_id": ObjectId(post_id)})

    if delete_result.deleted_count == 1:
        return True
    # id not found, action not performed
    return False

async def update_scheduled_post(updated_post: dict):

    data = jsonable_encoder(updated_post)
    old_document = await posts.find_one({'_id': ObjectId(data['id'])})
    _id = old_document['_id']
    if 'id' in data: del data['id']
    
    result = await posts.replace_one({'_id': _id}, data)
    if result.modified_count==None or result.modified_count==0:
        return None
    new_document = await posts.find_one({'_id': _id})    
    return new_document

async def reschedule_datetime(scheduled_post):
    # Auto-detect zones:
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    myDate = parser.parse(scheduled_post['scheduled_datetime']).strftime("%Y-%m-%d %H:%M:%S")
    utc = datetime.strptime(myDate, '%Y-%m-%d %H:%M:%S')

    # Tell the datetime object that it's in UTC time zone since 
    utc = utc.replace(tzinfo=from_zone)

    # Convert time zone
    central = utc.astimezone(to_zone)
    now = datetime.now()
    if central.date() >= now.date() and central.hour>=now.hour and central.minute >= now.minute:
        await posts.update_one({"_id": ObjectId(scheduled_post['id'])}, {"$set": {"published": False,"expired":False}})
        return True
    else:
        return False


async def reschedule_scheduled_post(scheduled_post: dict):
    data = jsonable_encoder(scheduled_post)

    should_be_rescheduled=await reschedule_datetime(data)
    if not should_be_rescheduled:
        return None
 
    result = await posts.update_one({"_id": ObjectId(data['id'])}, 
        {"$set": {"scheduled_datetime": data['scheduled_datetime'],"timeformat":data['timeformat']}
    })
    if result.modified_count < 1:
        return None
    new_document = await posts.find_one({'_id': ObjectId(data['id'])})    
    return new_document