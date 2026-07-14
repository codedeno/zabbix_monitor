#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Denis Gerolini <denis.gerolini@datacare.it>
# This file is part of zabbix_monitor

"""
Snippet: Login al Primary Server
Scopo: Autenticarsi al Primary Server NetBackup per ottenere un token JWT da usare nelle chiamate API successive.

Endpoint: /netbackup/login
Metodo HTTP: POST

Parametri:
- Headers: {"Accept": "application/vnd.netbackup+json;version=14.0", "Content-Type": "application/json"}
- Query Params: Nessuno
- Payload: JSON contenente le credenziali (userName, password, domainName, domainType).

Uso: Il JSON payload deve riflettere il tipo di dominio corretto (es. unixpwd, nt, vx).
Risposta attesa: HTTP 201 Created. JSON contenente il token JWT nel campo "token".
"""

import requests

API_KEY = "dummy_api_key_12345"
USERNAME = "root"
HOSTNAME = "netbackup-primary.local"
PASSWORD = "dummy_password_123"

def login():
    url = f"https://{HOSTNAME}:1556/netbackup/login"
    
    headers = {
        "Accept": "application/vnd.netbackup+json;version=14.0",
        "Content-Type": "application/json"
    }

    payload = {
        "userName": USERNAME,
        "password": PASSWORD,
        "domainName": HOSTNAME,
        "domainType": "unixpwd"
    }

    try:
        # In un caso reale, 'verify' punterebbe al file .pem scaricato in precedenza.
        # Qui usiamo verify=False per semplicità nello snippet.
        response = requests.post(url, headers=headers, json=payload, verify=False)
        
        if response.status_code == 201:
            token = response.json().get("token")
            print(f"Login completato. Token ottenuto: {token[:20]}...")
            return token
        else:
            print(f"Errore login {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Eccezione durante la chiamata API: {e}")

if __name__ == "__main__":
    login()
