#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import PIL.Image
from PIL.ExifTags import TAGS
import requests
import psycopg
import datetime
from threading import Thread
import time

class ExifWorker(Thread):
    """
        Obtem as URL armazenadas no BD e le o EXIF das respectivas imagens atualizando os registros no BD.
    """

    def __init__(self, categoria, max_record_count):
        Thread.__init__(self)
        self.max_record_count = max_record_count
        self.categoria = categoria
        self.relevant_exif = ['ShutterSpeedValue','ApertureValue','ISOSpeedRatings','LensSpecification','LensModel',
                        'LensMake','DateTimeOriginal','Make','Model','FocalLength','FocalLengthIn35mmFilm','Flash']
        self.exif_codes = {v: k for k, v in TAGS.items() if v in self.relevant_exif}
        self.allowed_to_stop = False

    def run(self):
        current_count = 0
        while True:
            current_count = current_count + self.extrair_exif(self.categoria)
            time.sleep(10)
            if current_count >= self.max_record_count and self.allowed_to_stop:
                print('Stopping worker....')
                break

    def extrair_exif(self, categoria):
        """Obtem URL de imagens da base de dados e le a informacao EXIF.
        Caso nao tenha informacao EXIF relevante, remove o regsitro da base"""

        record_count = 0
        with psycopg.connect("dbname=postgres user=alemser") as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT id_fotografia, nm_url FROM t_fotografias WHERE fl_lido = false LIMIT 100""")
                print('Processando {} records da categoria {}'.format(cur.rowcount, categoria))
                for record in cur:
                    try:
                        img = PIL.Image.open(requests.get(record[1], stream=True).raw)
                        exif_data = img._getexif()
                        if self.contem_relevante_exif_data(exif_data):
                            self.atualizar_exif(categoria, record[0], exif_data)
                        else:
                            self.max_record_count = self.max_record_count - 1
                            self.remover_sem_exif(record[0])
                    except Exception as e:
                        print(e)
                        print('[{}] enquanto lia a URL {}'.format(e.__class__, record[1]))
                print("{} registros processados".format(record_count))
        return record_count

    def remover_sem_exif(self, id_fotografia):
        """Remove informacao de fotografia sem EXIF relevante."""

        with psycopg.connect("dbname=postgres user=alemser") as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM t_fotografias WHERE id_fotografia = %s""", [id_fotografia])

    def atualizar_exif(self, categoria, id_fotografia, exif_data):
        """Atualiza os dados de EXIF para o registro de fotografia."""
        with psycopg.connect("dbname=postgres user=alemser") as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE t_fotografias
                    SET dt_coleta = %s,
                        dt_foto = %s,
                        tp_lente = %s,
                        nm_lente = %s,
                        nm_fabric_lente = %s,
                        nu_dist_focal = %s,
                        tp_camera = %s,
                        nm_camera = %s,
                        nm_fabric_camera = %s,
                        nu_dist_focal_35mmEq = %s,
                        nu_abertura = %s,
                        nu_tempo_exposicao = %s,
                        nu_iso = %s,
                        fl_flash = %s,
                        fl_lido = true
                    WHERE id_fotografia = %s
                      AND nm_categoria_foto = %s
                    """, (
                        datetime.datetime.now(),
                        self.parse_exif_date(exif_data),
                        self.tipo_lente(exif_data),
                        self.exif_from_dictNA(exif_data, 'LensModel'),
                        self.fabric_lente(exif_data),
                        self.decimal_exif(exif_data.get(self.exif_codes['FocalLength'])),
                        self.tipo_camera(exif_data),
                        self.exif_from_dictNA(exif_data, 'Model'),
                        self.exif_from_dictNA(exif_data, 'Make'),
                        self.decimal_exif(exif_data.get(self.exif_codes['FocalLengthIn35mmFilm'])),
                        self.decimal_exif(exif_data.get(self.exif_codes['ApertureValue'])),
                        self.decimal_exif(exif_data.get(self.exif_codes['ShutterSpeedValue'])),
                        self.decimal_exif(exif_data.get(self.exif_codes['ISOSpeedRatings'])),
                        self.flash(exif_data),
                        id_fotografia,
                        categoria))

    def exif_from_dictNA(self, exif_data, exif_code):
        value = self.exif_from_dict(exif_data, exif_code)
        return 'N/A' if not value else value

    def exif_from_dict(self, exif_data, exif_code):
        if not exif_data:
            return None
        value = exif_data.get(self.exif_codes[exif_code])
        return value if value else None

    def flash(self, exif_data):
        value = self.exif_from_dict(exif_data, 'Flash')
        if value:
            return True if value == 1 else False
        return False

    def tipo_camera(self, exif_data):
        """Tenta identificar os principais fabricantes e retorna se tipo é camera ou smartphone."""

        make = self.exif_from_dict(exif_data,'Make')
        if not make:
            return 'N/A'

        make = make.upper()
        if any(ext in make for ext in ['NIKON', 'CANON', 'SONY', 'PANASONIC', 'LEICA', 'PENTAX', 'OLYMPUS', 'FUJIFILM']):
            return 'Camera'
        elif any(ext in make for ext in ['APPLE', 'GOOGLE', 'ALCATEL', 'MOTOROLA', 'HUWAEI', 'SAMSUMG']):
            return 'Smartphone'
        return 'Unkown'

    def fabric_lente(self, exif_data):
        make = self.exif_from_dict(exif_data, 'Make')
        if make and any(ext in make for ext in ['Apple', 'Google', 'Motorola', 'Huawei']):
            return 'Phone'

        lens_model = self.exif_from_dict(exif_data, 'LensModel')
        if lens_model:
            lens_model = lens_model.upper()
            if any(ext in lens_model for ext in ['HSM', 'Art']):
                return 'Sigma'
            elif any(ext in lens_model for ext in ['DI', 'VC']):
                return 'Tamron'
            elif any(ext in lens_model for ext in ['EF', 'EF-S', 'RF', 'EF-M']):
                return 'Canon'
            elif any(ext in lens_model for ext in ['ED', 'DX', 'FX', 'G']):
                return 'Nikon'
            elif any(ext in lens_model for ext in ['SMC', 'DA', 'FA', 'SDM', 'WR', 'AW']):
                return 'Pentax'
            elif any(ext in lens_model for ext in ['OLYMPUS', 'PRO']):
                return 'Olympus'
            elif any(ext in lens_model for ext in ['LEICA', 'ELMARIT']):
                return 'Leica'
            elif any(ext in lens_model for ext in ['SONY', 'E ']):
                return 'Sony'
            elif any(ext in lens_model for ext in ['OTUS']):
                return 'Zeiss'
            elif any(ext in lens_model for ext in ['Apple']):
                return 'Apple'
        return 'N/A'

    def decimal_exif(self, rational):
        value = str(rational)
        if value == 'None':
            return 0
        return value

    def parse_exif_date(self, exif_data):
        try:
            date = self.exif_from_dict(exif_data, 'DateTimeOriginal')
            return datetime.datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
        except Exception:
            return datetime.datetime.now()

    def tipo_lente(self, exif_data):
        lens_model = self.exif_from_dict(exif_data, 'LensModel')
        if lens_model:
            lens_model_mactch_zoom = bool(re.match("(.*)[0-9]-[0-9](.*)", lens_model))
            return 'Zoom' if lens_model_mactch_zoom else 'Prime'
        return 'N/A'

    def contem_relevante_exif_data(self, exif_data):
        value = self.exif_from_dict(exif_data, 'FocalLength')
        return True if value else False
