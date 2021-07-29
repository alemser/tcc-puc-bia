#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import psycopg2

try:
    with psycopg2.connect(dbname='postgres', user='postgres', password='docker', host='localhost', port=5432) as conn:
        with conn.cursor() as cur:
            cur.execute(open('modelo/tcc_alessandro_db_dump.sql', 'r').read())
            print("A base de dados foi pre-carregada")
except Exception as e:
    print(e)
