from fastapi import APIRouter
from app.models.paper_account import get_paper_account

router = APIRouter()


@router.get("")
async def list_positions():
    account = get_paper_account()
    return {"positions": account.get_positions()}
