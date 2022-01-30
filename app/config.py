import os
from dotenv import load_dotenv

load_dotenv()

TWITTER_API_KEY=os.getenv('API_KEY_3')
TWITTER_API_KEY_SECRET=os.getenv('API_KEY_SECRET_3')
TWITTER_BEARER_TOKEN=os.getenv('BEARER_TOKEN_3') 

MONGODB_DETAILS = os.getenv("MONGODB_URL")