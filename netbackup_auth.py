#!/usr/bin/env python3
"""
Script: netbackup_auth.py
Scopo: Gestione autenticazione (Login/Logout) e certificati SSL CA per NetBackup Primary Server.
       Legge le credenziali da credentials.json, scarica i certificati CA se non presenti,
       effettua il login tramite API Key e invalida la sessione con il logout.
"""

import os
import json
import requests
import warnings

# Disabilita i warning di urllib3 per le richieste HTTPS non verificate (verify=False)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

CREDENTIALS_FILE = "credentials.json"
CERTIFICATES_DIR = "certificates"

def carica_credenziali():
    """Carica l'elenco delle credenziali dal file JSON."""
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"Errore: Il file delle credenziali '{CREDENTIALS_FILE}' non esiste.")
        return []
    
    try:
        with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Errore durante la lettura del file delle credenziali: {e}")
        return []

def gestisci_certificato(domain):
    """
    Verifica se il certificato CA per il dominio è presente localmente.
    Se non presente, lo scarica dal Primary Server e lo salva nella cartella dei certificati.
    Ritorna il percorso del certificato da usare per la verifica SSL o False in caso di errore.
    """
    if not os.path.exists(CERTIFICATES_DIR):
        os.makedirs(CERTIFICATES_DIR)

    cert_path = os.path.join(CERTIFICATES_DIR, f"{domain}.pem")
    
    if os.path.exists(cert_path):
        print(f"Certificato per {domain} già presente localmente: {cert_path}")
        return cert_path

    print(f"Certificato non trovato in locale per {domain}. Download in corso...")
    url = f"https://{domain}:1556/netbackup/security/cacert"
    headers = {"accept": "*/*"}

    try:
        # Per scaricare il certificato CA usiamo verify=False poiché non lo possediamo ancora
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            cert_data = response.json().get("webRootCert")
            if cert_data:
                with open(cert_path, 'w', encoding='utf-8') as f:
                    f.write(cert_data)
                print(f"Certificato per {domain} salvato correttamente in: {cert_path}")
                return cert_path
            else:
                print(f"Errore: Risposta da {domain} non contiene il campo 'webRootCert'.")
        else:
            print(f"Errore download certificato da {domain} (Stato: {response.status_code}): {response.text}")
    except Exception as e:
        print(f"Eccezione durante il download del certificato per {domain}: {e}")
    
    return False

def esegui_login(domain, username, api_key, cert_path):
    """
    Effettua la chiamata di login al server usando l'API Key.
    Ritorna il token JWT se il login ha successo, altrimenti None.
    """
    url = f"https://{domain}:1556/netbackup/login"
    headers = {
        "Accept": "application/vnd.netbackup+json;version=11.0",
        "Content-Type": "application/vnd.netbackup+json;version=11.0"
    }
    payload = {
        "domainType": "vx",
        "domainName": "vrts.apikey",
        "userName": username,
        "password": api_key
    }

    try:
        response = requests.post(url, headers=headers, json=payload, verify=cert_path, timeout=15)
        
        if response.status_code == 201:
            token = response.json().get("token")
            print(f"Login completato su {domain}. Token ottenuto: {token[:20]}...")
            return token
        else:
            print(f"Errore login su {domain} (Stato {response.status_code}): {response.text}")
    except Exception as e:
        print(f"Eccezione durante il login su {domain}: {e}")
    
    return None

def esegui_logout(domain, token, cert_path):
    """Invalida il token JWT effettuando il logout dal server."""
    url = f"https://{domain}:1556/netbackup/logout"
    headers = {
        "accept": "*/*",
        "Authorization": token
    }

    try:
        response = requests.post(url, headers=headers, verify=cert_path, timeout=15)
        
        if response.status_code in [200, 204]:
            print(f"Logout completato con successo da {domain}.")
            return True
        else:
            print(f"Errore logout da {domain} (Stato {response.status_code}): {response.text}")
    except Exception as e:
        print(f"Eccezione durante il logout da {domain}: {e}")
    
    return False

def main():
    credenziali = carica_credenziali()
    if not credenziali:
        print("Nessuna credenziale da elaborare.")
        return

    for cred in credenziali:
        domain = cred.get("domain") or cred.get("Domain")
        username = cred.get("username") or cred.get("Username")
        api_key = cred.get("ApiKey") or cred.get("api_key")

        if not domain or not username or not api_key:
            print(f"Credenziali non valide rilevate: {cred}")
            continue

        print(f"\n--- Avvio elaborazione per il server: {domain} ---")
        
        # Gestione del certificato SSL CA
        cert_path = gestisci_certificato(domain)
        if not cert_path:
            print(f"Impossibile procedere con {domain} senza certificato CA validato.")
            continue

        # Esecuzione del login
        token = esegui_login(domain, username, api_key, cert_path)
        if not token:
            continue

        # Esecuzione immediata del logout per invalidare la sessione
        esegui_logout(domain, token, cert_path)

if __name__ == "__main__":
    main()
