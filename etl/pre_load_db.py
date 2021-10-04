#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import io
import psycopg2
import pandas as pd
from etl.constants import *

def pre_load_db():
    try:
        with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT) as conn:
            with conn.cursor() as cur:
                cur.copy_from(adjust_before_save('data/d_categoria.csv'), 'd_categoria', sep=',')
                cur.copy_from(adjust_before_save('data/d_tipo_lente.csv'), 'd_tipo_lente', sep=',')
                cur.copy_from(adjust_before_save('data/d_tipo_camera.csv'), 'd_tipo_camera', sep=',')
                cur.copy_from(adjust_before_save('data/d_camera.csv'), 'd_camera', sep=',')
                cur.copy_from(adjust_before_save('data/d_lente.csv'), 'd_lente', sep=',')
                cur.copy_from(adjust_before_save('data/d_imagem.csv'), 'd_imagem', sep=',')
                cur.copy_from(adjust_before_save('data/d_loja.csv'), 'd_loja', sep=',')
                cur.copy_from(adjust_before_save('data/d_tempo.csv'), 'd_tempo', sep=',')
                cur.copy_from(adjust_before_save('data/f_venda.csv'), 'f_venda', sep=',')
                cur.copy_from(adjust_before_save('data/t_fotografia.csv'), 't_fotografias', sep=',')
        print("Finish pre loading the DB")
    except Exception as e:
        print(e)

def adjust_before_save(csv_file_name):
    df = pd.read_csv(csv_file_name)
    df.replace(',', '-', regex=True, inplace=True)
    if csv_file_name == 'data/t_fotografia.csv':
        df.replace(r'^\s*$', 'NULL', regex=True, inplace=True)
        print(df)

    s_buf = io.StringIO()
    df.to_csv(s_buf, index=False, header=False)
    s_buf.seek(0)
    return s_buf
