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

def extrair_exif():
    #while True:
    with psycopg.connect("dbname=postgres user=alemser") as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT id_fotografia, nm_url FROM t_fotografias WHERE fl_lido = false LIMIT 100""")
            remaining_records = cur.rowcount
            print("Atualizando", remaining_records, " registros")
            for record in cur:
                img = PIL.Image.open(requests.get(record[1], stream=True).raw)
                exif_data = img._getexif()
                data_dict = {'id_fotografia': record[0]}
                if exif_data:
                    for k in exif_data:
                        if (TAGS[k] == 'ShutterSpeedValue'):
                            data_dict['nu_tempo_exposicao'] = exif_data[k]._numerator / exif_data[k]._denominator
                            print('=>',data_dict['nu_tempo_exposicao'])
                        if (TAGS[k] == 'ApertureValue'):
                            data_dict['nu_abertura'] = exif_data[k]._numerator / exif_data[k]._denominator
                        if (TAGS[k] == 'ISOSpeedRatings'):
                            data_dict['nu_iso'] = exif_data[k]
                        if (TAGS[k] == 'LensSpecification'):
                            data_dict['tp_lente'] = 'Zoom' if len(exif_data[k]) > 1 else 'Prime'
                        if (TAGS[k] == 'LensModel'):
                            data_dict['nm_lente'] = exif_data[k]
                        if (TAGS[k] == 'LensMake'):
                            data_dict['nm_fabric_lente'] = exif_data[k]
                        if (TAGS[k] == 'DateTimeOriginal'):
                            data_dict['dt_foto'] = exif_data[k]
                        if (TAGS[k] == 'DateTimeOriginal'):
                            data_dict['dt_foto'] = exif_data[k]
                        if (TAGS[k] == 'Make'):
                            data_dict['nm_fabric_camera'] = exif_data[k]
                        if (TAGS[k] == 'Model'):
                            data_dict['nm_camera'] = exif_data[k]
                        if (TAGS[k] == 'FocalLength'):
                            print(exif_data[k]._numerator,exif_data[k]._denominator,exif_data[k])
                            data_dict['nu_dist_focal_lente'] = exif_data[k]._numerator / exif_data[k]._denominator
                        if (TAGS[k] == 'FocalLengthIn35mmFilm'):
                            data_dict['nu_dist_focal_lente_35mmEq'] = exif_data[k]
                        if (TAGS[k] == 'Flash'):
                            data_dict['fl_flash'] = False if exif_data[k] == 0 else True

                atualizar_exif(data_dict)
        #sleep(1000)

def atualizar_exif(data_dict):
    with psycopg.connect("dbname=postgres user=alemser") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE t_fotografias
                SET dt_coleta = %s,
                    tp_lente = %s,
                    nm_lente = %s,
                    nm_fabric_lente = %s,
                    nu_dist_focal_lente = %s,
                    tp_camera = %s,
                    nm_camera = %s,
                    nm_fabric_camera = %s,
                    nu_dist_focal_lente_35mmEq = %s,
                    nu_abertura = %s,
                    nu_tempo_exposicao = %s,
                    nu_iso = %s,
                    fl_flash = %s,
                    fl_lido = true
                WHERE id_fotografia = %s
                """, (datetime.datetime.now(),
                    value_or_default(data_dict, 'tp_lente', None),
                    value_or_default(data_dict, 'nm_lente', None),
                    value_or_default(data_dict, 'nm_fabric_lente', None),
                    value_or_default(data_dict, 'nu_dist_focal_lente', 0.0),
                    value_or_default(data_dict, 'tp_camera', None),
                    value_or_default(data_dict, 'nm_camera', None),
                    value_or_default(data_dict, 'nm_fabric_camera', None),
                    value_or_default(data_dict, 'nu_dist_focal_lente_35mmEq', 0.0),
                    value_or_default(data_dict, 'nu_abertura', 0.0),
                    value_or_default(data_dict, 'nu_tempo_exposicao', 0.0),
                    value_or_default(data_dict, 'nu_iso', 0.0),
                    value_or_default(data_dict, 'fl_flash', False),
                    data_dict['id_fotografia']))

def value_or_default(dict, key, default_value):
    try:
        return dict[key]
    except Exception as e:
        print(key, 'Default: ',default_value)
        return default_value
