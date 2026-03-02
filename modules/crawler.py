# modules/crawler.py
from urllib.parse import urljoin, urlparse
from typing import Set

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT, USER_AGENT  # import adicionado
from utils import logger

def obter_sitemap(dominio: str, session: requests.Session) -> Set[str]:
    urls = set()
    base_urls = [f"https://{dominio}", f"http://{dominio}"]
    for base in base_urls:
        for sitemap_path in ['/sitemap.xml', '/sitemap_index.xml']:
            s_url = urljoin(base, sitemap_path)
            try:
                resp = session.get(s_url, timeout=REQUEST_TIMEOUT)
                if resp.status_code == 200 and 'xml' in resp.headers.get('Content-Type', ''):
                    soup = BeautifulSoup(resp.text, 'xml')
                    for loc in soup.find_all('loc'):
                        urls.add(loc.text.strip())
                    logger.info(f"Sitemap encontrado: {s_url} com {len(urls)} URLs")
                    return urls
            except Exception:
                continue
    return urls

def crawl(dominio: str, session: requests.Session, max_paginas: int = 999999) -> Set[str]:
    """
    Crawl sem limite de páginas (max_paginas padrão enorme).
    """
    base_urls = [f"https://{dominio}", f"http://{dominio}"]
    visitadas = set()
    fila = list(base_urls)
    encontradas = set()

    while fila:
        url = fila.pop(0)
        if url in visitadas:
            continue
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                continue
            visitadas.add(url)
            encontradas.add(url)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                parsed = urlparse(full_url)
                if parsed.hostname and (parsed.hostname == dominio or parsed.hostname.endswith('.' + dominio)):
                    if full_url not in visitadas and full_url not in fila:
                        fila.append(full_url)
            # Se ultrapassar limite, ainda continua (não paramos)
        except Exception as e:
            logger.debug(f"Erro ao acessar {url}: {e}")
    logger.info(f"Crawling concluído: {len(encontradas)} páginas encontradas.")
    return encontradas