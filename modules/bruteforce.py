import concurrent.futures
from urllib.parse import urljoin
from typing import List, Set

import requests

from config import MAX_THREADS
from utils import logger

import logging
logger = logging.getLogger(__name__)

def brute_force_paths(dominio: str, session: requests.Session, wordlist: List[str],
                      extensions: List[str] = None, num_threads: int = 50) -> Set[str]:
    """Brute force agressivo com muitas threads."""
    if extensions is None:
        extensions = ['', '.php', '.html', '.txt', '.asp', '.aspx', '.jsp', '.do', '.action']
    encontrados = set()
    base_urls = [f"https://{dominio}", f"http://{dominio}"]
    caminhos = [path + ext for path in wordlist for ext in extensions]

    def testar(caminho):
        for base in base_urls:
            url = urljoin(base, caminho)
            try:
                resp = session.get(url, timeout=3, allow_redirects=False)
                if resp.status_code in [200, 401, 403, 500]:
                    logger.debug(f"Encontrado: {url} [{resp.status_code}]")
                    return url
            except:
                pass
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futuros = {executor.submit(testar, p): p for p in caminhos}
        for futuro in concurrent.futures.as_completed(futuros):
            resultado = futuro.result()
            if resultado:
                encontrados.add(resultado)
    logger.info(f"Brute force agressivo: {len(encontrados)} caminhos encontrados.")
    return encontrados