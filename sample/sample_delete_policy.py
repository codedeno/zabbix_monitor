"""
Snippet: Eliminazione Policy
Scopo: Cancellare definitivamente una policy dal server NetBackup.

Endpoint: /netbackup/config/policies/{policy_name}
Metodo HTTP: DELETE

Parametri:
- Headers: {"accept": "*/*", "Authorization": "<TOKEN>"}
- Query Params: Nessuno
- Payload: Nessuno

Uso: Specificare il nome della policy esatto nel path. Operazione distruttiva, non richiede conferma tramite payload.
Risposta attesa: HTTP 204 No Content in caso di eliminazione corretta.
"""

import requests

API_KEY = "dummy_jwt_token_12345"
USERNAME = "root"
HOSTNAME = "netbackup-primary.local"

def delete_policy(policy_name):
    url = f"https://{HOSTNAME}:1556/netbackup/config/policies/{policy_name}"
    
    headers = {
        "accept": "*/*",
        "Authorization": API_KEY
    }

    try:
        response = requests.delete(url, headers=headers, verify=False)
        
        if response.status_code == 204:
            print(f"Policy '{policy_name}' eliminata con successo (204 No Content).")
        else:
            print(f"Errore eliminazione policy {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Eccezione durante la chiamata API: {e}")

if __name__ == "__main__":
    delete_policy("POLICY_TO_DELETE")
