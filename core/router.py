from fastapi import APIRouter

from accounts.endpoints import router as account_router

router = APIRouter()

router.include_router(account_router)
