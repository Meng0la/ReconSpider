#!/usr/bin/env python3
"""
Filtra e analisa o arquivo auditoria_resultados.csv do ReconSpider.
Uso: python filtrar_csv.py --arquivo <caminho> [opções]
"""

import argparse
import csv
import re
import sys
from collections import Counter

def ler_csv(arquivo):
    """Lê o CSV e retorna lista de dicionários (linhas)."""
    with open(arquivo, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames

def aplicar_filtros(linhas, modulo=None, tipo=None, pesquisar=None):
    """Aplica filtros por módulo, tipo e texto livre."""
    resultados = []
    for linha in linhas:
        if modulo and linha.get('modulo', '').lower() != modulo.lower():
            continue
        if tipo and linha.get('tipo', '').lower() != tipo.lower():
            continue
        if pesquisar:
            # busca case-insensitive em valor e detalhes
            valor = linha.get('valor', '')
            detalhes = linha.get('detalhes', '')
            if not (pesquisar.lower() in valor.lower() or pesquisar.lower() in detalhes.lower()):
                continue
        resultados.append(linha)
    return resultados

def extrair_urls_com_parametros(linhas):
    """Filtra linhas onde 'valor' parece uma URL contendo '?'."""
    urls = []
    for linha in linhas:
        valor = linha.get('valor', '')
        if '?' in valor and valor.startswith('http'):
            urls.append(linha)
    return urls

def obter_unicos(linhas, campo):
    """Retorna lista de valores únicos de um campo."""
    valores = [linha.get(campo, '') for linha in linhas if linha.get(campo)]
    # remove vazios e ordena
    unicos = sorted(set(valores))
    return unicos

def salvar_csv(linhas, fieldnames, arquivo_saida):
    """Salva as linhas filtradas em um novo CSV."""
    with open(arquivo_saida, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(linhas)
    print(f"[+] Resultados salvos em {arquivo_saida}")

def main():
    parser = argparse.ArgumentParser(description='Filtra resultados do ReconSpider')
    parser.add_argument('--arquivo', '-a', required=True, help='Arquivo CSV de entrada')
    parser.add_argument('--modulo', '-m', help='Filtrar por módulo (ex: js, bruteforce, sql_injection)')
    parser.add_argument('--tipo', '-t', help='Filtrar por tipo (ex: endpoint_js, path_encontrado)')
    parser.add_argument('--pesquisar', '-p', help='Texto a pesquisar nos campos valor e detalhes')
    parser.add_argument('--urls-com-parametros', action='store_true', help='Extrair apenas URLs com "?"')
    parser.add_argument('--unicos', choices=['modulo', 'tipo', 'valor', 'detalhes'], help='Listar valores únicos de um campo')
    parser.add_argument('--output', '-o', help='Salvar resultado em arquivo CSV')
    parser.add_argument('--contar', action='store_true', help='Exibir contagem de ocorrências por tipo/módulo')

    args = parser.parse_args()

    # Carrega dados
    try:
        linhas, fieldnames = ler_csv(args.arquivo)
    except FileNotFoundError:
        print(f"Erro: arquivo '{args.arquivo}' não encontrado.")
        sys.exit(1)

    print(f"[+] Total de linhas no CSV: {len(linhas)}")

    # Aplica filtros
    filtradas = linhas
    if args.modulo or args.tipo or args.pesquisar:
        filtradas = aplicar_filtros(linhas, args.modulo, args.tipo, args.pesquisar)
        print(f"[+] Após filtros: {len(filtradas)} linhas")

    # Extrai URLs com parâmetros
    if args.urls_com_parametros:
        filtradas = extrair_urls_com_parametros(filtradas)
        print(f"[+] URLs com parâmetros: {len(filtradas)}")

    # Exibe valores únicos de um campo
    if args.unicos:
        unicos = obter_unicos(filtradas, args.unicos)
        print(f"\n--- Valores únicos de '{args.unicos}' ({len(unicos)}) ---")
        for item in unicos:
            print(item)
        return

    # Exibe contagem por módulo/tipo
    if args.contar:
        contagem_modulo = Counter(l['modulo'] for l in filtradas)
        contagem_tipo = Counter(l['tipo'] for l in filtradas)
        print("\n--- Contagem por módulo ---")
        for mod, cnt in contagem_modulo.most_common():
            print(f"{mod}: {cnt}")
        print("\n--- Contagem por tipo ---")
        for tipo, cnt in contagem_tipo.most_common():
            print(f"{tipo}: {cnt}")
        return

    # Salva resultado se solicitado
    if args.output:
        salvar_csv(filtradas, fieldnames, args.output)
    else:
        # Exibe as primeiras 20 linhas como amostra
        print("\n--- Amostra das primeiras 1000 linhas filtradas ---")
        for i, linha in enumerate(filtradas[:1000]):
            print(f"{i+1}. {linha['modulo']} | {linha['tipo']} | {linha['valor'][:80]}")

if __name__ == '__main__':
    main()