"""
Snippet: Creazione Policy
Scopo: Creare una nuova policy su NetBackup inviando la struttura JSON completa (Policy Payload).

Endpoint: /netbackup/config/policies
Metodo HTTP: POST

Parametri:
- Headers: {"Accept": "application/vnd.netbackup+json;version=14.0", "Content-Type": "application/vnd.netbackup+json;version=14.0", "Authorization": "<TOKEN>"}
- Query Params: Nessuno
- Payload: JSON rappresentante l'intera configurazione della policy (incluso "id", ovvero il nome della policy).

Uso: Viene usato per creare da zero, o duplicare (previo cambio nome/id) una policy.
Risposta attesa: HTTP 204 No Content se la creazione avviene con successo. In caso di errore di validazione viene ritornato un JSON con l'errore.
"""

import requests

API_KEY = "dummy_jwt_token_12345"
USERNAME = "root"
HOSTNAME = "netbackup-primary.local"

def create_policy(policy_payload):
    url = f"https://{HOSTNAME}:1556/netbackup/config/policies"
    
    headers = {
        "Accept": "application/vnd.netbackup+json;version=14.0",
        "Content-Type": "application/vnd.netbackup+json;version=14.0",
        "Authorization": API_KEY
    }

    try:
        response = requests.post(url, headers=headers, json=policy_payload, verify=False)
        
        if response.status_code == 204:
            print("Policy creata con successo (204 No Content).")
        else:
            print(f"Errore creazione policy {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Eccezione durante la chiamata API: {e}")

if __name__ == "__main__":
    # Struttura di esempio minima
    dummy_policy = {
        "data": {
            "type": "policy",
            "id": "NEW_SAMPLE_POLICY",
            "attributes": {
                "policyType": "Standard",
                "active": False
            }
        }
    }
    create_policy(dummy_policy)
