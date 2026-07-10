# Procedura di installazione offline (server senza accesso a internet)

Questa guida serve per preparare l'ambiente `.venv` di `job_monitor.py` su un server che ha già **Python 3 installato** ma **non ha accesso a internet/pip** (es. server di produzione isolato).

Le dipendenze dirette in `requirements.txt` (`requests`, `tzdata`, `zabbix_utils`) sono wheel **pure Python** (`py3-none-any`). Attenzione però a `charset_normalizer` (dipendenza transitiva di `requests`): pubblica anche wheel **binari specifici per piattaforma/interprete** (es. `...cp310-cp310-macosx_10_9_universal2.whl`). Se `pip download` viene eseguito su un Mac (o comunque su un sistema diverso dal server target), scarica il wheel compilato per quella piattaforma, incompatibile con il server Linux offline → vedi `errors.md` punto 6. Per questo motivo il comando di download va sempre eseguito specificando esplicitamente piattaforma/versione Python/ABI del server target (vedi step 1).

Non serve un eseguibile standalone (tipo PyInstaller) — quello servirebbe solo se il server target non avesse affatto Python 3 installato.

## 1. Sulla macchina CON internet

Scarica i pacchetti e tutte le loro dipendenze transitive in una cartella, specificando esplicitamente piattaforma/versione Python/ABI del server offline target (verificabili sul server con `python3 --version` e `uname -m`), per evitare di scaricare wheel compilati per la piattaforma della macchina locale invece che per quella del server:

```bash
cd /path/to/zabbix_monitor
pip download -r requirements.txt -d vendor_wheels/ \
  --platform manylinux2014_x86_64 \
  --python-version 3.9 \
  --implementation cp \
  --abi cp39 \
  --only-binary=:all:
```

(Esempio per server Linux x86_64 con Python 3.9 — adattare `--platform`/`--python-version`/`--abi` al server reale.)

Questo scarica anche le dipendenze transitive di `requests` (`certifi`, `charset-normalizer`, `idna`, `urllib3`).

## 2. Trasferisci sul server offline

Copia la cartella `vendor_wheels/` insieme al resto del progetto (scp, chiavetta USB, rsync, ecc.):

```bash
scp -r vendor_wheels/ requirements.txt job_monitor.py netbackup_auth.py credentials.json utente@server-nuovo:/path/to/zabbix_monitor/
```

## 3. Sul server offline: crea il venv e installa senza rete

```bash
cd /path/to/zabbix_monitor
python3 -m venv .venv
source .venv/bin/activate
pip install --no-index --find-links=vendor_wheels -r requirements.txt
```

- `--no-index` dice a pip di non contattare PyPI.
- `--find-links` gli indica dove cercare i pacchetti localmente (la cartella `vendor_wheels/`).

## 4. Esegui lo script

```bash
python3 job_monitor.py --lookback-hours 24
```

## Alternativa scartata: vendoring via sys.path/PYTHONPATH

Si potrebbe anche estrarre i wheel (sono file zip) in una cartella e aggiungerla a `sys.path`/`PYTHONPATH` senza passare da un venv. Funziona, ma è più fragile: si perde l'isolamento del venv, bisogna gestire a mano eventuali conflitti di versione con altri script Python sul server, e non c'è un modo pulito per disinstallare/aggiornare. Dato che il server ha già `pip`/`venv` funzionanti (manca solo internet, non gli strumenti), l'approccio `--find-links` sopra è preferibile.
