#!/usr/bin/env python3

from etl.image_url_extractor import ImageUrlExtractor
from etl.exif_worker import ExifWorker
from etl.load_dw import load
from etl.dw_csv import export_csv
from etl.pre_load_db import pre_load_db
from etl.create_tables import create_tables
import sys
from threading import Thread
import time

def processar(ler_categorias):
    MAX_COUNT_PER_CATEGORY = 10000
    categoria_label_dict = {
        'Esporte': 'sports',
        'Casamento': 'wedding',
        'Natureza': 'nature',
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
    if (len(argv) == 1):
        if argv[0] == 'csv':
            print("Exportando DW para CSV CSV")
            export_csv()
        elif argv[0] == 'loaddw':
            print("Caregando DW e exportando para CSV")
            load()
            export_csv()
        elif argv[0] == 'preload':
            print("Recriando tabela e restaurando dados a partir dos CSVs")
            create_tables()
            pre_load_db()
        elif argv[0] == 'exif':
            print("Processar exif somente")
            processar(False)
    else:
        processar(True)

if __name__ == '__main__':
    main(sys.argv[1:])
