import scapy.all as scapy
import socket
import time

from application import Application

class ScannerRete:
    def __init__(self, logger):
        self.logger = Application.get_instance().logger

    def get_ip_range(self):
        """Funzione per ottenere l'IP di destinazione e la subnet"""
        try:
            ip = scapy.get_if_addr(scapy.conf.iface)  # Usa l'interfaccia di rete predefinita
            subnet = ip.rsplit('.', 1)[0] + '.0/24'  # La subnet predefinita sarà della forma "x.x.x.0/24"
            self.logger.info(f"Range IP ottenuto: {subnet}")
            return subnet
        except Exception as e:
            self.logger.error(f"Errore durante l'ottenimento del range IP: {e}")
            raise

    def scan(self):
        """Funzione di scansione che avvia la rilevazione dei dispositivi sulla rete"""
        try:
            ip_range = self.get_ip_range()  # Ottieni il range di IP da scansionare
            dispositivi = self.scan_dispositivi(ip_range)  # Scansiona i dispositivi nel range
            self.logger.info(f"Numero totale di dispositivi rilevati: {len(dispositivi)}")

            if not dispositivi:
                self.logger.warning("Nessun dispositivo trovato nella rete.")
            return dispositivi

        except Exception as e:
            self.logger.error(f"Errore durante la scansione della rete: {e}")
            return []

    def scan_dispositivi(self, ip_range):
        self.logger.info(f"Avvio scansione sulla rete: {ip_range}")

        dispositivi = []

        # richiesta ARP per tutti gli indirizzi IP nella subnet
        arp_request = scapy.ARP(pdst=ip_range)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast Ethernet per tutti gli indirizzi MAC
        richiesta_completa = broadcast / arp_request

        risposte = scapy.srp(richiesta_completa, timeout=10, verbose=False)[0]

        self.logger.info(f"Numero di risposte ARP ricevute: {len(risposte)}")

        for risposta in risposte:
            ip = risposta[1].psrc
            mac = risposta[1].hwsrc

            try:
                # ping ICMP per ottenere ulteriori informazioni
                start_time = time.time()  # Registra il tempo di partenza
                risposta_ping = scapy.sr1(scapy.IP(dst=ip) / scapy.ICMP(), timeout=1, verbose=False)
                if risposta_ping:
                    ttl = risposta_ping.ttl  # Time to Live dal pacchetto ICMP
                    tempo_risposta = time.time() - start_time  # Calcola il tempo di risposta
                    sistema_operativo = self.deduce_os(ttl)  # Deduzione del sistema operativo basata su TTL
                else:
                    ttl = "Sconosciuto"
                    tempo_risposta = "Non disponibile"
                    sistema_operativo = "Sconosciuto"
                # Scansiona le porte per rilevare i servizi attivi sul dispositivo
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
                dispositivo['Tipologia'] = self.classifica_dispositivo(dispositivo)
                dispositivi.append(dispositivo)
                self.logger.info(f"Dispositivo trovato: {dispositivo}")
            except Exception as e:
                self.logger.error(f"Errore durante la scansione di {ip}: {e}")
        return dispositivi

    def ping_ip(self, ip):
        """Funzione per eseguire un ping su un IP e ottenere una risposta"""
        try:
            risposta = scapy.sr1(scapy.IP(dst=ip) / scapy.ICMP(), timeout=1, verbose=False)
            return risposta
        except Exception as e:
            self.logger.error(f"Errore durante il ping dell'IP {ip}: {e}")
            return None

    def scan_ports(self, ip, port_range=[80, 443, 22, 21, 53, 51820]):
        """Scansiona le porte aperte per un dato IP e associa il servizio alla porta aperta"""
        servizi_attivi = {}
        for porta in port_range:
            self.logger.info(f"Scansione della porta {porta} su {ip}")
            try:
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
                    else:
                        self.logger.warning(f"Porta {porta} su {ip} non raggiungibile, codice di errore: {risultato}")
            except Exception as e:
                self.logger.error(f"Errore durante la scansione della porta {porta} su {ip}: {e}")
        return servizi_attivi

    def deduce_os(self, ttl):
        """Metodo per dedurre il sistema operativo in base al TTL osservato"""
        try:
            if ttl >= 128:
                return "Windows"
            elif ttl <= 64:
                return "Unix/Linux"
            else:
                return "Sconosciuto"
        except Exception as e:
            self.logger.error(f"Errore durante la deduzione del sistema operativo per TTL {ttl}: {e}")
            return "Sconosciuto"

    def classifica_dispositivo(self, dispositivo):
        mac = dispositivo.get('MAC', 'Sconosciuto')
        servizi = dispositivo.get('Servizi Attivi', {})
        ttl = dispositivo.get('TTL', 'Sconosciuto')
        mac_prefissi_domestici = [
            '00:1E:C2',  # Apple (iPhone, iPad, Mac)
            'A4:8E:34',  # Apple (iPhone, iPad, Mac)
            '78:24:AF',  # Apple (iPhone, iPad, Mac)
            '00:18:91',  # Samsung (Smartphone, Smart TV)
            'F8:8F:CA',  # Samsung (Smartphone, Smart TV)
            '00:18:99',  # Huawei (Smartphone, Tablet)
            'A0:88:69',  # Xiaomi (Smartphone)
            '5C:5D:63',  # LG (Smart TV)
            '18:FE:34',  # TP-Link (Router)
            'D0:67:E5',  # Netgear (Router)
            '00:50:56'  # VMware (Spesso associato a dispositivi virtuali)
        ]
        # Se il MAC address inizia con uno dei prefissi comuni per i router
        if mac.startswith("00:00:5E") or mac.startswith("00:50:56"):
            return "Router"
        # Se il MAC address appartiene a dispositivi domestici (smartphone, smart TV, ecc.)
        if any(mac.startswith(prefisso) for prefisso in mac_prefissi_domestici):
            return "Dispositivo Domestico"

        if (80 in servizi or 443 in servizi) and 53 in servizi:
            return "Router"

        elif any(port in servizi for port in [80, 443, 22, 21, 53, 25, 110]):
            return "Server"

        elif isinstance(ttl, int) and ttl > 64:
            # Se il dispositivo ha porte comuni di server (80 o 443), lo consideriamo un Router
            return "Router" if 80 in servizi or 443 in servizi else "Client"
        else:
            return "Client"
