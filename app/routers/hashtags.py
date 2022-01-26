from fastapi import APIRouter,UploadFile,File
from typing import List, Optional
from app.toolkit.HashtagRecommender.model import HashtagRecommenderModel
from app.utils.image_processing import read_image

hashtags_view = APIRouter()

@hashtags_view.post("/recommend")
async def recommend(files: Optional[List[UploadFile]] = File(None)):
    hashtags = []
    for file in files:
        extension = file.filename.split(".")[-1] in ("jpg", "jpeg", "png")
        if not extension:
            return "Image must be jpg or png format!"
        image = read_image(await file.read())
        model = HashtagRecommenderModel()
        image_hashtags=model.recommend_hashtags(image)
        hashtags.extend(image_hashtags)
    hashtags = list(set(hashtags))
    return {
        "hashtags":hashtags
    }
