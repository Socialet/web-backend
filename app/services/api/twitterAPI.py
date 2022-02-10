import tweepy
from app.config import TWITTER_API_KEY,TWITTER_API_KEY_SECRET,get_logger

class TwitterAPI:
    def __init__(self,access_token,access_token_secret) -> None:
        self.api_key = TWITTER_API_KEY
        self.api_key_secret = TWITTER_API_KEY_SECRET
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.logger = get_logger()
    
        auth = tweepy.OAuth1UserHandler(self.api_key,self.api_key_secret,self.access_token,self.access_token_secret)
        self.api = tweepy.API(auth,parser=tweepy.parsers.JSONParser())

    def get_user_profile(self,user_id,screen_name):
        try:
            profile = self.api.get_user(user_id=user_id,screen_name=screen_name,include_entities=1)
        except Exception as e:
            self.logger.error(f"Something went wrong while getting user profile: {str(e)}")
            return None

        return{
            "user_id":profile.id_str,
            "name":profile.name,
            "description":profile.description,
            "screen_name":profile.screen_name,
            "profile_image_url":profile.profile_image_url
        }
    
    def get_user_feed(self):
        try:
            feed=self.api.home_timeline(count=20,tweet_mode="extended")
        except Exception as e:
            self.logger.error(f"Something went wrong while fetching Feed: {str(e)}")
            return None
        return feed

    # geocode format --> '18.520430,73.856743,25km' (string)
    def get_searched_tweets(self, query, geocode):
        try:
            searched_tweets=self.api.search_tweets(q=query,geocode=geocode,tweet_mode="extended",count=100)
        except Exception as e:
            self.logger.error(f"Something went wrong while searching Topic: {str(e)}")
            return None
        return searched_tweets
    
    def upload_media(self,filename):
        try:
            media = self.api.media_upload(filename=filename)
        except Exception as e:
            self.logger.error(f"Something went wrong while uploading the File: {str(e)}")
            return None
        return media.media_id_string

    def create_tweet(self,text,media_ids):
        try:
            new_tweet = self.api.update_status(status =text,media_ids = media_ids)
        except Exception as e:
            self.logger.error(f"Something went wrong while creating new tweet: {str(e)}")
            return None
        return new_tweet
    
    def reply_tweet(self, text, media_ids, tweet_id):
        try:
            reply = self.api.update_status(status = text, media_ids = media_ids, in_reply_to_status_id = tweet_id , auto_populate_reply_metadata=True)
        except Exception as e:
            self.logger.error(f"Something went wrong while replying to tweet: {str(e)}")
            return None
        return reply
    
    def get_tweet(self, tweet_id):
        try:
            tweet = self.api.get_status(id = tweet_id)
        except Exception as e:
            self.logger.error(f"Something went wrong while fetching tweet by id: {str(e)}")
            return None
        return tweet
