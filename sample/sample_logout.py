#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Denis Gerolini <denis.gerolini@datacare.it>
# This file is part of zabbix_monitor

"""
Snippet: Logout dal Primary Server
Scopo: Invalidare il token JWT corrente chiudendo la sessione attiva.

Endpoint: /netbackup/logout
Metodo HTTP: POST

Parametri:
- Headers: {"accept": "*/*", "Authorization": "Bearer <TOKEN>"}
- Query Params: Nessuno
- Payload: Nessuno

Uso: Una volta invocato, il token usato per l'autorizzazione non sarà più valido.
Risposta attesa: HTTP 200 OK senza payload significativo oppure HTTP 204 No Content a seconda della versione.
"""

import requests

API_KEY = "dummy_jwt_token_12345" # Rappresenta il token JWT ottenuto al login
USERNAME = "root"
HOSTNAME = "netbackup-primary.local"

def logout():
    url = f"https://{HOSTNAME}:1556/netbackup/logout"
    
    headers = {
        "accept": "*/*",
        "Authorization": API_KEY  # Token passato come intestazione di autorizzazione
    }

    try:
        # verify=False usato qui solo per lo snippet.
        response = requests.post(url, headers=headers, verify=False)
        
        if response.status_code in [200, 204]:
            print("Logout effettuato correttamente.")
        else:
            print(f"Errore logout {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Eccezione durante la chiamata API: {e}")

if __name__ == "__main__":
    logout()
