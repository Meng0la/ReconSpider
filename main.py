#!/usr/bin/env python3
"""
ReconSpider - Ferramenta completa de auditoria ofensiva
Uso exclusivo em domínios próprios ou com autorização.

Desenvolvido por Meng0la
"""

import argparse
import json
import sys
import logging
import time
import os
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3

# Define o caminho absoluto para o arquivo de log (no mesmo diretório do script)
log_file = os.path.join(os.path.dirname(__file__), "reconspider.log")

# Configura o logging com file handler e stream handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Sistema de logging inicializado. Arquivo de log: %s", log_file)

# Suprime warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Importações dos módulos locais
from config import (
    USER_AGENT, DEFAULT_WORDLIST, DEFAULT_USERLIST, DEFAULT_PASSLIST,
    COMMON_ADMIN_PATHS, COMMON_PORTS, MAX_THREADS
)
from utils import normalizar_dominio, salvar_resultados
from modules import dorks, crawler, bruteforce, js_analysis, portscan, auth, sql_injection

def banner():
    """Exibe banner ASCII com crédito."""
    print(r"""
===============================================================================
Bem-vindo / Welcome / Bienvenido 

$$$$$$$\                                           $$$$$$\            $$\       $$\
$$  __$$\                                         $$  __$$\           \__|      $$ |
$$ |  $$ | $$$$$$\   $$$$$$$\  $$$$$$\  $$$$$$$\  $$ /  \__| $$$$$$\  $$\  $$$$$$$ | $$$$$$\   $$$$$$\
$$$$$$$  |$$  __$$\ $$  _____|$$  __$$\ $$  __$$\ \$$$$$$\  $$  __$$\ $$ |$$  __$$ |$$  __$$\ $$  __$$\ 
$$  __$$< $$$$$$$$ |$$ /      $$ /  $$ |$$ |  $$ | \____$$\ $$ /  $$ |$$ |$$ /  $$ |$$$$$$$$ |$$ |  \__|
$$ |  $$ |$$   ____|$$ |      $$ |  $$ |$$ |  $$ |$$\   $$ |$$ |  $$ |$$ |$$ |  $$ |$$   ____|$$ |      
$$ |  $$ |\$$$$$$$\ \$$$$$$$\ \$$$$$$  |$$ |  $$ |\$$$$$$  |$$$$$$$  |$$ |\$$$$$$$ |\$$$$$$$\ $$ |      
\__|  \__| \_______| \_______| \______/ \__|  \__| \______/ $$  ____/ \__| \_______| \_______|\__|      
                                                            $$ |                                        
                                                            $$ |                                        
                                                            \__|                                       
===============================================================================
Desenvolvido por Meng0la
    """)

def exibir_ajuda():
    """Exibe ajuda do modo interativo."""
    print("\n" + "AJUDA DO RECONSPIDER".center(60, '━'))
    print("Comandos disponíveis no menu interativo:")
    print("  • Números (1-8) → Ativam os módulos correspondentes")
    print("  • 0             → Sai do programa")
    print("  • /help ou help → Exibe esta mensagem")
    print("\nMódulos e suas funcionalidades:\n")
    print("1. Google Dorks")
    print("   - Baixa listas do repositório Proviesec e busca no Google por exposições.")
    print("2. Crawler + Sitemap")
    print("   - Mapeia URLs via sitemap.xml e crawling de links internos.")
    print("3. Brute Force de Diretórios")
    print("   - Testa caminhos comuns com wordlist (suporta extensões).")
    print("4. Análise JavaScript")
    print("   - Extrai endpoints e possíveis segredos de arquivos JS.")
    print("5. Varredura de Portas")
    print("   - Verifica portas TCP comuns e tenta obter banner.")
    print("6. Testes de Autenticação")
    print("   - Detecta páginas de login e, opcionalmente, realiza brute force.")
    print("7. SQL Injection Avançado")
    print("   - Testa parâmetros GET/POST com payloads e integra SQLMap para exploração.")
    print("8. Todos os módulos")
    print("   - Executa os módulos 1 a 7 em sequência.\n")
    print("Parâmetros configuráveis:")
    print("  • Domínio alvo")
    print("  • Máximo de resultados por consulta")
    print("  • Delay entre requisições")
    print("  • Número de threads")
    print("  • Arquivo de saída CSV")
    print("  • Modo verbose")
    print("  • Ignorar erros SSL")
    print("\nUse apenas em domínios próprios ou com autorização!")
    print("━" * 60 + "\n")

def modo_interativo():
    """Modo interativo com menu."""
    banner()
    while True:
        print("\nOpções disponíveis:")
        print("  1. Google Dorks")
        print("  2. Crawler + Sitemap")
        print("  3. Brute Force de Diretórios")
        print("  4. Análise JavaScript")
        print("  5. Varredura de Portas")
        print("  6. Testes de Autenticação")
        print("  7. SQL Injection")
        print("  8. Todos os módulos")
        print("  0. Sair")
        escolha = input("\nDigite o número da opção desejada (ou /help para ajuda): ").strip().lower()
        if escolha in ['/help', 'help']:
            exibir_ajuda()
            continue
        elif escolha == '0':
            print("Saindo...")
            sys.exit(0)
        elif escolha not in [str(i) for i in range(1,9)]:
            print("❌ Opção inválida. Digite um número de 1 a 8 ou /help.")
            continue
        else:
            break

    dominio = input("Digite o domínio alvo (ex: meusite.com.br): ").strip()
    dominio = normalizar_dominio(dominio)
    if not dominio:
        print("Domínio inválido. Saindo.")
        sys.exit(1)

    max_results = input("Número máximo de resultados por consulta (padrão 50): ").strip()
    max_results = int(max_results) if max_results.isdigit() else 50

    delay = input("Delay entre requisições em segundos (padrão 2.0): ").strip()
    delay = float(delay) if delay.replace('.','',1).isdigit() else 2.0

    threads = input("Número de threads (padrão 10): ").strip()
    threads = int(threads) if threads.isdigit() else 10

    output = input("Nome do arquivo de saída (padrão auditoria_resultados.csv): ").strip()
    output = output if output else "auditoria_resultados.csv"
    output = os.path.join(os.path.dirname(__file__), output)  # caminho absoluto

    verbose = input("Modo verbose? (s/N): ").strip().lower() == 's'
    ignore_ssl = input("Ignorar erros de certificado SSL? (s/N): ").strip().lower() == 's'

    # Opções avançadas (agressividade)
    modo_agressivo = input("Modo agressivo (reduz delay, aumenta threads)? (s/N): ").strip().lower() == 's'
    ignorar_rate_limit = input("Ignorar rate limits (pode causar bloqueios)? (s/N): ").strip().lower() == 's'

    if modo_agressivo:
        logger.info("Modo agressivo ativado.")
        delay = max(0.1, delay * 0.5)
        threads = int(threads * 1.5)
    if ignorar_rate_limit:
        logger.warning("Ignorando rate limits! Possível bloqueio.")
        delay = 0.1

    login_bruteforce = False
    sqlmap_path = 'sqlmap'
    sql_technique = 'BEUSTQ'
    sql_dbms = None
    sql_dump = False

    if escolha == '6' or escolha == '8':
        resp = input("Deseja realizar brute force de login (requer wordlists)? (s/N): ").strip().lower()
        login_bruteforce = resp == 's'
    if escolha == '7' or escolha == '8':
        sqlmap_path = input("Caminho para o SQLMap (padrão 'sqlmap'): ").strip() or 'sqlmap'
        resp = input("Técnica SQLMap (padrão BEUSTQ): ").strip().upper()
        if resp:
            sql_technique = resp
        resp = input("Banco de dados alvo (ex: mysql, mssql, oracle, postgresql) [deixe vazio para auto]: ").strip()
        if resp:
            sql_dbms = resp
        resp = input("Realizar dump de dados? (s/N) [cuidado!]: ").strip().lower()
        sql_dump = resp == 's'

    if verbose:
        logger.setLevel(logging.DEBUG)

    ativar_dorks = escolha in ['1', '8']
    ativar_crawler = escolha in ['2', '8']
    ativar_bruteforce = escolha in ['3', '8']
    ativar_js = escolha in ['4', '8']
    ativar_portscan = escolha in ['5', '8']
    ativar_auth = escolha in ['6', '8']
    ativar_sql = escolha in ['7', '8']

    # No modo interativo, usamos a wordlist padrão (poderíamos permitir entrada de arquivo, mas simplificado)
    executar_auditoria(
        dominio, max_results, delay, output,
        ativar_dorks, ativar_crawler, ativar_bruteforce,
        ativar_js, ativar_portscan, ativar_auth, ativar_sql,
        threads, ignore_ssl, login_bruteforce, sqlmap_path,
        DEFAULT_USERLIST, DEFAULT_PASSLIST,
        sql_technique=sql_technique, sql_dbms=sql_dbms, sql_dump=sql_dump,
        wordlist=DEFAULT_WORDLIST  # no modo interativo, wordlist padrão
    )

def executar_auditoria(dominio, max_results, delay, output,
                       dorks_on, crawler_on, bruteforce_on, js_on, portscan_on, auth_on, sql_on,
                       threads, ignore_ssl=False, login_bruteforce=False, sqlmap_path='sqlmap',
                       userlist=None, passlist=None,
                       sql_technique='BEUSTQ', sql_dbms=None, sql_dump=False,
                       wordlist=None):  # NOVO PARÂMETRO wordlist
    """Executa a auditoria com base nos módulos selecionados."""
    if userlist is None:
        userlist = DEFAULT_USERLIST
    if passlist is None:
        passlist = DEFAULT_PASSLIST
    if wordlist is None:
        wordlist = DEFAULT_WORDLIST  # fallback para a padrão

    logger.info(f"Iniciando auditoria para {dominio}")

    with requests.Session() as session:
        session.verify = not ignore_ssl
        retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(pool_connections=50, pool_maxsize=50, max_retries=retry)  # pool maior
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        session.headers.update({'User-Agent': USER_AGENT})

        resultados_gerais = {
            'dorks': [], 'crawler': [], 'bruteforce': [], 'js': [],
            'portscan': [], 'auth': [], 'sql_injection': []
        }

        # Módulo 1: Dorks
        if dorks_on:
            logger.info("=== Módulo: Google Dorks ===")
            dorks_list = dorks.baixar_dorks(dorks.DORK_SOURCES)
            queries = dorks.construir_queries(dominio, dorks_list)
            for i, query in enumerate(queries, 1):
                logger.info(f"[{i}/{len(queries)}] {query}")
                urls = dorks.buscar_no_google(query, max_results, delay)
                for url in urls:
                    resultados_gerais['dorks'].append({
                        'tipo': 'url_google',
                        'valor': url,
                        'detalhes': f"query: {query}"
                    })
                time.sleep(delay)

        # Módulo 2: Crawler
        if crawler_on:
            logger.info("=== Módulo: Crawler e Sitemap ===")
            urls_sitemap = crawler.obter_sitemap(dominio, session)
            for url in urls_sitemap:
                resultados_gerais['crawler'].append({
                    'tipo': 'sitemap',
                    'valor': url,
                    'detalhes': 'origin: sitemap.xml'
                })
            urls_crawl = crawler.crawl(dominio, session, max_paginas=max_results)
            for url in urls_crawl:
                resultados_gerais['crawler'].append({
                    'tipo': 'crawled',
                    'valor': url,
                    'detalhes': 'origin: internal link'
                })

        # Módulo 3: Brute Force
        if bruteforce_on:
            logger.info("=== Módulo: Brute Force de Diretórios ===")
            # Usa a wordlist recebida
            encontrados = bruteforce.brute_force_paths(dominio, session, wordlist, num_threads=threads)
            for url in encontrados:
                resultados_gerais['bruteforce'].append({
                    'tipo': 'path_encontrado',
                    'valor': url,
                    'detalhes': 'via wordlist'
                })

        # Módulo 4: JS
        if js_on:
            logger.info("=== Módulo: Análise de JavaScript ===")
            urls_js = set()
            for modulo in ['crawler', 'dorks']:
                for item in resultados_gerais.get(modulo, []):
                    url = item['valor']
                    if url.endswith('.js') or '.js?' in url:
                        urls_js.add(url)
            if not urls_js:
                logger.info("Nenhum JS encontrado. Executando crawl rápido...")
                paginas = crawler.crawl(dominio, session, max_paginas=10)
                for p in paginas:
                    try:
                        resp = session.get(p)
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        for script in soup.find_all('script', src=True):
                            js_url = urljoin(p, script['src'])
                            if dominio in js_url:
                                urls_js.add(js_url)
                    except:
                        pass
            if urls_js:
                logger.info(f"Analisando {len(urls_js)} arquivos JS...")
                js_result = js_analysis.analisar_js(dominio, session, urls_js)
                for endpoint in js_result['endpoints']:
                    resultados_gerais['js'].append({
                        'tipo': 'endpoint_js',
                        'valor': endpoint,
                        'detalhes': 'extraído de JS'
                    })
                for secret in js_result['secrets']:
                    resultados_gerais['js'].append({
                        'tipo': 'possivel_secret',
                        'valor': secret[:100],
                        'detalhes': 'encontrado em JS'
                    })

        # Módulo 5: Port Scan
        if portscan_on:
            logger.info("=== Módulo: Varredura de Portas ===")
            portas_abertas = portscan.scan_ports(dominio, COMMON_PORTS, num_threads=threads)
            for porta, banner in portas_abertas:
                resultados_gerais['portscan'].append({
                    'tipo': 'porta_aberta',
                    'valor': str(porta),
                    'detalhes': banner
                })

        # Módulo 6: Autenticação
        if auth_on:
            logger.info("=== Módulo: Testes de Autenticação ===")
            paths_teste = COMMON_ADMIN_PATHS.copy()
            for item in resultados_gerais.get('bruteforce', []):
                path = urlparse(item['valor']).path
                if path and path not in paths_teste:
                    paths_teste.append(path)

            login_pages = auth.detectar_login_urls(dominio, session, paths_teste)
            for page in login_pages:
                resultados_gerais['auth'].append({
                    'tipo': 'página_login',
                    'valor': page['url'],
                    'detalhes': f"título: {page['titulo']}, campos: {page['campos']}"
                })

                if login_bruteforce:
                    logger.info(f"Executando brute force em {page['url']}")
                    if 'username_field' in page['campos'] and 'password_field' in page['campos']:
                        credenciais = auth.brute_force_login(
                            page['url'], session,
                            page['campos']['username_field'],
                            page['campos']['password_field'],
                            userlist, passlist,
                            metodo=page.get('metodo', 'POST')
                        )
                        for cred in credenciais:
                            resultados_gerais['auth'].append({
                                'tipo': 'credencial_valida',
                                'valor': f"{cred['usuario']}:{cred['senha']}",
                                'detalhes': cred['indicador']
                            })
                    else:
                        logger.warning("Campos de login não identificados automaticamente.")

        # Módulo 7: SQL Injection
        if sql_on:
            logger.info("=== Módulo: SQL Injection Avançado ===")
            urls_coletadas = set()
            for modulo in ['crawler', 'dorks', 'bruteforce']:
                for item in resultados_gerais.get(modulo, []):
                    urls_coletadas.add(item['valor'])
            if not urls_coletadas:
                logger.warning("Nenhuma URL coletada para SQL Injection.")
            else:
                cookies = session.cookies.get_dict()
                sql_resultados = sql_injection.modulo_sql_injection(
                    dominio, session, list(urls_coletadas),
                    cookies=cookies,
                    sqlmap_path=sqlmap_path,
                    sql_technique=sql_technique,
                    sql_dbms=sql_dbms,
                    sql_dump=sql_dump
                )
                for critico in sql_resultados.get('criticos', []):
                    valor = critico.get('url', critico.get('parametro', 'N/A'))
                    detalhes = json.dumps(critico)
                    resultados_gerais['sql_injection'].append({
                        'tipo': 'sql_injection_critica',
                        'valor': valor,
                        'detalhes': detalhes
                    })
                for suspeito in sql_resultados.get('suspeitos', []):
                    resultados_gerais['sql_injection'].append({
                        'tipo': 'possivel_sql',
                        'valor': suspeito.get('parametro', 'N/A'),
                        'detalhes': f"score: {suspeito.get('score')}, payload: {suspeito.get('payload')}"
                    })
                for exp in sql_resultados.get('exploracao', []):
                    resultados_gerais['sql_injection'].append({
                        'tipo': 'exploracao_sql',
                        'valor': exp.get('parametro', 'N/A'),
                        'detalhes': f"payload: {exp.get('payload')} - resumo: {exp.get('resumo')}"
                    })
                logger.info(f"SQL Injection: {len(sql_resultados.get('criticos', []))} críticos, {len(sql_resultados.get('suspeitos', []))} suspeitos.")

        # Salva os resultados (fora de qualquer if)
        salvar_resultados(resultados_gerais, output)

    logger.info("Auditoria concluída. Verifique o arquivo CSV para detalhes.")

def main():
    if len(sys.argv) == 1:
        modo_interativo()
    else:
        parser = argparse.ArgumentParser(description='ReconSpider - Auditoria ofensiva completa')
        parser.add_argument('--dominio', required=True, help='Domínio alvo (ex: meusite.com.br)')
        parser.add_argument('--dorks', action='store_true', help='Ativar Google Dorks')
        parser.add_argument('--crawler', action='store_true', help='Ativar crawler e sitemap')
        parser.add_argument('--bruteforce', action='store_true', help='Ativar brute force de diretórios')
        parser.add_argument('--js', action='store_true', help='Ativar análise JavaScript')
        parser.add_argument('--portscan', action='store_true', help='Ativar varredura de portas')
        parser.add_argument('--auth', action='store_true', help='Ativar testes de autenticação')
        parser.add_argument('--sql', action='store_true', help='Ativar SQL Injection avançado')
        parser.add_argument('--all', action='store_true', help='Todos os módulos')
        parser.add_argument('--max', type=int, default=50, help='Máx resultados por dork (padrão 50)')
        parser.add_argument('--delay', type=float, default=2.0, help='Delay entre requisições (padrão 2s)')
        parser.add_argument('--output', default='auditoria_resultados.csv', help='Arquivo CSV de saída')
        parser.add_argument('--wordlist', nargs='+', default=DEFAULT_WORDLIST, help='Wordlist para brute force (lista inline)')
        parser.add_argument('--threads', type=int, default=MAX_THREADS, help='Número de threads')
        parser.add_argument('--verbose', action='store_true', help='Log detalhado')
        parser.add_argument('--ignore-ssl', action='store_true', help='Ignorar erros de certificado SSL')
        parser.add_argument('--login-bruteforce', action='store_true', help='Brute force de login')
        parser.add_argument('--sqlmap-path', type=str, default='sqlmap', help='Caminho do SQLMap')
        parser.add_argument('--userlist', nargs='+', default=DEFAULT_USERLIST, help='Lista de usuários')
        parser.add_argument('--passlist', nargs='+', default=DEFAULT_PASSLIST, help='Lista de senhas')
        parser.add_argument('--wordlist-file', type=str, help='Arquivo com wordlist para brute force (uma por linha)')
        parser.add_argument('--sql-technique', type=str, default='BEUSTQ',
                            help='Técnicas SQLMap: B=Boolean, E=Error, U=Union, S=Stacked, T=Time, Q=Inline (padrão: BEUSTQ)')
        parser.add_argument('--sql-dbms', type=str, default=None,
                            help='Banco de dados alvo (ex: mysql, mssql, oracle, postgresql)')
        parser.add_argument('--sql-dump', action='store_true',
                            help='Executar dump de dados (cuidado!)')
        # Parâmetros de agressividade
        parser.add_argument('--aggressive', action='store_true', help='Modo agressivo (reduz delay, aumenta threads)')
        parser.add_argument('--no-rate-limit', action='store_true', help='Ignorar rate limits (pode causar bloqueios)')
        parser.add_argument('--sql-level', type=int, default=3, help='Nível SQLMap (1-5)')
        parser.add_argument('--sql-risk', type=int, default=2, help='Risco SQLMap (1-3)')
        parser.add_argument('--sql-time-sec', type=int, default=5, help='Delay para time-based')
        parser.add_argument('--sql-threads', type=int, default=5, help='Threads do SQLMap')

        args = parser.parse_args()
        args.dominio = normalizar_dominio(args.dominio)

        # Carregar wordlist: prioridade para --wordlist-file, depois --wordlist, depois padrão
        wordlist = DEFAULT_WORDLIST
        if args.wordlist_file:
            try:
                with open(args.wordlist_file, 'r', encoding='utf-8') as f:
                    wordlist = [linha.strip() for linha in f if linha.strip()]
                logger.info(f"Wordlist carregada do arquivo {args.wordlist_file}: {len(wordlist)} entradas")
            except Exception as e:
                logger.error(f"Erro ao ler wordlist file: {e}")
                sys.exit(1)
        elif args.wordlist:
            wordlist = args.wordlist

        if args.verbose:
            logger.setLevel(logging.DEBUG)

        if args.all:
            args.dorks = args.crawler = args.bruteforce = args.js = args.portscan = args.auth = args.sql = True

        # Ajustes de agressividade
        delay = args.delay
        threads = args.threads
        if args.aggressive:
            logger.info("Modo agressivo ativado via CLI.")
            delay = max(0.1, delay * 0.5)
            threads = int(threads * 1.5)
        if args.no_rate_limit:
            logger.warning("Ignorando rate limits via CLI.")
            delay = 0.1

        executar_auditoria(
            args.dominio,
            args.max,
            delay,
            args.output,
            args.dorks,
            args.crawler,
            args.bruteforce,
            args.js,
            args.portscan,
            args.auth,
            args.sql,
            threads,
            args.ignore_ssl,
            args.login_bruteforce,
            args.sqlmap_path,
            args.userlist,
            args.passlist,
            sql_technique=args.sql_technique,
            sql_dbms=args.sql_dbms,
            sql_dump=args.sql_dump,
            wordlist=wordlist  # Agora passamos a wordlist corretamente
        )

if __name__ == '__main__':
    main()