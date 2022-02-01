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
        feed=self.api.home_timeline(count=20,tweet_mode="extended")
        return feed

    # geocode format --> '18.520430,73.856743,25km' (string)
    def get_searched_tweets(self, query, geocode):
        searched_tweets=self.api.search_tweets(q=query,geocode=geocode,tweet_mode="extended",count=100)
        return searched_tweets
    
    def upload_media(self,filename):
        try:
            media = self.api.media_upload(filename=filename)
        except Exception as e:
            print("Something went wrong while uploading the File.")
        return media.media_id_string

    def create_tweet(self,text,media_ids):
        try:
            new_tweet = self.api.update_status(status =text,media_ids = media_ids)
        except Exception as e:
            print("Something went wrong while creating new tweet.")
        return new_tweet