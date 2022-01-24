from fastapi import APIRouter
from app.routers import posts,hashtags

app_api = APIRouter()

app_api.include_router(posts.post_view,prefix="/posts",tags=["posts"])
app_api.include_router(hashtags.hashtags_view,prefix="/hashtags",tags=['hashtags'])