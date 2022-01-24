import numpy as np
import joblib
import os
import time
from keras.models import load_model
from tqdm import tqdm
from annoy import AnnoyIndex
from app.toolkit.HashtagRecommender.preprocessors import extract_features
from app.utils.image_processing import preprocess

class HashtagRecommenderModel():
    def __init__(self) -> None:
        #Data reading
        self.recommender_df = joblib.load(os.path.join(os.path.dirname(__file__), './trained_model/recommender_df.pkl'))
        self.hashtag_features = joblib.load(os.path.join(os.path.dirname(__file__), './trained_model/hashtag_features.pkl'))
        self.hashtags_df = joblib.load(os.path.join(os.path.dirname(__file__), './trained_model/hashtags_df.pkl'))
        self.neural_network = load_model(os.path.join(os.path.dirname(__file__), './trained_model/neuralNet.h5'))
    
    def build_annoy_model(self):    
        rdf = self.recommender_df.copy()
        feature_dim = len(rdf['deep_features'][0])
        t = AnnoyIndex(feature_dim, metric='angular')
        deep_feature_list = rdf['deep_features'].tolist()

        for i in tqdm(range(len(deep_feature_list))):
            t.add_item(i, deep_feature_list[i])
            
        _ = t.build(1280)
        t.save("./trained_model/annoy_model.ann")
    
    def load_annoy_model(self):
        feature_dim = len(self.recommender_df['deep_features'][0])
        t = AnnoyIndex(feature_dim, metric='angular')

        t.load(os.path.join(os.path.dirname(__file__), './trained_model/annoy_model.ann'))
        return t

    #Defining function to get similar images output in dataframe of the base image index we give as parameter
    def get_similar_images_annoy(self,img):
        t = self.load_annoy_model()
        prep_image = preprocess(img)
        pics = extract_features(prep_image, self.neural_network)    
        similar_img_ids = t.get_nns_by_vector(pics, 10)
        return self.recommender_df.iloc[similar_img_ids[1:]]
    
    def recommend_hashtags(self,img):
        print(time.localtime())
        similar_images = self.get_similar_images_annoy(img)
        features = [item for item in similar_images['features']]        

        avg_features = np.mean(np.asarray(features), axis=0)

        # Add new column to the hashtag features which will be the dot product with the average image(user) features
        self.hashtag_features['dot_product'] = self.hashtag_features['features'].apply(lambda x: np.asarray(x).dot(avg_features))


        # Find the 10 hashtags with the highest feature dot products
        final_recs = self.hashtag_features.sort_values(by='dot_product', ascending=False).head(10)
        # Look up hashtags by their numeric IDs
        output = []
        for hashtag_id in final_recs.id.values:
            output.append(self.hashtags_df.iloc[hashtag_id]['hashtag'])
        print(time.localtime())
        return output