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

## Requisitos para execucao: requirements.txt

# Identificando o diretorio onde as imagens de controle estao
controle_dir = os.getcwd() + "/training_data/controle/"

# Removendo arquivos oriundos de classificacoes anteriores.
for f in os.listdir(controle_dir):
    if f.endswith(".miss"):
        os.remove(os.path.join(controle_dir, f))

# Carregamento do modelo gerado usando o Teachable Machine
model = tf.keras.models.load_model("keras_model.h5")

# Criado array com as categorias existentes
categorias_existentes = ["Natureza", "Esporte", "Casamento", "Retrato"]

for categ in categorias_existentes:
    for i in range(1, 11):
        # Para cada uma das 10 imagens de cada categoria, realizada a classificacao

        try:

            # Leitura e processamento da imagem
            req = urllib.request.urlopen("file://" + controle_dir + categ + str(i) + ".jpg")
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

            if categ != categorias_existentes[predicted_class]:
                # Modelo classificou de forma diferente - registrando isso no arquivo .miss
                print(categ, " difere de ", categorias_existentes[predicted_class])
                f = open(controle_dir + categ + str(i) + ".miss", "a")
                f.write("Classificado pelo modelo como: " + categorias_existentes[predicted_class])
                f.close()
        except Exception as e:
            print("Error:", e)

print("Processamento finalizado")
