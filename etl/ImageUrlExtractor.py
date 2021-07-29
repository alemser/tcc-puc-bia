#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flickrapi import FlickrAPI
import sys
import psycopg
from threading import Thread
from time import sleep
import psycopg
from .ExifWorker import *

key=u'820a5f399dc0032c41be29241cecdf36'
secret=u'33d128d07ba9406a'

class ImageUrlExtractor():

    def __init__(self, category, tags, max_record_count):
        self.category = category
        self.tags = tags
        self.max_record_count = max_record_count

    def extract_urls(self):
        print("Extraindo URLs da categoria {}".format(self.category))
        flickr = FlickrAPI(key, secret)
        photos = flickr.walk(media='photos',
                            content_type=1,
                            tag_mode='all',
                            tags=self.tags,
                            extras='url_o,tags',
                            per_page=500,
                            sort='date-posted-desc',
                            privacy_filter=1)
        count = 0
        for photo in photos:
            url = photo.get('url_o')
            if url and len(url) > 0:
                titulo = None if not photo.get('title') else photo.get('title')
                tags = None if not photo.get('tags') else photo.get('tags')
                self.inserir_info_basica_bd(titulo, url, tags, self.category)
                count = count + 1
            if count > self.max_record_count:
                break
        print(count, "URLs de imagens armazenadas para a categoria", self.category)

    def inserir_info_basica_bd(self, titulo, url, tags, categoria):
        with psycopg.connect("dbname=postgres user=alemser") as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO t_fotografias (de_titulo, nm_url, nm_categoria_foto, nm_tags)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (nm_url) DO NOTHING;
                    """, (titulo, url, categoria, tags))
