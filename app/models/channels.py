from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from bson import ObjectId
from app.models.main import PyObjectId

class Tokens(BaseModel):
    oauth_token: Optional[str] = None
    oauth_verifier: Optional[str] = None
    user_id:Optional[str] = None

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

class FavoritesTweet(BaseModel):
    tweet_id:str
    user_id:str
    favorite:str


class FollowUser(BaseModel):
    user_id: str
    id: str
    following: str

class ReTweet(BaseModel):
    tweet_id:str
    user_id:str
    retweet:str

class FollowerObject(BaseModel):
    date: str
    count: int

# OAuthSchema for twitter object in MongoDB Collection->Channel
class TwitterOAuthSchema(BaseModel):
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    user_id: Optional[str] = None
    screen_name: Optional[str] = None
    description: Optional[str] = None
    profile_image_url:Optional[HttpUrl] = None
    followers: Optional[List[FollowerObject]] = None
    followings: Optional[List[FollowerObject]] = None

# Schema for MongoDB Collection->Channel
class ChannelSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(...)
    twitter: Optional[TwitterOAuthSchema] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "id":"xxxxxxxxxxxxxxxxxx",
                "user_id": "xxxxxxxxxxxxx",
                "twitter": {
                    "access_token":"*************",
                    "access_token_secret":"************",
                    "user_id":"**************", # twitter user id
                    "screen_name":"profile44"
                }
            }
        }

