#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Denis Gerolini <denis.gerolini@datacare.it>
# This file is part of zabbix_monitor

"""
Snippet: Creazione Storage Unit (STU)
Scopo: Creare in maniera programmatica una nuova Storage Unit (es. per automazione Leonardo su Flex Appliance).

Endpoint: /netbackup/storage/storage-units
Metodo HTTP: POST

Parametri:
- Headers: {"Accept": "application/vnd.netbackup+json;version=14.0", "Content-Type": "application/vnd.netbackup+json;version=14.0", "Authorization": "<TOKEN>"}
- Query Params: Nessuno
- Payload: JSON contenente le specifiche della STU (nome, server media, server storage, disk pool).

Uso: Passando le specifiche corrette al payload si istanzia una STU mappata su un disk pool preesistente.
Risposta attesa: HTTP 201 Created (o 204 No Content) in base alla versione di NetBackup.
"""

import requests

API_KEY = "dummy_jwt_token_12345"
USERNAME = "root"
HOSTNAME = "netbackup-primary.local"

def create_storage_unit(stu_payload):
    url = f"https://{HOSTNAME}:1556/netbackup/storage/storage-units"
    
    headers = {
        "Accept": "application/vnd.netbackup+json;version=14.0",
        "Content-Type": "application/vnd.netbackup+json;version=14.0",
        "Authorization": API_KEY
    }

    try:
        response = requests.post(url, headers=headers, json=stu_payload, verify=False)
        
        if response.status_code in [201, 204]:
            print(f"Storage Unit creata con successo. ({response.status_code})")
        else:
            print(f"Errore creazione Storage Unit {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Eccezione durante la chiamata API: {e}")

if __name__ == "__main__":
    # Payload di esempio estratto dalla logica Leonardo
    dummy_stu_payload = {
        "data": {
            "type": "storage-unit",
            "attributes": {
                "name": "GOLD_VMWARE_STU_MSDP_MEDIA1",
                "storageUnitType": "Disk",
                "storageServerName": "MEDIA1.leonardo.local",
                "diskPoolName": "FLEX_DP_MSDP_VIA_5GE_MEDIA1",
                "mediaServerName": "MEDIA1",
                "storageServerType": "PureDisk"
            }
        }
    }
    create_storage_unit(dummy_stu_payload)
