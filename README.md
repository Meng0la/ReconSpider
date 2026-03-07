RECONSPIDER
                                                     

# ReconSpider

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![RedTeam](https://img.shields.io/badge/Red%20Team-Tool-red)
![CyberSecurity](https://img.shields.io/badge/CyberSecurity-Offensive%20Security-black)
![Pentest](https://img.shields.io/badge/Pentest-Reconnaissance-green)
![Status](https://img.shields.io/badge/status-active-success)
![License](https://img.shields.io/badge/license-MIT-blue)

    [ ReconSpider ] > Framework de Reconhecimento Ofensivo
    [ Autor ]      > Meng0la
    [ Linguagem ]  > Python
    [ Propósito ]  > Red Team | Pentest | Pesquisa em Segurança

------------------------------------------------------------------------

# 🕷️ ReconSpider

**ReconSpider** é um framework de **reconhecimento ofensivo para
segurança cibernética**, escrito em Python.

A ferramenta foi projetada para:

-   Red Team
-   Pentest autorizado
-   Pesquisa em segurança ofensiva
-   Descoberta de exposições acidentais

O objetivo é **mapear superfícies de ataque** em aplicações web.

------------------------------------------------------------------------

# ⚠️ Aviso Legal

    USO EXCLUSIVO PARA TESTES AUTORIZADOS

Esta ferramenta deve ser utilizada **somente** em:

-   sistemas que você possui
-   sistemas que você tem autorização explícita para testar

Uso não autorizado pode violar leis.

O autor **não se responsabiliza por uso indevido**.

------------------------------------------------------------------------

# ⚡ Módulos do ReconSpider

  Módulo                  Função
  ----------------------- ----------------------------------------------
  Google Dorks            Busca arquivos sensíveis indexados no Google
  Crawler                 Descobre páginas internas automaticamente
  Sitemap Parser          Extrai rotas do sitemap.xml
  Directory Bruteforce    Descobre diretórios ocultos
  JavaScript Analyzer     Extrai endpoints e possíveis segredos
  Port Scanner            Varredura de portas abertas
  Login Analyzer          Detecta formulários de autenticação
  SQL Injection Scanner   Testa parâmetros GET/POST
  SQLMap Integration      Exploração profunda de banco de dados

------------------------------------------------------------------------

# 📦 Instalação

Clone o projeto:

``` bash
git clone https://github.com/Meng0la/ReconSpider.git
cd ReconSpider
```

Crie ambiente virtual:

``` bash
python -m venv venv
```

Ative o ambiente:

Linux / Mac

``` bash
source venv/bin/activate
```

Windows

``` bash
venv\Scripts\activate
```

Instale dependências:

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

# ⚙️ Uso

Modo interativo:

``` bash
python main.py
```

Modo CLI:

``` bash
python main.py --dominio alvo.com
```

------------------------------------------------------------------------

# 🔥 Exemplos de Uso

## Reconhecimento completo

``` bash
python main.py --dominio alvo.com --all
```

## Recon + JS Analysis

``` bash
python main.py --dominio alvo.com --crawler --js
```

## SQL Injection

``` bash
python main.py --dominio alvo.com --sql
```

## Bruteforce de diretórios

``` bash
python main.py --dominio alvo.com --bruteforce
```

------------------------------------------------------------------------

# 📄 Output

Resultados são exportados em CSV:

    modulo,tipo,valor,detalhes,timestamp
    crawler,url_encontrada,https://site/login,200,2026-03-07

------------------------------------------------------------------------

# 🧠 Filosofia

    Eu não posso saber tudo.
    Mas eu fuço até descobrir.

Segurança ofensiva é sobre:

-   curiosidade
-   exploração
-   engenharia reversa
-   aprendizado constante

------------------------------------------------------------------------

# 👨‍💻 Autor

Gabriel Mengue Barros\
Security Researcher

GitHub:

https://github.com/Meng0la

------------------------------------------------------------------------

# ⭐ Apoie o Projeto

Se você gostou da ferramenta:

    ⭐ dê uma estrela no repositório
    🔧 contribua com código
    🐞 reporte bugs
