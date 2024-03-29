from pyparsing import FollowedBy
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
            "user_id":profile['id_str'],
            "name":profile['name'],
            "description":profile['description'],
            "screen_name":profile['screen_name'],
            "profile_image_url":profile['profile_image_url']
        }

    def get_user_feed(self, page_num):
        feed = []
        try:
            for page in tweepy.Cursor(self.api.home_timeline, tweet_mode="extended").pages(page_num):
                feed = page
        except Exception as e:
            self.logger.error(f"Something went wrong while fetching Feed: {str(e)}")
            return None
        return feed

    # geocode format --> '18.520430,73.856743,25km' (string)
    def get_searched_tweets(self, query, page ,geocode):
        searched_tweets=None
        try:
            for pageResult in tweepy.Cursor(self.api.search_tweets, q=query, geocode=geocode, tweet_mode="extended").pages(page):
                searched_tweets = pageResult
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
        return media['media_id_string']

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

    def favorites_tweet(self, tweet_id):
        try:
            fav_tweet = self.api.create_favorite(id = tweet_id)
        except Exception as e:
            self.logger.error(f"Something went wrong while liking the tweet: {str(e)}")
            return None
        return fav_tweet

    def destory_favorite_tweet(self,tweet_id):
        try:
            destroy_tweet = self.api.destroy_favorite(id = tweet_id)
        except Exception as e:
            self.logger.error(f"Something went wrong while disliking the tweet: {str(e)}")
            return None
        return destroy_tweet

    def re_tweet(self, tweet_id):
        try:
            retweet = self.api.retweet(id = tweet_id)
        except Exception as e:
            self.logger.error(f"Something went wrong while retweeting: {str(e)}")
            return None
        return retweet
    
    def un_retweet(self, tweet_id):
        try:
            retweet = self.api.unretweet(id = tweet_id)
        except Exception as e:
            self.logger.error(f"Something went wrong while unretweeting the tweet: {str(e)}")
            return None
        return retweet

    def get_user_posts(self, user_id, screen_name, page):
        posts = []
        try:
            for page in tweepy.Cursor(self.api.user_timeline, user_id=user_id, screen_name=screen_name, tweet_mode="extended").pages(page):
                posts = page
        except Exception as e:
            self.logger.error(
                f"Something went wrong while fetching Posts: {str(e)}")
            return None
        return posts

    def get_user_mentions_timeline(self, page):
        mentions = []
        try:
            for page in tweepy.Cursor(self.api.mentions_timeline, tweet_mode="extended").pages(page):
                mentions = page
        except Exception as e:
            self.logger.error(
                f"Something went wrong while fetching Posts: {str(e)}")
            return None
        return mentions

    def get_user_followers(self, user_id, screen_name, page):
        followers = []
        try:
            for page in tweepy.Cursor(self.api.get_followers, user_id=user_id, screen_name=screen_name, tweet_mode="extended").pages(page):
                followers = page
        except Exception as e:
            self.logger.error(
                f"Something went wrong while fetching User Followers: {str(e)}")
            return None
        return followers

    def get_user_following(self, user_id, screen_name, page):
        following = []
        try:
            for page in tweepy.Cursor(self.api.get_friends, user_id=user_id, screen_name=screen_name, tweet_mode="extended").pages(page):
                following = page
        except Exception as e:
            self.logger.error(
                f"Something went wrong while fetching User Following: {str(e)}")
            return None
        return following

    def get_user(self, user_id, screen_name):
        try:
           profile = self.api.get_user(
               user_id=user_id, screen_name=screen_name)
        except Exception as e:
            self.logger.error(
                f"Something went wrong while fetching User Profile: {str(e)}")
            return None
        return profile

    def follow_user(self, user_id):
        try:
            follow_tweet = self.api.create_friendship(
                user_id=user_id, follow=True)
        except Exception as e:
            self.logger.error(
                f"Something went wrong while following the user: {str(e)}")
            return None
        return follow_tweet

    def unfollow_user(self, user_id):
        try:
            unfollow_tweet = self.api.destroy_friendship(
                user_id=user_id, follow=True)
        except Exception as e:
            self.logger.error(
                f"Something went wrong while following the user: {str(e)}")
            return None
        return unfollow_tweet

    def get_followers(self, user_id):
        try:
            followers = self.api.get_followers(user_id=user_id)
        except Exception as e:
            self.logger.error(
                f"Something went wrong while fetching user followers: {str(e)}")
            return None
        return followers

    def get_my_tweets(self, user_id):
        try:
            tweets = self.api.user_timeline(tweet_mode="extended")
        except Exception as e:
            self.logger.error(
                f"Something went wrong while fetching user tweets: {str(e)}")
            return None
        return tweets

    def get_my_200_tweets(self, user_id):
        try:
            tweets = self.api.user_timeline(tweet_mode="extended",count=200)
        except Exception as e:
            self.logger.error(
                f"Something went wrong while fetching user tweets: {str(e)}")
            return None
        return tweets


    def get_mentions(self, user_id):
        try:
            timeline = self.api.mentions_timeline(
                user_id=user_id, include_rts=False)
        except Exception as e:
            self.logger.error(
                f"Something went wrong while fetching user mentions timeline: {str(e)}")
            return None
        return timeline
    
    
    def get_closest_trends(self,latitude,longitude):
        try:
            trends = self.api.closest_trends(latitude,longitude)
        except Exception as e:
            self.logger.error(
                f"Something went wrong while fetching closest trends: {str(e)}")
            return None
        return trends
    
    def get_place_trends(self,woeId):
        try:
            trends = self.api.get_place_trends(woeId)
        except Exception as e:
            self.logger.error(
                f"Something went wrong while fetching place trends: {str(e)}")
            return None
        return trends
    