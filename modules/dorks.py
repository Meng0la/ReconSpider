# modules/dorks.py
import time
import random
import re
from collections import OrderedDict
from typing import List
from urllib.parse import quote_plus, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

from config import USER_AGENT, REQUEST_TIMEOUT, DORK_SOURCES, THIRD_PARTY_DORKS
from utils import logger

# Lista de User-Agents para rodízio (evita bloqueios)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/121.0"
]

def baixar_dorks(urls: List[str]) -> List[str]:
    """Baixa listas de dorks do repositório (mantido igual)."""
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
    """Combina domínio com dorks (mantido igual)."""
    queries_set = OrderedDict()
    for dork in dorks_lista:
        queries_set[f"site:{dominio} {dork}"] = None
    for dork_tp in THIRD_PARTY_DORKS:
        queries_set[dork_tp.format(dominio=dominio)] = None
    return list(queries_set.keys())

def buscar_no_google(query: str, max_results: int, delay: float) -> List[str]:
    """
    Executa busca no Google manualmente com requests e BeautifulSoup.
    Inclui:
    - Headers realistas com User-Agent aleatório
    - Backoff exponencial em caso de 429
    - Parsing dos resultados da página
    """
    urls = []
    tentativas = 0
    max_tentativas = 5
    backoff = delay
    start = 0
    resultados_por_pagina = 10  #Google usa 10 por página (Usar com cuidado, pois pode dar bloqueio)

    while len(urls) < max_results and tentativas < max_tentativas:
        try:
            #Escolhe User-Agent aleatório (Da para modificar os agentes)
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://www.google.com/'
            }
            
            #Parâmetros da busca
            params = {
                'q': query,
                'num': resultados_por_pagina,
                'start': start,
                'hl': 'pt-BR'
            }
            
            #Faz a requisição
            resp = requests.get(
                'https://www.google.com/search',
                headers=headers,
                params=params,
                timeout=REQUEST_TIMEOUT
            )
            
            #Trata bloqueio
            if resp.status_code == 429:
                logger.warning(f"Rate limit (429). Aguardando {backoff}s...")
                time.sleep(backoff)
                backoff *= 2
                tentativas += 1
                continue
            
            if resp.status_code != 200:
                logger.error(f"Resposta inesperada: {resp.status_code}")
                break
            
            #Parse da página
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            #Seletores comuns do Google (podem mudar, mas funcionam na maioria)
            links_encontrados = 0
            for result in soup.find_all('a', href=True):
                href = result['href']
                #Filtra links de resultados reais
                if href.startswith('/url?q='):
                    #Extrai URL real
                    url = href.split('/url?q=')[1].split('&')[0]
                    #Ignora resultados do próprio Google
                    if 'google.com' not in url and url not in urls:
                        urls.append(url)
                        links_encontrados += 1
                        if len(urls) >= max_results:
                            break
            
            #Se não encontrou links, tenta outro seletor (fallback)
            if links_encontrados == 0:
                for result in soup.find_all('div', class_='yuRUbf'):
                    a = result.find('a')
                    if a and a.get('href'):
                        url = a['href']
                        if url not in urls and 'google.com' not in url:
                            urls.append(url)
                            if len(urls) >= max_results:
                                break
            
            start += resultados_por_pagina
            time.sleep(delay)  # Delay entre páginas
            
        except Exception as e:
            logger.error(f"Erro na requisição: {e}")
            break
    
    return urls[:max_results]