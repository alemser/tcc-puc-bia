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

DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "alemser"
DB_PASS = ""
DB_NAME = "postgres"
LABEL_FNAME = "labels.txt";

model = tf.keras.models.load_model("keras_model.h5")
print("Modelo pronto")

categorias_existentes = {}

with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT) as conn:
    with conn.cursor() as cur:
        conn.autocommit = True
        cur.execute("""SELECT id_categoria, nm_categoria FROM d_categoria""")
        for record in cur:
            categorias_existentes[record[1]] = record[0]

        print("Mapa de categorias pronto")

        count = 0
        cur.execute(
            """SELECT i.id_imagem, i.nm_url
               FROM d_imagem i
               JOIN f_venda f ON f.id_imagem = i.id_imagem""")
        for record in cur:
            try:
                req = urllib.request.urlopen(record[1])
                arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
                image = cv2.imdecode(arr, -1)

                img = cv2.resize(image,(224,224))
                img = np.array(img,dtype=np.float32)
                img = np.expand_dims(img,axis=0)

                img = img/255

                prediction = model.predict(img)
                predicted_class = np.argmax(prediction[0], axis=-1)
                max_prob = int(max(prediction[0]) * 100)

                id_categoria = 0
                if 0 == predicted_class:
                    id_categoria = categorias_existentes["Natureza"]
                if 1 == predicted_class:
                    id_categoria = categorias_existentes["Esporte"]
                if 2 == predicted_class:
                    id_categoria = categorias_existentes["Casamento"]
                if 3 == predicted_class:
                    id_categoria = categorias_existentes["Retrato"]

                insert_cursor = conn.cursor()
                insert_cursor.execute("""Update d_imagem Set id_categoria_ml = %s, nu_categoria_ml_prob = %s Where id_imagem = %s""", (id_categoria, max_prob, record[0]))
                conn.commit()
                count = count + 1
                print(count, "registros processados")
            except Exception as e:
                print("Error:", e)

    print("Terminado")
