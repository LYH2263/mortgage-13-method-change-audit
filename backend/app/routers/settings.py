from fastapi import APIRouter, Query
from app.schemas.settings import MethodSwitch
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.get("/settings")
def settings():
    with MortgageService() as s: return s.settings()
@router.post("/settings/method")
def switch_method(body: MethodSwitch):
    with MortgageService() as s: return s.switch_method(body.method, body.note)
@router.get("/settings/method/history")
def method_history(limit: int = Query(default=50, ge=1, le=500)):
    with MortgageService() as s: return {"items": s.method_history(limit)}
