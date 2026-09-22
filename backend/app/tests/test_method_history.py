import os, tempfile
os.environ["DATA_DIR"] = tempfile.mkdtemp()
import pytest
from app import seed
from app.db import DB_PATH
from app.services.mortgage_service import MortgageService

@pytest.fixture(autouse=True)
def fresh_db():
    if DB_PATH.exists(): DB_PATH.unlink()
    seed.init_db()
    yield

def test_switch_appends_history(fresh_db):
    with MortgageService() as s:
        r = s.set_default_method("equal_principal", "转等额本金")
        assert r["changed"] is True and r["from_method"] == "equal_payment"
        assert s.settings()["method"] == "equal_principal"
        items = s.method_history()
    assert len(items) == 1
    h = items[0]
    assert h["from_method"] == "equal_payment" and h["to_method"] == "equal_principal"
    assert h["note"] == "转等额本金" and h["created_at"]

def test_same_method_noop(fresh_db):
    with MortgageService() as s:
        r = s.set_default_method("equal_payment")
        assert r["changed"] is False
        assert s.method_history() == []

def test_history_newest_first_and_limit(fresh_db):
    with MortgageService() as s:
        s.set_default_method("equal_principal")
        s.set_default_method("equal_payment")
        s.set_default_method("equal_principal", "第三次")
        items = s.method_history()
        assert [h["to_method"] for h in items] == ["equal_principal", "equal_payment", "equal_principal"]
        top2 = s.method_history(2)
        assert len(top2) == 2 and top2[0]["note"] == "第三次"

def test_calc_runs_untouched_by_switch(fresh_db):
    with MortgageService() as s:
        before = s.history(100)
        s.set_default_method("equal_principal", "不影响试算记录")
        s.set_default_method("equal_payment")
        assert s.history(100) == before

def test_schedule_response_includes_method_info(fresh_db):
    with MortgageService() as s:
        out = s.schedule(1000000, 3.5, 360, None, False)
        assert out["default_method"] == "equal_payment"
        assert out["last_method_change_at"] is None
        s.set_default_method("equal_principal")
        out = s.schedule(1000000, 3.5, 360, None, False)
        assert out["default_method"] == "equal_principal"
        assert out["last_method_change_at"] == s.method_history(1)[0]["created_at"]

def test_invalid_method_rejected(fresh_db):
    with MortgageService() as s:
        with pytest.raises(ValueError):
            s.set_default_method("combo")
        assert s.method_history() == []
