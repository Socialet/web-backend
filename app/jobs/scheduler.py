from datetime import datetime
from dateutil import parser,tz
import tzlocal
from bson import ObjectId
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.connect import posts
from app.controllers.posts import post_scheduled_tweet
from app.config import get_logger

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
        if now.date()==central.date() and now.hour == central.hour and now.minute == central.minute:
            res=await post_scheduled_tweet(post)
            if res==True:
                logger.info(f"Scheduled Post ID-{str(post['_id'])} Published Successfully on scheduled Date and Time: {central.date()} {central.time()}")
                await posts.update_one({'_id':ObjectId(post['_id'])}, {'$set': {'published': True,'expired': True}})
            else:
                # if could not publish due to some problem
                logger.error(f"Scheduled Post ID-{str(post['_id'])} Could Not Be Published on scheduled Date and Time: {central.date()} {central.time()}")
                await posts.update_one({'_id':ObjectId(post['_id'])}, {'$set': {'published': False,'expired': True}})
            

class TwitterScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
        
    def starter(self):
        self.scheduler.add_job(tweet_scheduler,trigger='cron', minute='*')
        logger.info("Post Scheduler is Up and Running...")
        self.scheduler.start()

    def stopper(self):
        self.scheduler.shutdown(wait=False)