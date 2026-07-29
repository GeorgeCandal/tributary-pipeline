import os
import json
import paramiko
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

FIELDS = [
    ("corp_number",                   1,    12),
    ("corp_name",                    13,   192),
    ("status",                      205,     1),
    ("filing_type",                 206,    15),
    ("address_1",                   221,    42),
    ("address_2",                   263,    42),
    ("city",                        305,    28),
    ("state",                       333,     2),
    ("zip",                         335,    10),
    ("country",                     345,     2),
    ("mail_address_1",              347,    42),
    ("mail_address_2",              389,    42),
    ("mail_city",                   431,    28),
    ("mail_state",                  459,     2),
    ("mail_zip",                    461,    10),
    ("mail_country",                471,     2),
    ("file_date",                   473,     8),
    ("fei_number",                  481,    14),
    ("more_than_six_officers",      495,     1),
    ("last_transaction_date",       496,     8),
    ("state_country",               504,     2),
    ("report_year_1",               506,     4),
    ("filler_1",                    510,     1),
    ("report_date_1",               511,     8),
    ("report_year_2",               519,     4),
    ("filler_2",                    523,     1),
    ("report_date_2",               524,     8),
    ("report_year_3",               532,     4),
    ("filler_3",                    536,     1),
    ("report_date_3",               537,     8),
    ("registered_agent_name",       545,    42),
    ("registered_agent_type",       587,     1),
    ("registered_agent_address",    588,    42),
    ("registered_agent_city",       630,    28),
    ("registered_agent_state",      658,     2),
    ("registered_agent_zip",        660,     9),
    ("officer_1_title",             669,     4),
    ("officer_1_type",              673,     1),
    ("officer_1_name",              674,    42),
    ("officer_1_address",           716,    42),
    ("officer_1_city",              758,    28),
    ("officer_1_state",             786,     2),
    ("officer_1_zip",               788,     9),
    ("officer_2_title",             797,     4),
    ("officer_2_type",              801,     1),
    ("officer_2_name",              802,    42),
    ("officer_2_address",           844,    42),
    ("officer_2_city",              886,    28),
    ("officer_2_state",             914,     2),
    ("officer_2_zip",               916,     9),
    ("officer_3_title",             925,     4),
    ("officer_3_type",              929,     1),
    ("officer_3_name",              930,    42),
    ("officer_3_address",           972,    42),
    ("officer_3_city",             1014,    28),
    ("officer_3_state",            1042,     2),
    ("officer_3_zip",              1044,     9),
    ("officer_4_title",            1053,     4),
    ("officer_4_type",             1057,     1),
    ("officer_4_name",             1058,    42),
    ("officer_4_address",          1100,    42),
    ("officer_4_city",             1142,    28),
    ("officer_4_state",            1170,     2),
    ("officer_4_zip",              1172,     9),
    ("officer_5_title",            1181,     4),
    ("officer_5_type",             1185,     1),
    ("officer_5_name",             1186,    42),
    ("officer_5_address",          1228,    42),
    ("officer_5_city",             1270,    28),
    ("officer_5_state",            1298,     2),
    ("officer_5_zip",              1300,     9),
    ("officer_6_title",            1309,     4),
    ("officer_6_type",             1313,     1),
    ("officer_6_name",             1314,    42),
    ("officer_6_address",          1356,    42),
    ("officer_6_city",             1398,    28),
    ("officer_6_state",            1426,     2),
    ("officer_6_zip",              1428,     9),
    ("filler_4",                   1437,     4),
]


CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS raw_fl_business_entities (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data        JSONB        NOT NULL,
    loaded_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);
"""

INSERT_SQL = "INSERT INTO raw_fl_business_entities (data) VALUES %s"

def connect_sftp() -> tuple[paramiko.SFTPClient, paramiko.Transport]:
    host = os.environ["SUNBIZ_HOST"]
    user = os.environ["SUNBIZ_USER"]
    password = os.environ["SUNBIZ_PASSWORD"]

    transport = paramiko.Transport((host, 22))
    transport.connect(username=user, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    return sftp, transport

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def create_landing_table(conn):
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLE_SQL)

def parse_record(line: str) -> dict:
    record = {}
    for name, start, length in FIELDS:
        record[name] = line[start-1 : start-1+length].strip()

    return record

def insert_page(conn, records):
    """Insert a batch of JSON records into the landing table."""
    values = [(json.dumps(record),) for record in records]
    with conn.cursor() as cur:
        execute_values(cur, INSERT_SQL, values)

if __name__ == "__main__":
    pass