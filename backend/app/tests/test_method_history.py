import json
import sqlite3
import pytest
from app.repositories import settings as settings_repo
from app.services.mortgage_service import MortgageService

SCHEMA = """
CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE calc_runs(id INTEGER PRIMARY KEY, kind TEXT, loan_id INTEGER, input_json TEXT, result_json TEXT, created_at TEXT);
CREATE TABLE method_history(id INTEGER PRIMARY KEY, from_method TEXT, to_method TEXT, note TEXT, created_at TEXT);
"""

def make_conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    c.execute("INSERT INTO settings(key,value) VALUES ('method','equal_payment')")
    c.commit()
    return c

def make_service(monkeypatch, conn):
    monkeypatch.setattr("app.services.mortgage_service.connect", lambda: conn)
    return MortgageService()

def test_switch_appends_history(monkeypatch):
    s = make_service(monkeypatch, make_conn())
    r = s.switch_method("equal_principal", "商贷转公积金")
    assert r["changed"] is True and r["from_method"] == "equal_payment"
    assert s.settings()["method"] == "equal_principal"
    items = s.method_history()
    assert len(items) == 1
    assert items[0]["from_method"] == "equal_payment"
    assert items[0]["to_method"] == "equal_principal"
    assert items[0]["note"] == "商贷转公积金"
    assert items[0]["created_at"]

def test_switch_same_method_no_history(monkeypatch):
    s = make_service(monkeypatch, make_conn())
    r = s.switch_method("equal_payment")
    assert r == {"method": "equal_payment", "changed": False}
    assert s.method_history() == []

def test_history_newest_first_and_limit(monkeypatch):
    s = make_service(monkeypatch, make_conn())
    s.switch_method("equal_principal")
    s.switch_method("equal_payment", "回切")
    items = s.method_history()
    assert [i["to_method"] for i in items] == ["equal_payment", "equal_principal"]
    assert items[0]["note"] == "回切" and items[1]["note"] is None
    top = s.method_history(limit=1)
    assert len(top) == 1 and top[0]["to_method"] == "equal_payment"

def test_invalid_method_rejected(monkeypatch):
    s = make_service(monkeypatch, make_conn())
    with pytest.raises(ValueError):
        s.switch_method("weekly")
    assert s.method_history() == []
    assert s.settings()["method"] == "equal_payment"

def test_switch_does_not_touch_calc_runs(monkeypatch):
    conn = make_conn()
    conn.execute("INSERT INTO calc_runs(kind,loan_id,input_json,result_json,created_at) VALUES ('schedule',1,'{}','{}','t0')")
    conn.commit()
    before = [dict(r) for r in conn.execute("SELECT * FROM calc_runs ORDER BY id").fetchall()]
    s = make_service(monkeypatch, conn)
    s.switch_method("equal_principal", "x")
    s.switch_method("equal_payment")
    after = [dict(r) for r in conn.execute("SELECT * FROM calc_runs ORDER BY id").fetchall()]
    assert after == before

def test_schedule_response_carries_method_info(monkeypatch):
    conn = make_conn()
    s = make_service(monkeypatch, conn)
    out = s.schedule(1_000_000, 3.5, 360, None, False)
    assert out["default_method"] == "equal_payment"
    assert out["last_method_switch_at"] is None
    sw = s.switch_method("equal_principal")
    out = s.schedule(1_000_000, 3.5, 360, None, True)
    assert out["default_method"] == "equal_principal"
    assert out["last_method_switch_at"] == sw["created_at"]
    stored = json.loads(conn.execute("SELECT result_json FROM calc_runs WHERE id=?", (out["run_id"],)).fetchone()["result_json"])
    assert "default_method" not in stored and "last_method_switch_at" not in stored
