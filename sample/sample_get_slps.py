#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Denis Gerolini <denis.gerolini@datacare.it>
# This file is part of zabbix_monitor

"""
Snippet: Recupero Storage Lifecycle Policies (SLP)
Scopo: Ottenere la lista di tutte le SLP (Storage Lifecycle Policies) configurate nel sistema.

Endpoint: /netbackup/config/slps
Metodo HTTP: GET

Parametri:
- Headers: {"Accept": "application/vnd.netbackup+json;version=14.0", "Authorization": "<TOKEN>"}
- Query Params:
    - page[limit]: limite di elementi per pagina
    - page[offset]: offset
- Payload: Nessuno

Uso: Permette di validare che la SLP di destinazione esista prima di modificare una policy.
Risposta attesa: HTTP 200 OK con l'elenco delle SLP nel nodo "data".
"""

import requests

API_KEY = "dummy_jwt_token_12345"
USERNAME = "root"
HOSTNAME = "netbackup-primary.local"

def get_slps():
    url = f"https://{HOSTNAME}:1556/netbackup/config/slps?page%5Blimit%5D=100&page%5Boffset%5D=0"
    
    headers = {
        "Accept": "application/vnd.netbackup+json;version=14.0",
        "Authorization": API_KEY
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            slp_list = [item["attributes"]["slpName"] for item in data.get("data", [])]
            print(f"Trovate {len(slp_list)} SLP:")
            print(slp_list[:5])
        else:
            print(f"Errore recupero SLPs {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Eccezione durante la chiamata API: {e}")

if __name__ == "__main__":
    get_slps()
