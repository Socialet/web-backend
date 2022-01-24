from PIL import Image
from io import BytesIO
import tensorflow as tf

def read_image(image_encoded):
    image = Image.open(BytesIO(image_encoded))
    return image
    

def preprocess(image: Image.Image):
    img = tf.cast(image, tf.float32)
    img = (img/127.5) - 1
    img = tf.image.resize(img, (160, 160))
    # Reshape grayscale images to match dimensions of color images
    if img.shape != (160, 160, 3):
        img = tf.concat([img, img, img], axis=2)
    
    return img