import socket
import concurrent.futures
from typing import List, Tuple

from config import MAX_THREADS
from utils import logger

import logging
logger = logging.getLogger(__name__)

def scan_port(dominio: str, porta: int) -> Tuple[int, str]:
    """Verifica se uma porta está aberta e tenta obter banner."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    resultado = sock.connect_ex((dominio, porta))
    sock.close()
    if resultado == 0:
        try:
            s = socket.socket()
            s.settimeout(2)
            s.connect((dominio, porta))
            s.send(b'HEAD / HTTP/1.0\r\n\r\n')
            banner = s.recv(100).decode().strip()
            s.close()
            return porta, banner.split('\n')[0][:50]
        except:
            return porta, "open (no banner)"
    return porta, "closed"

def scan_ports(dominio: str, portas: List[int], num_threads: int = MAX_THREADS) -> List[Tuple[int, str]]:
    """Varre lista de portas em paralelo."""
    abertas = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futuros = {executor.submit(scan_port, dominio, p): p for p in portas}
        for futuro in concurrent.futures.as_completed(futuros):
            porta, status = futuro.result()
            if "closed" not in status:
                abertas.append((porta, status))
    logger.info(f"Port scan: {len(abertas)} portas abertas.")
    return abertas