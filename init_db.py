import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "loan.db"


def _connect():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def init_db():
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            income REAL NOT NULL,
            credit_score INTEGER NOT NULL,
            loan_amount REAL NOT NULL,
            collateral_value REAL DEFAULT 0,
            risk_score REAL,
            decision TEXT,
            interest_rate REAL,
            emi REAL,
            kyc_status TEXT,
            risk_json TEXT,
            explanation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute("PRAGMA table_info(applications)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    required_columns = {
        "email": "TEXT",
        "phone": "TEXT",
        "collateral_value": "REAL DEFAULT 0",
        "risk_score": "REAL",
        "interest_rate": "REAL",
        "emi": "REAL",
        "kyc_status": "TEXT",
        "risk_json": "TEXT",
        "explanation": "TEXT",
        "created_at": "TIMESTAMP",
    }

    for column_name, definition in required_columns.items():
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE applications ADD COLUMN {column_name} {definition}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database ready.")
