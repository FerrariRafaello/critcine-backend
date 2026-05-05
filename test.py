from dotenv import load_dotenv
import os
import psycopg

load_dotenv("/home/rafaello/EXERCICES/Reviews/.env")
url = os.getenv("DATABASE_URL")
print("DATABASE_URL loaded:", bool(url))

with psycopg.connect(url) as conn:
    with conn.cursor() as cur:
        cur.execute("select 1;")
print("DB test:", cur.fetchone())