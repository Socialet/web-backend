from fastapi import APIRouter
from app.routers import hashtags,twitter,profile,emotions

app_api = APIRouter()

app_api.include_router(hashtags.hashtags_view,prefix="/hashtags",tags=['hashtags'])
app_api.include_router(twitter.twitter_view,prefix="/twitter",tags=['twitter'])
app_api.include_router(profile.profile_view,prefix="/profile",tags=['profile'])
app_api.include_router(emotions.emotions_view,prefix="/emotions",tags=['emotions'])