from fastapi import APIRouter
from app.routers import hashtags,twitter,profile,emotions,posts,dashboard,adminDashboard,facebook


app_api = APIRouter()

app_api.include_router(hashtags.hashtags_view,prefix="/hashtags",tags=['hashtags'])
app_api.include_router(twitter.twitter_view,prefix="/twitter",tags=['twitter'])
app_api.include_router(profile.profile_view,prefix="/profile",tags=['profile'])
app_api.include_router(emotions.emotions_view,prefix="/emotions",tags=['emotions'])
app_api.include_router(posts.posts_view,prefix="/posts",tags=['posts'])
app_api.include_router(dashboard.dashboard_view,prefix="/dashboard",tags=['dashboard'])
app_api.include_router(adminDashboard.admin_dashboard_view,prefix="/admin",tags=['Admin Dashboard'])
app_api.include_router(facebook.facebook_view,prefix="/facebook",tags=['Facebook'])
