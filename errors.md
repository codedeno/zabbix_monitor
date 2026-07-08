# Database degli Errori di NetBackup API

Questo file raccoglie gli errori riscontrati durante lo sviluppo, la configurazione o l'esecuzione degli script Python per le API di NetBackup 10.4, con le relative cause e risoluzioni. **Deve essere consultato solo ed esclusivamente in caso di errori.**

---

## 1. Errore di Comando Non Trovato (`python`)

- **Errore riscontrato:** `zsh: command not found: python`
- **Contesto:** Tentativo di eseguire uno script Python tramite terminale usando `python`.
- **Causa:** Nei sistemi macOS moderni o in altri ambienti Unix, l'eseguibile `python` (Python 2) non è configurato di default nel PATH o non è installato.
- **Soluzione:** Utilizzare `python3` per eseguire gli script:
  ```bash
  python3 nome_script.py
  ```

---

## 2. Errore HTTP 406 - Media Type Non Supportato

- **Errore riscontrato:** `Stato 406: {"errorCode":8952,"errorMessage":"A response cannot be generated in the media type specified by the request accept header.","attributeErrors":{},"fileUploadErrors":[],"errorDetails":[]}`
- **Contesto:** Chiamata all'endpoint `/netbackup/login`.
- **Causa:** L'intestazione `Accept` o `Content-Type` contiene una versione non supportata dall'endpoint sul server (es. `version=14.0` anziché la versione corretta `version=11.0` documentata in `gateway.yaml`).
- **Soluzione:**
  - Allineare entrambi gli header `Accept` e `Content-Type` con la versione corretta indicata nei file YAML di specifica:
    ```python
    headers = {
        "Accept": "application/vnd.netbackup+json;version=11.0",
        "Content-Type": "application/vnd.netbackup+json;version=11.0"
    }
    ```

---

## 3. Warning di Richiesta HTTPS Non Verificata (`Unverified HTTPS request`)

- **Errore riscontrato:** `InsecureRequestWarning: Unverified HTTPS request is being made to host...`
- **Contesto:** Chiamata API effettuata con `verify=False` (solitamente per scaricare il certificato CA iniziale).
- **Causa:** Il modulo `urllib3` segnala che la connessione SSL non è verificata.
- **Soluzione:** Disabilitare o ignorare il warning specifico all'inizio del file:
  ```python
  import warnings
  warnings.filterwarnings('ignore', message='Unverified HTTPS request')
  ```

---

## 4. Errore di Autenticazione con API Key (Credenziali Errate/Non Valide)

- **Errore riscontrato:** Risposta `401 Unauthorized` o `400 Bad Request` durante il login tramite API Key.
- **Causa:** Quando si effettua il login a `/netbackup/login` usando una API Key invece di nome utente e password tradizionali, i parametri di dominio devono essere compilati in modo specifico:
  - `domainType` deve essere esattamente `"vx"`.
  - `domainName` deve essere esattamente `"vrts.apikey"`.
  - `password` deve contenere il valore dell'API Key.
- **Soluzione:** Assicurarsi che il payload della richiesta `POST` rispetti questa struttura:
  ```json
  {
      "domainType": "vx",
      "domainName": "vrts.apikey",
      "userName": "<username>",
      "password": "<api_key>"
  }
  ```

---

## 5. SSL Handshake Error (Mancanza Certificato CA)

- **Errore riscontrato:** `requests.exceptions.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain...`
- **Contesto:** Chiamate API eseguite con `verify=True` senza che il certificato CA del server sia registrato nel sistema o fornito a Requests.
- **Soluzione:**
  1. Scaricare preventivamente il certificato CA dall'endpoint `/netbackup/security/cacert` (porta 1556, usando temporaneamente `verify=False`).
  2. Salvare la stringa di testo `webRootCert` in un file locale (es. `certificates/dominio_server.pem`).
  3. Utilizzare il percorso del file `.pem` come parametro di validazione nelle chiamate successive:
     ```python
     requests.post(url, headers=headers, json=payload, verify='certificates/dominio_server.pem')
     ```
