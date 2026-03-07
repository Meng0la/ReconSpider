# modules/bruteforce.py
import concurrent.futures
import os
from urllib.parse import urljoin
from typing import List, Set, Tuple, Optional

import requests

from config import MAX_THREADS, REQUEST_TIMEOUT
from utils import logger

def brute_force_paths(dominio: str, session: requests.Session, wordlist: List[str],
                      extensions: Optional[List[str]] = None,
                      num_threads: int = MAX_THREADS) -> Set[str]:
    """
    Testa caminhos comuns com força bruta.
    Retorna um conjunto de URLs encontradas (status 200, 204, 301, 302, 401, 403).
    Status 500 são registrados em log, mas não retornados.
    """
    if extensions is None:
        extensions = ['', '.php', '.html', '.txt', '.asp', '.aspx', '.jsp', '.do', '.action', '.json', '.xml']

    base_urls = [f"https://{dominio}", f"http://{dominio}"]
    encontrados = set()
    erros_500 = []

    # Gerador de caminhos para evitar consumo excessivo de memória
    def gerar_caminhos():
        for path in wordlist:
            # Se o path já tem extensão (ex.: .env), não adicionar outras
            if '.' in path.split('/')[-1]:
                yield path
            else:
                for ext in extensions:
                    yield path + ext

    def testar(caminho: str) -> Optional[Tuple[str, int]]:
        """Testa um caminho em todas as bases. Retorna (url, status) se encontrado."""
        for base in base_urls:
            # Garantir barra inicial
            if not caminho.startswith('/'):
                caminho = '/' + caminho
            url = urljoin(base, caminho)
            try:
                resp = session.get(url, timeout=REQUEST_TIMEOUT, allow_redirects=False)
                if resp.status_code in [200, 204, 301, 302, 401, 403]:
                    logger.debug(f"Encontrado: {url} [{resp.status_code}]")
                    return (url, resp.status_code)
                elif resp.status_code == 500:
                    erros_500.append((url, resp.status_code))
            except Exception as e:
                logger.debug(f"Erro ao testar {url}: {e}")
        return None

    # Usa ThreadPoolExecutor para paralelismo
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Mapeia cada caminho para a função testar
        futuros = {executor.submit(testar, caminho): caminho for caminho in gerar_caminhos()}
        for futuro in concurrent.futures.as_completed(futuros):
            resultado = futuro.result()
            if resultado:
                url, status = resultado
                encontrados.add(url)

    # Registra os erros 500 encontrados (podem indicar endpoints interessantes)
    if erros_500:
        logger.info(f"Brute force: {len(erros_500)} respostas com status 500 (possíveis endpoints)")

    logger.info(f"Brute force concluído: {len(encontrados)} caminhos encontrados.")
    return encontrados