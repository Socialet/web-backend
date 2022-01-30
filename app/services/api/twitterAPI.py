import tweepy
from app.config import TWITTER_API_KEY,TWITTER_API_KEY_SECRET

class TwitterAPI:
    def __init__(self,access_token,access_token_secret) -> None:
        self.api_key = TWITTER_API_KEY
        self.api_key_secret = TWITTER_API_KEY_SECRET
        self.access_token = access_token
        self.access_token_secret = access_token_secret
    
        auth = tweepy.OAuth1UserHandler(self.api_key,self.api_key_secret,self.access_token,self.access_token_secret)
        self.api = tweepy.API(auth)

    def get_user_profile(self,user_id,screen_name):
        profile = self.api.get_user(user_id=user_id,screen_name=screen_name,include_entities=1)

        return{
            "user_id":profile.id_str,
            "name":profile.name,
            "description":profile.description,
            "screen_name":profile.screen_name,
            "profile_image_url":profile.profile_image_url
        }
    
    def get_user_feed(self):
        feed=self.api.home_timeline(count=20)
        return feed