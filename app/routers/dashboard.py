from typing import Optional
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
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
    profile = await fetch_follower_details(channel,api,screen_name)

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

    resp = {
        "followers": profile["followers"],
        "followings": profile["followings"],
        "followers_wa": followers_wa,
        "followings_wa": followings_wa
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=resp)
