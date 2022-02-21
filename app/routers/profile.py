from typing import Optional
from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse
from app.models.main import ErrorResponseModel
from app.models.profile import SurveyData
from app.controllers.profile import create_profile, get_social_accounts, disconnect_social_account
from app.controllers.twitter import get_channel_details
from app.services.api.twitterAPI import TwitterAPI

profile_view = APIRouter()


@profile_view.post('/survey', response_description="POST SURVEY DATA UPON NEW USER REGISTRATION")
async def survey_upon_new_user_registration(survey_data: SurveyData = Body(...)):
    await create_profile(survey_data)
    return JSONResponse(content='Thanks for filling 😊', status_code=status.HTTP_200_OK)


@profile_view.get('/social/accounts', response_description="GET ALL SOCIAL ACCOUNTS INFO BY USER ID")
async def get_social_sccounts_details_of_user(user_id: str):
    user_accounts_details = await get_social_accounts(user_id)
    return JSONResponse(content=user_accounts_details, status_code=status.HTTP_200_OK)


@profile_view.patch('/social/account', response_description="DELETE SPECIFIC SOCIAL ACCOUNT FROM THE USER CHANNELS")
async def delete_social_account_of_user(bodyData=Body(...)):
    delete_account = await disconnect_social_account(bodyData['user_id'], bodyData['social_account_name'])
    if delete_account == None:
        return ErrorResponseModel(
            error="Attempt to Disconnect Channel Failed.",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Attempt to Disconnect Channel Failed. Please Try Again."
        )

    return JSONResponse(content=bodyData['social_account_name'] + " disconnected successfully", status_code=status.HTTP_200_OK)


@profile_view.get("/user/timeline", description="GET POSTS FOR PARTICULAR USER")
async def get_user_timeline(user_id: str, page: int = None, screen_name: Optional[str] = None):
    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])
    posts = api.get_user_posts(
        channel['twitter']['user_id'], screen_name, page)

    if posts == None:
        return ErrorResponseModel(
            error="Something went wrong while fetching your posts.",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Get Your Posts. Please Try Again Later."
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"posts": posts})


@profile_view.get("/user/mentions", description="GET USER MENTIONS TIMELINE OF A PARTICULAR USER")
async def get_user_mentions(user_id: str, page: int):
    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])
    mentions = api.get_user_mentions_timeline(page)

    if mentions == None:
        return ErrorResponseModel(
            error="Something went wrong while fetching user mentions timeline.",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Get User mentions timeline. Please Try Again Later."
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"mentions": mentions})


@profile_view.get("/user/followers", description="GET USER FOLLOWERS")
async def get_user_followers(user_id: str, page: int, screen_name: Optional[str] = None):
    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])
    followers = api.get_user_followers(
        channel['twitter']['user_id'], screen_name, page)

    if followers == None:
        return ErrorResponseModel(
            error="Something went wrong while fetching user followers.",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Get User followers. Please Try Again Later."
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"followers": followers['users']})


@profile_view.get("/user/following", description="GET USER FOLLOWERS")
async def get_user_following(user_id: str, page: int, screen_name: Optional[str] = None):
    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])
    following = api.get_user_following(
        channel['twitter']['user_id'], screen_name, page)

    if following == None:
        return ErrorResponseModel(
            error="Something went wrong while fetching user following.",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Get User following. Please Try Again Later."
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"following": following['users']})


@profile_view.get("/user/profile", description="GET USER FOLLOWERS")
async def get_user_profile(user_id: str, screen_name: Optional[str] = None):
    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])
    profile = api.get_user(channel['twitter']['user_id'], screen_name)

    if profile == None:
        return ErrorResponseModel(
            error="Something went wrong while fetching user Profile.",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Get User Profile. Please Try Again Later."
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"profile": profile})
