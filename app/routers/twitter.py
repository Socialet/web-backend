from fastapi import APIRouter
from typing import Optional
from app.services.auth.twitterOAuth import TwitterOAuth
from app.services.api.twitterAPI import TwitterAPI
from pydantic import BaseModel

twitter_view = APIRouter()

class Tokens(BaseModel):
    oauth_token: Optional[str] = None
    oauth_verifier: Optional[str] = None

# response model for GET REQUEST -> /twitter/connect
class ConnectOut(BaseModel):
    oauth_url: str

# response model for POST REQUEST -> /twitter/oauth
class OAuthOut(BaseModel):
    user_id: str
    name: str
    description: str
    screen_name: str
    profile_image_url: str
   

@twitter_view.get("/connect",response_model=ConnectOut)
def twitter_connect():
    oAuth = TwitterOAuth()
    auth_url=oAuth.fetch_auth_url()
    return {
        "oauth_url":auth_url
    }

@twitter_view.post("/oauth",response_model=OAuthOut)
def fetch_access_tokens(tokens: Tokens):
    oAuth = TwitterOAuth()
    # pass received oauth_tokens(request_token) and oauth_verifier to fetch access tokens for user.
    access_token,access_token_secret,user_id,screen_name=oAuth.fetch_access_tokens(tokens.oauth_token,tokens.oauth_verifier)

    api = TwitterAPI(access_token=access_token,access_token_secret=access_token_secret)
    profile=api.get_user_profile(user_id,screen_name)
    # save these objects in DB to retrieve later and make API calls.

    return profile