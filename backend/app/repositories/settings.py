import sqlite3
from datetime import datetime, timezone

VALID_METHODS = ("equal_payment", "equal_principal")

def get_map(conn): return {r["key"]: r["value"] for r in conn.execute("SELECT * FROM settings").fetchall()}

def get_method(conn):
    row = conn.execute("SELECT value FROM settings WHERE key='method'").fetchone()
    return row["value"] if row else None

def switch_method(conn, to_method, note=None):
    """更新默认方式并追加一条履历,单次提交;履历仅追加,不提供改写/删除。"""
    frm = get_method(conn)
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("INSERT OR REPLACE INTO settings(key,value) VALUES ('method',?)", (to_method,))
    cur = conn.execute("INSERT INTO method_history(from_method,to_method,note,created_at) VALUES (?,?,?,?)",
        (frm, to_method, note, now))
    conn.commit()
    return {"from_method": frm, "to_method": to_method, "created_at": now, "history_id": int(cur.lastrowid)}

def list_method_history(conn, limit=50):
    return [dict(r) for r in conn.execute("SELECT * FROM method_history ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]

def latest_method_history(conn):
    row = conn.execute("SELECT * FROM method_history ORDER BY id DESC LIMIT 1").fetchone()
    return dict(row) if row else None
