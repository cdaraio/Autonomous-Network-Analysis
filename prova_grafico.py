import networkx as nx
import matplotlib.pyplot as plt

# Creazione di un grafo per rappresentare la rete LAN
G = nx.Graph()

# Aggiunta dei dispositivi come nodi
devices = {
    "Router": (0, 0),
    "PC1": (1, 1),
    "PC2": (1, -1),
    "Switch": (2, 0),
    "Printer": (3, 1),
    "Server": (3, -1)
}

# Aggiunta dei nodi con le posizioni (opzionali, per un layout personalizzato)
for device, pos in devices.items():
    G.add_node(device, pos=pos)

# Aggiunta delle connessioni tra dispositivi
connections = [
    ("Router", "PC1"),
    ("Router", "PC2"),
    ("Router", "Switch"),
    ("Switch", "Printer"),
    ("Switch", "Server")
]

G.add_edges_from(connections)

# Disegno della rete
pos = nx.spring_layout(G)  # Layout automatico
pos.update(devices)        # Usa le posizioni specificate

plt.figure(figsize=(8, 6))
nx.draw(G, pos, with_labels=True, node_size=2000, node_color="skyblue", font_size=12, font_weight="bold")
nx.draw_networkx_edges(G, pos, edgelist=connections, width=2)
plt.title("LAN Network Diagram")

# Salva il grafico come file immagine
plt.savefig("network_diagram.png")  # Salva il grafico nella cartella del progetto
plt.close()  # Chiudi il grafico per liberare memoria
