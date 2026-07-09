# Guida alla lettura dei Job NetBackup (Activity Monitor via API)

## Scopo

Questa guida descrive come interpretare il JSON restituito dall'endpoint di listing dei job di NetBackup, ad esempio:

```
GET https://<primary-server>:1556/netbackup/admin/jobs?page%5Blimit%5D=10
```

L'obiettivo è individuare, a partire dalla risposta, quali job di backup sono **andati a buon fine** e quali sono **falliti**, e per quale client/server, in modo da poter inviare lo stato corretto a Zabbix.

Riferimento di specifica: [`doc_10.4.0.1/admin.yaml`](../doc_10.4.0.1/admin.yaml).

- Endpoint: `GET /admin/jobs` (lista, paginato) e `GET /admin/jobs/{jobId}` (singolo job).
- Header richiesto: `Accept: application/vnd.netbackup+json;version=11.0` (media-type version specifica per questa operazione — non dare per scontato che coincida con la versione di altri endpoint).
- Schema risposta: `getJobsResponse` → `data[]` (array di oggetti `type: "job"`) → ogni elemento ha un blocco `attributes` (schema `getJobDetailsResponse.attributes` in `admin.yaml`) che contiene tutti i campi descritti sotto.

Esempi reali di risposta usati per questa guida si trovano in `sample/sample_json/`:
- `sample_Oracle.json` — job Oracle e VMware misti, comprende anche esempi di job `DONE` con `status: 0`.
- `sample_fs_fails.json` — esempio di job Filesystem/Standard fallito (`state: REQUEUED`, `status: 71`).
- `sample_SQL_server.json` — attualmente vuoto: nessun esempio reale disponibile, vedi nota nella sezione SQL Server più sotto.

## Lettura base dei campi JSON

Ogni job è un elemento di `data[]`, con i campi rilevanti dentro `attributes`:

| Campo | Significato |
|---|---|
| `jobId` | Identificativo del job, indispensabile per correlarlo al numero mostrato nell'Activity Monitor. |
| `parentJobId` | ID del job che ha lanciato questo job. Se `parentJobId = 4`, allora il job con `jobId = 4` è il "padre" che ha lanciato il job corrente. `0` indica un job radice (nessun padre). |
| `jobPath` | Catena di ID dal job radice fino a questo job, formato `grandParentJobId.parentJobId.jobId` (per i job radice è semplicemente il proprio `jobId`). Utile per ricostruire la gerarchia senza risalire manualmente i `parentJobId`. |
| `jobType` | Il tipo di operazione: `BACKUP`, `RESTORE`, `DUPLICATE`, `DBBACKUP`, `VERIFY`, `ARCHIVE`, `INSTANT_ACCESS`, ecc. (46 valori enumerati in `admin.yaml`). Per il monitoraggio dei backup, il valore di interesse principale è **`BACKUP`** (i job Oracle nei sample hanno comunque `jobType: BACKUP`, non un valore dedicato — vedi nota Oracle sotto). |
| `policyType` | Il "workload" della policy: `STANDARD`, `MSWINDOWS`, `VMWARE`, `SQL_SERVER`, `OBACKUP` (Oracle), ecc. |
| `policyName` | Nome della policy configurata in NetBackup. |
| `scheduleType` | Tipo di schedulazione: `FULL_BACKUP`, `DIFFERENTIAL_INCREMENTAL_BACKUP`, `TRANSACTION_LOG_BACKUP`, `ARCHIVE_REDO_LOG_BACKUP`, ecc. |
| `scheduleName` | Nome della schedulazione configurata (es. `Incr`, `Tlog`, `Archive`, `Manual`). |
| `clientName` | Il nome del client. **Attenzione**: non è sempre il client di cui si sta facendo il backup — per workload VMware può essere il media server / backup host. Per gli altri workload (SQL Server, Oracle, Filesystem) è tipicamente il client effettivo. Vedi le sezioni per workload più sotto. |
| `status` | Codice di stato finale del job. Lo spec (`admin.yaml`) lo documenta solo come *"The final job status code"*, **senza specificare un range numerico ufficiale di successo/warning/errore**. In pratica, dal comportamento osservato nei sample: `status = 0` corrisponde a un job completato con successo (sempre abbinato a `state: DONE`); un valore diverso da `0` indica un problema (warning o errore, a seconda del codice — i codici di errore NetBackup sono documentati nel manuale prodotto, non nello spec REST). **Nota**: il campo `status` è assente/non popolato finché il job è ancora attivo — compare solo a job concluso. |
| `state` | Stato corrente del job nel suo ciclo di vita. Valori enumerati in `admin.yaml`: `QUEUED`, `ACTIVE`, `REQUEUED`, `DONE`, `SUSPENDED`, `INCOMPLETE`. Solo quando `state = DONE` il campo `status` è significativo per giudicare successo/fallimento. |
| `childCount` | Numero di job figli diretti lanciati da questo job (non include i discendenti dei figli). Fondamentale per capire se un job è quello "operativo": <br>• `childCount = 0` e `state = DONE` → questo è il job che ha effettivamente eseguito il backup: guardarne `status` per il risultato.<br>• `childCount = 0` ma ancora in `ACTIVE`/`QUEUED` → non è detto che questo job stia facendo il lavoro; potrebbe non aver ancora lanciato figli.<br>• `childCount = N ≠ 0` → questo è un job padre/orchestratore che ha lanciato N job figli: può essere **ignorato** ai fini della verifica dell'esito del backup, il risultato va cercato nei job figli. |
| `lastUpdateTime` | Timestamp dell'ultimo aggiornamento del job. Utile per capire se un job "fermo" in `ACTIVE`/`QUEUED` è effettivamente bloccato o si è mosso di recente. |
| `workloadDisplayName` | Nome "umano" del workload. **Vitale per i backup VMware**: è qui che compare il display name della VM VMware (mentre `clientName` per VMware riporta spesso il backup host/media server, non la VM). Per gli altri workload spesso coincide con `clientName`/`assetDisplayableName`. |

Note aggiuntive utili in fase di debug (non richieste per la logica base, ma disponibili nello schema):
- `jobQueueReason`: motivo per cui un job è in coda (enum numerico, `-99` = non applicabile/valore non valido). Utile solo quando `state = QUEUED`.
- `try` + endpoint `GET /admin/jobs/{jobId}/try-logs`: espone `tryStatusCode`/`tryStatusMessage` per ogni tentativo del job — utile per approfondire *perché* un job è fallito, oltre al semplice `status` finale.

## Lettura campi per workload SQL Server

> Sample di riferimento: `sample/sample_json/sample_SQL_server.json` — **attualmente il file è vuoto (0 righe di contenuto utile)**. Questa sezione riporta quindi solo l'indicazione fornita finché non sarà disponibile un JSON di esempio popolato da aggiungere in seguito.

- Il nome del client va letto dal campo **`clientName`**.

## Lettura campi per workload Oracle

> Sample di riferimento: `sample/sample_json/sample_Oracle.json`

- Il workload Oracle si riconosce dal campo **`policyType: "OBACKUP"`** (non da `jobType`, che nei job Oracle osservati vale sempre `BACKUP`, come per gli altri workload — es. job `812697` e `812695` nel sample hanno `jobType: "BACKUP"` e `policyType: "OBACKUP"`).
- Il nome del client è dato da **`clientName`** (es. `accs3237.agustawestland.local`).
- Il nome dell'istanza/database Oracle è riportato separatamente nel campo `instanceDatabaseName` (es. `DBELCMDL`), e `workloadDisplayName` riporta il nome in minuscolo dell'asset (es. `dbelcmdl`).

## Lettura campi per workload Filesystem (Standard / MSWindows)

> Sample di riferimento: `sample/sample_json/sample_fs_fails.json` — esempio di job fallito.

- Il nome del client si trova in **`clientName`** (es. `L99801C007056.leonardo.local`).
- Il workload si riconosce da **`policyType: "STANDARD"`** (o `MSWINDOWS` per client Windows).
- Esempio di job fallito dal sample: `jobId: 12`, `status: 71`, `state: "REQUEUED"` — un `status` diverso da `0` con `state` non ancora `DONE` indica che il job è stato rimesso in coda dopo un tentativo fallito; va monitorato fino a raggiungere `state: DONE` per un giudizio finale, oppure trattato come "in ritentativo" se lo stato resta `REQUEUED` a lungo (confrontando `lastUpdateTime`).

## Nota su VMware

Pur non essendo uno dei workload esplicitamente richiesti, i sample disponibili (`sample_Oracle.json`) contengono numerosi job VMware, utili come riferimento:

- `policyType: "VMWARE"`.
- `clientName` riporta spesso il **backup host / media server** (es. `L00301C006927.leonardo.local` in alcuni contesti), non la VM.
- Il nome della VM va letto da **`workloadDisplayName`** (es. `accs5178`, `accs5183`) — coerente con quanto indicato nella sezione "Lettura base dei campi json".
- `assetDisplayableName` riporta anch'esso il nome della VM ed è generalmente allineato a `workloadDisplayName`.

## Riferimenti

- Specifica OpenAPI: [`doc_10.4.0.1/admin.yaml`](../doc_10.4.0.1/admin.yaml) — schema `getJobsResponse` / `getJobDetailsResponse` (blocco `attributes`).
- Guida generale API: [`doc_10.4.0.1/getting-started.md`](../doc_10.4.0.1/getting-started.md) — autenticazione, versioning, paginazione.
- Esempi JSON reali: `sample/sample_json/sample_Oracle.json`, `sample/sample_json/sample_fs_fails.json`, `sample/sample_json/sample_SQL_server.json` (da popolare).
