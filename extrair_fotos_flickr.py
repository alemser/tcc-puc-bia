#!/usr/bin/env python3
# -*- coding: utf-8 -*-
## run
## > python flickr_GetUrl.py tag number_of_images_to_attempt_to_download

from flickrapi import FlickrAPI
import sys
import psycopg
from extrair_exif_fotos import extrair_exif
from threading import Thread
from time import sleep
import psycopg

key=u'820a5f399dc0032c41be29241cecdf36'
secret=u'33d128d07ba9406a'

def get_urls(image_tag,MAX_COUNT):
    flickr = FlickrAPI(key, secret)
    photos = flickr.walk(media='photos',
                        text=image_tag,
                        content_type=1,
                        tag_mode='all',
                        tags=image_tag,
                        extras='url_o,tags',
                        per_page=500,
                        sort='date-posted-desc',
                        privacy_filter=1)
    count = 0

    # thread = Thread(target = extrair_exif, args = [])
    # thread.start()
    # print("thread para extrair EXIF iniciada...")

    for photo in photos:
        url=photo.get('url_o')
        titulo=photo.get('title')
        tags = photo.get('tags')
        if url and len(url) > 0:
            inserir_info_basica_bd(titulo, url, tags, image_tag)
            extrair_exif()
            count = count + 1
        if count > MAX_COUNT:
            break
    print(count, "imagens armazenadas")
    # thread.join()

def inserir_info_basica_bd(titulo, url, tags, categoria):
    with psycopg.connect("dbname=postgres user=alemser") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO t_fotografias (de_titulo, nm_url, nm_categoria_foto, nm_tags)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (nm_url) DO NOTHING;
                """, (titulo, url, categoria, tags))

def main():
    tag=sys.argv[1]
    MAX_COUNT=int(sys.argv[2])
    get_urls(tag,MAX_COUNT)

#https://gist.github.com/yunjey/14e3a069ad2aa3adf72dee93a53117d6

if __name__=='__main__':
    main()
