#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import cv2
from time import sleep
import tensorflow.keras
from keras.preprocessing import image
import tensorflow as tf

model = tensorflow.keras.models.load_model("keras_model.h5")


image = cv2.imread("img_sport.jpg")
img = cv2.resize(image,(224,224))
img = np.array(img,dtype=np.float32)
img = np.expand_dims(img,axis=0)

img = img/255

prediction = model.predict(img)
predicted_class = np.argmax(prediction[0], axis=-1)

if 0 == predicted_class:
    print("Natureza")

if 1 == predicted_class:
    print("Esporte")
