#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Denis Gerolini <denis.gerolini@datacare.it>
# This file is part of zabbix_monitor

"""
Snippet: Recupero Storage Units (PureDisk)
Scopo: Recuperare l'elenco delle Storage Unit, filtrando in base alla tipologia (es. server MSDP - PureDisk).

Endpoint: /netbackup/storage/storage-units
Metodo HTTP: GET

Parametri:
- Headers: {"Accept": "application/vnd.netbackup+json;version=14.0", "Authorization": "<TOKEN>"}
- Query Params:
    - filter: stringa OData per filtrare le STU (es. "storageServerType eq 'PureDisk'")
    - page[limit]: paginazione
    - page[offset]: paginazione
- Payload: Nessuno

Uso: Utile per popolare liste a discesa o validare la disponibilità di una Storage Unit specifica prima di un restore/backup.
Risposta attesa: HTTP 200 OK con un JSON contenente l'array delle Storage Unit nel nodo "data".
"""

import requests

API_KEY = "dummy_jwt_token_12345"
USERNAME = "root"
HOSTNAME = "netbackup-primary.local"

def get_storage_units():
    base_url = f"https://{HOSTNAME}:1556/netbackup/storage/storage-units"
    url = f"{base_url}?filter=storageServerType%20eq%20%27PureDisk%27&page%5Blimit%5D=500&page%5Boffset%5D=0"
    
    headers = {
        "Accept": "application/vnd.netbackup+json;version=14.0",
        "Authorization": API_KEY
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            stu_list = [item["attributes"]["name"] for item in data.get("data", [])]
            print(f"Trovate {len(stu_list)} Storage Unit (PureDisk):")
            print(stu_list[:5])  # Stampa le prime 5
        else:
            print(f"Errore recupero Storage Units {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Eccezione durante la chiamata API: {e}")

if __name__ == "__main__":
    get_storage_units()
