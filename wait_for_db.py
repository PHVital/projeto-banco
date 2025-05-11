# wait_for_db.py
import os
import time
import psycopg2
from urllib.parse import urlparse

db_url_str = os.environ.get("DATABASE_URL")
if not db_url_str:
    print(
        "DATABASE_URL não definida. Assumindo que o banco não é necessário ou é SQLite."
    )
    exit(0)

print(f"Tentando conectar ao banco de dados: {db_url_str}")
parsed_url = urlparse(db_url_str)
db_host = parsed_url.hostname
db_port = parsed_url.port or 5432  # Default PostgreSQL port
db_name = parsed_url.path[1:]  # Remove leading /
db_user = parsed_url.username
db_password = parsed_url.password

retries = 10
delay = 5  # segundos

for i in range(retries):
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            connect_timeout=3,  # Tempo para tentar conectar
        )
        conn.close()
        print("Conexão com o PostgreSQL bem-sucedida!")
        exit(0)
    except psycopg2.OperationalError as e:
        print(f"Tentativa {i+1}/{retries} falhou: {e}")
        if i < retries - 1:
            print(f"Tentando novamente em {delay} segundos...")
            time.sleep(delay)
        else:
            print("Não foi possível conectar ao banco de dados após várias tentativas.")
            exit(1)
