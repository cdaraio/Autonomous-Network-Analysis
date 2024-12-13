class Traceroute:
    def __init__(self, hop, ip, hostname, tempo_ms, regione):
        self.hop = hop
        self.ip = ip
        self.hostname = hostname
        self.tempo_ms = tempo_ms
        self.regione = regione

    def __str__(self):
        return f"Hop: {self.hop}, IP: {self.ip}, Hostname: {self.hostname}, Tempo: {self.tempo_ms} ms, Regione: {self.regione}"
