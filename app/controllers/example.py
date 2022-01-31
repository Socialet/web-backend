from app.db.connect import posts_collection,users
from app.models.example import userHelper

async def create_post(post: dict):
    new_post = await posts_collection.insert_one(post)
    created_post = await posts_collection.find_one({"_id": new_post.inserted_id})
    return created_post

async def get_users():
    all_users = await users.find().to_list(10)
    res = [userHelper(x) for x in all_users]
    return res