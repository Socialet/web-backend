# from pyfacebook import GraphAPI
import requests
from urllib.parse import urlparse,parse_qs
from app.config import FACEBOOK_APP_ID,FACEBOOK_APP_SECRET,FACEBOOK_REDIRECT_URI
from app.models.main import ErrorResponseModel

class FacebookOAuth:
    def __init__(self) -> None:
        self.fb_app_id = FACEBOOK_APP_ID # app_id a.k.a client_id
        self.fb_app_secret = FACEBOOK_APP_SECRET
        self.fb_redirect_uri = FACEBOOK_REDIRECT_URI
        self.auth_endpoint = f"https://www.facebook.com/v6.0/dialog/oauth?client_id={self.fb_app_id}&redirect_uri={self.fb_redirect_uri}&scope=public_profile&state=Socialet"
        # self.api = GraphAPI(app_id=self.fb_app_id, app_secret=self.fb_app_secret, oauth_flow=True)
    # AUTH ENDPOINT
    def fetch_auth_url(self):
        auth_url = self.auth_endpoint
        return auth_url
    
    # ACCESS TOKEN ENDPOINT
    def fetch_access_token(self,code):
        self.token_endpoint = f"https://graph.facebook.com/v6.0/oauth/access_token?redirect_uri={self.fb_redirect_uri}&client_id={self.fb_app_id}&client_secret={self.fb_app_secret}&code={code}"
        try:
            access_token=requests.get(self.token_endpoint).json()
        except:
            return ErrorResponseModel(error="Internal Server Error",code=500,message="Something went wrong while getting access tokens")
        return access_token

    
    
    # def fetch_access_tokens(self,oauth_token,oauth_verifier):
    #     params = {
    #         "oauth_token":oauth_token,
    #         "oauth_verifier":oauth_verifier
    #     }
    #     try:
    #         res = requests.post(self.access_token_url,params=params)
    #     except:
    #         return {
    #             "error":"Internal Server Error",
    #             "message":"Something went wrong while accessing Tokens from Twitter"
    #         }
    #     # build url string with response to parse for query params received
    #     # https://api.twitter.com/oauth/access_token?oauth_token=XXXXX&oauth_token_secret=XXXXX&user_id=XXXXX&screen_name=XXXXX

    #     response_url = f"{self.access_token_url}?{res.text}"
        
    #     # parse response_url using urllib
    #     parsed_url = urlparse(response_url)

    #     # fetch all keys returned
    #     oauth_access_token = parse_qs(parsed_url.query)['oauth_token'][0]
    #     oauth_access_token_secret = parse_qs(parsed_url.query)['oauth_token_secret'][0]
    #     user_id = parse_qs(parsed_url.query)['user_id'][0]
    #     screen_name = parse_qs(parsed_url.query)['screen_name'][0]

    #     return oauth_access_token,oauth_access_token_secret,user_id,screen_name

