from pydantic import BaseModel, Field
from bson import ObjectId
from app.models.main import PyObjectId


class PostSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    text: str = Field(...)
    views: int = Field(..., ge=0)
    likes: int = Field(..., ge=0)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "text":"This is a post",
                "views": 4,
                "likes": 10,
            }
        }
