from app.config import DEFAULT_LINING, DEFAULT_OVERLAP
from app.db import connect

def get_all():
    c = connect()
    try:
        d = {r["key"]: r["value"] for r in c.execute("SELECT key,value FROM settings").fetchall()}
        d.setdefault("overlap", str(DEFAULT_OVERLAP))
        d.setdefault("lining_coef", str(DEFAULT_LINING))
        return d
    finally:
        c.close()

def get_overlap():
    return float(get_all().get("overlap", DEFAULT_OVERLAP))

def get_lining():
    return float(get_all().get("lining_coef", DEFAULT_LINING))

def upsert(key: str, value: str):
    c = connect()
    try:
        c.execute(
            "INSERT INTO settings(key,value) VALUES (?,?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        c.commit()
    finally:
        c.close()
