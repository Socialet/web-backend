from fastapi import APIRouter, Body, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, List
from app.services.auth.twitterOAuth import TwitterOAuth
from app.services.api.twitterAPI import TwitterAPI
from app.controllers.twitter import create_channel, get_channel_details, media_handler, scheduled_media_handler, post_saver
from app.models.main import ErrorResponseModel
from app.models.channels import ConnectOut, OAuthOut, Tokens, ReTweet, FavoritesTweet

twitter_view = APIRouter()

# -------------------- AUTH ROUTES --------------------

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
    created_channel = await create_channel(user_id=tokens.user_id, channel_name="twitter",channel_obj=twitterDict)

    if created_channel == None:
        return ErrorResponseModel(
            error="Something went wrong while creating user profile",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Get Your Profile. Please Try Again."
        )

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=profile)

# -------------------- API ROUTES --------------------

# GET METHODS
@twitter_view.get("/feed/", description="GET FEED/HOME TIMELINE FOR USER")
async def get_feed(user_id: str, page: int):
    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])
    tweets = api.get_user_feed(page)

    if tweets == None:
        return ErrorResponseModel(
            error="Something went wrong while fetching user feed.",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Get Your Feed. Please Try Again Later."
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"feed": tweets})


@twitter_view.get("/search", description="GET TWEETS BASED ON SEARCH QUERY FOR USER")
async def search_tweets(user_id: str, query: str, page: int, geocode: Optional[str] = None):

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

    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])

    tweets = api.get_searched_tweets(new_query, page, geocode)
    if tweets == None:
        return ErrorResponseModel(
            error="Something went wrong while searching for topic",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Search Your Topic."
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"searched_tweets": tweets['statuses']})


@twitter_view.get("/tweet", description="FETCH TWEET DETAILS BY ID")
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

# POST METHODS

@twitter_view.post("/tweet", description="CREATE TWEET/ CREATE TWITTER STATUS (WITH AND WITHOUT MEDIA)")
async def create_tweet(files: Optional[List[UploadFile]] = File(None), user_id: str = Form(...),text: str = Form(...)):
    channel = await get_channel_details(user_id=user_id)

    if channel == None:
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

    return JSONResponse(content=tweet, status_code=status.HTTP_201_CREATED)


@twitter_view.post("/tweet/schedule",description="SCHEDULE TWEET/ SCHEDULE TWITTER STATUS (WITH AND WITHOUT MEDIA)")
async def schedule_tweet(files: Optional[List[UploadFile]] = File(None), user_id: str = Form(...),
text: str = Form(...), scheduled_datetime: Optional[str] = Form(None), time_format: Optional[str] = Form(None)):
    channel = await get_channel_details(user_id=user_id)

    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )

    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])

    # check if post is to be scheduled
    media=await scheduled_media_handler(files=files)
    if isinstance(media, dict):
        # Error returned
        return media
    
    # if success
    scheduled_post = {
        "user_id":user_id,
        "text":text,
        "scheduled_datetime":scheduled_datetime,
        "timeformat":time_format,
        "files": media
    }
    post_created = await post_saver(scheduled_post=scheduled_post)
    if post_created == None:
        return ErrorResponseModel(
            error="Could Not Schedule New Tweet",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Your Tweet was not scheduled. Please Try Again."
        )
    # convert ObjectId to String for JSON
    post_created['_id'] = str(post_created['_id'])
    
    return JSONResponse(content=post_created, status_code=status.HTTP_201_CREATED)


@twitter_view.post("/reply", description="REPLY TO TWEET (WITH AND WITHOUT MEDIA)")
async def reply_tweet(files: Optional[List[UploadFile]] = File(None), tweet_id: str = Form(...), user_id: str = Form(...), text: str = Form(...)):
    channel = await get_channel_details(user_id=user_id)
    if channel == None:
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

    tweet = api.reply_tweet(text, media_response, tweet_id)
    if tweet == None:
        return ErrorResponseModel(
            error="Could Not Reply to Tweet",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Your Reply was not created. Please Try Again."
        )
    return JSONResponse(content=tweet, status_code=status.HTTP_201_CREATED)

# PATCH METHODS

@twitter_view.patch("/favorite", description="FAVORITE/LIKE A TWEET")
async def favorite_tweet(data: FavoritesTweet = Body(...)):
    
    channel = await get_channel_details(user_id=data.user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )

    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])

    if data.favorite=="False":
        tweet = api.destory_favorite_tweet(data.tweet_id)
    else:
        tweet = api.favorites_tweet(data.tweet_id)

    if tweet == None:
        return ErrorResponseModel(
            error="Could Not Favorite Tweet",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Your Tweet was not favorited. Please Try Again."
        )

    return JSONResponse(content=tweet, status_code=status.HTTP_202_ACCEPTED)


@twitter_view.patch("/retweet", description="RETWEET/ UNDO RETWEET")
async def re_tweet(data: ReTweet = Body(...)):

    channel = await get_channel_details(user_id=data.user_id)

    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )

    api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])

    if data.retweet=="False":
        tweet = api.un_retweet(data.tweet_id)
    else:
        tweet = api.re_tweet(data.tweet_id)
    
    if tweet == None:
        return ErrorResponseModel(
            error="Could Not ReTweet.",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could not perform Retweet. Please Try Again."
        )

    return JSONResponse(content={"message":"Message has been retweeted."}, status_code=status.HTTP_202_ACCEPTED)
