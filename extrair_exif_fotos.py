#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## run
## > python flickr_GetUrl.py tag number_of_images_to_attempt_to_download

import PIL.Image
from PIL.ExifTags import TAGS
import requests
from time import sleep
import psycopg
import datetime


relevant_exif = ['ShutterSpeedValue','ApertureValue','ISOSpeedRatings','LensSpecification','LensModel',
                'LensMake','DateTimeOriginal','Make','Model','FocalLength','FocalLengthIn35mmFilm','Flash']
exif_codes = {v: k for k, v in TAGS.items() if v in relevant_exif}

def extrair_exif():
    """Obtem URL de imagens da base de dados e le a informacao EXIF.
    Caso nao tenha informacao EXIF relevant, remove o regsitro da base"""

    with psycopg.connect("dbname=postgres user=alemser") as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT id_fotografia, nm_url FROM t_fotografias WHERE fl_lido = false LIMIT 100""")
            remaining_records = cur.rowcount
            for record in cur:
                img = PIL.Image.open(requests.get(record[1], stream=True).raw)
                exif_data = img._getexif()
                if contem_relevante_exif_data(exif_data):
                    atualizar_exif(record[0], exif_data)
                else:
                    remover_sem_exif(record[0])
        #sleep(1000)

def remover_sem_exif(id_fotografia):
    """Remove informacao de fotografia sem EXIF relevante."""

    with psycopg.connect("dbname=postgres user=alemser") as conn:
        with conn.cursor() as cur:
            cur.execute("""DELETE FROM t_fotografias WHERE id_fotografia = %s""", [id_fotografia])

def atualizar_exif(id_fotografia, exif_data):
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
                    parse_exif_date(exif_data.get(exif_codes['DateTimeOriginal'])),
                    tipo_lente(exif_data.get(exif_codes['LensSpecification'])),
                    exif_data.get(exif_codes['LensModel']),
                    fabric_lente(exif_data),
                    decimal_exif(exif_data.get(exif_codes['FocalLength'])),
                    tipo_camera(exif_data),
                    exif_data.get(exif_codes['Model']),
                    exif_data.get(exif_codes['Make']),
                    decimal_exif(exif_data.get(exif_codes['FocalLengthIn35mmFilm'])),
                    decimal_exif(exif_data.get(exif_codes['ApertureValue'])),
                    decimal_exif(exif_data.get(exif_codes['ShutterSpeedValue'])),
                    decimal_exif(exif_data.get(exif_codes['ISOSpeedRatings'])),
                    True if exif_data.get(exif_codes['Flash']) == 1 else False,
                    id_fotografia))

def tipo_camera(exif_data):
    """Tenta identificar os principais fabricantes e retorna se tipo é camera ou smartphone."""

    value = exif_data.get(exif_codes['Make'])
    try:
        if value.lower() in ['nikon', 'canon', 'panasonic', 'leica', 'pentax', 'olympus']:
            return 'camera'
        return 'smartphone'
    except Exception:
        None

def fabric_lente(exif_data):
    value = exif_data.get(exif_codes['LensMake'])
    if not value:
        return exif_data.get(exif_codes['Make'])
    return value

def decimal_exif(rational):
    value = str(rational)
    if value == 'None':
        return
    return value

def parse_exif_date(exif_date):
    try:
        return datetime.datetime.strptime(exif_date, '%Y:%m:%d %H:%M:%S')
    except Exception:
        None

def tipo_lente(lens_specification):
    try:
        return 'Zoom' if len(lens_specification) > 1 else 'Prime'
    except Exception:
        None

def contem_relevante_exif_data(exif_data):
    return exif_data and decimal_exif(exif_data.get(exif_codes['FocalLength']))
