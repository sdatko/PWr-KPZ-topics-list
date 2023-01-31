#!/usr/bin/env python3
from collections import defaultdict
import csv
from datetime import datetime
from glob import glob
import os.path
import re
from urllib.request import urlopen

from jinja2 import Environment
from jinja2 import FileSystemLoader

import yaml


#
# Variables
#
with open('config.yml', 'r') as file:
    CONFIG = yaml.safe_load(file)

SPREADSHEET_ID = CONFIG.get('spreadsheet_id')
SHEET_ID = CONFIG.get('sheet_id')

SHEET_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export'
SHEET_URL += f'?format=csv&id={SPREADSHEET_ID}&gid={SHEET_ID}'

TEMPLATES_DIR = CONFIG.get('templates_dir')
TEMPLATE_FILE = CONFIG.get('html_template_file')
OUTPUT_FILE = CONFIG.get('html_output_file')

LOGOS_DIR = CONFIG.get('logos_dir')
LOGOS_URL = CONFIG.get('logos_url')

COLORS = CONFIG.get('colors', {})
COMPANIES = defaultdict(dict)
PROJECTS = defaultdict(list)


#
# Text sanitizer
#
# – removes white characters from the beginning and the end of a string
# – replaces < and > with HTML entities to not allow extra tags in text
# – replaces newline characters with HTML line break tag
# – inserts non-breaking space after single letter or number
#
def sanitize(text: str) -> str:
    sanitized = text.strip()
    sanitized = sanitized.replace('<', '&lt;').replace('>', '&gt;')
    sanitized = sanitized.replace('\n', '<br />')
    sanitized = re.sub('[ ]([a-z0-9])[ ]', r' \1&nbsp;', sanitized)
    return sanitized


#
# Translator
#
translations = {
    'Konsultacje merytoryczne ze strony pracownika firmy.':
        'Consultations by an employee of the company.',
    'Nadzór merytoryczny pracownika firmy'
    ' nad całością lub fragmentami projektu.':
        'Supervision over the project by an employee of the company.',
    'Udział pracownika firmy w spotkaniach projektowych.':
        'Participation of a company employee in project meetings.',
    'Udostępnienie/sfinansowanie przez firmę'
    ' niezbędnego sprzętu/oprogramowania.':
        'Company will provision/finance the necessary hardware/software.',
    '3 osoby':
        '3 people',
    '4 osoby':
        '4 people',
    '5 osób':
        '5 people',
    '6 osób':
        '6 people',
    '7 osób':
        '7 people',
    '8 lub więcej osób':
        '8 or more people',
    'angielski':
        'English',
    'polski':
        'Polish',
    '(brak)':
        '(none)',
}


def translate(text):
    text = text.replace('&nbsp;', ' ')
    for i, j in translations.items():
        text = text.replace(i, j)
    text = re.sub('[ ]([a-z0-9])[ ]', r' \1&nbsp;', text)
    return text


#
# Read template
#
template_loader = FileSystemLoader(searchpath=TEMPLATES_DIR)
template_env = Environment(loader=template_loader)
template = template_env.get_template(TEMPLATE_FILE)

#
# Fetch data
#
data = urlopen(SHEET_URL).read().decode('utf-8')
lines = data.replace('\xa0', ' ').split('\r\n')
reader = csv.reader(lines[1:])

#
# Process projects
#
for row in reader:
    if len(row) == 13:  # Topic was not verified yet, so do not display it
        row[13] = 'NIE'
        row[14] = '0'
    if len(row) < 16:
        row[15] = 'PL'

    # time = row[0]  # Sygnatura czasowa
    # email = row[1]  # Adres e-mail
    # name = row[2]  # Imię i nazwisko
    # phone = row[3]  # Numer telefonu
    company = sanitize(row[4])  # Nazwa firmy
    title = sanitize(row[5])  # Tytuł projektu
    description = sanitize(row[6])  # Opis projektu
    offers = row[7]  # Planowane formy współpracy
    sizes = sanitize(row[8])  # Akceptowana wielkość grupy
    groups = sanitize(row[9])  # Liczba równoległych realizacji
    english = (row[10] == 'TAK')  # Czy może być angielskojęzyczny?
    appendix = sanitize(row[11])  # Dodatkowe uwagi
    # reserved = row[12]  # Przed-rezerwacja
    verified = (row[13] == 'TAK')  # ZWERYFIKOWANY
    available = sanitize(row[14])  # DOSTĘPNE GRUPY
    polish_labels = (row[15] == 'PL')  # JĘZYK ETYKIET

    if verified:
        offers = [sanitize(offer) for offer in offers.split(', ')]

        language = 'angielski, polski' if english else 'polski'

        if not appendix:
            appendix = '(brak)'

        if not polish_labels:
            appendix = translate(appendix)
            language = translate(language)
            offers = [translate(offer) for offer in offers]
            sizes = translate(sizes)

        company_ID = ''.join(filter(str.isalnum,
                                    company.lower().strip().split()[0]))

        logos = glob(f'{LOGOS_DIR}/{company_ID}.*')
        if logos:
            logo = logos[0]
            logo = os.path.join(LOGOS_URL, os.path.basename(logo))
        else:
            logo = None

        company = {
            'name': company,
            'logo': logo,
        }

        project = {
            'title': title,
            'description': description,
            'offers': offers,
            'sizes': sizes,
            'groups': groups,
            'language': language,
            'appendix': appendix,
            'available': available,
            'polish_labels': polish_labels,
        }

        COMPANIES[company_ID] = company
        PROJECTS[company_ID].append(project)

#
# Generate output
#
with open(OUTPUT_FILE, 'w') as file:
    last_update = str(datetime.now().astimezone().isoformat())
    file.write(template.render(
        COLORS=COLORS,
        COMPANIES=COMPANIES,
        PROJECTS=PROJECTS,
        last_update=last_update,
    ))
