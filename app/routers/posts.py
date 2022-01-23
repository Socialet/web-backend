from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

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