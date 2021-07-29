#!/usr/bin/env python3

from etl.ImageUrlExtractor import ImageUrlExtractor
from etl.ExifWorker import ExifWorker
from etl.LoadDW import load
import sys
from threading import Thread
import time

def main(argv):
    ler_categorias = True
    if (len(argv) == 1):
        print("Processar exif somente")
        ler_categorias = False

    MAX_COUNT_PER_CATEGORY = 5000
    categoria_label_dict = {
        'Esporte': 'sports,olympics,football',
        'Casamento': 'wedding,bride,bridesmaid',
        'Natureza': 'nature,landscape',
        'Retratos': 'portrait'}
    qt_category = len(categoria_label_dict.items())

    worker = ExifWorker(qt_category * MAX_COUNT_PER_CATEGORY)
    worker.daemon = True
    worker.start()

    if ler_categorias:
        for k, v in categoria_label_dict.items():
            extractor = ImageUrlExtractor(k, v, MAX_COUNT_PER_CATEGORY)
            extractor.extract_urls()

    worker.join()

    load()

    print("Processo finalizado")

if __name__ == '__main__':
    main(sys.argv[1:])
