"""
Snippet: Download Certificato CA
Scopo: Scaricare il certificato CA (webRootCert) dal Primary Server NetBackup, necessario per le successive validazioni SSL.

Endpoint: /netbackup/security/cacert
Metodo HTTP: GET

Parametri:
- Headers: {"accept": "*/*"}
- Query Params: Nessuno
- Payload: Nessuno

Uso: L'endpoint viene invocato sulla porta 1556 in HTTPS. Essendo il certificato CA, la validazione SSL deve essere disabilitata (verify=False) per questa prima chiamata.
Risposta attesa: JSON contenente il certificato CA nel campo "webRootCert".
"""

import requests
import warnings

# Sopprimiamo il warning per la richiesta non verificata (verify=False)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Variabili simulate (non usate per questa specifica chiamata perché non autenticata)
API_KEY = "dummy_api_key_12345"
USERNAME = "root"
HOSTNAME = "netbackup-primary.local"

def get_certificate():
    url = f"https://{HOSTNAME}:1556/netbackup/security/cacert"
    headers = {"accept": "*/*"}

    try:
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            cert_data = response.json().get("webRootCert")
            print("Certificato scaricato con successo:")
            print(cert_data[:100] + "...\n") # Stampa i primi 100 caratteri
        else:
            print(f"Errore {response.status_code}: {response.text}")

    except Exception as e:
        print(f"Eccezione durante la chiamata API: {e}")

if __name__ == "__main__":
    get_certificate()
