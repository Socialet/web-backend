import numpy as np
import tensorflow as tf
from io import BytesIO
  
def prepare_image(img_path, height=160, width=160, where='s3'):
    """Downsample and scale image to prepare it for neural network"""
    if where=='s3':
        img = fetch_image_from_s3_to_array('instagram-images-mod4', img_path)
    elif where == 'local':
    # If the image is stored locally:
        img = tf.io.read_file(img_path)
        img = tf.image.decode_image(img)
    img = tf.cast(img, tf.float32)
    img = (img/127.5) - 1
    img = tf.image.resize(img, (height, width))
    # Reshape grayscale images to match dimensions of color images
    if img.shape != (160, 160, 3):
        img = tf.concat([img, img, img], axis=2)
    return img


def extract_features(image, neural_network):
    """Return a vector of 1280 deep features for image."""
    image_np = image.numpy()
    images_np = np.expand_dims(image_np, axis=0)
    deep_features = neural_network.predict(images_np)[0]
    return deep_features