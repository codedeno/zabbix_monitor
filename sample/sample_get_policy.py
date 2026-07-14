#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Denis Gerolini <denis.gerolini@datacare.it>
# This file is part of zabbix_monitor

"""
Snippet: Dettaglio Singola Policy
Scopo: Recuperare l'intero oggetto JSON descrittivo di una specifica policy.

Endpoint: /netbackup/config/policies/{policy_name}
Metodo HTTP: GET

Parametri:
- Headers: 
    - "Accept": "application/vnd.netbackup+json;version=14.0"
    - "Authorization": "<TOKEN>"
    - "X-NetBackup-Include-OData-VMware": "true" (se si desiderano campi estesi VMware)
    - "X-NetBackup-Include-OData-HyperV": "true" (se si desiderano campi estesi HyperV)
- Query Params: Nessuno
- Payload: Nessuno

Uso: Il nome della policy viene inserito direttamente nel path della URL.
Risposta attesa: HTTP 200 OK. JSON con tutti i dettagli (attributi, client, schedule, selezioni di backup).
"""

import requests

API_KEY = "dummy_jwt_token_12345"
USERNAME = "root"
HOSTNAME = "netbackup-primary.local"

def get_policy(policy_name):
    url = f"https://{HOSTNAME}:1556/netbackup/config/policies/{policy_name}"
    
    headers = {
        "Accept": "application/vnd.netbackup+json;version=14.0",
        "Authorization": API_KEY,
        "X-NetBackup-Include-OData-VMware": "true",
        "X-NetBackup-Include-OData-HyperV": "true"
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            policy_data = response.json()
            print(f"Policy {policy_name} recuperata correttamente.")
            print(f"Tipo policy (policyType): {policy_data.get('data', {}).get('attributes', {}).get('policyType')}")
        else:
            print(f"Errore recupero policy {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Eccezione durante la chiamata API: {e}")

if __name__ == "__main__":
    get_policy("TEST_POLICY_VMWARE")
