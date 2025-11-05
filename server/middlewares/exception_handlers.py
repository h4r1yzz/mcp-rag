from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from logger import logger

async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.exception(f"UNHANDLED EXCEPTION")
        return JSONResponse(
            status_code=500,
            content={"ERROR": str(e)},
        )