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

## Requisitos para execucao: requirements.txt

DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "alemser"
DB_PASS = ""
DB_NAME = "postgres"
LABEL_FNAME = "labels.txt";

# Carregamento do modelo gerado usando o Teachable Machine
model = tf.keras.models.load_model("keras_model.h5")

# Criado array com as categorias existentes
categorias_existentes = ["Natureza", "Esporte", "Casamento", "Retrato"]

# Array que ira conter o codigo que cada categoria possui no banco de dados (chave primaria)
codigo_categorias_no_bd = {}

with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT) as conn:
    with conn.cursor() as cur:
        conn.autocommit = True

        # Obtendo o codigo de cada categoria (chave primaria)
        cur.execute("""SELECT id_categoria, nm_categoria FROM d_categoria""")
        for record in cur:
            codigo_categorias_no_bd[record[1]] = record[0]

        # Execucao principal - obtendo a URL das imagens do banco de dados
        count = 0
        cur.execute(
            """SELECT i.id_imagem, i.nm_url
               FROM d_imagem i
               JOIN f_venda f ON f.id_imagem = i.id_imagem""")
        for record in cur:
            try:

                # Leitura e processamento da imagem
                req = urllib.request.urlopen(record[1])
                arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
                image = cv2.imdecode(arr, -1)

                img = cv2.resize(image,(224,224))
                img = np.array(img,dtype=np.float32)
                img = np.expand_dims(img,axis=0)

                img = img/255

                # Obtendo as predicoes a partir do modelo
                prediction = model.predict(img)

                # Obtendo a classe - inteiro que ira corresponder ao indice da categoria em categorias_existentes
                predicted_class = np.argmax(prediction[0], axis=-1)

                # Obtendo a probabilidade
                max_prob = int(max(prediction[0]) * 100)

                # Nome da categoria resultante da classificacao
                categoria_classificada = categorias_existentes[predicted_class]

                # Obtendo o ID (chave primaria) que a categoria possui no banco de dados
                id_categoria = codigo_categorias_no_bd[categoria_classificada]

                # Atualizando a dimensao d_imagens com a categoria classificada e a probabilidade
                insert_cursor = conn.cursor()
                insert_cursor.execute("""Update d_imagem Set id_categoria_ml = %s, nu_categoria_ml_prob = %s Where id_imagem = %s""", (id_categoria, max_prob, record[0]))
                conn.commit()
                count = count + 1
                print(count, "registros processados.", categoria_classificada, id_categoria)
            except Exception as e:
                print("Error:", e)

    print("Terminado")
