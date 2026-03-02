# ReconSpider

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-academic--project-orange)
![Security
Research](https://img.shields.io/badge/domain-cybersecurity-informational)

------------------------------------------------------------------------

## 🇧🇷 Versão em Português

### Visão Geral

O ReconSpider é um framework modular de auditoria de segurança
desenvolvido em Python para análise controlada de superfícies web em
ambientes autorizados.

Ele integra técnicas estruturadas de:

-   OSINT controlado\
-   Crawling e enumeração de URLs\
-   Descoberta de diretórios\
-   Análise estática de JavaScript\
-   Inspeção de portas TCP\
-   Análise de superfícies de autenticação\
-   Detecção heurística de possíveis vulnerabilidades SQL Injection (com
    integração opcional ao SQLMap)

O objetivo principal do projeto é acadêmico e defensivo, permitindo a
identificação preventiva de exposições antes que possam ser exploradas.

------------------------------------------------------------------------

### Aviso Legal

Esta ferramenta deve ser utilizada exclusivamente em domínios próprios,
ambientes de laboratório ou mediante autorização formal.

O uso não autorizado pode violar legislações vigentes. Os autores não se
responsabilizam por qualquer uso indevido.

------------------------------------------------------------------------

### Instalação

#### Requisitos

-   Python 3.8 ou superior
-   pip
-   (Opcional) SQLMap instalado no sistema

#### Passos

Clonar o repositório:

    git clone https://github.com/Meng0la/ReconSpider.git
    cd reconspider

Criar ambiente virtual:

Linux / macOS:

    python -m venv venv
    source venv/bin/activate

Windows:

    python -m venv venv
    venv\Scripts\activate

Instalar dependências:

    pip install -r requirements.txt

------------------------------------------------------------------------

### Execução

Modo Interativo:

    python main.py

Modo CLI:

    python main.py --dominio exemplo.com [opções]

------------------------------------------------------------------------

### Argumentos Principais

--dominio DOMINIO\
--dorks\
--crawler\
--bruteforce\
--js\
--portscan\
--auth\
--sql\
--all

Configurações adicionais:

--max\
--delay\
--output\
--threads\
--verbose\
--ignore-ssl

------------------------------------------------------------------------

### Estrutura do Projeto

reconspider/ │ ├── main.py ├── config.py ├── utils.py ├──
requirements.txt │ ├── modules/ │ ├── dorks.py │ ├── crawler.py │ ├──
bruteforce.py │ ├── js_analysis.py │ ├── portscan.py │ ├── auth.py │ └──
sql_injection.py │ └── README.md

------------------------------------------------------------------------

## 🇺🇸 English Version

### Overview

ReconSpider is a modular security auditing framework developed in Python
for controlled web surface analysis in authorized environments.

It integrates structured techniques including:

-   Controlled OSINT discovery\
-   Website crawling and URL enumeration\
-   Directory discovery\
-   Static JavaScript analysis\
-   TCP port inspection\
-   Authentication surface analysis\
-   Heuristic SQL Injection detection (optional SQLMap integration)

The primary objective of this project is academic and defensive
cybersecurity research.

------------------------------------------------------------------------

### Legal Notice

This tool must be used exclusively on domains you own or where explicit
authorization has been granted.

Unauthorized usage may violate local or international laws. The authors
assume no responsibility for misuse.

------------------------------------------------------------------------

### Installation

#### Requirements

-   Python 3.8+
-   pip
-   (Optional) SQLMap installed and accessible via PATH

#### Setup

Clone repository:

    git clone https://github.com/Meng0la/ReconSpider.git
    cd reconspider

Create virtual environment:

Linux / macOS:

    python -m venv venv
    source venv/bin/activate

Windows:

    python -m venv venv
    venv\Scripts\activate

Install dependencies:

    pip install -r requirements.txt

------------------------------------------------------------------------

### Execution

Interactive Mode:

    python main.py

CLI Mode:

    python main.py --dominio example.com [options]

------------------------------------------------------------------------

### Output

Results are exported as CSV with the following structure:

module, type, value, details, timestamp

------------------------------------------------------------------------

### Technical Notes

-   Google-based modules may encounter HTTP 429 rate limits.
-   SQL module requires parameterized URLs.
-   SQLMap integration is optional.
-   Increase --delay in real environments to avoid blocking.

------------------------------------------------------------------------

## License

This project is distributed under the MIT License.\
You may modify and use it for academic and authorized security research
purposes.
