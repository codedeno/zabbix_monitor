# Modifica comportamento script job_monitor.py

Questo piano descrive le modifiche da apportare a [job_monitor.py](file:///Users/datadeno/Datacare%20Dropbox/Denis%20Gerolini/Mac/Documents/Antigravity/zabbix_monitor/job_monitor.py) per ottimizzare la scansione dei job, riducendo il carico di richieste bulk e gestendo in modo mirato l'aggiornamento dei job pendenti e l'acquisizione incrementale dei nuovi.

---

## Prima scansione (comportamento attuale)
1. Se non sono presenti database sqlite (`netbackup_jobs.db` o tabella vuota) effettua una richiesta massiva (bulk) dei job basata sulla finestra temporale `--lookback-hours`.
2. Scrive nel database e rigenera il CSV.

## Scansioni successive
Per ogni Primary Server:
1. **Verifica dei JOB pendenti**:
   * Interroga il database sqlite per identificare tutti i job correnti di quel Primary Server che non sono stati completati (quindi con `state != 'DONE'`).
   * Effettua una chiamata API diretta per ogni JOB ID individuato verso l'endpoint:
     `GET https://{domain}:1556/netbackup/admin/jobs/{jobId}`
     (facendo riferimento alle specifiche per `/admin/jobs/{jobId}` definite in [admin.yaml](file:///Users/datadeno/Datacare%20Dropbox/Denis%20Gerolini/Mac/Documents/Antigravity/zabbix_monitor/doc_10.4.0.1/admin.yaml)).
2. **Aggiornamento dei dati**:
   * Verifica se il job ha terminato o è stato aggiornato, registrando le variazioni nel database e nel CSV.
3. **Chiamata incrementale per i nuovi JOB**:
   * Al termine della verifica dei job pendenti, individua il `jobId` più grande (massimo) salvato nel database per quel Primary Server.
   * Effettua una chiamata massiva recuperando solo i job più recenti a partire da tale ID, usando il filtro OData `jobId gt {max_job_id}`.
     Ad esempio: `netbackup/admin/jobs?filter=jobId%20gt%208414&page%5Blimit%5D=100` (in questo caso l'ultimo JobId nel database era 8414).
4. **Popolamento finale**:
   * Popola il database con i nuovi job recuperati e rigenera il CSV.
