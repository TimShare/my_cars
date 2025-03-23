from interface.routers.secured.user import router as user_router
from fastapi import APIRouter, Depends
from interface.dependencies import JWTBearer

router = APIRouter(prefix="/secured", dependencies=[Depends(JWTBearer())])
router.include_router(user_router)
