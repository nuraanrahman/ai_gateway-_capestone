from fastapi import APIRouter, Depends
from app.core.dependencies import get_api_key_user
from app.core import store
from app.providers.registry import list_providers

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("")
async def get_providers(user: store.User = Depends(get_api_key_user)):
    return list_providers()
