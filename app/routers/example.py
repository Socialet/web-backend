from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from fastapi import APIRouter, Body,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse  

from app.models.example import PostSchema
from app.controllers.example import create_post,get_users

post_view = APIRouter()

# BaseModel is used to define request body paramters
class Post(BaseModel):
    text: str
    body: str
    published: Optional[bool] = False # setting default

# usage of query parameters
# directly try the query: localhost:8000/posts/?limit=20&published=False&sort=latest
@post_view.get('/posts')
def get_posts(limit=10,published: bool = True,sort: Optional[str]=None):
    """
    Limit has a default value attached here.(Used when argument is not used)
    published also has a default bool value
    sort is Optional Query Parameter.
    """
    return {
        'data':{
            'posts':[]
        }
    }

@post_view.post('/publish')
def publish_post(request: Post):
    """
    request can be named anything like post or anything else
    attributes can be accessed using request.title so on
    """
    return request


@post_view.post("/post", response_description="Post data added into the database",status_code=201)
async def add_post_data(post: PostSchema = Body(...)):
    # jsonable_encoder will give a dictionary
    post = jsonable_encoder(post)
    # call controller here -> create_post
    created_post = await create_post(post)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_post)

@post_view.get('/users',response_description="GET ALL users",status_code=200)
async def get_all_users():
    users = await get_users()
    return JSONResponse(status_code=status.HTTP_200_OK, content=users)