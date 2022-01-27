import tweepy
from dotenv import load_dotenv
import os
import requests
from urllib.parse import urlparse,parse_qs

load_dotenv()  # take environment variables from .env.


class TwitterOAuth:
    def __init__(self) -> None:
        self.api_key = os.getenv('API_KEY_3')
        self.api_key_secret = os.getenv('API_KEY_SECRET_3')
        self.bearer_token = os.getenv('BEARER_TOKEN_3')
        self.oauth1_user_handler = tweepy.OAuth1UserHandler(self.api_key,self.api_key_secret,callback="http://localhost:3000/admin/redirect")

        self.access_token_url ="https://api.twitter.com/oauth/access_token"


    def fetch_auth_url(self):
        # Log in with Twitter, you can set the signin_with_twitter parameter when getting the authorization URL
        return self.oauth1_user_handler.get_authorization_url(signin_with_twitter=True)        
    
    def fetch_access_tokens(self,oauth_token,oauth_verifier):
        params = {
            "oauth_token":oauth_token,
            "oauth_verifier":oauth_verifier
        }
        try:
            res = requests.post(self.access_token_url,params=params)
        except:
            return {
                "error":"Internal Server Error",
                "message":"Something went wrong while accessing Tokens from Twitter"
            }
        # build url string with response to parse for query params received
        # https://api.twitter.com/oauth/access_token?oauth_token=XXXXX&oauth_token_secret=XXXXX&user_id=XXXXX&screen_name=XXXXX

        response_url = f"{self.access_token_url}?{res.text}"
        
        # parse response_url using urllib
        parsed_url = urlparse(response_url)

        # fetch all keys returned
        oauth_access_token = parse_qs(parsed_url.query)['oauth_token'][0]
        oauth_access_token_secret = parse_qs(parsed_url.query)['oauth_token_secret'][0]
        user_id = parse_qs(parsed_url.query)['user_id'][0]
        screen_name = parse_qs(parsed_url.query)['screen_name'][0]

        return oauth_access_token,oauth_access_token_secret,user_id,screen_name