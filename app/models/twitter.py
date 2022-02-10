from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from bson import ObjectId
from app.models.main import PyObjectId


class SurveyData(BaseModel):
    user_id: str
    orgName: str
    numPeople: str
    location: str
    language: str
    role: str
    hereFor: List[str]
