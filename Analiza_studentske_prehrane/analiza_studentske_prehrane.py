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
csv_datoteka = 'vse-restavracije.csv'


def pripravi_imenik(ime_datoteke):
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)


def url_v_niz(url):
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('stran ne obstaja!')
        return 
    return r.text


def shrani_niz(text, ime_datoteke, filename):
    os.makedirs(ime_datoteke, exist_ok=True)
    path = os.path.join(ime_datoteke, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None


def vsebina_datoteke(ime_datoteke):
    with open(ime_datoteke, encoding='utf-8') as datoteka:
        return datoteka.read()


def zapisi_csv(slovarji, imena_polj, ime_datoteke):
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as csv_datoteka:
        writer = csv.DictWriter(csv_datoteka, fieldnames=imena_polj)
        writer.writeheader()
        for slovar in slovarji:
            writer.writerow(slovar)


def zapisi_json(objekt, ime_datoteke):
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as json_datoteka:
        json.dump(objekt, json_datoteka, indent=4, ensure_ascii=False)



vzorec = re.compile(
    r'<div class="row restaurant-row (?P<ugodnosti>.*?)".*?'
    #r'.*? data-doplacilo="(?P<doplacilo>.*?)".*?'
    r'data-lokal="(?P<ime>.*?)".*?'
    r'data-city="(?P<kraj>.*?)"',
    #r'<small><i>(?P<naslov>.*?)</i>.*?',
    re.DOTALL
)
    

def izloci_podatke(ujemanje):
    podatki_restavracije = ujemanje.groupdict()
    podatki_restavracije['ugodnosti'] = podatki_restavracije['ugodnosti'].strip()
    #podatki_restavracije['doplacilo'] = (podatki_restavracije['doplacilo']).replace(',', '.')
    #podatki_restavracije['doplacilo'] = float(podatki_restavracije['doplacilo'])
    podatki_restavracije['ime'] = podatki_restavracije['ime'].strip()
    #podatki_restavracije['naslov'] = podatki_restavracije['naslov'].strip()
    podatki_restavracije['kraj'] = podatki_restavracije['kraj'].strip()
    return podatki_restavracije

podatki_restavracije = []
stevec = 0
vsebina = vsebina_datoteke('imenik_restavracij/frontpage.html')
for ujemanje in vzorec.finditer(vsebina):
    stevec += 1
    print(stevec)
    podatki_restavracije.append(izloci_podatke(ujemanje))
zapisi_json(podatki_restavracije, 'obdelani-podatki/vse-restavracije.json')
zapisi_csv(podatki_restavracije, ["ime", "kraj", "ugodnosti"], 'obdelani-podatki/vse-restavracije.csv')
