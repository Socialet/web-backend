from datetime import datetime
from dateutil import parser,tz
import tzlocal
from bson import ObjectId
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.controllers.twitter import fetch_follower_details
from app.db.connect import posts
from app.db.connect import channels
from app.controllers.posts import post_scheduled_tweet
# from app.controllers.twitter import post_scheduled_tweet
from app.config import get_logger
from app.services.api.twitterAPI import TwitterAPI

logger = get_logger()

async def tweet_scheduler():

    posts_list = [document async for document in posts.find({})]
    for post in posts_list:
        # Auto-detect zones:
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()

        myDate = parser.parse(post['scheduled_datetime']).strftime("%Y-%m-%d %H:%M:%S")
        utc = datetime.strptime(myDate, '%Y-%m-%d %H:%M:%S')

        # Tell the datetime object that it's in UTC time zone since 
        utc = utc.replace(tzinfo=from_zone)

        # Convert time zone
        central = utc.astimezone(to_zone)
        now = datetime.now()
        if now.date()==central.date() and now.hour == central.hour and now.minute == central.minute and (not post['published'] or not post['expired']):
            res=await post_scheduled_tweet(post)
            if res==True:
                logger.info(f"Scheduled Post ID-{str(post['_id'])} Published Successfully on scheduled Date and Time: {central.date()} {central.time()}")
                await posts.update_one({'_id':ObjectId(post['_id'])}, {'$set': {'published': True,'expired': True}})
            else:
                # if could not publish due to some problem
                logger.error(f"Scheduled Post ID-{str(post['_id'])} Could Not Be Published on scheduled Date and Time: {central.date()} {central.time()}")
                await posts.update_one({'_id':ObjectId(post['_id'])}, {'$set': {'published': False,'expired': True}})
            
async def follow_counter():

    channels_list = [document async for document in channels.find({})]
    for channel in channels_list:
        api = TwitterAPI(access_token=channel['twitter']['access_token'],
                     access_token_secret=channel['twitter']['access_token_secret'])
        current = await fetch_follower_details(channel,api,channel['twitter']['screen_name'])
        now = datetime.utcnow()
        current_followers = {
            'date': now,
            'count': current['followers']
        }
        current_followings = {
            'date': now,
            'count': current['followings']
        }

        temp = []
        if channel['twitter']['followers']!=None and len(channel['twitter']['followers'])>0:
            temp = channel['twitter']['followers']
            temp.append(current_followers)
        else:
            temp.append(current_followers)

        temp1 = []
        if channel['twitter']['followings']!=None and len(channel['twitter']['followings'])>0:
            temp1 = channel['twitter']['followings']
            temp1.append(current_followings)
        else:
            temp1.append(current_followings)

        await channels.update_one({'_id':ObjectId(channel['_id'])}, {'$set': {'twitter.followers': temp,'twitter.followings': temp1}})
        print("JOB DONE!! \n Updated the follower count")


class TwitterScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
        
    def starter(self):
        self.scheduler.add_job(tweet_scheduler,trigger='cron', minute='*')
        self.scheduler.add_job(follow_counter,trigger='cron',  hour='00', minute='01')

        logger.info("Post Scheduler is Up and Running...")
        self.scheduler.start()

    def stopper(self):
        self.scheduler.shutdown(wait=False)