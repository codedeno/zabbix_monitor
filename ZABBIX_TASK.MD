# Funzione invio info verso Zabbix

## Modifica del database
Il database creato da `job_monitor.py` deve contenere un campo in più chiamato "sent" (CSV $14_sent). Il suo valore è TRUE o FALSE e ha il seguente significato:
- TRUE: il job è stato inviato a Zabbix
- FALSE: il job non è stato inviato a Zabbix

## File sample
I seguenti file non sono da prendere in considerazione per la produzione ma servono esclusivamente per lo sviluppatore e l'agente come riferimento per comprendere il funzionamento del protocollo zabbix:

*   `docs/sample_sender.json`
*   `docs/sample_sender_multiple.json`

## Modalità di invio

`doc/sample_sender.py` contiene uno snippet di codice per l'invio di informazioni verso Zabbix. Preferirei questa modalità di invio piuttosto che utilizzare librerie esterne dato che è complicato installare librerie esterne in ambiente chiuso.
Sarà quindi necessario utilizzare dei thread che inviano messaggi a Zabbix server. 
L'invio avverrà in una unica send per massimizzare l'efficienza e diminuire il traffico di rete.

La scelta sarà quindi tra le seguenti:
- Inviare un messaggio a zabbix per ogni dominio di backup (quindi per ogni HOST_NAME_IN_ZABBIX)
- Inviare un unico messaggio a zabbix per tutti i domini di backup

Dato che le API requests dovrebbero essere fatte in multithread, la soluzione migliore è inviare un messaggio a zabbix per ogni dominio di backup. In questo modo anche Zabbix elabora meno dati per volta a seconda della dimensione del dominio e quindi del payload.

### Campi dedicati a Zabbix

Creato un file json `zabbix.json`che contiene informazioni di connessione verso il server Zabbix

- ZABBIX_SERVER = "192.168.1.100" 
- ZABBIX_PORT = 10051
- ITEM_KEY = "netbackup.job.payload"

Questi campi saranno inseriti all'interno del file dedicato a zabbix e verranno letti all'avvio dello script

### Payload
Il payload sarà il seguente (ignorare i file sample):
- "client_name"
- "job_id"
- "status_code"
- "policy_name"
- "schedule_name"
- "schedule_type"

### HOST_NAME_IN_ZABBIX
Il campo HOST_NAME_IN_ZABBIX sarà uguale a quello del primary server, quindi può essere preso cal `credentials.json` chiave "domain".

### Logging

Logga anche gli invii verso Zabbix.

## Cosa inviare

- Inviare tutti i job con "state" = "DONE" e "sent" = "FALSE"
- Una volta inviato il job a Zabbix, impostare "sent" = "TRUE"
- Quando lo script viene avviato nuovamente, per ogni chiamata netbackup/admin/jobs/{BACKUP_ID} verifica se lo stato di quel JOBID è cambiato in "DONE" (stesso comportamento in pratica per l'aggiornamento del database) e se lo è invia a zabbix il messaggio (o lo inserisce nel messaggio cumulativo per quel HOST_NAME_IN_ZABBIX) impostando sent = "TRUE".