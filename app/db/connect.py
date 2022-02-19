from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGODB_DETAILS

client = AsyncIOMotorClient(MONGODB_DETAILS)

database = client.smwt

# get all collections here
users = database.get_collection("users")
channels = database.get_collection("channels")
profiles = database.get_collection("profiles")
posts = database.get_collection("posts")
