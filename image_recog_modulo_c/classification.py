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

DB_HOST = 'localhost'
DB_PORT = 5432
DB_USER = 'alemser'
DB_PASS = ''
DB_NAME = 'postgres'

model = tensorflow.keras.models.load_model("keras_model.h5")

categorias_existentes = {}

with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT) as conn:
    with conn.cursor() as cur:
        cur.execute("""SELECT id_categoria, nm_categoria FROM d_categoria""")
        for record in cur:
            categorias_existentes[record[1]] = record[0]

        cur.execute("""SELECT id_imagem, nm_url FROM d_imagem limit 10""")
        for record in cur:
            req = urllib.request.urlopen(record[1])
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            image = cv2.imdecode(arr, -1)

            img = cv2.resize(image,(224,224))
            img = np.array(img,dtype=np.float32)
            img = np.expand_dims(img,axis=0)

            img = img/255

            prediction = model.predict(img)
            predicted_class = np.argmax(prediction[0], axis=-1)

            if 0 == predicted_class:
                print("Natureza", "Codigo", categorias_existentes["Natureza"])

            if 1 == predicted_class:
                print("Esporte", "Codigo", categorias_existentes["Esporte"])
