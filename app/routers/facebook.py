import requests
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from app.services.auth.facebookOAuth import FacebookOAuth
# from app.services.api.facebook import TwitterAPI
from app.models.main import ErrorResponseModel
from app.controllers.twitter import create_channel,get_channel_details

facebook_view = APIRouter()

# -------------------- AUTH ROUTES --------------------

@facebook_view.get("/connect", status_code=200)
def facebook_connect():
    oAuth = FacebookOAuth()
    auth_url = oAuth.fetch_auth_url()
    return JSONResponse(content=auth_url)

@facebook_view.get('/tokens',status_code=200)
async def facebook_access_token(code,user_id):
    oAuth = FacebookOAuth()
    res=oAuth.fetch_access_token(code=code)
    print(res)

    try:
        me_res=requests.get("https://graph.facebook.com/me",headers={
            "Authorization":f"Bearer {res['access_token']}"
        }).json()
    except:
        return ErrorResponseModel(error="Internal Server Error",code=500,message="Something went wrong while getting access tokens")
    # return access_token    
    print(f"me res: {me_res}")
    
    # get profile info
    try:
        profile = requests.get(f"https://graph.facebook.com/v6.0/{me_res['id']}?fields=first_name,last_name,picture.type(large)",headers={
            "Authorization":f"Bearer {res['access_token']}"
        }).json()
    except:
        return ErrorResponseModel(error="Internal Server Error",code=500,message="Something went wrong while getting access tokens")
        
    print(f"profile: {profile}")

    # save these objects in DB to retrieve later and make API calls.
    facebookDict = {
        "access_token": res['token_type'],
        "token_type":res['token_type'],
        "expires_in":res['expires_in'],
        "name": me_res['name'],
        "user_id": me_res['id'],
        "profile_image_url": profile['picture']['data']['url'],
    }

    # returns None if channel is not created
    created_channel = await create_channel(user_id=user_id, channel_name="facebook",channel_obj=facebookDict)

    if created_channel == None:
        return ErrorResponseModel(
            error="Something went wrong while creating user profile",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Could Not Get Your Profile. Please Try Again."
        )
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=facebookDict)


# -------------------- API ROUTES --------------------
@facebook_view.get("/feed/", description="GET FEED/HOME TIMELINE FOR USER",status_code=200)
async def get_page_feed(user_id:str):
    print(user_id)
    channel = await get_channel_details(user_id=user_id)
    if channel == None:
        return ErrorResponseModel(
            error="User Id Could Not be Found for channel.",
            code=status.HTTP_400_BAD_REQUEST,
            message="Channel Not Registered."
        )
    
    print(channel)
    # api = TwitterAPI(access_token=channel['twitter']['access_token'],
    #                  access_token_secret=channel['twitter']['access_token_secret'])
    # tweets = api.get_user_feed(page)

    # if tweets == None:
    #     return ErrorResponseModel(
    #         error="Something went wrong while fetching user feed.",
    #         code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         message="Could Not Get Your Feed. Please Try Again Later."
    #     )

    return JSONResponse(status_code=status.HTTP_200_OK, content={"feed": channel})
