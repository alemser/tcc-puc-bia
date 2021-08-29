#!/usr/bin/env python3

from etl.image_url_extractor import ImageUrlExtractor
from etl.exif_worker import ExifWorker
from etl.load_dw import load
from etl.dw_csv import export_csv
import sys
from threading import Thread
import time

def processar():
    MAX_COUNT_PER_CATEGORY = 5000
    categoria_label_dict = {
        'Esporte': 'sports,olympics,football,soccer',
        'Casamento': 'wedding,bride,bridesmaid',
        'Natureza': 'nature,landscape',
        'Retratos': 'portrait'}
    qt_category = len(categoria_label_dict.items())

    # Processando a EXIF
    worker = ExifWorker(qt_category * MAX_COUNT_PER_CATEGORY)
    worker.daemon = True
    worker.start()

    # Lendo URL de imagens por categoria
    if ler_categorias:
        for k, v in categoria_label_dict.items():
            extractor = ImageUrlExtractor(k, v, MAX_COUNT_PER_CATEGORY)
            extractor.extract_urls()

    worker.image_url_extractor_finalizado = True
    worker.join()

    # Carregando o modelo dimensional
    load()

    # Exporta o resultado para CSV
    export_csv()

    print("Processo finalizado")

def main(argv):
    ler_categorias = True
    if (len(argv) == 1):
        if argv[0] == 'csv':
            export_csv()
        else:
            print("Processar exif somente")
            ler_categorias = False
            processar()

if __name__ == '__main__':
    main(sys.argv[1:])
