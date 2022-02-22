from fastapi import APIRouter, Body
from app.toolkit.EmotionRecognition.model import EmotionRecognitionModel
from app.toolkit.LanguageDetection.model import LanguageDetection
from app.models.emotions import EmotionsBody

emotions_view = APIRouter()


@emotions_view.post("/recognise")
async def recognise(body_data: EmotionsBody = Body(...)):
    tweets_with_emotions = []
    for tweet in body_data.tweets:
        extracted_tweet = tweet.tweet
        try:
            langDetector = LanguageDetection()
            lang = langDetector.predict_lang(extracted_tweet)[0][0]
        except:
            lang = None

        if lang != None and lang == "__label__en":
            model = EmotionRecognitionModel()
            tweet_list = []
            tweet_list.append(extracted_tweet)
            tweet_with_emotion = model.recognise_emotion(tweet_list)
            tweet_with_emotion["id"] = tweet.id
            tweets_with_emotions.append(tweet_with_emotion)
        else:
            non_eng = {"id": tweet.id, "tweet": extracted_tweet, "emotion": "neutral"}
            tweets_with_emotions.append(non_eng)

    return {"tweets": tweets_with_emotions}
