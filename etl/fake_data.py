#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from decimal import *

websites = ['FlickrBuy','ShelterStock', 'AdoreStock']

def get_website():
    return random.choice(websites)

def get_nu_copias():
    return random.randrange(1, 9)

def get_image_value(lens_model):
    if lens_model in 'L IS' or lens_model in 'TAMRON SP' or lens_model in 'LEICA Summilux' or lens_model in 'Zeiss':
        return rnd(1200, 4000)
    elif lens_model in 'NIKKOR Z' or lens_model in 'OLYMPUS' or lens_model in 'PENTAX':
        return rnd(545, 900)
    else:
        return rnd(120, 500)

def rnd(min, max):
    return Decimal(str(random.randrange(1200, 4000)) +'.'+ str(random.randrange(0, 99)))
