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

    def __init__(self, max_record_count):
        Thread.__init__(self)
        self.max_record_count = max_record_count
        self.relevant_exif = ['ShutterSpeedValue','ApertureValue','ISOSpeedRatings','LensSpecification','LensModel',
                        'LensMake','DateTimeOriginal','Make','Model','FocalLength','FocalLengthIn35mmFilm','Flash']
        self.exif_codes = {v: k for k, v in TAGS.items() if v in self.relevant_exif}

    def run(self):
        current_count = 0
        time.sleep(30)
        while True:
            current_count = current_count + self.extrair_exif()
            time.sleep(1)
            if self.check_remaining_size() == 0:
                print('Stopping worker....')
                break

    def extrair_exif(self):
        """Obtem URL de imagens da base de dados e le a informacao EXIF.
        Caso nao tenha informacao EXIF relevante, remove o regsitro da base"""

        record_count = 0
        with psycopg.connect("dbname=postgres user=alemser") as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT id_fotografia, nm_url FROM t_fotografias WHERE fl_falha_exif = false AND fl_lido = false LIMIT 250""")
                print('Processando {} records'.format(cur.rowcount))
                for record in cur:
                    try:
                        img = PIL.Image.open(requests.get(record[1], stream=True).raw)
                        exif_data = img._getexif()
                        if self.contem_relevante_exif_data(exif_data):
                            self.atualizar_exif(record[0], exif_data)
                        else:
                            self.max_record_count = self.max_record_count - 1
                            self.remover_sem_exif(record[0])
                    except Exception as e:
                        print(e)
                        self.marcar_como_falho(record[0])
        return record_count

    def check_remaining_size(self):
        count = 0
        with psycopg.connect("dbname=postgres user=alemser") as conn:
            with conn.cursor() as cur:
                cur.execute("""select count(*) from t_fotografias where fl_lido = False and fl_falha_exif = False""")
                count = cur.fetchone()[0]
        return count

    def remover_sem_exif(self, id_fotografia):
        with psycopg.connect("dbname=postgres user=alemser") as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM t_fotografias WHERE id_fotografia = %s""", [id_fotografia])

    def marcar_como_falho(self, id_fotografia):
        with psycopg.connect("dbname=postgres user=alemser") as conn:
            with conn.cursor() as cur:
                cur.execute("""UPDATE t_fotografias SET fl_falha_exif = True WHERE id_fotografia = %s""", [id_fotografia])

    def atualizar_exif(self, id_fotografia, exif_data):
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
                        id_fotografia))

    def exif_from_dictNA(self, exif_data, exif_code):
        value = self.exif_from_dict(exif_data, exif_code)
        return 'N/A' if not value else value

    def exif_from_dict(self, exif_data, exif_code):
        if not exif_data:
            return None
        try:
            value = exif_data[self.exif_codes[exif_code]]
            return value if value else None
        except Exception:
            return None

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
            if any(ext in lens_model for ext in ['HSM', 'ART', 'CONTEMPORARY', 'SIGMA']):
                return 'Sigma'
            elif any(ext in lens_model for ext in ['DI', 'VC']):
                return 'Tamron'
            elif any(ext in lens_model for ext in ['EF', 'EF-S', 'RF', 'EF-M', 'USM']):
                return 'Canon'
            elif any(ext in lens_model for ext in ['NIKKOR', 'DX', 'FX', 'VR']):
                return 'Nikon'
            elif any(ext in lens_model for ext in ['PENTAX', 'SMC', 'DA', 'FA', 'SDM', 'WR', 'AW']):
                return 'Pentax'
            elif any(ext in lens_model for ext in ['OLYMPUS', 'PRO']):
                return 'Olympus'
            elif any(ext in lens_model for ext in ['LEICA', 'ELMARIT', 'SUMMILUX', 'ASPH', 'SUMMICRON']):
                return 'Leica'
            elif any(ext in lens_model for ext in ['SONY', 'E ', 'OSS', 'FE', 'SSM']):
                return 'Sony'
            elif any(ext in lens_model for ext in ['OTUS', 'BATIS', 'ZEISS', 'SONNAR']):
                return 'Zeiss'
            elif any(ext in lens_model for ext in ['APPLE']):
                return 'Apple'
            elif any(ext in lens_model for ext in ['SAMYANG']):
                return 'Samyang'
            elif any(ext in lens_model for ext in ['LUMIX']):
                return 'Panasonic'
            elif any(ext in lens_model for ext in ['VILTROX']):
                return 'Viltrox'
            elif any(ext in lens_model for ext in ['FUJI', 'XF', 'FUJINON']):
                return 'Fujifilm'
            elif any(ext in lens_model for ext in ['VOIGTLANDER']):
                return 'Voigtlander'



        return 'N/A'

    def decimal_exif(self, rational):
        try:
            value = str(rational)
            if value == 'None':
                return None
            return value
        except Exception:
            return None

    def parse_exif_date(self, exif_data):
        try:
            date = self.exif_from_dict(exif_data, 'DateTimeOriginal')
            if date:
                return datetime.datetime.strptime(date, '%Y:%m:%d %H:%M:%S')
        except Exception:
            print('Data invalida, data padrao sera usada (10000 dias atras)')

        return datetime.datetime.now() - datetime.timedelta(10000)

    def tipo_lente(self, exif_data):
        lens_model = self.exif_from_dict(exif_data, 'LensModel')
        if lens_model:
            lens_model_mactch_zoom = bool(re.match("(.*)[0-9]-[0-9](.*)", lens_model))
            return 'Zoom' if lens_model_mactch_zoom else 'Prime'
        return 'N/A'

    def contem_relevante_exif_data(self, exif_data):
        value = self.exif_from_dict(exif_data, 'FocalLength')
        return True if value else False
