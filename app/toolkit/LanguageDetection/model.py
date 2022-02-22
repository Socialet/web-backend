import os
import fasttext


class LanguageDetection:

    def __init__(self):
        pretrained_lang_model = os.path.join(os.path.dirname(__file__), './trained_model/lid.176.ftz')
        # suppress warning
        fasttext.FastText.eprint = lambda x: None
        # loading pretrained model
        self.model = fasttext.load_model(pretrained_lang_model)

    def predict_lang(self, text):
        # returns top 1 matching language
        predictions = self.model.predict(text, k=1)
        return predictions