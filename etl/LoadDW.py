#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psycopg

def load():
    print("Carregando DWH")
    d_fabricante()
    d_categoria()
    d_tipo_lente()
    d_tipo_camera()
    d_camera()
    d_lente()
    d_imagem()
    f_foto()
    print("Carregamento completo")

def d_fabricante():
    sql = """
        INSERT INTO d_fabricante (nm_fabricante)
        	SELECT DISTINCT UPPER(SUBSTRING(nm_fabric_camera, 0, POSITION(' ' in nm_fabric_camera || ' '))) as nome
        	FROM t_fotografias
        	WHERE fl_lido = true
        	UNION DISTINCT
        	SELECT DISTINCT UPPER(SUBSTRING(nm_fabric_lente, 0, POSITION(' ' in nm_fabric_lente || ' '))) as nome
        	FROM t_fotografias
        	WHERE fl_lido = true
        ON CONFLICT (nm_fabricante) DO NOTHING;
        """
    _execute(sql)

def d_categoria():
    sql = """
        INSERT INTO d_categoria (nm_categoria)
        	SELECT DISTINCT nm_categoria_foto
        	FROM t_fotografias
        	WHERE fl_lido = true
        ON CONFLICT (nm_categoria) DO NOTHING;
        """
    _execute(sql)

def d_tipo_lente():
    sql = """
        INSERT INTO d_tipo_lente (nm_tipo_lente)
        	SELECT DISTINCT TP_LENTE
        	FROM t_fotografias
        	WHERE fl_lido = true
        ON CONFLICT (nm_tipo_lente) DO NOTHING;
        """
    _execute(sql)

def d_tipo_camera():
    sql = """
        INSERT INTO d_tipo_camera (nm_tipo_camera)
        	SELECT DISTINCT tp_camera
        	FROM t_fotografias
        	WHERE fl_lido = true
        ON CONFLICT (nm_tipo_camera) DO NOTHING;
        """
    _execute(sql)

def d_camera():
    sql = """
        INSERT INTO d_camera (nm_camera, id_fabricante, id_tipo_camera)
        	SELECT DISTINCT ft.nm_camera, fab.id_fabricante, tpc.id_tipo_camera
        	FROM t_fotografias ft
        	JOIN d_fabricante fab ON fab.nm_fabricante = UPPER(SUBSTRING(ft.nm_fabric_camera, 0, POSITION(' ' in ft.nm_fabric_camera || ' ')))
        	JOIN d_tipo_camera tpc ON tpc.nm_tipo_camera = ft.tp_camera
        	WHERE fl_lido = true
        ON CONFLICT (nm_camera) DO NOTHING;
        """
    _execute(sql)

def d_lente():
    sql = """
        INSERT INTO d_lente (nm_modelo, id_fabricante, id_tipo_lente)
        	SELECT DISTINCT ft.nm_lente, fab.id_fabricante, tpl.id_tipo_lente
        	FROM t_fotografias ft
        	JOIN d_fabricante fab ON fab.nm_fabricante = UPPER(SUBSTRING(ft.nm_fabric_lente, 0, POSITION(' ' in ft.nm_fabric_lente || ' ')))
        	JOIN d_tipo_lente tpl ON tpl.nm_tipo_lente = ft.tp_lente
        	WHERE fl_lido = true
        ON CONFLICT (nm_modelo) DO NOTHING;
        """
    _execute(sql)

def d_imagem():
    sql = """
        INSERT INTO d_imagem (nm_url, dt_imagem, de_titulo, nm_tags)
        	SELECT ft.nm_url, ft.dt_foto, ft.de_titulo, ft.nm_tags
        	FROM t_fotografias ft
        	WHERE fl_lido = true
        ON CONFLICT (nm_url) DO NOTHING;
        """
    _execute(sql)

def f_foto():
    sql = "DELETE FROM f_foto"
    _execute(sql)

    sql = """
        INSERT INTO f_foto (id_camera, id_categoria, id_lente, id_imagem, fl_flash, nu_iso, nu_distancia_focal, nu_abertura, nu_tempo_exposicao)
    	SELECT cam.id_camera, cat.id_categoria, len.id_lente, im.id_imagem, ft.fl_flash,
    		CASE
    			WHEN ft.nu_iso IS NULL THEN 0
    			ELSE nu_iso
    		END as nu_iso,
    		CASE
    			WHEN ft.nu_dist_focal_35mmEq IS NULL THEN ft.nu_dist_focal
    			ELSE ft.nu_dist_focal_35mmEq
    		END as nu_distancia_focal,
    		CASE
    			WHEN ft.nu_abertura IS NULL THEN 0
    			ELSE ft.nu_abertura
    		END as nu_abertura,
    		CASE
    			WHEN ft.nu_tempo_exposicao IS NULL THEN 0
    			ELSE ft.nu_tempo_exposicao
    		END as nu_tempo_exposicao
    	FROM t_fotografias ft
    	JOIN d_camera cam ON cam.nm_camera = ft.nm_camera
    	JOIN d_categoria cat ON cat.nm_categoria = ft.nm_categoria_foto
    	JOIN d_lente len ON len.nm_modelo = ft.nm_lente
    	JOIN d_imagem im ON im.nm_url = ft.nm_url
    	WHERE fl_lido = true
        """
    _execute(sql)

def _execute(sql):
    with psycopg.connect("dbname=postgres user=alemser") as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
