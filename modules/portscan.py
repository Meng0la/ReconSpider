# modules/portscan.py
import socket
import concurrent.futures
from typing import List, Tuple

from utils import logger

# Mapeamento de probes para serviços conhecidos
SERVICE_PROBES = {
    21: b'HELP\r\n',                    # FTP
    22: b'SSH-2.0\r\n',                  # SSH
    25: b'EHLO test\r\n',                 # SMTP
    80: b'HEAD / HTTP/1.0\r\n\r\n',       # HTTP
    443: b'HEAD / HTTP/1.0\r\n\r\n',      # HTTPS
    3306: b'\x00',                         # MySQL
    5432: b'\x00\x00\x00\x00',             # PostgreSQL
    8080: b'HEAD / HTTP/1.0\r\n\r\n',      # HTTP alternativo
    8443: b'HEAD / HTTP/1.0\r\n\r\n',      # HTTPS alternativo
}

def scan_port(dominio: str, porta: int, timeout: float = 1.0) -> Tuple[int, str]:
    """
    Verifica se uma porta está aberta e tenta obter banner.
    Retorna (porta, status) onde status pode ser "closed", "open (no banner)" ou banner.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        resultado = sock.connect_ex((dominio, porta))
        if resultado != 0:
            return porta, "closed"
        # Porta aberta, tenta obter banner
        banner = ""
        probe = SERVICE_PROBES.get(porta, b'')
        if probe:
            try:
                sock.send(probe)
                banner = sock.recv(100).decode().strip()
            except:
                banner = "open (no banner)"
        else:
            banner = "open"
        return porta, banner[:50]
    except Exception as e:
        logger.debug(f"Erro ao escanear porta {porta}: {e}")
        return porta, "error"
    finally:
        sock.close()

def scan_ports(dominio: str, portas: List[int], num_threads: int = 10, timeout: float = 1.0) -> List[Tuple[int, str]]:
    """
    Varre lista de portas em paralelo.
    Retorna lista de tuplas (porta, status) para portas abertas (incluindo possíveis banners).
    """
    abertas = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Mapeia cada porta para a função scan_port
        futuros = {executor.submit(scan_port, dominio, p, timeout): p for p in portas}
        for futuro in concurrent.futures.as_completed(futuros):
            porta, status = futuro.result()
            if "closed" not in status and "error" not in status:
                abertas.append((porta, status))
                logger.debug(f"Porta {porta} aberta: {status}")
    logger.info(f"Port scan: {len(abertas)} portas abertas encontradas.")
    return abertas