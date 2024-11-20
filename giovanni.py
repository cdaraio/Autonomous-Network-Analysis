
import nmap
import networkx as nx
import matplotlib.pyplot as plt

def detailed_scan(ip_range):
    # Inizializza lo scanner Nmap
    nm = nmap.PortScanner()

    # Esegui la scansione della rete
    nm.scan(hosts=ip_range, arguments='-sP -sV')  # -sP per ping scan, -sV per rilevare servizi

    devices = []
    for host in nm.all_hosts():
        if nm[host].state() == "up":
            device_info = {
                'ip': host,
                'mac': nm[host]['addresses'].get('mac', 'N/A'),
                'hostname': nm[host].hostname(),
                'os': nm[host].get('osmatch', [{'name': 'Unknown'}])[0]['name'],
                'open_ports': []
            }

            # Analisi delle porte aperte e dei servizi
            for proto in nm[host].all_protocols():
                ports = nm[host][proto].keys()
                for port in ports:
                    port_info = {
                        'port': port,
                        'service': nm[host][proto][port]['name'],
                        'state': nm[host][proto][port]['state']
                    }
                    device_info['open_ports'].append(port_info)

            devices.append(device_info)

    return devices

# Specifica l'intervallo di IP
ip_range = "192.168.1.0/24"  # Cambia l'intervallo in base alla tua rete
devices = detailed_scan(ip_range)

# Costruzione del grafo
G = nx.Graph()
G.add_node("Local Machine", color='red')  # Nodo centrale del dispositivo locale

# Aggiunta dei nodi e delle connessioni
for device in devices:
    # Creazione dell'etichetta del nodo con le porte aperte
    open_ports_text = "\n".join([f"{port['port']}/{port['service']} ({port['state']})" for port in device['open_ports']])
    label = f"{device['ip']}\n{device['hostname']}\nOS: {device['os']}\n{open_ports_text}"

    G.add_node(device['ip'], label=label)
    G.add_edge("Local Machine", device['ip'])

# Disegno del grafo
pos = nx.spring_layout(G)
plt.figure(figsize=(14, 10))

# Disegna il grafo con le etichette personalizzate
labels = nx.get_node_attributes(G, 'label')
nx.draw(G, pos, with_labels=True, labels=labels, node_size=2000, node_color="skyblue", font_size=8, font_weight="bold")

# Salva l'immagine
plt.savefig("detailed_network_scan_diagram_with_ports.png")
plt.close()

print("Analisi dettagliata completata e diagramma salvato come 'detailed_network_scan_diagram_with_ports.png'")


