#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import psycopg2
from constants import *

try:
    with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST) as conn:
        with conn.cursor() as cur:
            cur.execute(open('modelo/ddl.sql', 'r').read())
            cur.execute(open('modelo/dml.sql', 'r').read())
            print("A base de dados foi pre-carregada")
except Exception as e:
    print(e)
