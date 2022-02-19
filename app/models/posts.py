from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId
from app.models.main import PyObjectId


class PostSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(...)
    text: str = Field(...)
    files: Optional[List[str]] = Field(None)
    scheduledDateTime: Optional[str] = Field(None)
    timeFormat: Optional[str] = Field(None)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "user_id": "694f3a10i2031345",
                "text":"This is a post",
                "files": ["https://stockphotos.com/456165","https://stockphotos.com/4561"],
                "scheduledDateTime":"",
                "timeFormat":""
            }
        }