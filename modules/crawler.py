# modules/crawler.py
import time
from urllib.parse import urljoin, urlparse, parse_qs, urlencode, urlunparse
from collections import deque
from typing import Set

import requests
from bs4 import BeautifulSoup

from config import REQUEST_TIMEOUT
from utils import logger

# ------------------------------------------------------------
# Função para extrair URLs de sitemaps
# ------------------------------------------------------------
def obter_sitemap(dominio: str, session: requests.Session) -> Set[str]:
    """
    Tenta baixar e parsear sitemap.xml e sitemap_index.xml.
    Retorna um conjunto de URLs encontradas.
    """
    urls = set()
    base_urls = [f"https://{dominio}", f"http://{dominio}"]
    sitemap_paths = ['/sitemap.xml', '/sitemap_index.xml']

    for base in base_urls:
        for path in sitemap_paths:
            sitemap_url = urljoin(base, path)
            try:
                resp = session.get(sitemap_url, timeout=REQUEST_TIMEOUT)
                if resp.status_code == 200 and 'xml' in resp.headers.get('Content-Type', ''):
                    soup = BeautifulSoup(resp.text, 'xml')
                    # Procura por <loc> em sitemap ou sitemap index
                    for loc in soup.find_all('loc'):
                        urls.add(loc.text.strip())
                    logger.info(f"Sitemap encontrado: {sitemap_url} com {len(urls)} URLs")
                    return urls  # Retorna ao encontrar o primeiro sitemap válido
            except Exception as e:
                logger.debug(f"Erro ao acessar sitemap {sitemap_url}: {e}")
                continue
    return urls

# ------------------------------------------------------------
# Função auxiliar de normalização de URL
# ------------------------------------------------------------
def normalizar_url(url: str, remover_tracking: bool = True) -> str:
    """
    Normaliza uma URL: remove fragmentos, ordena parâmetros, remove parâmetros de tracking.
    """
    parsed = urlparse(url)
    query = parse_qs(parsed.query, keep_blank_values=True)
    if remover_tracking:
        tracking_params = {'utm_source', 'utm_medium', 'utm_campaign', 'utm_term',
                           'utm_content', 'ref', 'source', 'fbclid', 'gclid'}
        query = {k: v for k, v in query.items() if k not in tracking_params}
    sorted_query = urlencode(query, doseq=True)
    # Remove barra final do path, exceto se for a raiz
    path = parsed.path.rstrip('/') if parsed.path != '/' else '/'
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        path,
        parsed.params,
        sorted_query,
        ''  # remove fragmento
    ))
    return normalized

# ------------------------------------------------------------
# Classe de crawling ofensivo com controle de profundidade e limite
# ------------------------------------------------------------
class CrawlerOfensivo:
    """
    Crawler com fila eficiente, normalização, controle de profundidade e limite de páginas.
    """
    def __init__(self, dominio: str, session: requests.Session,
                 max_paginas: int = 100, profundidade: int = 3):
        self.dominio = dominio
        self.session = session
        self.max_paginas = max_paginas
        self.profundidade = profundidade
        self.visitadas = set()      # URLs normalizadas já visitadas
        self.fila = deque()          # (url, profundidade)
        self.resultados = set()      # URLs originais (para saída)
        self.norm_cache = {}         # cache de normalização

    def _normalizar(self, url: str) -> str:
        """Normaliza com cache."""
        if url in self.norm_cache:
            return self.norm_cache[url]
        norm = normalizar_url(url)
        self.norm_cache[url] = norm
        return norm

    def crawl(self) -> Set[str]:
        """
        Executa o crawling e retorna as URLs encontradas.
        """
        base_urls = [f"https://{self.dominio}", f"http://{self.dominio}"]
        for url in base_urls:
            self.fila.append((url, 0))

        while self.fila and len(self.visitadas) < self.max_paginas:
            url, prof = self.fila.popleft()
            url_norm = self._normalizar(url)

            if url_norm in self.visitadas:
                continue

            try:
                resp = self.session.get(url, timeout=REQUEST_TIMEOUT)
                if resp.status_code != 200:
                    continue

                self.visitadas.add(url_norm)
                self.resultados.add(url)  # guarda URL original

                if prof >= self.profundidade:
                    continue

                soup = BeautifulSoup(resp.text, 'html.parser')
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    parsed = urlparse(full_url)
                    # Filtra links do mesmo domínio ou subdomínio
                    if parsed.hostname and (parsed.hostname == self.dominio or
                                            parsed.hostname.endswith('.' + self.dominio)):
                        full_norm = self._normalizar(full_url)
                        if full_norm not in self.visitadas:
                            self.fila.append((full_url, prof + 1))
            except Exception as e:
                logger.debug(f"Erro ao acessar {url}: {e}")

        logger.info(f"Crawling concluído: {len(self.resultados)} páginas encontradas.")
        return self.resultados

# ------------------------------------------------------------
# Função de conveniência (mantém compatibilidade com chamadas antigas)
# ------------------------------------------------------------
def crawl(dominio: str, session: requests.Session, max_paginas: int = 50) -> Set[str]:
    """
    Função wrapper que instancia o crawler e executa.
    """
    crawler = CrawlerOfensivo(dominio, session, max_paginas=max_paginas)
    return crawler.crawl()