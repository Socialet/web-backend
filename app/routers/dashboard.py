from datetime import datetime
import json
from bson import ObjectId
from typing import Optional
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.models.main import ErrorResponseModel
from app.controllers.twitter import fetch_follower_details, get_channel_details
from app.services.api.twitterAPI import TwitterAPI

dashboard_view = APIRouter()


@dashboard_view.get("/followCount", description="GET USER FOLLOWERS")
async def get_user_details(user_id: str, screen_name: Optional[str] = None):
    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])
    profile = await fetch_follower_details(channel, api, screen_name)

    if profile == None:
        return ErrorResponseModel(
            error="Something went wrong while fetching user Profile.",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Get User Profile. Please Try Again Later."
        )
    followers_list = channel['twitter']['followers']
    followings_list = channel['twitter']['followings']
    if len(followers_list)-7 < 0:
        followers_wa = 0
        followings_wa = 0
    else:
        followers_wa = followers_list[len(followers_list)-7]
        followings_wa = followings_list[len(followings_list)-7]

    if followers_wa != 0:
        followers_percentage = (
            (profile["followers"] - followers_wa) / followers_wa) * 100
    else:
        followers_percentage = profile["followers"]

    if followings_wa != 0:
        followings_percentage = (
            (profile["followings"] - followings_wa) / followings_wa) * 100
    else:
        followings_percentage = profile["followings"]

    resp = {
        "followers": profile["followers"],
        "followings": profile["followings"],
        "followers_wa": followers_wa,
        "followings_wa": followings_wa,
        "followers_percentage": followers_percentage,
        "followings_percentage": followings_percentage
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=resp)


@dashboard_view.get("/top_follower", description="GET TOP FOLLOWER")
async def get_top_follower(user_id: str):

    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )

    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])

    followers = api.get_followers(user_id)
    top_follower = {"follower_count": 0, "follower": {}}
    for follower in followers["users"]:
        if (follower["followers_count"] > top_follower["follower_count"]):
            top_follower["follower"] = follower
            top_follower["follower_count"] = follower["followers_count"]

    return JSONResponse(content=top_follower, status_code=status.HTTP_202_ACCEPTED)


@dashboard_view.get("/top_tweet", description="GET TOP FOLLOWER")
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
    user_timeline = api.get_my_tweets(user_id)

    for timeline in user_timeline:
        retweet = timeline["retweet_count"]
        like = timeline["favorite_count"]
        denominator = (retweet+like)
        if denominator == 0:
            score = 0
        else:
            score = (retweet*0.7 + like*0.3)/denominator

        if score > bummer["impression_score"]:
            bummer["impression_score"] = score
            bummer["tweet"] = timeline

    return JSONResponse(content=bummer, status_code=status.HTTP_202_ACCEPTED)


@dashboard_view.get("/top_media_tweet", description="GET TOP FOLLOWER")
async def get_top_media_tweet(user_id: str):

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
    user_timeline = api.get_my_tweets(user_id)

    for timeline in user_timeline:
        if "media" in timeline["entities"]:
            retweet = timeline["retweet_count"]
            like = timeline["favorite_count"]
            denominator = (retweet+like)
            if denominator == 0:
                score = 0
            else:
                score = (retweet*0.7 + like*0.3)/denominator

            if score > bummer["impression_score"]:
                bummer["impression_score"] = score
                bummer["tweet"] = timeline

    return JSONResponse(content=bummer, status_code=status.HTTP_202_ACCEPTED)


@dashboard_view.get("/top_mention", description="GET TOP MENTION")
async def get_top_mention(user_id: str):

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
    bummer = {"impression_score": 0, "mention": {}}
    mentions = api.get_mentions(user_id)

    for mention in mentions:
        retweet = mention["retweet_count"]
        like = mention["favorite_count"]
        denominator = (retweet+like)
        if denominator == 0:
            score = 0
        else:
            score = (retweet*0.7 + like*0.3)/denominator

        if score > bummer["impression_score"]:
            bummer["impression_score"] = score
            bummer["mention"] = mention

    return JSONResponse(content=bummer, status_code=status.HTTP_202_ACCEPTED)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return str(o)
        return json.JSONEncoder.default(self, o)


@dashboard_view.get("/timeline", description="GET TIMELINE FOR PLOTTING FOLLOWERS/FOLLOWING PICTORIAL REPRESENTATION")
async def get_timeline(user_id: str):

    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    followers = jsonable_encoder(channel["twitter"]["followers"])
    followings = jsonable_encoder(channel["twitter"]["followings"])
    return JSONResponse(content={"followers": followers, "followings": followings}, status_code=status.HTTP_202_ACCEPTED)
