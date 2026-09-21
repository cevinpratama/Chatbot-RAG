from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import AppException

async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
            },
            "path": request.url.path
        }
    )

async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code = 500,
        content={
            "succes":False,
            "error" : {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Terjadi kesalahan internal pada server. Tim kami sedang menanganinya."
            },
            "path": request.url.path
        }
    )