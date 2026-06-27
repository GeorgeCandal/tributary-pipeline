import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.environ["TRIBUTARY_DB_HOST"],
    "port": os.environ["TRIBUTARY_DB_PORT"],
    "dbname": os.environ["TRIBUTARY_DB_NAME"],
    "user": os.environ["TRIBUTARY_DB_USER"],
    "password": os.environ["TRIBUTARY_DB_PASSWORD"],
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw_co_business_entities (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data        JSONB        NOT NULL,
    loaded_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);
"""

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_landing_table():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
    print("Landing table ready: raw_co_business_entities")

if __name__ == "__main__":
    create_landing_table()