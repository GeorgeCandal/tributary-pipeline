import os
import json
import requests
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

load_dotenv()

# --- config ---
DB_CONFIG = {
    "host": os.environ["TRIBUTARY_DB_HOST"],
    "port": os.environ["TRIBUTARY_DB_PORT"],
    "dbname": os.environ["TRIBUTARY_DB_NAME"],
    "user": os.environ["TRIBUTARY_DB_USER"],
    "password": os.environ["TRIBUTARY_DB_PASSWORD"],
}

API_URL = "https://data.colorado.gov/resource/4ykn-tg5h.json"
PAGE_SIZE = 1000          # records per API request (Socrata's max default)
MAX_RECORDS = 3000        # cap for this run; set to None to load everything

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw_co_business_entities (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data        JSONB        NOT NULL,
    loaded_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);
"""

INSERT_SQL = "INSERT INTO raw_co_business_entities (data) VALUES %s"


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_landing_table(conn):
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)


def fetch_page(offset):
    """Fetch one page of records from the API, starting at `offset`."""
    params = {"$limit": PAGE_SIZE, "$offset": offset}
    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def insert_page(conn, records):
    """Insert a batch of JSON records into the landing table."""
    values = [(json.dumps(record),) for record in records]
    with conn.cursor() as cur:
        execute_values(cur, INSERT_SQL, values)


def load_colorado():
    with get_connection() as conn:
        create_landing_table(conn)

        offset = 0
        total_loaded = 0

        while True:
            records = fetch_page(offset)
            if not records:                      # empty page = no more data
                break

            insert_page(conn, records)
            total_loaded += len(records)
            offset += PAGE_SIZE
            print(f"Loaded {total_loaded} records...")

            if MAX_RECORDS is not None and total_loaded >= MAX_RECORDS:
                break

    print(f"Done. Total records loaded: {total_loaded}")


if __name__ == "__main__":
    load_colorado()