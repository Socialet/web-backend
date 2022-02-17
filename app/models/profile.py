from pydantic import BaseModel
from typing import List

class SurveyData(BaseModel):
    user_id: str
    orgName: str
    numPeople: str
    location: str
    language: str
    role: str
    hereFor: List[str]