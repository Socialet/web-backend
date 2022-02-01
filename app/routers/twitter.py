from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from typing import Optional
from app.services.auth.twitterOAuth import TwitterOAuth
from app.services.api.twitterAPI import TwitterAPI
from app.controllers.twitter import create_channel, get_channel_details
from app.models.main import ErrorResponseModel
from app.models.channels import ConnectOut,OAuthOut,Tokens,FeedOut,TweetsOut

twitter_view = APIRouter()
   

@twitter_view.get("/connect",response_model=ConnectOut,status_code=200)
def twitter_connect():
    oAuth = TwitterOAuth()
    auth_url=oAuth.fetch_auth_url()
    return ConnectOut(oauth_url=auth_url)

@twitter_view.post("/oauth",response_model=OAuthOut,status_code=201)
async def fetch_access_tokens(tokens: Tokens):
    oAuth = TwitterOAuth()
    # pass received oauth_tokens(request_token) and oauth_verifier to fetch access tokens for user.
    access_token,access_token_secret,user_id,screen_name=oAuth.fetch_access_tokens(tokens.oauth_token,tokens.oauth_verifier)

    api = TwitterAPI(access_token=access_token,access_token_secret=access_token_secret)
    profile = api.get_user_profile(user_id,screen_name)

    # save these objects in DB to retrieve later and make API calls.
    twitterDict = {
        "access_token":access_token,
        "access_token_secret":access_token_secret,
        "user_id":user_id,
        "screen_name":screen_name,
        "description":profile['description'],
        "profile_image_url":profile['profile_image_url']
    }

    # returns None if channel is not created
    created_channel = await create_channel(user_id=tokens.user_id,twitterOAuth=twitterDict)
    
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=profile)


@twitter_view.get("/feed/",response_model=FeedOut,response_description="GET FEED/HOME TIMELINE FOR USER")
async def get_feed(user_id:str):
    channel=await get_channel_details(user_id=user_id)
    if channel==None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code= status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    api = TwitterAPI(access_token=channel['twitter']['access_token'],access_token_secret=channel['twitter']['access_token_secret'])
    tweets = api.get_user_feed()
    feed=[tweet._json for tweet in tweets]

    return FeedOut(feed=feed)
        

@twitter_view.get("/search",response_model=TweetsOut,response_description="GET TWEETS BASED ON SEARCH QUERY FOR USER")
async def search_tweets(user_id: str, query: str, geocode: Optional[str] = None):

    # query fomatting for hashtags
    new_query = ""
    if query.startswith('hashtag'):
        new_query = query.replace('hashtag', '#')
    else:
        new_query = query
    
    channel=await get_channel_details(user_id=user_id)
    if channel==None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code= status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )

    api = TwitterAPI(access_token=channel['twitter']['access_token'],access_token_secret=channel['twitter']['access_token_secret'])
    tweets = api.get_searched_tweets(new_query, geocode)     
    tweets=[tweet._json for tweet in tweets]
    return TweetsOut(tweets=tweets)