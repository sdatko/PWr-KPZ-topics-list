#!/usr/bin/env python3
from collections import defaultdict
import csv
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
TEMPLATE_FILE = CONFIG.get('csv_template_file')
OUTPUT_FILE = CONFIG.get('csv_output_file')

COMPANIES = defaultdict(str)
PROJECTS = defaultdict(list)


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
    # time = row[0]  # Sygnatura czasowa
    # email = row[1]  # Adres e-mail
    # name = row[2]  # Imię i nazwisko
    # phone = row[3]  # Numer telefonu
    company = row[4].strip()  # Nazwa firmy
    title = row[5].strip()  # Tytuł projektu
    # description = row[6]  # Opis projektu
    # offers = row[7]  # Planowane formy współpracy
    # sizes = row[8]  # Akceptowana wielkość grupy
    groups = int(row[9].strip())  # Liczba równoległych realizacji
    # english = (row[10] == 'TAK')  # Czy może być angielskojęzyczny?
    # appendix = row[11]  # Dodatkowe uwagi
    reserved = bool(row[12].strip())  # Przed-rezerwacja
    verified = (row[13] == 'TAK')  # ZWERYFIKOWANY
    # available = row[14]  # DOSTĘPNE GRUPY

    if verified:
        company_ID = ''.join(filter(str.isalnum,
                                    company.lower().strip().split()[0]))

        COMPANIES[company_ID] = company
        PROJECTS[company_ID].append({
            'title': title,
            'groups': groups,
            'reserved': reserved,
        })

#
# Generate output
#
with open(OUTPUT_FILE, 'w') as file:
    file.write(template.render(
        COMPANIES=COMPANIES,
        PROJECTS=PROJECTS,
    ))
