import sqlite3
from pathlib import Path
from typing import Iterable
from registry.models.rule import RuleMetadata

DB_PATH = Path('registry') / 'budgetops.db'

DDL = """
CREATE TABLE IF NOT EXISTS rule_registry (
  rule_id TEXT NOT NULL,
  version INTEGER NOT NULL,
  scope TEXT NOT NULL,
  description TEXT,
  PRIMARY KEY(rule_id, version)
);
"""


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(DDL)
    return conn


def upsert_rules(rules: Iterable[RuleMetadata]) -> None:
    with get_conn() as conn:
        for r in rules:
            # if same rule_id with lower version exists, insert new version
            conn.execute(
                "INSERT OR REPLACE INTO rule_registry(rule_id, version, scope, description) VALUES (?,?,?,?)",
                (r.rule_id, r.version, r.scope, r.description),
            )
        conn.commit()
