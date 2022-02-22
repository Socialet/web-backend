from pydantic import BaseModel
from typing import List


class TweetItem(BaseModel):
    tweet: str
    id: int

class EmotionsBody(BaseModel):
    tweets: List[TweetItem]
