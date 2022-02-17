from fastapi import APIRouter, Body, status
from fastapi.responses import JSONResponse
from app.models.main import ErrorResponseModel
from app.models.profile import SurveyData
from app.controllers.profile import create_profile,get_social_accounts,disconnect_social_account

profile_view = APIRouter()


@profile_view.post('/survey', response_description="POST SURVEY DATA UPON NEW USER REGISTRATION")
async def survey_upon_new_user_registration(survey_data: SurveyData = Body(...)):
    await create_profile(survey_data)
    return JSONResponse(content='Thanks for filling 😊', status_code=status.HTTP_200_OK)


@profile_view.get('/social/accounts', response_description="GET ALL SOCIAL ACCOUNTS INFO BY USER ID")
async def get_social_sccounts_details_of_user(user_id: str):
    user_accounts_details = await get_social_accounts(user_id)
    return JSONResponse(content=user_accounts_details, status_code=status.HTTP_200_OK)


@profile_view.patch('/social/account', response_description="DELETE SPECIFIC SOCIAL ACCOUNT FROM THE USER CHANNELS")
async def delete_social_account_of_user(bodyData = Body(...)):
    delete_account = await disconnect_social_account(bodyData['user_id'], bodyData['social_account_name'])
    if delete_account==None:
        return ErrorResponseModel(
            error="Attempt to Disconnect Channel Failed.",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Attempt to Disconnect Channel Failed. Please Try Again."
        )

    return JSONResponse(content=bodyData['social_account_name'] + " disconnected successfully", status_code=status.HTTP_200_OK)
