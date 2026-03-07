#!/usr/bin/env python3
"""
Processa o CSV de resultados do ReconSpider (módulo js) e gera wordlists.
Uso: python process_js_results.py <arquivo.csv> [--output wordlist.txt] [--run-reconspider]
"""

import csv
import argparse
import os
import subprocess
import sys
from collections import defaultdict
from urllib.parse import urlparse

def carregar_endpoints(csv_file):
    """Lê o CSV e retorna lista de endpoints únicos."""
    endpoints = set()
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('tipo') == 'endpoint_js':
                endpoint = row.get('valor', '').strip()
                if endpoint:
                    endpoints.add(endpoint)
    return sorted(endpoints)

def carregar_segredos(csv_file):
    """Lê o CSV e retorna lista de possíveis segredos (únicos)."""
    segredos = set()
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('tipo') == 'possivel_secret':
                secret = row.get('valor', '').strip()
                if secret and len(secret) > 10:  # ignora strings muito curtas
                    segredos.add(secret)
    return sorted(segredos)

def categorizar_endpoints(endpoints):
    """Separa endpoints por tipo (API, admin, etc.)."""
    categorias = defaultdict(list)
    for ep in endpoints:
        if ep.startswith('/api/'):
            categorias['api'].append(ep)
        elif any(admin in ep for admin in ['/admin', '/login', '/user', '/painel']):
            categorias['admin'].append(ep)
        else:
            categorias['outros'].append(ep)
    return categorias

def salvar_wordlist(lista, arquivo):
    """Salva lista em arquivo, um item por linha."""
    with open(arquivo, 'w', encoding='utf-8') as f:
        for item in lista:
            f.write(item + '\n')
    print(f"[+] Wordlist salva em {arquivo} com {len(lista)} entradas.")

def executar_reconspider(dominio, wordlist_file, outros_args=None):
    """Executa o ReconSpider com a wordlist gerada (módulo bruteforce)."""
    cmd = ['python', 'main.py', '--dominio', dominio, '--bruteforce', '--wordlist-file', wordlist_file]
    if outros_args:
        cmd.extend(outros_args)
    print(f"[*] Executando: {' '.join(cmd)}")
    subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(description='Processa resultados JS do ReconSpider')
    parser.add_argument('csv_file', help='Arquivo CSV de entrada')
    parser.add_argument('--output', '-o', default='wordlist_js.txt',
                        help='Arquivo de saída para wordlist de endpoints')
    parser.add_argument('--secrets-output', '-s', default='secrets.txt',
                        help='Arquivo de saída para possíveis segredos')
    parser.add_argument('--run-reconspider', action='store_true',
                        help='Executa ReconSpider com a wordlist gerada')
    parser.add_argument('--dominio', help='Domínio alvo (obrigatório se --run-reconspider)')
    parser.add_argument('--extra-args', nargs=argparse.REMAINDER,
                        help='Argumentos extras para o ReconSpider (ex: --delay 1 --verbose)')
    args = parser.parse_args()

    if not os.path.exists(args.csv_file):
        print(f"Erro: Arquivo {args.csv_file} não encontrado.")
        sys.exit(1)

    # Carrega dados
    endpoints = carregar_endpoints(args.csv_file)
    segredos = carregar_segredos(args.csv_file)

    print(f"[+] Total de endpoints únicos: {len(endpoints)}")
    print(f"[+] Total de possíveis segredos: {len(segredos)}")

    # Categoriza endpoints
    categorias = categorizar_endpoints(endpoints)
    for cat, lista in categorias.items():
        print(f"    - {cat}: {len(lista)}")

    # Salva wordlist principal
    salvar_wordlist(endpoints, args.output)

    # Salva segredos (opcional)
    if segredos:
        salvar_wordlist(segredos, args.secrets_output)

    # Se solicitado, executa ReconSpider
    if args.run_reconspider:
        if not args.dominio:
            print("Erro: --dominio é obrigatório com --run-reconspider")
            sys.exit(1)
        # Verifica se o arquivo principal existe
        if not os.path.exists('main.py'):
            print("Erro: main.py não encontrado no diretório atual. Execute o script na raiz do ReconSpider.")
            sys.exit(1)
        executar_reconspider(args.dominio, args.output, args.extra_args)

if __name__ == '__main__':
    main()