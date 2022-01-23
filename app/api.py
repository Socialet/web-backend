from fastapi import APIRouter
from app.routers import posts

app_api = APIRouter()

app_api.include_router(posts.post_view,prefix="/posts",tags=["posts"])