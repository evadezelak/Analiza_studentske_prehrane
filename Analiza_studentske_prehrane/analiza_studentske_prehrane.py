import csv
import json
import os
import re
import sys

import requests


url = 'https://www.studentska-prehrana.si/sl/restaurant'
# mapa, v katero bomo shranili podatke
imenik = 'imenik_restavracij'
# ime datoteke v katero bomo shranili glavno stran
frontpage = 'frontpage.html'
# ime CSV datoteke v katero bomo shranili podatke
csv_datoteka = 'imenik_restavracij.csv'


def url_v_niz(url):
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('stran ne obstaja!')
        return 
    return r.text


def shrani_niz(text, directory, filename):
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None


def shrani_frontpage(url, ime_datoteke):
    vsebina = url_v_niz(url)
    with open(ime_datoteke, 'w', encoding='utf-8') as datoteka:
        datoteka.write(vsebina)
    print('shranjeno!')


shrani_frontpage(url, frontpage)
