from fastapi import APIRouter
from typing import Optional
from app.services.auth.twitterOAuth import TwitterOAuth
from app.services.api.twitterAPI import TwitterAPI
from pydantic import BaseModel

twitter_view = APIRouter()

class Tokens(BaseModel):
    oauth_token: Optional[str] = None
    oauth_verifier: Optional[str] = None

@twitter_view.get("/connect")
def twitter_connect():
    oAuth = TwitterOAuth()
    auth_url=oAuth.fetch_auth_url()
    return {
        "oauth_url":auth_url
    }

@twitter_view.post("/oauth")
def fetch_access_tokens(tokens: Tokens):
    oAuth = TwitterOAuth()
    # pass received oauth_tokens(request_token) and oauth_verifier to fetch access tokens for user.
    access_token,access_token_secret,user_id,screen_name=oAuth.fetch_access_tokens(tokens.oauth_token,tokens.oauth_verifier)

    api = TwitterAPI(access_token=access_token,access_token_secret=access_token_secret)
    profile=api.get_user_profile(user_id,screen_name)
    # save these objects in DB to retrieve later and make API calls.

    return profile