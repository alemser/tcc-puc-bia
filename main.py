#!/usr/bin/env python3

from etl.extrair_fotos_flickr import get_urls
import sys
from threading import Thread
import time

def main():
    threads = []

    t1 = Thread(target=get_urls, args=('sports', 999))
    t1.start()
    threads.append(t1)
    time.sleep(10)

    t2 = Thread(get_urls, ('wedding', 999))
    t2.start()
    threads.append(t2)
    time.sleep(10)

    t3 = Thread(get_urls, ('nature', 999))
    t3.start()
    threads.append(t3)
    time.sleep(10)

    t4 = Thread(get_urls, ('widelife', 999))
    t4.start()
    threads.append(t4)
    time.sleep(10)

    t5 = Thread(get_urls, ('landscape', 999))
    t5.start()
    threads.append(t5)
    time.sleep(10)

    t6 = Thread(get_urls, ('portrait', 999))
    t5.start()
    threads.append(t5)
    time.sleep(10)

    for t in threads:
        t.join()

    print("Processo finalizado")

if __name__ == '__main__':
    main()
