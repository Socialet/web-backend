from fastapi import APIRouter, Body
from app.toolkit.EmotionRecognition.model import EmotionRecognitionModel
from app.toolkit.LanguageDetection.model import LanguageDetection
from app.models.emotions import EmotionsBody
from deep_translator import GoogleTranslator

emotions_view = APIRouter()


@emotions_view.post("/recognise")
async def recognise(body_data: EmotionsBody = Body(...)):
    tweets_with_emotions = []
    tweet_emotion_counter = {'Happy': 0.0, 'Angry': 0.0, 'Surprise': 0.0, 'Sad': 0.0, 'Fear': 0.0}
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
            # print(tweet_list)
            tweet_with_emotion = model.recognize_emotion_text2emotion(tweet_list[0])
            for key in tweet_with_emotion.keys():
                tweet_emotion_counter[key]+=tweet_with_emotion[key]
            # tweet_with_emotion = model.recognise_emotion(tweet_list)
            tweet_with_emotion["emotion"] = max(tweet_with_emotion, key=tweet_with_emotion.get)
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
    new_copy = {}

    new_copy['Happy'] = (tweet_emotion_counter['Happy']/sum(tweet_emotion_counter.values()))*100
    new_copy['Angry'] = (tweet_emotion_counter['Angry']/sum(tweet_emotion_counter.values()))*100
    new_copy['Surprise'] = (tweet_emotion_counter['Surprise']/sum(tweet_emotion_counter.values()))*100
    new_copy['Sad'] = (tweet_emotion_counter['Sad']/sum(tweet_emotion_counter.values()))*100
    new_copy['Fear'] = (tweet_emotion_counter['Fear']/sum(tweet_emotion_counter.values()))*100

        # tweet_emotion_counter[key] = ((tweet_emotion_counter[key]*100)/sum(tweet_emotion_counter.values()))
    return {"tweets": tweets_with_emotions, "chart_data":new_copy}
