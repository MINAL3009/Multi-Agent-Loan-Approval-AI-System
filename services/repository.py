import json
import sqlite3
import time
from pathlib import Path
from typing import Dict

from init_db import init_db


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "loan.db"


def _connect():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def save_application(result: Dict):
    init_db()
    application = result["application"]
    kyc = result.get("kyc", {})
    risk = result.get("risk", {})
    underwriting = result.get("underwriting", {})

    payload = (
        application["name"],
        application["email"],
        application["phone"],
        application["income"],
        application["credit_score"],
        application["loan_amount"],
        application["collateral_value"],
        risk.get("score"),
        underwriting.get("decision"),
        underwriting.get("interest_rate"),
        underwriting.get("emi"),
        kyc.get("status"),
        json.dumps(risk, default=str),
        result.get("explanation_text", ""),
    )

    last_error = None
    for attempt in range(3):
        conn = None
        try:
            conn = _connect()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO applications (
                    name, email, phone, income, credit_score, loan_amount, collateral_value,
                    risk_score, decision, interest_rate, emi, kyc_status, risk_json, explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                payload,
            )
            conn.commit()
            return
        except sqlite3.OperationalError as exc:
            last_error = exc
            if "locked" not in str(exc).lower() or attempt == 2:
                raise
            time.sleep(0.5 * (attempt + 1))
        finally:
            if conn is not None:
                conn.close()

    if last_error:
        raise last_error
