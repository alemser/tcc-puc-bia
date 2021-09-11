#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
from etl.constants import *

def export_csv():
    print("DWH 2 CSV")
    d_categoria()
    d_tipo_lente()
    d_tipo_camera()
    d_camera()
    d_lente()
    d_imagem()
    d_loja()
    d_tempo()
    f_foto()
    t_fotografia()
    print("Carregamento CSV completo")

def d_categoria():
    sql = """
        COPY (SELECT * FROM d_categoria) TO STDOUT WITH CSV HEADER DELIMITER ',';
        """
    _execute(sql, 'd_categoria')

def d_tipo_lente():
    sql = """
        COPY (SELECT * FROM d_tipo_lente) TO STDOUT WITH CSV HEADER DELIMITER ',';
        """
    _execute(sql, 'd_tipo_lente')

def d_tipo_camera():
    sql = """
        COPY (SELECT * FROM d_tipo_camera) TO STDOUT WITH CSV HEADER DELIMITER ',';
        """
    _execute(sql, 'd_tipo_camera')

def d_camera():
    sql = """
        COPY (SELECT * FROM d_camera) TO STDOUT WITH CSV HEADER DELIMITER ',';
        """
    _execute(sql, 'd_camera')

def d_lente():
    sql = """
        COPY (SELECT * FROM d_lente) TO STDOUT WITH CSV HEADER DELIMITER ',';
        """
    _execute(sql, 'd_lente')

def d_imagem():
    sql = """
        COPY (SELECT * FROM d_imagem) TO STDOUT WITH CSV HEADER DELIMITER ',';
        """
    _execute(sql, 'd_imagem')

def d_loja():
    sql = """
        COPY (SELECT * FROM d_loja) TO STDOUT WITH CSV HEADER DELIMITER ',';
        """
    _execute(sql, 'd_loja')

def d_tempo():
    sql = """
        COPY (SELECT * FROM d_tempo) TO STDOUT WITH CSV HEADER DELIMITER ',';
        """
    _execute(sql, 'd_tempo')

def f_foto():
    sql = """
        COPY (SELECT * FROM f_foto) TO STDOUT WITH CSV HEADER DELIMITER ',';
        """
    _execute(sql, 'f_foto')

def t_fotografia():
    sql = """
        COPY (SELECT * FROM t_fotografias) TO STDOUT WITH CSV HEADER DELIMITER ',';
        """
    _execute(sql, 't_fotografia')

def _execute(sql, csv_file_name):
    with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT) as conn:
        with conn.cursor() as cur:
            with open('data/'+csv_file_name+'.csv', 'w+') as file:
                cur.copy_expert(sql, file)
    print(csv_file_name, 'exported to csv')
