from app.db.connect import users,channels

async def create_channel(user_id:str,twitterOAuth: dict):
    channel = await channels.find_one({"user_id":user_id})
    if channel!=None:
        # do not insert as a new channel
        return None
    channel_inserted = await channels.insert_one({"user_id":user_id,"twitter":twitterOAuth})
    updated_user = await users.find_one_and_update({"_id": user_id},{'$set': {"channel_id":channel_inserted.inserted_id}})
    return channel_inserted

# gets channel details if channel exists
async def get_channel_details(user_id:str):
    channel = await channels.find_one({"user_id":user_id})
    if channel==None:
        return None
    return channel