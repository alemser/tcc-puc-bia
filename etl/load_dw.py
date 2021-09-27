#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg2
from etl.constants import *

def load():
    print("Carregando DWH")
    d_categoria()
    d_tipo_lente()
    d_tipo_camera()
    d_camera()
    d_lente()
    d_imagem()
    d_loja()
    d_tempo()
    f_foto()
    print("Carregamento completo")

def d_categoria():
    sql = """
        INSERT INTO d_categoria (nm_categoria)
        	SELECT DISTINCT nm_categoria_foto
        	FROM t_fotografias
        	WHERE fl_lido = true
        ON CONFLICT DO NOTHING;
        """
    _execute(sql)

def d_tipo_lente():
    sql = """
        INSERT INTO d_tipo_lente (nm_tipo_lente)
        	SELECT DISTINCT TP_LENTE
        	FROM t_fotografias
        	WHERE fl_lido = true
        ON CONFLICT DO NOTHING;
        """
    _execute(sql)

def d_tipo_camera():
    sql = """
        INSERT INTO d_tipo_camera (nm_tipo_camera)
        	SELECT DISTINCT tp_camera
        	FROM t_fotografias
        	WHERE fl_lido = true
        ON CONFLICT DO NOTHING;
        """
    _execute(sql)

def d_camera():
    sql = """
        INSERT INTO d_camera (nm_camera, nm_fabricante, id_tipo_camera)
        	SELECT DISTINCT ft.nm_camera, UPPER(SUBSTRING(ft.nm_fabric_camera, 0, POSITION(' ' in ft.nm_fabric_camera || ' '))), tpc.id_tipo_camera
        	FROM t_fotografias ft
        	JOIN d_tipo_camera tpc ON tpc.nm_tipo_camera = ft.tp_camera
        	WHERE fl_lido = true
        ON CONFLICT DO NOTHING;
        """
    _execute(sql)

def d_lente():
    sql = """
        INSERT INTO d_lente (nm_modelo, nm_fabricante, id_tipo_lente)
        	SELECT DISTINCT ft.nm_lente, UPPER(SUBSTRING(ft.nm_fabric_lente, 0, POSITION(' ' in ft.nm_fabric_lente || ' '))), tpl.id_tipo_lente
        	FROM t_fotografias ft
        	JOIN d_tipo_lente tpl ON tpl.nm_tipo_lente = ft.tp_lente
        	WHERE fl_lido = true
        ON CONFLICT DO NOTHING;
        """
    _execute(sql)

def d_imagem():
    sql = """
        INSERT INTO d_imagem (nm_url, dt_imagem, de_titulo, nm_tags, nu_distancia_focal)
        	SELECT ft.nm_url, ft.dt_foto, ft.de_titulo, ft.nm_tags,
    		CASE
    			WHEN ft.nu_dist_focal_35mmEq IS NULL THEN ft.nu_dist_focal
    			ELSE ft.nu_dist_focal_35mmEq
    		END as nu_distancia_focal
        	FROM t_fotografias ft
        	WHERE fl_lido = true
        ON CONFLICT (nm_url) DO NOTHING;
        """
    _execute(sql)

def d_loja():
    sql = """
        INSERT INTO d_loja (nm_loja, nm_url_site)
        	SELECT ft.nm_website, ft.nm_url_website
        	FROM t_fotografias ft
        	WHERE fl_lido = true
            ON CONFLICT DO NOTHING;
        """
    _execute(sql)

def d_tempo():
    sql = """
        INSERT INTO d_tempo (nu_dia, nu_mes, nu_ano, nu_trimestre, nu_semestre, dt_tempo)
        	SELECT extract(day from ft.dt_foto), extract(month from ft.dt_foto), extract(year from ft.dt_foto),
            CASE
                WHEN (extract(month from ft.dt_foto) >= 1 AND extract(month from ft.dt_foto) <=3) THEN 1
                WHEN (extract(month from ft.dt_foto) >= 4 AND extract(month from ft.dt_foto) <=6) THEN 2
                WHEN (extract(month from ft.dt_foto) >= 7 AND extract(month from ft.dt_foto) <=9) THEN 3
                WHEN (extract(month from ft.dt_foto) >= 10 AND extract(month from ft.dt_foto) <=12) THEN 4
            END as nu_tri,
            CASE
                WHEN (extract(month from ft.dt_foto) >= 1 AND extract(month from ft.dt_foto) <=6) THEN 1
                WHEN (extract(month from ft.dt_foto) >= 7 AND extract(month from ft.dt_foto) <=12) THEN 2
            END as nu_sem, 
            ft.dt_foto
        	FROM t_fotografias ft
        	WHERE fl_lido = true
            ON CONFLICT DO NOTHING;
        """
    _execute(sql)


def f_foto():
    sql = "DELETE FROM f_foto;"
    _execute(sql)

    sql = """
        INSERT INTO f_foto (id_camera, id_categoria, id_lente, id_imagem, id_loja, id_tempo, vl_imagem, nu_copias)
    	SELECT cam.id_camera, cat.id_categoria, len.id_lente, im.id_imagem, lj.id_loja, tp.id_tempo, ft.vl_venda, ft.nu_copias
    	FROM t_fotografias ft
    	JOIN d_camera cam ON cam.nm_camera = ft.nm_camera
    	JOIN d_categoria cat ON cat.nm_categoria = ft.nm_categoria_foto
    	JOIN d_lente len ON len.nm_modelo = ft.nm_lente
    	JOIN d_imagem im ON im.nm_url = ft.nm_url
        JOIN d_loja lj ON lj.nm_loja = ft.nm_website
        JOIN d_tempo tp ON
                tp.nu_dia = extract(day from ft.dt_foto)
            and tp.nu_mes = extract(month from ft.dt_foto)
            and tp.nu_ano = extract(year from ft.dt_foto)
    	WHERE fl_lido = true
          and ft.nu_dist_focal >= 14
        """
    _execute(sql)

def _execute(sql):
    with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
