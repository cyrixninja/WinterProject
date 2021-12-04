from datetime import time
import re
import requests
from twilio.twiml.messaging_response import MessagingResponse
import os
import requests   
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image, ImageOps
import numpy as np


app = Flask(__name__)

def respond(message):
    response = MessagingResponse()
    response.message(message)
    return str(response)

def classifier(img, file):
    np.set_printoptions(suppress=True)
    model = keras.models.load_model(file)
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    image = img
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array
    prediction = model.predict(data)
    return prediction

@app.route('/bot', methods=['POST'])
def reply():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()
    sender = request.form.get('From')
    message = request.form.get('Body')
    media_url = request.form.get('MediaUrl0')
    print(media_url)
    print(f'{sender} sent {message}')
    response = requests.get(media_url)
    if response.status_code == 200:
        with open("data.jpg", 'wb') as f:
            f.write(response.content)
    image = Image.open("data.jpg").convert('RGB')
    label = classifier(image, 'model.h5')
    winter= (label[0][0])
    summer= (label[0][1])
    if winter >= 0.6:
        msg.media('https://www.almanac.com/sites/default/files/styles/landscape/public/image_nodes/winter_sunrise-2.jpg')
        msg.body("Favorable in Winter.Not suitable in Summer conditions")
        
    elif summer >= 0.6:
        msg.media('https://adminassets.devops.arabiaweather.com/sites/default/files/field/image/Summer-beach-image.jpg')
        msg.body("Favorable in Summers. Not good for Cold Weather")
  
    return str(resp)
if __name__ == '__main__':
    app.run()