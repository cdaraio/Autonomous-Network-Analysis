import scapy.all as scapy
import socket
import time
import logging

from application import Application
from modello.subnet import Subnet


class ScannerRete:
    def __init__(self, logger):
        self.logger = logger  # Salviamo il logger per usarlo successivamente
        self.subnet_trovate = []  # Lista per memorizzare gli oggetti Subnet

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

            if self.subnet_trovate:
                self.logger.info(f"Subnet trovate: {self.subnet_trovate}")
            else:
                self.logger.info("Nessuna subnet aggiuntiva trovata.")

            return dispositivi  # Restituisci la lista dei dispositivi rilevati

        except Exception as e:
            self.logger.error(f"Errore durante la scansione della rete: {e}")
            return []  # In caso di errore, ritorna una lista vuota

    def scan_dispositivi(self, ip_range):
        # Log l'avvio della scansione sulla rete
        self.logger.info(f"Avvio scansione sulla rete: {ip_range}")

        # Lista per memorizzare i dispositivi trovati
        dispositivi = []

        # Creiamo una richiesta ARP per tutti gli indirizzi IP nella subnet
        arp_request = scapy.ARP(pdst=ip_range)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast Ethernet per tutti gli indirizzi MAC
        richiesta_completa = broadcast / arp_request

        # Invia la richiesta ARP e ottieni tutte le risposte
        risposte = scapy.srp(richiesta_completa, timeout=3, verbose=False)[0]

        # Log per mostrare il numero di risposte ARP ricevute
        self.logger.info(f"Numero di risposte ARP ricevute: {len(risposte)}")

        # Ciclo sulle risposte ARP per raccogliere informazioni
        for risposta in risposte:
            ip = risposta[1].psrc  # IP del dispositivo che ha risposto
            mac = risposta[1].hwsrc  # MAC del dispositivo che ha risposto

            try:
                # Esegui il ping ICMP per ottenere ulteriori informazioni
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

                # Crea un dizionario con tutte le informazioni sul dispositivo
                dispositivo = {
                    'IP': ip,
                    'MAC': mac,
                    'Sistema Operativo': sistema_operativo,
                    'TTL': ttl,
                    'Tempo di Risposta': f"{tempo_risposta:.4f} s" if isinstance(tempo_risposta,
                                                                                 float) else tempo_risposta,
                    'Servizi Attivi': servizi_attivi
                }

                # Classifica il dispositivo in base alle informazioni raccolte
                dispositivo['Tipologia'] = self.classifica_dispositivo(dispositivo)

                # Aggiungi il dispositivo alla lista
                dispositivi.append(dispositivo)

                # Log per mostrare il dispositivo trovato
                self.logger.info(f"Dispositivo trovato: {dispositivo}")

            except Exception as e:
                # Log in caso di errore durante la scansione di un dispositivo
                self.logger.error(f"Errore durante la scansione di {ip}: {e}")

        # Ritorna la lista dei dispositivi trovati
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

    def detect_other_subnets(self, ip, tipo_rete="Sconosciuto", dispositivi=None, gateway=None):
        """Funzione per rilevare altre subnet tramite un ping a un dispositivo"""
        try:
            ip_parts = ip.split(".")
            indirizzo_subnet = ".".join(ip_parts[:3]) + ".0"
            maschera = "24"

            if indirizzo_subnet not in [subnet.indirizzo for subnet in self.subnet_trovate]:
                nuova_subnet = Subnet(
                    indirizzo=indirizzo_subnet,
                    maschera=maschera,
                    tipo_rete=tipo_rete,
                    dispositivi=dispositivi,
                    gateway=gateway
                )
                self.subnet_trovate.append(nuova_subnet)
                self.logger.info(f"Nuova subnet trovata: {nuova_subnet}")
        except Exception as e:
            self.logger.error(f"Errore durante il rilevamento di altre subnet per IP {ip}: {e}")

    def classifica_dispositivo(self, dispositivo):
        """
        Metodo per determinare se un dispositivo è un client, un server, un router o un dispositivo domestico.

        :param dispositivo: Dizionario con le informazioni del dispositivo.
        :return: Stringa che indica il tipo di dispositivo.
        """
        # Estrai le informazioni dal dizionario del dispositivo
        ip = dispositivo.get('IP', 'Sconosciuto')
        mac = dispositivo.get('MAC', 'Sconosciuto')
        servizi = dispositivo.get('Servizi Attivi', {})
        ttl = dispositivo.get('TTL', 'Sconosciuto')

        # Lista di prefissi MAC per dispositivi domestici comuni
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

        # Heuristics per determinare il tipo

        # Se il MAC address inizia con uno dei prefissi comuni per i router
        if mac.startswith("00:00:5E") or mac.startswith("00:50:56"):
            return "Router"

        # Se il MAC address appartiene a dispositivi domestici (smartphone, smart TV, ecc.)
        if any(mac.startswith(prefisso) for prefisso in mac_prefissi_domestici):
            return "Dispositivo Domestico"

        # Se il dispositivo ha una delle porte 80 o 443 **e** la porta 53 aperte, consideralo un router
        if (80 in servizi or 443 in servizi) and 53 in servizi:
            return "Router"

        # Verifica la presenza di altre porte comuni per determinare se è un server
        elif any(port in servizi for port in [80, 443, 22, 21, 53, 25, 110]):
            return "Server"

        # Se il TTL è alto (es. più di 64), potrebbe essere un router o un server
        elif isinstance(ttl, int) and ttl > 64:
            # Se il dispositivo ha porte comuni di server (80 o 443), consideriamo un "Router"
            return "Router" if 80 in servizi or 443 in servizi else "Client"

        # Se nessuna delle condizioni sopra è vera, classifica come "Client"
        else:
            return "Client"
