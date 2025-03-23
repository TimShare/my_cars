from interface.routers.secured.user import router as user_router
from interface.routers.secured.admin_car import router as admin_car_router
from interface.routers.secured.car import router as car_router
from fastapi import APIRouter, Depends
from interface.dependencies import JWTBearer

router = APIRouter(prefix="/secured", dependencies=[Depends(JWTBearer())])
router.include_router(user_router)
router.include_router(admin_car_router)
router.include_router(car_router)
