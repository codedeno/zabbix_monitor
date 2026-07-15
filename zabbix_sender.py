import json
import os
import socket
import struct
import threading

ZABBIX_CONFIG_FILE = "zabbix.json"

def load_config(logger_callback):
    if not os.path.exists(ZABBIX_CONFIG_FILE):
        if logger_callback:
            logger_callback("WARN", f"File di configurazione Zabbix {ZABBIX_CONFIG_FILE} non trovato. Invio a Zabbix disabilitato.")
        return None
    try:
        with open(ZABBIX_CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as e:
        if logger_callback:
            logger_callback("ERROR", f"Errore nella lettura di {ZABBIX_CONFIG_FILE}: {e}")
        return None

def send_domain_batch(domain, jobs, config, logger_callback, results_dict):
    zabbix_server = config.get("Zabbix_server")
    zabbix_port = config.get("port", 10051)
    item_key = config.get("item_key")

    if not zabbix_server or not item_key:
        if logger_callback:
            logger_callback("ERROR", f"Configurazione Zabbix non valida per il server {zabbix_server}")
        return

    # Preparazione payload Zabbix
    zabbix_data_list = []
    job_ids = []

    for job in jobs:
        job_id = job["job_id"]
        status = job["status"] if job["status"] is not None else -1
        client = job["client"] if job["client"] is not None else "unknown"
        policy_name = job["policy_name"] if job["policy_name"] is not None else "unknown"
        schedule_name = job["schedule_name"] if job["schedule_name"] is not None else "unknown"
        schedule_type = job["schedule_type"] if job["schedule_type"] is not None else "unknown"

        payload_dict = {
            "client_name": client,
            "job_id": job_id,
            "status_code": status,
            "policy_name": policy_name,
            "schedule_name": schedule_name,
            "schedule_type": schedule_type
        }

        zabbix_data_list.append({
            "host": domain,
            "key": item_key,
            "value": json.dumps(payload_dict)
        })
        job_ids.append(job_id)

    payload = {"request": "sender data", "data": zabbix_data_list}
    data_string = json.dumps(payload).encode("utf-8")
    data_len = len(data_string)
    header = b"ZBXD\x01" + struct.pack("<Q", data_len)
    packet = header + data_string

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(15.0)
            s.connect((zabbix_server, zabbix_port))
            s.sendall(packet)
            
            # Ricezione risposta
            risposta_bytes = s.recv(1024)
            if not risposta_bytes or len(risposta_bytes) < 13:
                if logger_callback:
                    logger_callback("ERROR", f"[{domain}] Risposta Zabbix non valida o vuota.")
                return

            risposta_json_str = risposta_bytes[13:].decode("utf-8")
            risposta = json.loads(risposta_json_str)
            
            # Analisi della risposta (es. {"response":"success","info":"processed: N; failed: X; total: Y; ..."})
            if risposta.get("response") == "success":
                info = risposta.get("info", "")
                if "failed: 0" in info:
                    # Tutti processati con successo
                    results_dict[domain] = job_ids
                    if logger_callback:
                        logger_callback("ZABBIX", f"[{domain}] Invio Zabbix completato con successo: {info}")
                else:
                    if logger_callback:
                        logger_callback("WARN", f"[{domain}] Invio Zabbix con fallimenti: {info}")
            else:
                if logger_callback:
                    logger_callback("ERROR", f"[{domain}] Zabbix ha risposto con errore: {risposta_json_str}")

    except Exception as e:
        if logger_callback:
            logger_callback("ERROR", f"[{domain}] Errore socket nell'invio a Zabbix: {e}")

def process_and_send(conn, logger_callback):
    config = load_config(logger_callback)
    if not config:
        return

    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs WHERE state = 'DONE' AND sent = 'FALSE'")
    
    # Costruiamo dizionari leggendo i nomi colonne
    columns = [description[0] for description in cur.description]
    all_pending_jobs = [dict(zip(columns, row)) for row in cur.fetchall()]

    if not all_pending_jobs:
        return

    # Raggruppamento per primary_server (domain)
    jobs_by_domain = {}
    for job in all_pending_jobs:
        domain = job["primary_server"]
        if domain not in jobs_by_domain:
            jobs_by_domain[domain] = []
        jobs_by_domain[domain].append(job)

    results_dict = {}
    threads = []

    # Avvio dei thread per dominio
    for domain, jobs in jobs_by_domain.items():
        t = threading.Thread(
            target=send_domain_batch,
            args=(domain, jobs, config, logger_callback, results_dict)
        )
        threads.append(t)
        t.start()

    # Attesa terminazione thread
    for t in threads:
        t.join()

    # Aggiornamento SQLite (Main Thread)
    successful_job_ids = []
    for domain, job_ids in results_dict.items():
        successful_job_ids.extend([(domain, j_id) for j_id in job_ids])

    if successful_job_ids:
        try:
            # Update parametrizzato per tuple (primary_server, job_id)
            cur.executemany(
                "UPDATE jobs SET sent = 'TRUE' WHERE primary_server = ? AND job_id = ?",
                successful_job_ids
            )
            conn.commit()
            if logger_callback:
                logger_callback("ZABBIX", f"Database aggiornato: marcati come inviati {len(successful_job_ids)} job.")
        except Exception as e:
            if logger_callback:
                logger_callback("ERROR", f"Errore nell'aggiornamento SQLite per Zabbix: {e}")
