# utils.py
import csv
import time
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__) 

def normalizar_dominio(dominio: str) -> str:
    """Remove protocolo e barras do domínio."""
    if dominio.startswith('http://'):
        dominio = dominio[7:]
    elif dominio.startswith('https://'):
        dominio = dominio[8:]
    dominio = dominio.rstrip('/')
    if '/' in dominio:
        dominio = dominio.split('/')[0]
    return dominio

def sanitizar_csv(texto: Any) -> str:
    """Previne CSV injection convertendo para string e escapando caracteres perigosos."""
    texto_str = str(texto) if texto is not None else ''
    if texto_str and texto_str[0] in ('=', '+', '-', '@'):
        return "'" + texto_str
    return texto_str

def salvar_resultados(resultados_gerais: Dict, arquivo: str):
    """Salva resultados em CSV."""
    with open(arquivo, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['modulo', 'tipo', 'valor', 'detalhes', 'timestamp'])
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        for modulo, itens in resultados_gerais.items():
            for item in itens:
                writer.writerow([
                    modulo,
                    item.get('tipo', ''),
                    sanitizar_csv(item.get('valor', '')),
                    sanitizar_csv(item.get('detalhes', '')),
                    timestamp
                ])
    print(f"[+] Resultados consolidados salvos em {arquivo}")