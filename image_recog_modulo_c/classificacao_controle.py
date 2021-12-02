#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import cv2
from time import sleep
import tensorflow.keras
from keras.preprocessing import image
import tensorflow as tf
import psycopg2
import urllib.request
import os

controle_dir = os.getcwd() + "/training_data/controle/"
for f in os.listdir(controle_dir):
    if f.endswith(".miss"):
        os.remove(os.path.join(controle_dir, f))

model = tf.keras.models.load_model("keras_model.h5")

categorias_existentes = ["Natureza", "Esporte", "Casamento", "Retrato"]

for categ in categorias_existentes:
    for i in range(1, 11):
        try:
            req = urllib.request.urlopen("file://" + controle_dir + categ + str(i) + ".jpg")
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            image = cv2.imdecode(arr, -1)

            img = cv2.resize(image,(224,224))
            img = np.array(img,dtype=np.float32)
            img = np.expand_dims(img,axis=0)

            img = img/255

            prediction = model.predict(img)
            predicted_class = np.argmax(prediction[0], axis=-1)
            max_prob = int(max(prediction[0]) * 100)

            if categ != categorias_existentes[predicted_class]:
                print(categ, " difere de ", categorias_existentes[predicted_class])
                f = open(controle_dir + categ + str(i) + ".miss", "a")
                f.write("Classificado pelo modelo como: " + categorias_existentes[predicted_class])
                f.close()

        except Exception as e:
            print("Error:", e)

print("Processamento finalizado")
