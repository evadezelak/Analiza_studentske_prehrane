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
    r'<div class="row restaurant-row.*?".*?'
    r'<img src=.*? />',
    flags = re.DOTALL
)

restavracija = re.compile(
    r'<div class="row restaurant-row (?P<vegetarijansko>service-1)? ?(?P<dostop_za_invalide>service-3)? ?(?P<dostava>service-5)? ?(?P<odprto_ob_vikendih>service-20)?.*?(?P<nov_lokal>service-69)?"(?:\s|\n)*data.*?'
    r'.*? data-doplacilo="(?P<doplacilo>.*?)".*?'
    r'data-lokal="(?P<ime>.*?)".*?'
    r'data-city="(?P<kraj>.*?)".*?'
    r'<div class="acidjs-rating-stars acidjs-rating-disabled">(?:\s|\n)*(?P<ocena>.*?)</div>.*?'
    r'<small><i>(?P<naslov>.*?)</i>.*?',
    flags = re.DOTALL
)

ocena = re.compile(
    r'<input checked="checked".*?value="(?P<ocena>\d+)?".*?></label>.*?',
    flags = re.DOTALL
)



def izloci_podatke(vzorec):
    podatki_restavracije = restavracija.search(vzorec).groupdict()

    txt = podatki_restavracije['ocena']
    ocena1 = ocena.search(txt)
    if ocena1 is None:
        ocena1 = '/'
    else:
        ocena1 = ocena.search(txt).groupdict()
        ocena1 = ocena1['ocena']
    podatki_restavracije['ocena'] = ocena1

    for polje in ['vegetarijansko', 'dostop_za_invalide', 'dostava', 'odprto_ob_vikendih', 'nov_lokal']:
        if podatki_restavracije[polje] is not None:
            podatki_restavracije[polje] = 'DA'
        else:
            podatki_restavracije[polje] = 'NE'

    podatki_restavracije['doplacilo'] = (podatki_restavracije['doplacilo']).replace(',', '.')
    podatki_restavracije['doplacilo'] = float(podatki_restavracije['doplacilo'])
    podatki_restavracije['ime'] = podatki_restavracije['ime'].strip()
    podatki_restavracije['ime'] = podatki_restavracije['ime'].replace('&quot;', '"')
    podatki_restavracije['ime'] = podatki_restavracije['ime'].replace('&amp;', '&')
    podatki_restavracije['ime'] = podatki_restavracije['ime'].replace('&#39;', "'")
    podatki_restavracije['ime'] = podatki_restavracije['ime'].replace('&#180;', "'")
    podatki_restavracije['naslov'] = podatki_restavracije['naslov'].strip()
    podatki_restavracije['kraj'] = podatki_restavracije['kraj'].strip()
    return podatki_restavracije

podatki_restavracije = []
vsebina = vsebina_datoteke('imenik_restavracij/frontpage.html')
for ujemanje in restavracija.finditer(vsebina):
    print('Računam')
    podatki_restavracije.append(izloci_podatke(ujemanje.group(0)))
zapisi_json(podatki_restavracije, 'obdelani-podatki/vse-restavracije.json')
zapisi_csv(podatki_restavracije, ["ime", "naslov", "kraj", "ocena", "doplacilo", "vegetarijansko", "dostop_za_invalide", "dostava", "odprto_ob_vikendih", "nov_lokal"], 'obdelani-podatki/vse-restavracije.csv')

print(len(podatki_restavracije))
