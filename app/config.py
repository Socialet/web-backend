import os
from dotenv import load_dotenv
from datetime import datetime
import logging
import cloudinary

load_dotenv()

TWITTER_API_KEY=os.getenv('API_KEY_3')
TWITTER_API_KEY_SECRET=os.getenv('API_KEY_SECRET_3')
TWITTER_BEARER_TOKEN=os.getenv('BEARER_TOKEN_3')

# Facebook
FACEBOOK_APP_ID=os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET=os.getenv('FACEBOOK_APP_SECRET')
FACEBOOK_REDIRECT_URI=os.getenv('redirect_uri_encoded')

MONGODB_DETAILS = os.getenv("MONGODB_URL")

def application_shutdown():

    file_path = os.path.join(os.getcwd(),f'logs\log.txt')
    if not os.path.exists(os.path.join(os.getcwd(),f'logs')):
        os.makedirs(os.path.join(os.getcwd(),f'logs'))

    with open(file_path, mode="a") as log:
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log.write(f"\nApplication shutdown: {date}")
    log = logging.getLogger("uvicorn")
    
    log.info("Shutting down server gracefully...")
    log.info("Check logs to find more info...")
    
    return None

def get_logger():
    logger = logging.getLogger("uvicorn")
    return logger

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_KEY_SECRET')
)