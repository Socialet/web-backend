from fastapi import APIRouter
from app.routers import example,hashtags,twitter,profile

app_api = APIRouter()

app_api.include_router(example.post_view,prefix="/example",tags=["example"])
app_api.include_router(hashtags.hashtags_view,prefix="/hashtags",tags=['hashtags'])
app_api.include_router(twitter.twitter_view,prefix="/twitter",tags=['twitter'])
app_api.include_router(profile.profile_view,prefix="/profile",tags=['profile'])