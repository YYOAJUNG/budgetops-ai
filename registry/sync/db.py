import os
from typing import Iterable
import psycopg2
from psycopg2.extras import execute_values
from registry.models.rule import RuleMetadata

DDL = """
CREATE TABLE IF NOT EXISTS rule_registry (
  rule_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  scope TEXT NOT NULL,
  description TEXT,
  PRIMARY KEY(rule_id, version)
);
"""


def get_conn():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        host = os.getenv("PGHOST", "localhost")
        port = os.getenv("PGPORT", "5432")
        db   = os.getenv("PGDATABASE", "budgetops")
        user = os.getenv("PGUSER", "postgres")
        pw   = os.getenv("PGPASSWORD", "postgres")
        dsn = f"host={host} port={port} dbname={db} user={user} password={pw}"
    conn = psycopg2.connect(dsn)
    with conn.cursor() as cur:
        cur.execute(DDL)
        conn.commit()
    return conn


def upsert_rules(rules: Iterable[RuleMetadata]) -> None:
    records = [(r.rule_id, r.version, r.scope, r.description) for r in rules]
    if not records:
        return
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Upsert on (rule_id, version)
            execute_values(
                cur,
                """
                INSERT INTO rule_registry(rule_id, version, scope, description)
                VALUES %s
                ON CONFLICT (rule_id, version)
                DO UPDATE SET scope = EXCLUDED.scope, description = EXCLUDED.description
                """,
                records,
            )
        conn.commit()
