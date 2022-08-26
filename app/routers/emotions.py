from urllib import response
from fastapi import APIRouter, Body
from app.toolkit.EmotionRecognition.model import EmotionRecognitionModel
from app.toolkit.LanguageDetection.model import LanguageDetection
from app.models.emotions import EmotionsBody, TranslateBody
from deep_translator import GoogleTranslator

emotions_view = APIRouter()

@emotions_view.post("/translate")
async def translate(body_data: TranslateBody = Body(...)):
    try:
        translated = GoogleTranslator(
            'auto',body_data.language).translate(body_data.text)
    except:
        translated = None
        
    if translated != None:
        return_format = {"translated": translated}
    else:
        return_format = {"translated": "language not supported!"}
    return return_format
        
        
    

@emotions_view.post("/recognise")
async def recognise(body_data: EmotionsBody = Body(...)):
    tweets_with_emotions = []
    for tweet in body_data.tweets:
        extracted_tweet = tweet.tweet
        try:
            translated = GoogleTranslator(
                'auto', 'en').translate(extracted_tweet)
        except:
            translated = None

        if translated != None:
            model = EmotionRecognitionModel()
            tweet_list = []
            tweet_list.append(translated)
            tweet_with_emotion = model.recognise_emotion(tweet_list)
            tweet_with_emotion["id"] = tweet.id
            tweets_with_emotions.append(tweet_with_emotion)
        else:
            unsupported_format = {"id": tweet.id,
                                  "tweet": extracted_tweet, "emotion": "neutral"}
            tweets_with_emotions.append(unsupported_format)

        # if lang != None and lang == "__label__en":
        #     model = EmotionRecognitionModel()
        #     tweet_list = []
        #     tweet_list.append(extracted_tweet)
        #     tweet_with_emotion = model.recognise_emotion(tweet_list)
        #     tweet_with_emotion["id"] = tweet.id
        #     tweets_with_emotions.append(tweet_with_emotion)
        # else:
        #     print(GoogleTranslator('auto','en').translate('Hola!'))
        #     non_eng = {"id": tweet.id, "tweet": extracted_tweet, "emotion": "neutral"}
        #     tweets_with_emotions.append(non_eng)

    return {"tweets": tweets_with_emotions}
