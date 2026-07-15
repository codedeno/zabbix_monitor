# GEMINI.md

This file provides guidance to Gemini when working with code in this repository.

## What this repository is

The purpose of this project is to develop a standalone Python automation script that queries a specified number of Veritas NetBackup Primary (Master) Servers using the REST APIs documented in the `doc_10.4.0.1/` directory. The gathered data regarding backup success or failure per server is then transmitted directly to a Zabbix server using official Zabbix integration libraries to monitor the exact backup status of each infrastructure client.

This repository serves as both the reference platform for the NetBackup 10.4 REST API specifications and the development environment for this Zabbix monitoring tool.

There is **no build, lint, or test tooling** and no dependency manifest. The Python samples are standalone snippets, not a package. The runtime dependencies include `requests` (`pip install requests`) and the required Zabbix integration library.

## Layout

- `doc_10.4.0.1/` — 26 OpenAPI 3.0 YAML specs, one per NetBackup functional area (`config.yaml`, `storage.yaml`, `security.yaml`, `recovery.yaml`, `admin.yaml`, `catalog.yaml`, `malware.yaml`, …). These are the **source of truth** for endpoints, request/response schemas, required media-type versions, and RBAC enforcement. Several are very large (`config.yaml` ~600 KB, `storage.yaml` / `security.yaml` ~500 KB) — grep for a path or `operationId` rather than reading whole files.
- `doc_10.4.0.1/getting-started.md` — the authoritative narrative guide: authentication (JWT / API key / MFA / adaptive MFA), SSL cert validation, RBAC model, versioning rules, pagination, filtering, async patterns. Read this before writing or explaining any API interaction.
- `sample/` — nine Python snippets (`sample_login.py`, `sample_logout.py`, `sample_create_policy.py`, `sample_list_policies.py`, `sample_get_policy.py`, `sample_delete_policy.py`, `sample_create_storage_unit.py`, `sample_get_storage_units.py`, `sample_get_certificate.py`, `sample_get_slps.py`). Each is a self-contained `requests`-based function with an Italian docstring describing endpoint, HTTP method, headers/params/payload, and expected status code.
- `doc/job_guide.md` — guida (in italiano) alla lettura del JSON restituito da `GET /netbackup/admin/jobs`: semantica dei campi `status`/`state`/`jobType`/`childCount` e differenze tra workload (SQL Server, Oracle, Filesystem, VMware) ai fini della determinazione di successo/fallimento dei backup per client.

## Development Rules and Workflow

- **Automatic Commits:** Every individual task executed by the AI assistant MUST be followed immediately by a Git commit. The commit message must clearly explain exactly what changes or implementations were made during that specific task.

## Conventions that hold across the repo

- **Base URL / port:** all API calls go to `https://<primary-server>:1556/netbackup/...`. Port 1556 is the fixed NetBackup PBX port.
- **API versioning is via media type, not the URL.** Every request sets `Accept` (and `Content-Type` for bodies) to `application/vnd.netbackup+json;version=<major>.<minor>`. If both headers are present they must match. The correct version for a given endpoint is documented per-operation in the YAML specs — always take it from there, and note that a spec file's top-level `info.version` may differ from the version an individual endpoint requires.
- **Auth flow:** `POST /netbackup/login` returns a JWT in the `token` field; pass it verbatim in the `Authorization` header (no `Bearer ` prefix in these samples) on subsequent calls. `POST /netbackup/logout` invalidates it. MFA and adaptive-MFA variants are documented in `getting-started.md`.
- **Status codes vary by operation and version** (e.g. login → 201, policy create → 204, storage-unit create → 201 or 204). Check the specific operation's spec rather than assuming 200.
- **RBAC:** each endpoint's spec `description` states `Enforcement-Type` (API-Level vs Object-Level), the access-control `Namespace` (pipe-delimited, e.g. `|PROTECTION|POLICIES|`), and the `Requires Operation` (e.g. `|OPERATIONS|VIEW|`). Preserve this when explaining access requirements.
- **Pagination / filtering:** `page[offset]` & `page[limit]` (default page size 10); `filter` uses OData syntax. Query parameter names and values must be percent-encoded (`page%5Blimit%5D`, etc.); paginated responses carry a `links.next` URL to follow.

## Working notes for editing samples

- Samples deliberately use placeholder credentials (`dummy_...`, `root`, `netbackup-primary.local`) and `verify=False` for brevity. In real usage `verify` should point at the CA cert fetched from `GET /netbackup/security/cacert` (see `sample_get_certificate.py` and getting-started Step 1–3). Keep the placeholder/insecure style only if matching the existing snippet idiom; don't introduce real hosts or secrets.
- Docstrings and comments in samples are in **Italian** — match that when extending them.
- When adding a sample for a new endpoint, mirror the existing template: module docstring (Snippet / Scopo / Endpoint / Metodo HTTP / Parametri / Uso / Risposta attesa), one function, and a `if __name__ == "__main__":` driver. Source the endpoint path, media-type version, payload shape, and success status from the matching `doc_10.4.0.1/*.yaml` spec.

## Error Handling / Database Errori

- In caso di errore durante l'esecuzione di script Python, la connessione o l'interazione con le API di NetBackup, l'agente artificiale deve consultare **solo ed esclusivamente** il file errors.md nella root principale per identificare le soluzioni note e le cause tipiche degli errori riscontrati.

## Modalità di sviluppo
Gli script girano in un ambiente chiuso. Quasi impossibile utilizzare librerie esterne. Preferibile librerie base Python.
Attualmente sul server di produzione sono rispettate le sole dipendenze `./requirements.txt`.

## Sync CLAUDE.md
If this file if updated the assistant must update the `./CLAUDE.md` file with the same content.