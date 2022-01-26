import tensorflow as tf
import matplotlib.pyplot as plt
import joblib
import pickle
import collections
import random
import numpy as np
import os
import time
import json
from PIL import Image

class imageCaptioningModel():
    def __init__(self) -> None:
        #Data reading
        self.decoder = joblib.load(os.path.join(os.path.dirname(__file__), './trained_model/decoder.pkl'))
        self.image_features_extract_model = joblib.load(os.path.join(os.path.dirname(__file__), './trained_model/image_features_extract_model.pkl'))
        self.encoder = joblib.load(os.path.join(os.path.dirname(__file__), './trained_model/encoder.pkl'))
        self.tokenizer_disk = pickle.load(open("tokenizer.pkl", "rb"))
        self.tokenizer = tf.keras.layers.TextVectorization.from_config(self.tokenizer_disk['config'])
        self.tokenizer.adapt(tf.data.Dataset.from_tensor_slices(["xyz"]))
        self.tokenizer.set_weights(self.tokenizer_disk['weights'])

        self.word_to_index = tf.keras.layers.StringLookup(mask_token="", vocabulary= self.tokenizer.get_vocabulary())
        self.index_to_word = tf.keras.layers.StringLookup(mask_token="",vocabulary= self.tokenizer.get_vocabulary(), invert=True)

        self.BATCH_SIZE = 128
        self.BUFFER_SIZE = 1000
        self.embedding_dim = 256
        self.units = 512
        self.num_steps = len(24007) // self.BATCH_SIZE
        self.features_shape = 2048
        self.attention_features_shape = 64
        self.max_length = 50 
    
    def load_image(image_path):
        img = tf.io.read_file(image_path)
        img = tf.io.decode_jpeg(img, channels=3)
        img = tf.keras.layers.Resizing(299, 299)(img)
        img = tf.keras.applications.inception_v3.preprocess_input(img)
        return img, image_path

    def evaluate(self, image):
        attention_plot = np.zeros((self.max_length, self.attention_features_shape))
        hidden = self.decoder.reset_state(batch_size=1)
        temp_input = tf.expand_dims(self.load_image(image)[0], 0)
        img_tensor_val = self.image_features_extract_model(temp_input)
        img_tensor_val = tf.reshape(img_tensor_val, (img_tensor_val.shape[0],
                                                    -1,
                                                    img_tensor_val.shape[3]))
        features = self.encoder(img_tensor_val)
        dec_input = tf.expand_dims([self.word_to_index('<start>')], 0)
        result = [] 
        for i in range(self.max_length):
            predictions, hidden, attention_weights = self.decoder(dec_input, features, hidden)
            attention_plot[i] = tf.reshape(attention_weights, (-1, )).numpy()
            predicted_id = tf.random.categorical(predictions, 1)[0][0].numpy()
            predicted_word = tf.compat.as_text(self.index_to_word(predicted_id).numpy())
            result.append(predicted_word)
            if predicted_word == '<end>':
                return result, attention_plot
            dec_input = tf.expand_dims([predicted_id], 0)
        attention_plot = attention_plot[:len(result), :]
        return result, attention_plot