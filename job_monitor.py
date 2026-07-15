#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: 2026 Denis Gerolini <denis.gerolini@datacare.it>
# This file is part of zabbix_monitor

"""
Script: job_monitor.py
Scopo: Interroga periodicamente GET /netbackup/admin/jobs su ciascun primary server
       elencato in credentials.json, applica la logica di stato (running/DONE) e per
       workload descritta in doc/job_guide.md, e persiste il risultato in un database
       SQLite (netbackup_jobs.db). In questa fase di test viene inoltre rigenerato ad
       ogni run un CSV (jobs_export.csv) che rispecchia esattamente la tabella, per
       ispezione manuale con awk.
Endpoint: GET /netbackup/admin/jobs
Metodo HTTP: GET
Parametri:
    - page[limit] (query): dimensione pagina (paginazione cursor-based)
    - page[after] (query): cursore di paginazione, ricavato da links.next.href
    - sort (query): "-lastUpdateTime,jobId"
    - filter (query, OData): "lastUpdateTime ge \"<timestamp UTC>\"" per limitare il
      fetch ai job aggiornati nella finestra --lookback-hours (default 24h); se il
      server rifiuta il filtro (HTTP 400), lo script ripiega su un fetch non filtrato.
    - Header Accept: application/vnd.netbackup+json;version=11.0
    - Header Authorization: token JWT ottenuto da netbackup_auth.esegui_login
Uso:
    python3 job_monitor.py [--lookback-hours N]
    (va lanciato dalla directory che contiene credentials.json e la cartella
     certificates/; login/logout e gestione certificati sono delegati a
     netbackup_auth.py)
Risposta attesa: 200 con body {"data": [...], "links": {"next": {...}}, "meta": {...}}
"""

import argparse
import csv
import os
import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests

import netbackup_auth
from netbackup_auth import (
    carica_credenziali,
    esegui_login,
    esegui_logout,
    gestisci_certificato,
)
import zabbix_sender

DB_PATH = "netbackup_jobs.db"
CSV_PATH = "jobs_export.csv"
API_VERSION = "11.0"
PAGE_LIMIT = 100
LOOKBACK_HOURS = 24
ROME_TZ = ZoneInfo("Europe/Rome")

LOG_DIR = "log"
LOG_RETENTION_DAYS = 10
log_lock = threading.Lock()


def setup_logging():
    """Crea la cartella log/ se non presente ed elimina i log più vecchi di 10 giorni."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Cancella i log più vecchi di 10 giorni
    now = datetime.now()
    limit = now - timedelta(days=LOG_RETENTION_DAYS)
    try:
        for filename in os.listdir(LOG_DIR):
            if filename.startswith("log_") and filename.endswith(".log"):
                filepath = os.path.join(LOG_DIR, filename)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if file_mtime < limit:
                    os.remove(filepath)
    except Exception as e:
        print(f"Errore durante la pulizia dei vecchi log: {e}")


def get_log_filepath():
    """Genera il percorso del file di log per la giornata corrente."""
    today_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"log_{today_str}.log")


def log_api_command(method, url):
    """Scrive nel log l'operazione API nel formato richiesto: HH:MM:SS GG/MM/AAA Comando_API."""
    now = datetime.now()
    timestamp_str = now.strftime("%H:%M:%S %d/%m/%Y")
    log_line = f"{timestamp_str} {method} {url}\n"

    filepath = get_log_filepath()
    with log_lock:
        try:
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception as e:
            print(f"Errore durante la scrittura del log: {e}")


CSV_FIELDS = [
    "primary_server",
    "job_id",
    "job_type",
    "policy_type",
    "state",
    "updated",
    "client",
    "status",
    "policy_name",
    "schedule_type",
    "schedule_name",
    "percent_complete",
    "result",
    "sent",
]

CSV_HEADERS = [
    "$1_primary_server",
    "$2_job_id",
    "$3_job_type",
    "$4_policy_type",
    "$5_state",
    "$6_updated",
    "$7_client",
    "$8_st",
    "$9_policy_name",
    "$10_schedule_type",
    "$11_schedule_name",
    "$12_%compl",
    "$13_res",
    "$14_sent",
]

DDL_JOBS_TABLE = """
CREATE TABLE IF NOT EXISTS jobs (
    primary_server   TEXT    NOT NULL,
    job_id           INTEGER NOT NULL,
    job_type         TEXT,
    policy_type      TEXT,
    state            TEXT    NOT NULL,
    updated          TEXT    NOT NULL,
    client           TEXT,
    status           INTEGER,
    policy_name      TEXT,
    schedule_type    TEXT,
    schedule_name    TEXT,
    percent_complete INTEGER,
    result           TEXT    NOT NULL,
    sent             TEXT    DEFAULT 'FALSE',
    PRIMARY KEY (primary_server, job_id)
)
"""


def init_db(db_path=DB_PATH):
    """Apre (creandolo se necessario) il database SQLite con la tabella jobs."""
    conn = sqlite3.connect(db_path)
    # Imposta esplicitamente che le righe vengano restituite come tuple per compatibilità,
    # anche se cursor.description è disponibile
    conn.row_factory = None
    conn.execute(DDL_JOBS_TABLE)
    
    # Migrazione per aggiungere la colonna sent nei DB esistenti
    try:
        conn.execute("ALTER TABLE jobs ADD COLUMN sent TEXT DEFAULT 'FALSE'")
    except sqlite3.OperationalError:
        pass # La colonna esiste già
    
    # Migrazione per dati storici: rimuove lo spazio dal timestamp di aggiornamento
    conn.execute("UPDATE jobs SET updated = replace(updated, ' ', 'T') WHERE updated LIKE '% %'")
    
    conn.commit()
    return conn


def parse_utc(timestamp):
    """Converte un timestamp ISO 8601 UTC con suffisso 'Z' (es. lastUpdateTime) in datetime aware."""
    return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def to_rome_str(dt_utc):
    """Converte un datetime UTC nella stringa locale Europe/Rome 'YYYY-MM-DDTHH:MM:SS'."""
    return dt_utc.astimezone(ROME_TZ).strftime("%Y-%m-%dT%H:%M:%S")


def derive_result(state, status):
    """OK/WARNING/ERROR sono significativi solo a job concluso (state=DONE); status=0 e'
    successo, status=1 e' un warning NetBackup, qualsiasi altro valore e' un errore."""
    if state != "DONE":
        return "RUNNING"
    if status == 0:
        return "OK"
    if status == 1:
        return "WARNING"
    return "ERROR"


def resolve_client(policy_type, attributes):
    """Per VMware clientName riporta spesso il backup host: il nome VM e' in workloadDisplayName."""
    if policy_type == "VMWARE":
        return attributes.get("workloadDisplayName") or attributes.get("clientName")
    return attributes.get("clientName")


def transform_job(domain, attributes):
    """Converte il blocco 'attributes' di un job NetBackup nella riga da persistere."""
    policy_type = attributes.get("policyType")
    state = attributes.get("state")
    status = attributes.get("status")
    updated_utc = parse_utc(attributes["lastUpdateTime"])

    return {
        "primary_server": domain,
        "job_id": attributes.get("jobId"),
        "job_type": attributes.get("jobType"),
        "policy_type": policy_type,
        "state": state,
        "updated": to_rome_str(updated_utc),
        "updated_utc": updated_utc,  # solo per il confronto in upsert_jobs, non va su DB/CSV
        "client": resolve_client(policy_type, attributes),
        "status": status,
        "policy_name": attributes.get("policyName"),
        "schedule_type": attributes.get("scheduleType"),
        "schedule_name": attributes.get("scheduleName"),
        "percent_complete": attributes.get("percentComplete"),
        "result": derive_result(state, status),
    }


def build_jobs_url(domain, since_utc, page_limit=PAGE_LIMIT):
    # I letterali date-time OData di NetBackup non vanno tra virgolette (verificato
    # contro il server reale: con le virgolette il filtro viene rifiutato con 400
    # errorCode 9401 "The OData filter criteria is invalid").
    since_str = since_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    filter_expr = f"lastUpdateTime ge {since_str}"
    return (
        f"https://{domain}:1556/netbackup/admin/jobs"
        f"?page%5Blimit%5D={page_limit}"
        f"&sort=-lastUpdateTime,jobId"
        f"&filter={quote(filter_expr, safe='')}"
    )


def _execute_bulk_fetch(domain, url, headers, cert_path):
    """Esegue un ciclo di fetch paginato (cursor-based) su un URL bulk."""
    unfiltered_url = (
        f"https://{domain}:1556/netbackup/admin/jobs"
        f"?page%5Blimit%5D={PAGE_LIMIT}&sort=-lastUpdateTime,jobId"
    )
    used_fallback = False
    rows = []

    while url:
        try:
            log_api_command("GET", url)
            response = requests.get(url, headers=headers, verify=cert_path, timeout=30)
        except requests.exceptions.RequestException as exc:
            print(f"[{domain}] Errore di connessione: {exc}")
            break

        if response.status_code == 400 and not used_fallback and "filter=" in url:
            print(f"[{domain}] Filtro rifiutato (400), ripiego su fetch non filtrato.")
            used_fallback = True
            url = unfiltered_url
            continue

        if response.status_code != 200:
            print(f"[{domain}] Errore {response.status_code}: {response.text}")
            break

        body = response.json()
        for job in body.get("data", []):
            attributes = job.get("attributes", {})
            if attributes.get("jobId") is None or attributes.get("lastUpdateTime") is None:
                continue
            rows.append(transform_job(domain, attributes))

        url = body.get("links", {}).get("next", {}).get("href")

    return rows


def fetch_jobs_for_domain(domain, headers, cert_path, since_utc):
    """Prima scansione: recupera (paginazione cursor-based) tutti i job aggiornati dopo since_utc."""
    url = build_jobs_url(domain, since_utc)
    return _execute_bulk_fetch(domain, url, headers, cert_path)


def fetch_single_job(domain, headers, cert_path, job_id):
    """Interroga direttamente l'endpoint per un singolo job."""
    url = f"https://{domain}:1556/netbackup/admin/jobs/{job_id}"
    try:
        log_api_command("GET", url)
        response = requests.get(url, headers=headers, verify=cert_path, timeout=30)
    except requests.exceptions.RequestException as exc:
        print(f"[{domain}] Errore di connessione per job {job_id}: {exc}")
        return None

    if response.status_code == 404:
        print(f"[{domain}] Job {job_id} non trovato (404). Sarà marcato come DONE/KO.")
        return {
            "primary_server": domain,
            "job_id": job_id,
            "state": "DONE",
            "result": "KO",
            "updated": to_rome_str(datetime.now(timezone.utc)),
            "is_404": True,
        }

    if response.status_code != 200:
        print(f"[{domain}] Errore {response.status_code} su job {job_id}: {response.text}")
        return None

    body = response.json()
    job_data = body.get("data", {})
    attributes = job_data.get("attributes", {})
    if not attributes.get("jobId") or not attributes.get("lastUpdateTime"):
        return None
    return transform_job(domain, attributes)


def fetch_incremental_jobs(domain, headers, cert_path, max_job_id):
    """Scansione incrementale: recupera i nuovi job creati dopo max_job_id."""
    filter_expr = f"jobId gt {max_job_id}"
    url = (
        f"https://{domain}:1556/netbackup/admin/jobs"
        f"?page%5Blimit%5D={PAGE_LIMIT}"
        f"&sort=-lastUpdateTime,jobId"
        f"&filter={quote(filter_expr, safe='')}"
    )
    return _execute_bulk_fetch(domain, url, headers, cert_path)


def upsert_jobs(conn, rows):
    """Applica la logica running/DONE per ciascuna riga, in un'unica transazione/commit."""
    cur = conn.cursor()
    inserted = changed = unchanged = 0

    for row in rows:
        cur.execute(
            "SELECT state, updated, percent_complete FROM jobs WHERE primary_server = ? AND job_id = ?",
            (row["primary_server"], row["job_id"]),
        )
        existing = cur.fetchone()

        if existing is None:
            if row.get("is_404"):
                cur.execute(
                    """
                    INSERT INTO jobs (
                        primary_server, job_id, state, updated, result
                    ) VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        row["primary_server"], row["job_id"], row["state"],
                        row["updated"], row["result"],
                    ),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO jobs (
                        primary_server, job_id, job_type, policy_type, state, updated, client,
                        status, policy_name, schedule_type, schedule_name, percent_complete, result
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        row["primary_server"], row["job_id"], row["job_type"], row["policy_type"], row["state"],
                        row["updated"], row["client"], row["status"], row["policy_name"],
                        row["schedule_type"], row["schedule_name"], row["percent_complete"], row["result"],
                    ),
                )
            inserted += 1
            continue

        existing_state, existing_updated, existing_percent = existing

        if existing_state == "DONE":
            # Job gia' concluso in precedenza: stato terminale, non si aggiorna piu'.
            unchanged += 1
            continue

        if row.get("is_404"):
            cur.execute(
                """
                UPDATE jobs SET
                    state = ?, updated = ?, result = ?
                WHERE primary_server = ? AND job_id = ?
                """,
                (row["state"], row["updated"], row["result"], row["primary_server"], row["job_id"]),
            )
            changed += 1
            continue

        if row["state"] != "DONE" and row["updated"] == existing_updated and row["percent_complete"] == existing_percent:
            # Ancora in running ma nulla di rilevante e' cambiato dall'ultimo run.
            unchanged += 1
            continue

        cur.execute(
            """
            UPDATE jobs SET
                job_type = ?, policy_type = ?, state = ?, updated = ?, client = ?, status = ?,
                policy_name = ?, schedule_type = ?, schedule_name = ?,
                percent_complete = ?, result = ?
            WHERE primary_server = ? AND job_id = ?
            """,
            (
                row["job_type"], row["policy_type"], row["state"], row["updated"], row["client"], row["status"],
                row["policy_name"], row["schedule_type"], row["schedule_name"],
                row["percent_complete"], row["result"],
                row["primary_server"], row["job_id"],
            ),
        )
        changed += 1

    conn.commit()
    print(f"Upsert completato: {inserted} inseriti, {changed} aggiornati, {unchanged} invariati.")


def export_csv(conn, csv_path=CSV_PATH):
    """Rigenera per intero il CSV a partire dal contenuto corrente della tabella jobs."""
    cur = conn.cursor()
    cur.execute(f"SELECT {', '.join(CSV_FIELDS)} FROM jobs ORDER BY primary_server, job_id")
    rows = cur.fetchall()

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator='\n')
        writer.writerow(CSV_HEADERS)
        writer.writerows(rows)

    print(f"CSV rigenerato: {csv_path} ({len(rows)} righe).")


def _thread_target(domain, username, api_key, cert_path, since_utc, domain_state, results, index):
    token = esegui_login(domain, username, api_key, cert_path)
    if not token:
        print(f"[{domain}] Login fallito, dominio saltato.")
        results[index] = []
        return

    headers = {
        "Accept": f"application/vnd.netbackup+json;version={API_VERSION}",
        "Authorization": token,
    }

    rows = []
    if domain_state["is_empty"]:
        # Prima scansione
        rows = fetch_jobs_for_domain(domain, headers, cert_path, since_utc)
        print(f"[{domain}] Prima scansione: recuperati {len(rows)} job.")
    else:
        # Scansioni successive: 1. Aggiornamento pending
        for job_id in domain_state["pending_jobs"]:
            job_row = fetch_single_job(domain, headers, cert_path, job_id)
            if job_row:
                rows.append(job_row)
        
        # 2. Fetch incrementale nuovi job
        new_rows = fetch_incremental_jobs(domain, headers, cert_path, domain_state["max_job_id"])
        rows.extend(new_rows)
        print(f"[{domain}] Scansione successiva: aggiornati {len(domain_state['pending_jobs'])} pendenti, recuperati {len(new_rows)} nuovi job.")

    esegui_logout(domain, token, cert_path)
    results[index] = rows


def main():
    setup_logging()
    netbackup_auth.logger_callback = log_api_command

    parser = argparse.ArgumentParser(description="Monitor job NetBackup -> SQLite/CSV.")
    parser.add_argument(
        "--lookback-hours",
        type=float,
        default=LOOKBACK_HOURS,
        help="Finestra temporale (ore) di job da interrogare (default: %(default)s)",
    )
    args = parser.parse_args()
    since_utc = datetime.now(timezone.utc) - timedelta(hours=args.lookback_hours)

    credentials = carica_credenziali()
    if not credentials:
        print("Nessuna credenziale da elaborare.")
        return

    conn = init_db()

    # Pre-computo dello stato dal DB per ogni dominio
    domain_states = {}
    for cred in credentials:
        domain = cred["domain"]
        cur = conn.cursor()
        cur.execute("SELECT MAX(job_id) FROM jobs WHERE primary_server = ?", (domain,))
        row = cur.fetchone()
        max_job_id = row[0] if row and row[0] is not None else None
        
        cur.execute("SELECT job_id FROM jobs WHERE primary_server = ? AND state != 'DONE'", (domain,))
        pending_jobs = [r[0] for r in cur.fetchall()]
        
        domain_states[domain] = {
            "is_empty": max_job_id is None,
            "max_job_id": max_job_id,
            "pending_jobs": pending_jobs
        }

    # Risoluzione dei certificati CA in sequenza (non nei thread), per evitare una
    # race condition su os.makedirs(CERTIFICATES_DIR) se piu' domini fossero privi
    # di certificato locale contemporaneamente (stesso motivo di export_jobs_to_csv.py).
    domains_to_fetch = []
    for cred in credentials:
        domain = cred["domain"]
        cert_path = gestisci_certificato(domain)
        if not cert_path:
            print(f"[{domain}] Impossibile ottenere il certificato CA, dominio saltato.")
            continue
        domains_to_fetch.append((domain, cred["username"], cred["ApiKey"], cert_path))

    results = [None] * len(domains_to_fetch)
    threads = []
    for index, (domain, username, api_key, cert_path) in enumerate(domains_to_fetch):
        t = threading.Thread(
            target=_thread_target,
            args=(domain, username, api_key, cert_path, since_utc, domain_states[domain], results, index),
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    all_rows = [row for domain_rows in results if domain_rows for row in domain_rows]

    upsert_jobs(conn, all_rows)
    
    # Invio a Zabbix dei job completati e non ancora inviati
    zabbix_sender.process_and_send(conn, log_api_command)
    
    export_csv(conn)
    conn.close()


if __name__ == "__main__":
    main()
