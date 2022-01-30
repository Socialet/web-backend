from app.db.connect import posts_collection

async def create_post(post: dict):
    new_post = await posts_collection.insert_one(post)
    created_post = await posts_collection.find_one({"_id": new_post.inserted_id})
    return created_post