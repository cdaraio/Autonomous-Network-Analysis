import scapy.all as scapy
import socket
import time
import logging


class ScannerRete:
    def __init__(self, logger):
        self.logger = logger  # Salviamo il logger per usarlo successivamente
        self.subnet_trovate = []  # Lista per memorizzare le subnet rilevate

    def get_ip_range(self):
        """Funzione per ottenere l'IP di destinazione e la subnet"""
        ip = scapy.get_if_addr(scapy.conf.iface)  # Usa l'interfaccia di rete predefinita
        subnet = ip.rsplit('.', 1)[0] + '.0/24'  # La subnet predefinita sarà della forma "x.x.x.0/24"
        self.logger.info(f"Range IP ottenuto: {subnet}")
        return subnet

    def ping_ip(self, ip):
        """Funzione per eseguire un ping su un IP e ottenere una risposta"""
        risposta = scapy.sr1(scapy.IP(dst=ip) / scapy.ICMP(), timeout=1, verbose=False)
        return risposta

    def scan_ports(self, ip, port_range=[80, 443, 22, 21, 51820]):
        """Scansiona le porte aperte per un dato IP e associa il servizio alla porta aperta"""
        servizi_attivi = {}
        for porta in port_range:
            self.logger.info(f"Scansione della porta {porta} su {ip}")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.2)
                risultato = sock.connect_ex((ip, porta))
                self.logger.info(f"Risultato: {risultato}")
                if risultato == 0:  # Porta aperta
                    try:
                        servizio = socket.getservbyport(porta)
                    except OSError:  # Se il servizio non è conosciuto
                        servizio = "Servizio sconosciuto"
                    servizi_attivi[porta] = servizio
                    self.logger.info(f"Porta aperta trovata: {porta} ({servizio})")
                elif risultato != 0:
                    self.logger.warning(f"Porta {porta} su {ip} non raggiungibile, codice di errore: {risultato}")
        return servizi_attivi

    def scan_dispositivi(self, ip_range):
        self.logger.info(f"Avvio scansione sulla rete: {ip_range}")
        dispositivi = []

        # Creiamo una richiesta ARP per tutti gli indirizzi IP nella subnet
        arp_request = scapy.ARP(pdst=ip_range)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast Ethernet per tutti gli indirizzi MAC
        richiesta_completa = broadcast / arp_request

        # Invia la richiesta ARP e ottieni tutte le risposte
        risposte = scapy.srp(richiesta_completa, timeout=3, verbose=False)[0]

        # Log per mostrare il numero di risposte ARP ricevute
        self.logger.info(f"Numero di risposte ARP ricevute: {len(risposte)}")

        for risposta in risposte:
            ip = risposta[1].psrc  # IP del dispositivo che ha risposto
            mac = risposta[1].hwsrc  # MAC del dispositivo che ha risposto

            # Ottenere informazioni aggiuntive (TTL, sistema operativo, tempo di risposta)
            try:
                start_time = time.time()  # Registra il tempo di partenza
                risposta_ping = scapy.sr1(scapy.IP(dst=ip) / scapy.ICMP(), timeout=1, verbose=False)
                if risposta_ping:
                    ttl = risposta_ping.ttl  # Time to Live dal pacchetto ICMP
                    tempo_risposta = time.time() - start_time  # Calcola il tempo di risposta
                    sistema_operativo = self.deduce_os(ttl)  # Metodo per dedurre il sistema operativo in base al TTL
                else:
                    ttl = "Sconosciuto"
                    tempo_risposta = "Non disponibile"
                    sistema_operativo = "Sconosciuto"

                # Eseguire la scansione delle porte per ottenere i servizi attivi
                servizi_attivi = self.scan_ports(ip)

                dispositivo = {
                    'IP': ip,
                    'MAC': mac,
                    'Sistema Operativo': sistema_operativo,
                    'TTL': ttl,
                    'Tempo di Risposta': f"{tempo_risposta:.4f} s" if isinstance(tempo_risposta,
                                                                                 float) else tempo_risposta,
                    'Servizi Attivi': servizi_attivi
                }
                dispositivi.append(dispositivo)
                self.logger.info(f"Dispositivo trovato: {dispositivo}")

                # Rileva subnet diverse
                self.detect_other_subnets(ip)

            except Exception as e:
                self.logger.error(f"Errore durante la scansione di {ip}: {e}")

        return dispositivi

    def deduce_os(self, ttl):
        """Metodo per dedurre il sistema operativo in base al TTL osservato"""
        if ttl >= 128:
            return "Sistema Windows (possibile)"
        elif ttl <= 64:
            return "Sistema Unix/Linux (possibile)"
        else:
            return "Sistema operativo sconosciuto"

    def detect_other_subnets(self, ip):
        """Funzione per rilevare altre subnet tramite un ping a un dispositivo"""
        ip_parts = ip.split(".")
        ip_subnet = ".".join(ip_parts[:3]) + ".0/24"  # Converte l'IP in formato subnet x.x.x.0/24

        if ip_subnet not in self.subnet_trovate:
            self.subnet_trovate.append(ip_subnet)
            self.logger.info(f"Nuova subnet trovata: {ip_subnet}")

    def trace_route(self, destinazione, max_hops=30, timeout=2):
        """
        Rileva il percorso per raggiungere una destinazione.

        :param destinazione: L'indirizzo IP o il dominio da tracciare.
        :param max_hops: Numero massimo di salti (TTL) da testare.
        :param timeout: Timeout per ogni salto in secondi.
        :return: Lista di router intermedi e il loro IP.
        """
        percorso = []  # Lista per memorizzare i router intermedi
        self.logger.info(f"Avvio traceroute verso {destinazione}")

        for ttl in range(1, max_hops + 1):
            pacchetto = scapy.IP(dst=destinazione, ttl=ttl) / scapy.ICMP()
            risposta = scapy.sr1(pacchetto, timeout=timeout, verbose=False)

            if risposta is None:
                self.logger.warning(f"{ttl}: Nessuna risposta (Timeout)")
                percorso.append((ttl, "Nessuna risposta"))
            elif risposta.type == 11:  # ICMP Time Exceeded (nodo intermedio)
                ip_router = risposta.src
                self.logger.info(f"{ttl}: Router intermedio trovato: {ip_router}")
                percorso.append((ttl, ip_router))
            elif risposta.type == 0:  # ICMP Echo Reply (destinazione raggiunta)
                ip_destinazione = risposta.src
                self.logger.info(f"{ttl}: Destinazione raggiunta: {ip_destinazione}")
                percorso.append((ttl, ip_destinazione))
                break
            else:
                self.logger.error(f"{ttl}: Risposta ICMP non attesa, tipo {risposta.type}")
                percorso.append((ttl, "Risposta non attesa"))

        return percorso

    def scan(self):
        ip_range = self.get_ip_range()
        dispositivi = self.scan_dispositivi(ip_range)
        self.logger.info(f"Numero totale di dispositivi rilevati: {len(dispositivi)}")
