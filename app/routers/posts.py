from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.controllers.posts import get_scheduled_posts

posts_view = APIRouter()

@posts_view.get('/allposts')
async def get_all_posts(user_id:str):
    posts = await get_scheduled_posts(user_id=user_id)
    for post in posts:
        post['_id']=str(post['_id'])
    return JSONResponse(content=posts,status_code=status.HTTP_200_OK)