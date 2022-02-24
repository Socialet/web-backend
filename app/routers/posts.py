from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse
from app.models.main import ErrorResponseModel
from app.models.posts import UpdatePostSchema, ReSchedulePostSchema
from app.controllers.posts import get_scheduled_posts, remove_scheduled_post, reschedule_scheduled_post, update_scheduled_post

posts_view = APIRouter()

# GET ALL SCHEDULED POSTS OF THE USER
@posts_view.get('/scheduled')
async def get_all_posts(user_id:str):
    posts = await get_scheduled_posts(user_id=user_id)
    for post in posts:
        post['_id']=str(post['_id'])
    return JSONResponse(content=posts,status_code=status.HTTP_200_OK)

# REMOVE SCHEDULED POST OF THE USER
@posts_view.patch('/schedule/remove')
async def remove_schedule_post(post_id:str):
    res = await remove_scheduled_post(post_id)
    if not res:
        return ErrorResponseModel(
            error="Something went wrong while removing scheduled post.",
            code=500,
            message="Removal of Scheduled Post did not occur."
        )
    
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)

# UPDATE A SCHEDULED POST -> CHECK MODEL FOR UNDERSTANDING DATA TO BE SENT
@posts_view.patch('/schedule/update')
async def update_schedule_post(updated_post: UpdatePostSchema = Body(...)):
    res = await update_scheduled_post(updated_post=updated_post)
    if res==None:
        return ErrorResponseModel(
            error="Could not Update the Post",
            code=500,
            message="Something went wrong while updating the Post"
        )
    res['_id'] = str(res['_id'])
    return JSONResponse(content=res,status_code=status.HTTP_202_ACCEPTED)

@posts_view.patch('/reschedule')
async def reschedule_post(scheduled_post: ReSchedulePostSchema = Body(...)):
    res = await reschedule_scheduled_post(scheduled_post=scheduled_post)
    if res==None:
        return ErrorResponseModel(
            error="Could not Reschedule the Post",
            code=500,
            message="Something went wrong while rescheduling the Post"
        )
    res['_id'] = str(res['_id'])
    return JSONResponse(content=res,status_code=status.HTTP_202_ACCEPTED)
