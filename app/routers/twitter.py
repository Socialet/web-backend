from fastapi import APIRouter, Body, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Dict, Optional, List
from app.services.auth.twitterOAuth import TwitterOAuth
from app.services.api.twitterAPI import TwitterAPI
from app.controllers.twitter import create_channel, delete_user_social_account, get_channel_details, get_user_social_accounts_details, media_handler, profile_add_on_new_user_registration
from app.models.main import ErrorResponseModel
from app.models.channels import ConnectOut, OAuthOut, Tokens
from app.models.twitter import SurveyData

twitter_view = APIRouter()


@twitter_view.get("/connect", response_model=ConnectOut, status_code=200)
def twitter_connect():
    oAuth = TwitterOAuth()
    auth_url = oAuth.fetch_auth_url()
    return ConnectOut(oauth_url=auth_url)


@twitter_view.post("/oauth", response_model=OAuthOut, status_code=201)
async def fetch_access_tokens(tokens: Tokens):
    oAuth = TwitterOAuth()
    # pass received oauth_tokens(request_token) and oauth_verifier to fetch access tokens for user.
    access_token, access_token_secret, user_id, screen_name = oAuth.fetch_access_tokens(
        tokens.oauth_token, tokens.oauth_verifier)

    api = TwitterAPI(access_token=access_token,
                     access_token_secret=access_token_secret)
    profile = api.get_user_profile(user_id, screen_name)

    if profile == None:
        return ErrorResponseModel(
            error="Something went wrong while getting user profile",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Get Your Profile. Please Try Again."
        )

    # save these objects in DB to retrieve later and make API calls.
    twitterDict = {
        "access_token": access_token,
        "access_token_secret": access_token_secret,
        "user_id": user_id,
        "screen_name": screen_name,
        "description": profile['description'],
        "profile_image_url": profile['profile_image_url']
    }

    # returns None if channel is not created
    created_channel = await create_channel(user_id=tokens.user_id, twitterOAuth=twitterDict)

    if created_channel == None:
        return ErrorResponseModel(
            error="Something went wrong while creating user profile",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Get Your Profile. Please Try Again."
        )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=profile)


@twitter_view.get("/feed/", response_description="GET FEED/HOME TIMELINE FOR USER")
async def get_feed(user_id: str):
    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])
    tweets = api.get_user_feed()

    if tweets == None:
        return ErrorResponseModel(
            error="Something went wrong while fetching user feed.",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Get Your Feed. Please Try Again Later."
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"feed":tweets})
        


@twitter_view.get("/search", response_description="GET TWEETS BASED ON SEARCH QUERY FOR USER")
async def search_tweets(user_id: str, query: str, geocode: Optional[str] = None):

    # query fomatting for hashtags
    new_query = ""
    if query.startswith('hashtag'):
        new_query = query.replace('hashtag', '#')
    else:
        new_query = query

    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )

    api = TwitterAPI(access_token=channel['twitter']['access_token'],access_token_secret=channel['twitter']['access_token_secret'])
    
    tweets = api.get_searched_tweets(new_query, geocode)
    if tweets==None:
        return ErrorResponseModel(
            error="Something went wrong while searching for topic",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Search Your Topic."
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"tweets":tweets['statuses']})

@twitter_view.post("/tweet")
async def create_tweet(files: Optional[List[UploadFile]] = File(None), user_id: str = Form(...), text: str = Form(...)):

    channel=await get_channel_details(user_id=user_id)
    
    if channel==None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )

    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])

    media_response = None
    if files != None:
        media_response = await media_handler(files=files, api=api)
        # check if response is a dictionary returned by ErrorResponseModel
        if isinstance(media_response, dict):
            # Error returned
            return media_response

    tweet = api.create_tweet(text, media_response)
    if tweet == None:
        return ErrorResponseModel(
            error="Could Not Create New Tweet",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Your Tweet was not created. Please Try Again."
        )

    return JSONResponse(content=tweet,status_code=status.HTTP_201_CREATED)

@twitter_view.post("/reply")
async def reply_tweet(files: Optional[List[UploadFile]] = File(None), tweet_id: str=Form(...), user_id: str=Form(...), text: str=Form(...)):
    channel=await get_channel_details(user_id=user_id)
    if channel==None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code= status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    
    api = TwitterAPI(access_token=channel['twitter']['access_token'],access_token_secret=channel['twitter']['access_token_secret'])

    media_response=None
    if files!=None:
        media_response = await media_handler(files=files,api=api)
        # check if response is a dictionary returned by ErrorResponseModel
        if isinstance(media_response,dict):
            # Error returned
            return media_response
        
    tweet = api.reply_tweet(text, media_response, tweet_id)
    if tweet==None:
        return ErrorResponseModel(
            error="Could Not Reply to Tweet",
            code= status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Your Reply was not created. Please Try Again."
        )
    
    return JSONResponse(content=tweet,status_code=status.HTTP_201_CREATED) 

@twitter_view.get("/tweet")
async def get_tweet_by_id(tweet_id: str, user_id: str):
    channel=await get_channel_details(user_id=user_id)
    if channel==None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code= status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    
    api = TwitterAPI(access_token=channel['twitter']['access_token'],access_token_secret=channel['twitter']['access_token_secret'])
    
    tweet = api.get_tweet(tweet_id)
    if tweet == None:
        return ErrorResponseModel(
            error="Tweet not found",
            code= status.HTTP_404_NOT_FOUND,
            message="Tweet not found"
        )
    
    return JSONResponse(content=tweet,status_code=status.HTTP_200_OK) 


# profile routes
@twitter_view.post('/survey', response_description="POST SURVEY DATA UPON NEW USER REGISTRATION")
async def survey_upon_new_user_registration(survey_data: SurveyData = Body(...)):
    print(survey_data)
    await profile_add_on_new_user_registration(survey_data)
    return JSONResponse(content='Thanks for filling 😊', status_code=status.HTTP_200_OK)


@twitter_view.get('/social/accounts', response_description="GET ALL SOCIAL ACCOUNTS INFO BY USER ID")
async def get_social_sccounts_details_of_user(user_id: str):
    user_accounts_details = await get_user_social_accounts_details(user_id)
    return JSONResponse(content=user_accounts_details, status_code=status.HTTP_200_OK)

@twitter_view.delete('/social/accounts', response_description="DELETE SPECIFIC SOCIAL ACCOUNT FROM THE USER CHANNELS")
async def delete_social_account_of_user(user_id: str, social_account_name: str):
    delete_account = await delete_user_social_account(user_id, social_account_name)
    return JSONResponse(content=social_account_name + " disconncted successfully", status_code=status.HTTP_200_OK)
