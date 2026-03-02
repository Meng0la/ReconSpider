# modules/dorks.py
import time
import random
from collections import OrderedDict
from typing import List

import requests
from bs4 import BeautifulSoup

from config import USER_AGENT, REQUEST_TIMEOUT, DORK_SOURCES, THIRD_PARTY_DORKS
from utils import logger

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0"
]

def baixar_dorks(urls: List[str]) -> List[str]:
    dorks_map = OrderedDict()
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    for url in urls:
        try:
            logger.info(f"Baixando dorks de: {url}")
            r = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            for linha in r.text.splitlines():
                linha = linha.strip()
                if linha and not linha.startswith('#'):
                    dorks_map[linha] = None
        except Exception as e:
            logger.error(f"Falha ao baixar {url}: {e}")
    return list(dorks_map.keys())

def construir_queries(dominio: str, dorks_lista: List[str]) -> List[str]:
    queries_set = OrderedDict()
    for dork in dorks_lista:
        queries_set[f"site:{dominio} {dork}"] = None
    for dork_tp in THIRD_PARTY_DORKS:
        queries_set[dork_tp.format(dominio=dominio)] = None
    return list(queries_set.keys())

def buscar_no_google(query: str, max_results: int, delay: float) -> List[str]:
    urls = []
    start = 0
    tentativas = 0
    max_tentativas = 10  # aumentado para persistir mais
    backoff = delay

    while len(urls) < max_results and tentativas < max_tentativas:
        try:
            headers = {'User-Agent': random.choice(USER_AGENTS)}
            params = {
                'q': query,
                'num': 100,  # máximo permitido pelo Google
                'start': start,
                'hl': 'pt-BR'
            }
            resp = requests.get('https://www.google.com/search', headers=headers, params=params, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 429:
                logger.warning(f"Rate limit (429). Aguardando {backoff}s...")
                time.sleep(backoff)
                backoff *= 2
                tentativas += 1
                continue
            if resp.status_code != 200:
                logger.error(f"Resposta {resp.status_code}")
                break

            soup = BeautifulSoup(resp.text, 'html.parser')
            novos = 0
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/url?q='):
                    url = href.split('/url?q=')[1].split('&')[0]
                    if 'google.com' not in url and url not in urls:
                        urls.append(url)
                        novos += 1
                        if len(urls) >= max_results:
                            break
            if novos == 0:
                break  # sem resultados novos, encerra
            start += 100
            time.sleep(delay)
        except Exception as e:
            logger.error(f"Erro: {e}")
            break
    return urls[:max_results]