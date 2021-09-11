#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import psycopg2
from etl.constants import *

def create_tables():
    try:
        with psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT) as conn:
            with conn.cursor() as cur:
                cur.execute(open('modelo/ddl.sql', 'r').read())
                print("As tabelas foram criadas")
    except Exception as e:
        print(e)
