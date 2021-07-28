#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import PIL.Image
from PIL.ExifTags import TAGS
import requests
import psycopg
import datetime
from threading import Thread
import time

class ExifWorker(Thread):

    def __init__(self, record_count):
        Thread.__init__(self)
        self.record_count = record_count
        self.relevant_exif = ['ShutterSpeedValue','ApertureValue','ISOSpeedRatings','LensSpecification','LensModel',
                        'LensMake','DateTimeOriginal','Make','Model','FocalLength','FocalLengthIn35mmFilm','Flash']
        self.exif_codes = {v: k for k, v in TAGS.items() if v in self.relevant_exif}
        self.allowed_to_stop = False

    def run(self):
        current_count = 0
        while True:
            current_count = current_count + self.extrair_exif()
            time.sleep(10)
            if current_count >= self.record_count and self.allowed_to_stop:
                print('Stopping worker....')
                break

    def extrair_exif(self):
        """Obtem URL de imagens da base de dados e le a informacao EXIF.
        Caso nao tenha informacao EXIF relevant, remove o regsitro da base"""

        record_count = 0
        with psycopg.connect("dbname=postgres user=alemser") as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT id_fotografia, nm_url FROM t_fotografias WHERE fl_lido = false LIMIT 100""")
                print('Processando {} records'.format(cur.rowcount))
                for record in cur:
                    try:
                        img = PIL.Image.open(requests.get(record[1], stream=True).raw)
                        exif_data = img._getexif()
                        if self.contem_relevante_exif_data(exif_data):
                            self.atualizar_exif(record[0], exif_data)
                        else:
                            self.remover_sem_exif(record[0])
                        record_count = record_count + 1
                    except Exception:
                        print('[ERR] enquanto lia a URL {}'.format(record[1]))
                print("{} registros processados".format(record_count))
        return record_count

    def remover_sem_exif(self, id_fotografia):
        """Remove informacao de fotografia sem EXIF relevante."""

        with psycopg.connect("dbname=postgres user=alemser") as conn:
            with conn.cursor() as cur:
                cur.execute("""DELETE FROM t_fotografias WHERE id_fotografia = %s""", [id_fotografia])

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
                        self.parse_exif_date(exif_data.get(self.exif_codes['DateTimeOriginal'])),
                        self.tipo_lente(exif_data.get(self.exif_codes['LensSpecification'])),
                        exif_data.get(self.exif_codes['LensModel']),
                        self.fabric_lente(exif_data),
                        self.decimal_exif(exif_data.get(self.exif_codes['FocalLength'])),
                        self.tipo_camera(exif_data),
                        exif_data.get(self.exif_codes['Model']),
                        exif_data.get(self.exif_codes['Make']),
                        self.decimal_exif(exif_data.get(self.exif_codes['FocalLengthIn35mmFilm'])),
                        self.decimal_exif(exif_data.get(self.exif_codes['ApertureValue'])),
                        self.decimal_exif(exif_data.get(self.exif_codes['ShutterSpeedValue'])),
                        self.decimal_exif(exif_data.get(self.exif_codes['ISOSpeedRatings'])),
                        True if exif_data.get(self.exif_codes['Flash']) == 1 else False,
                        id_fotografia))

    def tipo_camera(self, exif_data):
        """Tenta identificar os principais fabricantes e retorna se tipo é camera ou smartphone."""

        make = exif_data.get(self.exif_codes['Make'])
        if not make:
            return None

        make = make.upper()
        if any(ext in make for ext in ['NIKON', 'CANON', 'SONY', 'PANASONIC', 'LEICA', 'PENTAX', 'OLYMPUS']):
            return 'camera'
        elif any(ext in make for ext in ['APPLE', 'GOOGLE', 'ALCATEL', 'MOTOROLA', 'HUWAEI', 'SAMSUMG']):
            return 'smartphone'
        return 'unkown'

    def fabric_lente(self, exif_data):
        lens_model = exif_data.get(self.exif_codes['LensModel'])
        make = exif_data.get(self.exif_codes['Make'])
        if make and any(ext in make for ext in ['Apple', 'Google', 'Motorola', 'Huawei']):
            return 'Phone'

        if lens_model:
            lens_model = lens_model.upper()
            if any(ext in lens_model for ext in ['DG', 'HSM', 'Art']):
                return 'Sigma'
            elif any(ext in lens_model for ext in ['DI', 'VC']):
                return 'Tamron'
            elif any(ext in lens_model for ext in ['EF', 'EF-S', 'RF', 'EF-M']):
                return 'Canon'
            elif any(ext in lens_model for ext in ['ED', 'DX', 'FX', 'G', 'f/2.8D']):
                return 'Nikon'
            elif any(ext in lens_model for ext in ['SMC', 'DA', 'FA', 'SDM', 'WR', 'AW']):
                return 'Pentax'
            elif any(ext in lens_model for ext in ['OLYMPUS', 'PRO']):
                return 'Olympus'
            elif any(ext in lens_model for ext in ['LEICA']):
                return 'Leica'

        return None

    def decimal_exif(self, rational):
        value = str(rational)
        if value == 'None':
            return
        return value

    def parse_exif_date(self, exif_date):
        try:
            return datetime.datetime.strptime(exif_date, '%Y:%m:%d %H:%M:%S')
        except Exception:
            None

    def tipo_lente(self, lens_specification):
        try:
            return 'Zoom' if len(lens_specification) > 1 else 'Prime'
        except Exception:
            None

    def contem_relevante_exif_data(self, exif_data):
        return exif_data and self.decimal_exif(exif_data.get(self.exif_codes['FocalLength']))
