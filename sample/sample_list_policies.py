"""
Snippet: Lista delle Policy (Paginata)
Scopo: Recuperare l'elenco di tutte le policy configurate nel Primary Server.

Endpoint: /netbackup/config/policies
Metodo HTTP: GET

Parametri:
- Headers: {"Accept": "application/vnd.netbackup+json;version=14.0", "Authorization": "<TOKEN>", "Cache-Control": "no-cache"}
- Query Params:
    - page[offset]: Offset per la paginazione
    - page[limit]: Numero massimo di elementi per pagina
    - filter: es. "autoManagedType eq 0" per filtrare solo le policy create manualmente
- Payload: Nessuno

Uso: Le risposte API restituiscono un dizionario che contiene un oggetto "links" con un URL "next" per la paginazione.
Risposta attesa: HTTP 200 OK. JSON con la struttura dati "data" contenente la lista ridotta delle policy.
"""

import requests

API_KEY = "dummy_jwt_token_12345"
USERNAME = "root"
HOSTNAME = "netbackup-primary.local"

def list_policies():
    base_url = f"https://{HOSTNAME}:1556/netbackup/config/policies"
    url = f"{base_url}/?page%5Boffset%5D=0&page%5Blimit%5D=50&filter=autoManagedType%20eq%200"
    
    headers = {
        "Accept": "application/vnd.netbackup+json;version=14.0",
        "Authorization": API_KEY,
        "Cache-Control": "no-cache"
    }

    policies = []

    try:
        while url:
            response = requests.get(url, headers=headers, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                # Estrazione del nome della policy
                for policy in data.get("data", []):
                    policies.append(policy.get("id"))
                
                # Controllo del link per la pagina successiva
                next_link = data.get("links", {}).get("next", {}).get("href")
                url = next_link  # Sarà None se non ci sono altre pagine
            else:
                print(f"Errore recupero policy {response.status_code}: {response.text}")
                break

        print(f"Recuperate {len(policies)} policy. Elenco parziale:")
        print(policies[:5])

    except Exception as e:
        print(f"Eccezione durante la chiamata API: {e}")

if __name__ == "__main__":
    list_policies()
