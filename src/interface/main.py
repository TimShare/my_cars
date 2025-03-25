from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from settings import get_settings
from logger import get_logger
from core.exceptions import (
    NotFoundError,
    DuplicateEntryError,
    AlreadyExistsError,
    InvalidCredentialsError,
    TokenExpiredError,
    InvalidTokenError,
    InvalidRequestError,
    PermissionDeniedError,
    UnauthorizedError,
    ValidationError,
    DatabaseError,
    CarNotAvailableError,
    InvalidVINError,
    DuplicateVINError,
    MaxPhotosLimitError,
    FileFormatError,
    FileSizeError,
    RateLimitError,
    PaymentError,
    SearchParameterError,
    InvalidDateRangeError,
    TooManyListingsError,
    InvalidPriceError,
    ExternalServiceError,
    ModelYearError,
    BrandModelMismatchError,
)
from interface.routers import router

config = get_settings()
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация настроек до запуска сервиса"""
    logger.info(app)
    yield


app = FastAPI(
    title=config.project_name,
    docs_url="/docs",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    description=config.project_description,
    version=config.project_version,
    lifespan=lifespan,
    debug=config.is_debug_mode,
)


@app.middleware("http")
async def custom_exception_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except NotFoundError as e:
        return JSONResponse(status_code=404, content={"detail": str(e)})
    except (DuplicateEntryError, AlreadyExistsError, DuplicateVINError) as e:
        return JSONResponse(status_code=409, content={"detail": str(e)})
    except (
        InvalidCredentialsError,
        TokenExpiredError,
        InvalidTokenError,
        UnauthorizedError,
    ) as e:
        return JSONResponse(status_code=401, content={"detail": str(e)})
    except PermissionDeniedError as e:
        return JSONResponse(status_code=403, content={"detail": str(e)})
    except (
        InvalidRequestError,
        InvalidVINError,
        InvalidDateRangeError,
        InvalidPriceError,
        ModelYearError,
        BrandModelMismatchError,
    ) as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})
    except ValidationError as e:
        content = {"detail": str(e.message)}
        if e.field:
            content["field"] = e.field
        if e.errors:
            content["errors"] = e.errors
        return JSONResponse(status_code=422, content=content)
    except CarNotAvailableError as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})
    except (MaxPhotosLimitError, FileFormatError, FileSizeError) as e:
        content = {"detail": str(e)}
        if hasattr(e, "max_photos"):
            content["max_photos"] = e.max_photos
        if hasattr(e, "supported_formats"):
            content["supported_formats"] = e.supported_formats
        if hasattr(e, "max_size_mb"):
            content["max_size_mb"] = e.max_size_mb
        return JSONResponse(status_code=400, content=content)
    except RateLimitError as e:
        headers = {}
        if e.retry_after:
            headers["Retry-After"] = str(e.retry_after)
        return JSONResponse(
            status_code=429, content={"detail": str(e)}, headers=headers
        )
    except PaymentError as e:
        content = {"detail": str(e)}
        if e.payment_id:
            content["payment_id"] = e.payment_id
        if e.error_code:
            content["error_code"] = e.error_code
        return JSONResponse(status_code=400, content=content)
    except SearchParameterError as e:
        content = {"detail": str(e)}
        if e.invalid_parameters:
            content["invalid_parameters"] = e.invalid_parameters
        return JSONResponse(status_code=400, content=content)
    except TooManyListingsError as e:
        content = {"detail": str(e)}
        if e.max_listings:
            content["max_listings"] = e.max_listings
        return JSONResponse(status_code=400, content=content)
    except ExternalServiceError as e:
        content = {"detail": str(e)}
        if e.service_name:
            content["service_name"] = e.service_name
        if e.status_code:
            content["external_status_code"] = e.status_code
        return JSONResponse(status_code=502, content=content)
    except DatabaseError as e:
        logger.error(f"Database error: {e.message}, Original error: {e.original_error}")
        return JSONResponse(status_code=500, content={"detail": "Ошибка базы данных"})
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return JSONResponse(
            status_code=500, content={"detail": "Internal Server Error"}
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
