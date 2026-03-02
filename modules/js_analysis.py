import re
from typing import Set

import requests

from config import REQUEST_TIMEOUT
from utils import logger

import logging
logger = logging.getLogger(__name__)

def analisar_js(dominio: str, session: requests.Session, urls_js: Set[str]) -> dict:
    """Analisa arquivos JS em busca de endpoints e segredos."""
    resultados = {'endpoints': set(), 'secrets': set()}
    padroes_secret = re.compile(r'(?i)(api[_-]?key|secret|token|password|aws[_-]?key|AKIA[0-9A-Z]{16})')
    padrao_endpoint = re.compile(r'(["\'])(/[a-zA-Z0-9_\-/{}]+?)\1')

    for js_url in urls_js:
        try:
            resp = session.get(js_url, timeout=REQUEST_TIMEOUT)
            if resp.status_code != 200:
                continue
            texto = resp.text
            for match in padrao_endpoint.findall(texto):
                endpoint = match[1]
                if len(endpoint) > 3:
                    resultados['endpoints'].add(endpoint)
            for linha in texto.splitlines():
                if padroes_secret.search(linha):
                    resultados['secrets'].add(linha.strip())
        except Exception as e:
            logger.debug(f"Erro ao analisar JS {js_url}: {e}")
    return resultados