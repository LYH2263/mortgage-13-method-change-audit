from fastapi import APIRouter
from app.schemas.settings import MethodUpdate
from app.services.mortgage_service import MortgageService
router = APIRouter()
@router.get("/settings")
def settings():
    with MortgageService() as s: return s.settings()
@router.get("/settings/method/history")
def method_history(limit: int = 50):
    with MortgageService() as s: return {"items": s.method_history(limit)}
@router.put("/settings/method")
def put_method(body: MethodUpdate):
    with MortgageService() as s: return s.set_default_method(body.method, body.note)
