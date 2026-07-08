"""
Snippet: Export multithread dei job NetBackup su CSV
Scopo: Per ciascun dominio NetBackup presente in credentials.json, recupera TUTTI i job
       (seguendo la paginazione cursor-based) e scrive un unico file CSV con le colonne
       job_id, domain, jobType, policyName, scheduleName, clientName, status, state, backupid.
       Ogni dominio viene interrogato in un thread indipendente (2 domini -> 2 thread);
       la scrittura su disco avviene UNA SOLA VOLTA, nel thread principale, dopo che tutti
       i thread sono terminati: i thread producono solo dati in memoria, quindi non esiste
       concorrenza sulla scrittura del CSV.
Endpoint: GET /netbackup/admin/jobs
Metodo HTTP: GET
Parametri:
    - page[limit] (query): dimensione pagina (paginazione cursor-based)
    - page[after] (query): cursore di paginazione, ricavato da links.next.href
    - sort (query): ordinamento, qui "-startTime,jobId"
    - Header Accept: application/vnd.netbackup+json;version=11.0 (versione richiesta da admin.yaml
      per la risposta di questo endpoint)
    - Header Authorization: API Key del dominio (nessun prefisso "Bearer")
Uso:
    python3 sample_export_jobs_to_csv.py
    (richiede un file credentials.json nella root del progetto, non incluso nel repo,
     con struttura [{"domain": ..., "username": ..., "ApiKey": ...}, ...])
Risposta attesa: 200 con body {"data": [...], "links": {"next": {...}}, "meta": {...}}
"""

import csv
import json
import threading

import requests

CREDENTIALS_PATH = "credentials.json"
CSV_OUTPUT_PATH = "sample/jobs_export.csv"
CSV_FIELDS = [
    "job_id",
    "domain",
    "jobType",
    "policyName",
    "scheduleName",
    "clientName",
    "status",
    "state",
    "backupid",
]
PAGE_LIMIT = 100


def load_credentials(path=CREDENTIALS_PATH):
    """Carica la lista di credenziali (domain, username, ApiKey) da credentials.json."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fetch_jobs_for_domain(domain, api_key, page_limit=PAGE_LIMIT):
    """
    Recupera tutti i job di un dominio NetBackup seguendo la paginazione cursor-based.
    Eseguita all'interno di un thread dedicato al dominio: non scrive mai su disco,
    ritorna solo la lista di righe pronte per il CSV.
    """
    headers = {
        "Accept": "application/vnd.netbackup+json;version=11.0",
        "Authorization": api_key,
    }
    url = (
        f"https://{domain}:1556/netbackup/admin/jobs"
        f"?page%5Blimit%5D={page_limit}&sort=-startTime,jobId"
    )

    rows = []
    while url:
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=30)
        except requests.exceptions.RequestException as exc:
            print(f"[{domain}] Errore di connessione: {exc}")
            break

        if response.status_code != 200:
            print(f"[{domain}] Errore {response.status_code}: {response.text}")
            break

        body = response.json()
        for job in body.get("data", []):
            attributes = job.get("attributes", {})
            rows.append(
                {
                    "job_id": attributes.get("jobId", ""),
                    "domain": domain,
                    "jobType": attributes.get("jobType", ""),
                    "policyName": attributes.get("policyName", ""),
                    "scheduleName": attributes.get("scheduleName", ""),
                    "clientName": attributes.get("clientName", ""),
                    "status": attributes.get("status", ""),
                    "state": attributes.get("state", ""),
                    "backupid": attributes.get("backupId", ""),
                }
            )

        url = body.get("links", {}).get("next", {}).get("href")

    print(f"[{domain}] Recuperati {len(rows)} job.")
    return rows


def write_jobs_csv(all_rows, csv_path=CSV_OUTPUT_PATH):
    """Scrive tutte le righe raccolte su un unico file CSV (unico punto di scrittura)."""
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)


def _thread_target(domain, api_key, results, index):
    results[index] = fetch_jobs_for_domain(domain, api_key)


if __name__ == "__main__":
    credentials = load_credentials()

    results = [None] * len(credentials)
    threads = []
    for index, cred in enumerate(credentials):
        t = threading.Thread(
            target=_thread_target,
            args=(cred["domain"], cred["ApiKey"], results, index),
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    all_rows = [row for domain_rows in results if domain_rows for row in domain_rows]

    write_jobs_csv(all_rows)
    print(f"Totale job esportati: {len(all_rows)} -> {CSV_OUTPUT_PATH}")
