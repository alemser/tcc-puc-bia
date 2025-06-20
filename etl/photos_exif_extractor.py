#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import psycopg2
from pathlib import Path
from etl.constants import DB_HOST, DB_PORT, DB_USER, DB_PASS, DB_NAME

class ImageUrlExtractor():

    def __init__(self, category, tags, max_record_count):
        self.photos_folder = "~/Pictures/Photos Library.photoslibrary/originals"

    def extract_urls(self, img_path):
        try:
            img = Image.open(img_path)
            exif_data = img._getexif()
            if not exif_data:
                return {}

            exif = {}
            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                exif[tag] = value
            return exif
        except Exception as e:
            print(f"Erro lendo EXIF da imagem {img_path}: {e}")
            return {}

    def inserir_info_basica_bd(self, img_path, categoria="PhotosLibrary"):

        exif = self.extract_urls(img_path)
        # Extrair campos úteis:
        dt = str(exif.get('DateTimeOriginal')) or str(exif.get('DateTime'))
        dt = dt.replace(":", "-", 2)
        if dt == 'None':   
            dt = None     
            
        camera = str(exif.get('Make', '')) + " " + str(exif.get('Model', '')) if str(exif.get('Make')) and (exif.get('Model')) else None

        focal_length = str(exif.get('FocalLength'))
        if isinstance(focal_length, tuple) and len(focal_length) == 2:
            focal_length = round(focal_length[0] / focal_length[1], 2) 
        if focal_length == 'None':   
            focal_length = None     

        titulo = os.path.basename(img_path)

        # Salvar no banco
        with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO t_fotografias (de_titulo, nm_url, nm_categoria_foto, dt_foto, nm_camera, nu_dist_focal)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (nm_url) DO NOTHING;
                """, (titulo, img_path, categoria, dt, camera, focal_length))
                print(f"Inserido no banco: {titulo}")

    def listar_e_processar_pasta(self, categoria="PhotosLibrary"):
        # Garante que self.photos_folder é uma string válida
        p = Path(self.photos_folder).expanduser()
        
        formatos = ['*.jpg', '*.jpeg', '*.heic', '*.png']
        arquivos = []
        for ext in formatos:
            arquivos.extend(p.rglob(ext))  # recursivo por padrão

        print(f"Encontrados {len(arquivos)} arquivos na pasta {p}")
        
        for arq in arquivos:
            self.inserir_info_basica_bd(str(arq), categoria)
