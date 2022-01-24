from fastapi import APIRouter,UploadFile,File
from app.toolkit.HashtagRecommender.model import HashtagRecommenderModel
from app.utils.image_processing import read_image

hashtags_view = APIRouter()

@hashtags_view.post("/recommend")
async def recommend(file: UploadFile = File(...)):
    extension = file.filename.split(".")[-1] in ("jpg", "jpeg", "png")
    if not extension:
        return "Image must be jpg or png format!"
    image = read_image(await file.read())
    model = HashtagRecommenderModel()
    hashtags=model.recommend_hashtags(image)

    return {
        "data":{
            "hashtags":hashtags
        }
    }
