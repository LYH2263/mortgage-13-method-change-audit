import sqlite3
from datetime import datetime, timezone

METHODS = ("equal_payment", "equal_principal")
DEFAULT_METHOD = "equal_payment"

def get_map(conn): return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}

def get_method(conn):
    r = conn.execute("SELECT value FROM settings WHERE key='method'").fetchone()
    return r["value"] if r else DEFAULT_METHOD

def set_method(conn, method, note=None):
    if method not in METHODS: raise ValueError("method")
    old = get_method(conn)
    if old == method: return {"changed": False, "method": method}
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("INSERT OR REPLACE INTO settings(key,value) VALUES ('method',?)", (method,))
    conn.execute("INSERT INTO method_history(from_method,to_method,note,created_at) VALUES (?,?,?,?)", (old, method, note, now))
    conn.commit()
    return {"changed": True, "method": method, "from_method": old, "created_at": now}

def list_method_history(conn, limit=50):
    return [dict(r) for r in conn.execute("SELECT * FROM method_history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]

def latest_method_change(conn):
    r = conn.execute("SELECT * FROM method_history ORDER BY id DESC LIMIT 1").fetchone()
    return dict(r) if r else None
