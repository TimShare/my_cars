from interface.routers.secured import router as secured_router
from interface.routers.public import router as public_router
from fastapi import APIRouter
from interface.routers.decorator import require_scopes

router = APIRouter()
router.include_router(secured_router)
router.include_router(public_router)

__all__ = ["require_scopes", "router"]
