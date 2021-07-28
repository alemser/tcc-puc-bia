#!/usr/bin/env python3

from etl.extrair_fotos_flickr import get_urls
import sys
from threading import Thread
import time

def main():
    threads = []

    t1 = Thread(target=get_urls, args=('Esporte','sports,olympics,football', 2000))
    t1.start()
    threads.append(t1)
    time.sleep(10)

    t2 = Thread(target=get_urls, args=('Casamento', 'wedding,bride,bridesmaid', 2000))
    t2.start()
    threads.append(t2)
    time.sleep(10)

    t3 = Thread(target=get_urls, args=('Natureza','nature,landscape', 2000))
    t3.start()
    threads.append(t3)
    time.sleep(10)

    t4 = Thread(target=get_urls, args=('Retratos','portrait', 2000))
    t4.start()
    threads.append(t4)
    time.sleep(10)

    t5 = Thread(target=get_urls, args=('Astro-fotografia','astro,astrophotography,starts,planets,moon', 2000))
    t5.start()
    threads.append(t5)
    time.sleep(10)

    for t in threads:
        t.join()

    print("Processo finalizado")

if __name__ == '__main__':
    main()
