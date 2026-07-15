import json
import socket
import struct

ZABBIX_SERVER = "192.168.1.100"
ZABBIX_PORT = 10051

# Struttura del pacchetto secondo il protocollo Zabbix
payload = {
    "request": "sender data",
    "data": [
        {
            "host": "NetBackup_Monitor",
            "key": "netbackup.job.payload",
            "value": json.dumps(
                {
                    "primary_server": "primary.home.lab",
                    "client_name": "primary.home.lab",
                    "status_code": 3,
                    "policy_name": "Duplica_Test",
                    "schedule_name": "5_minutes",
                }
            ),
        }
    ],
}

data_string = json.dumps(payload).encode("utf-8")
data_len = len(data_string)

# Header nativo Zabbix: 'ZBXD\x01' + lunghezza in formato 64-bit Little Endian
header = b"ZBXD\x01" + struct.pack("<Q", data_len)
packet = header + data_string

# Invio diretto via socket TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((ZABBIX_SERVER, ZABBIX_PORT))
    s.sendall(packet)
    risposta = s.recv(1024)
    print(risposta[13:].decode("utf-8"))  # Salta l'header della risposta