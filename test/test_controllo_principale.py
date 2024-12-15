import unittest
from unittest import mock
from modello.scanner import ScannerRete


class TestScannerRete(unittest.TestCase):

    @mock.patch('scapy.all.get_if_addr', return_value='192.168.1.10')
    def test_get_range_ip(self, mock_get_if_addr):
        scanner = ScannerRete(logger=mock.Mock())
        ip_range = scanner.get_ip_range()
        self.assertEqual(ip_range, '192.168.1.0/24')

    @mock.patch('scapy.all.get_if_addr', side_effect=Exception("Errore di rete"))
    def test_get_range_ip_errore(self, mock_get_if_addr):
        scanner = ScannerRete(logger=mock.Mock())
        with self.assertRaises(Exception):
            scanner.get_ip_range()
        mock_get_if_addr.assert_called_once()

    @mock.patch('scapy.sendrecv.sr1')
    @mock.patch.object(ScannerRete, 'scan_dispositivi')
    @mock.patch.object(ScannerRete, 'get_ip_range', return_value='192.168.1.0/24')
    def test_scansione_singolo_dispositivo(self, mock_get_ip_range, mock_scan_dispositivi, mock_sr1):
        mock_response = mock.Mock(ttl=64, src="192.168.1.20")
        mock_sr1.return_value = mock_response
        mock_scan_dispositivi.return_value = [
            {'IP': '192.168.1.20', 'MAC': '00:11:22:33:44:55', 'Sistema Operativo': 'Windows', 'TTL': 64,
             'Tempo di Risposta': '0.1234 s', 'Servizi Attivi': {}, 'Tipologia': 'Client'}
        ]
        scanner = ScannerRete(logger=mock.Mock())
        dispositivi = scanner.scan()
        self.assertEqual(len(dispositivi), 1)
        self.assertEqual(dispositivi[0]['IP'], '192.168.1.20')

    @mock.patch('scapy.sendrecv.sr1')
    @mock.patch('scapy.arch.get_if_addr', return_value='192.168.1.10')
    @mock.patch.object(ScannerRete, 'scan_dispositivi')
    def test_scansione_dispositivi_multipli(self, mock_scan_dispositivi, mock_get_if_addr, mock_sr1):
        mock_response_1 = mock.Mock(ttl=64, src="192.168.1.20")
        mock_response_2 = mock.Mock(ttl=64, src="192.168.1.21")
        mock_sr1.side_effect = [mock_response_1, mock_response_2]
        mock_scan_dispositivi.return_value = [
            mock.Mock(ip="192.168.1.20"),
            mock.Mock(ip="192.168.1.21")
        ]
        scanner = ScannerRete(logger=mock.Mock())
        dispositivi = scanner.scan()
        self.assertEqual(len(dispositivi), 2)
        self.assertEqual(dispositivi[0].ip, '192.168.1.20')
        self.assertEqual(dispositivi[1].ip, '192.168.1.21')
        mock_scan_dispositivi.assert_called_once()

    @mock.patch('scapy.arch.get_if_addr', return_value='192.168.1.10')
    @mock.patch('scapy.sendrecv.sr1')
    @mock.patch.object(ScannerRete, 'scan_dispositivi')
    def test_nessun_dispositivo_trovato(self, mock_scan_dispositivi, mock_sr1, mock_get_if_addr):
        mock_sr1.side_effect = [None]
        mock_scan_dispositivi.return_value = []
        scanner = ScannerRete(logger=mock.Mock())
        dispositivi = scanner.scan()
        self.assertEqual(len(dispositivi), 0)

if __name__ == '__main__':
    unittest.main()
