from datetime import datetime, timedelta
import time
import json
from bson import ObjectId
from typing import Optional
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.models.main import ErrorResponseModel
from app.controllers.twitter import fetch_follower_details, get_channel_details
from app.services.api.twitterAPI import TwitterAPI

admin_dashboard_view = APIRouter()


@admin_dashboard_view.get("/weekly_analysis", description="Weekly analysis")
async def get_top_tweet(user_id: str):

    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )

    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])

    # (retweet * 0.5 + reply * 0.3 + like * 0.2)/ (retweet+reply+like)
    bummer = {"impression_score": 0, "tweet": {}}
    user_timeline = api.get_my_200_tweets(user_id)

    # print(len(user_timeline))
    week_ago_date = datetime.now() - timedelta(days=7)
    count = 0
    likes = 0
    retweets = 0
    tweets= []
    
    for timeline in user_timeline:
        tweets.append(timeline)
        created_at = time.strftime('%Y-%m-%d',time.strptime(user_timeline[0]['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
        created_at_new=datetime.strptime(created_at,'%Y-%m-%d')

        if( week_ago_date.date() <= created_at_new.date()):
            count = count + 1
            likes = likes + timeline["user"]["favourites_count"]
            retweets = retweets + timeline["retweet_count"]
    
    print(f"{count}{likes}{retweets}")
        
    denominator = (retweets+likes)
    if denominator == 0:
        score = 0
    else:
        score = (retweets*0.7 + likes*0.3)/denominator

    if score > bummer["impression_score"]:
        bummer["impression_score"] = score
        bummer["count"] = count
        bummer["retweets"] = retweets
        bummer["likes"] = likes
        bummer["tweets"] = tweets

    return JSONResponse(content=bummer, status_code=status.HTTP_200_OK)
