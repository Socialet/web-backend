import tensorflow as tf
import numpy as np
import pickle
import os
import re
import text2emotion as te


class EmotionRecognitionModel():
    def __init__(self) -> None:
        self.model = tf.keras.models.load_model(os.path.join(os.path.dirname(__file__), './trained_model/emotion_model.h5'))
        self.index_to_classes = {0: 'fear', 1: 'anger', 2: 'sadness', 3: 'surprise', 4: 'joy', 5: 'love'}
        self.classes_to_index = {'anger': 1, 'fear': 0, 'joy': 4, 'love': 5, 'sadness': 2, 'surprise': 3}

    def preprocess(self, tweets):
        whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ$')
        for tweet in tweets:
            tweet = tweet.lower()
            tweet = re.sub('http[s]?://\S+', '', tweet)
            answer = ''.join(filter(whitelist.__contains__, tweet))
            tweet = answer
        return tweets

    def get_sequences(self, tokenizer, tweets):
        sequences = tokenizer.texts_to_sequences(tweets)
        padded_sequences = tf.keras.preprocessing.sequence.pad_sequences(sequences, truncating='post', maxlen=50, padding='post')
        return padded_sequences
    
    def create_tokenizer(self):
        path = os.path.join(os.path.dirname(__file__), './trained_model/tokenizer.pickle')
        with open(path, 'rb') as handle:
            tokenizer = pickle.load(handle)
        return tokenizer
        
    def recognise_emotion(self, tweet):
        tweet = self.preprocess(tweet)
        tokenizer = self.create_tokenizer();
        tweet_sequence = self.get_sequences(tokenizer, tweet)
        predict_x= self.model(np.expand_dims(tweet_sequence, axis=-1))
        classes_x= np.argmax(predict_x)
        emotion = self.index_to_classes.get(classes_x)
        tweet_and_emotion = {'tweet':tweet[0],'emotion':emotion}
        return tweet_and_emotion
    
    # second method
    def preprocess_text2emotion(self, tweet):
        whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ$')
        tweet = tweet.lower()
        tweet = re.sub('http[s]?://\S+', '', tweet)
        answer = ''.join(filter(whitelist.__contains__, tweet))
        return answer

    def recognize_emotion_text2emotion(self,text):
        res_tweet=self.preprocess_text2emotion(text)
        emotions=te.get_emotion(res_tweet)
        return emotions