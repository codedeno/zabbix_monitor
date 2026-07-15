import json
import socket
import struct

ZABBIX_SERVER = "192.168.1.100"
ZABBIX_PORT = 10051
HOST_NAME_IN_ZABBIX = "NetBackup_Monitor"
ITEM_KEY = "netbackup.job.payload"

# Ipotizziamo che questi dati arrivino da un ciclo di lettura sul tuo DB SQLite
jobs_da_inviare = [
    {
        "primary_server": "primary.home.lab",
        "client_name": "client_1.home.lab",
        "status_code": 0,
        "policy_name": "Duplica_Test",
        "schedule_name": "5_minutes",
    },
    {
        "primary_server": "primary.home.lab",
        "client_name": "client_2.home.lab",
        "status_code": 1,
        "policy_name": "Duplica_Test",
        "schedule_name": "5_minutes",
    },
    {
        "primary_server": "primary.home.lab",
        "client_name": "client_3.home.lab",
        "status_code": 3,
        "policy_name": "Duplica_Test",
        "schedule_name": "5_minutes",
    },
]

# Costruiamo la lista 'data' per Zabbix popolandola con i vari JSON
zabbix_data_list = []
for job in jobs_da_inviare:
    zabbix_data_list.append(
        {
            "host": HOST_NAME_IN_ZABBIX,
            "key": ITEM_KEY,
            "value": json.dumps(job),  # Ogni singolo job è un'entità JSON indipendente
        }
    )

# Payload finale che contiene TUTTI i messaggi
payload = {"request": "sender data", "data": zabbix_data_list}

# Serializzazione e calcolo della lunghezza
data_string = json.dumps(payload).encode("utf-8")
data_len = len(data_string)

# Composizione del pacchetto secondo il protocollo Zabbix
header = b"ZBXD\x01" + struct.pack("<Q", data_len)
packet = header + data_string

# Unico invio TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((ZABBIX_SERVER, ZABBIX_PORT))
    s.sendall(packet)
    risposta = s.recv(1024)

    # La risposta ti mostrerà quanti ne ha elaborati (es: processed: 3; failed: 0)
    print("Risposta da Zabbix:", risposta[13:].decode("utf-8"))