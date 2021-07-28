#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## run
## > python flickr_GetUrl.py tag number_of_images_to_attempt_to_download

from flickrapi import FlickrAPI
import sys
import psycopg
from threading import Thread
from time import sleep
import psycopg
from .ExifWorker import *

key=u'820a5f399dc0032c41be29241cecdf36'
secret=u'33d128d07ba9406a'

def get_urls(categoria, tags, MAX_COUNT):

    flickr = FlickrAPI(key, secret)
    photos = flickr.walk(media='photos',
                        content_type=1,
                        tag_mode='all',
                        tags=tags,
                        extras='url_o,tags',
                        per_page=500,
                        sort='date-posted-desc',
                        privacy_filter=1)
    count = 0

    worker = ExifWorker(categoria, MAX_COUNT)
    worker.daemon = True
    worker.start()

    for photo in photos:
        url = photo.get('url_o')
        if url and len(url) > 0:
            titulo = None if not photo.get('title') else photo.get('title')
            tags = None if not photo.get('tags') else photo.get('tags')
            inserir_info_basica_bd(titulo, url, tags, categoria)
            count = count + 1
        if count > MAX_COUNT:
            break
    print(count, "URLs de imagens armazenadas para a categoria", categoria)
    worker.allowed_to_stop = True
    worker.join()

def inserir_info_basica_bd(titulo, url, tags, categoria):
    with psycopg.connect("dbname=postgres user=alemser") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO t_fotografias (de_titulo, nm_url, nm_categoria_foto, nm_tags)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (nm_url) DO NOTHING;
                """, (titulo, url, categoria, tags))
