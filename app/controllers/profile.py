from app.db.connect import users, channels, profiles
from app.utils.helpers import fetch_social_accounts
from fastapi.encoders import jsonable_encoder
from bson import ObjectId


async def create_profile(survey_data):
    data = jsonable_encoder(survey_data)
    try:
        profile_inserted = await profiles.insert_one({"user_id": data['user_id'], "surveyData": data})
        ref_id_added_to_user = await users.update_one({"_id": ObjectId(data['user_id'])}, {"$set": {"profile_id": profile_inserted.inserted_id}})
    except:
        print("Some Error Occurred while creating profile.")
    
    return profile_inserted


async def get_social_accounts(user_id):
    available_accounts_of_user = {}
    accounts = fetch_social_accounts()
    channel = await channels.find_one({"user_id": user_id})


    if channel == None:
        return {account: False for account in accounts}
    
    channel = dict(channel)
    for account in accounts:
        if account in channel:
            available_accounts_of_user[account] = True
        else:
            available_accounts_of_user[account] = False

    return available_accounts_of_user


async def disconnect_social_account(user_id, social_account_name):
    channel = await channels.find_one({"user_id": user_id})
    if channel==None:
        return None
    await channels.update_one({"user_id": user_id}, {"$unset": {social_account_name: ""}})

    return channel
