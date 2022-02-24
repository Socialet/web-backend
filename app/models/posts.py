from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId
from app.models.main import PyObjectId


class ReSchedulePostSchema(BaseModel):
    id: str
    scheduled_datetime: Optional[str]
    timeformat: Optional[str]

class UpdatePostSchema(BaseModel):
    id: str
    user_id: str
    text: str
    files: Optional[List[str]]
    scheduled_datetime: Optional[str]
    timeformat: Optional[str]
    isReply: bool
    replyTweetId: Optional[str]


class PostSchema(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str = Field(...)
    text: str = Field(...)
    files: Optional[List[str]] = Field(None)
    scheduled_datetime: Optional[str] = Field(None)
    timeformat: Optional[str] = Field(None)
    published: bool = Field(False)
    expired: bool = Field(False)
    isReply: bool = Field(False)
    replyTweetId: Optional[str] = Field(None)

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