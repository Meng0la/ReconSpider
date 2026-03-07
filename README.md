# 🕷️ ReconSpider

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Security](https://img.shields.io/badge/Security-Penetration%20Testing-red)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

**ReconSpider** is a modular offensive security reconnaissance framework
written in Python.

It was designed for **authorized penetration testing, red team research,
and defensive security analysis**, helping security researchers identify
**accidental exposures, misconfigurations, and vulnerabilities** in web
applications.

> "If you're going to live with yourself until the end, it's better to
> be enchanted by what you do."\
> --- Clóvis de Barros

------------------------------------------------------------------------

# ⚠️ Legal Disclaimer

This tool must ONLY be used on systems that:

-   You own, or\
-   You have explicit written authorization to test.

Unauthorized use may violate laws and regulations.

The author assumes **no responsibility** for misuse or damages caused by
this software.

------------------------------------------------------------------------

# 🚀 Features

  -----------------------------------------------------------------------
  Module                 Description
  ---------------------- ------------------------------------------------
  Google Dorks           Searches Google for exposed files, directories,
                         and third‑party leaks.

  Crawler + Sitemap      Extracts URLs from sitemap.xml and crawls
                         internal links.

  Directory Bruteforce   Tests common directories and files using
                         wordlists.

  JavaScript Analysis    Extracts endpoints, API routes, and potential
                         secrets.

  Port Scanning          Scans common TCP ports and performs banner
                         grabbing.

  Authentication Testing Detects login pages and can perform brute‑force
                         testing.

  Advanced SQL Injection Tests parameters and integrates SQLMap for
                         exploitation.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 📦 Installation

Requirements:

-   Python 3.8+
-   pip
-   Optional: SQLMap

Clone repository:

``` bash
git clone https://github.com/Meng0la/ReconSpider.git
cd ReconSpider
```

Create virtual environment:

``` bash
python -m venv venv
```

Activate environment:

Linux / macOS

``` bash
source venv/bin/activate
```

Windows

``` bash
venv\Scripts\activate
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

# 🎮 Usage

Interactive mode:

``` bash
python main.py
```

CLI mode:

``` bash
python main.py --dominio example.com
```

------------------------------------------------------------------------

# 📋 CLI Arguments

  Argument       Description
  -------------- -------------------------------
  --dominio      Target domain
  --dorks        Enable Google dorks
  --crawler      Enable crawler
  --bruteforce   Directory brute force
  --js           JavaScript analysis
  --portscan     Port scanning
  --auth         Authentication tests
  --sql          SQL injection module
  --all          Run all modules
  --threads      Number of threads
  --delay        Delay between requests
  --output       Output CSV file
  --verbose      Verbose logging
  --ignore-ssl   Ignore SSL certificate errors

------------------------------------------------------------------------

# 📄 Output

Results are exported in CSV format.

Columns:

-   modulo
-   tipo
-   valor
-   detalhes
-   timestamp

------------------------------------------------------------------------

# ⚙️ Technical Notes

Google requests may hit rate limits.

Increase delay if needed:

``` bash
--delay 5
```

SQL injection requires parameterized URLs such as:

    https://target.com/product?id=1

------------------------------------------------------------------------

# 🤝 Contributing

Pull requests and suggestions are welcome.

Please keep code clean and documented.

------------------------------------------------------------------------

# 📄 License

MIT License

------------------------------------------------------------------------

# 👨‍💻 Author

Gabriel Mengue Barros\
Security Researcher

GitHub: https://github.com/Meng0la
