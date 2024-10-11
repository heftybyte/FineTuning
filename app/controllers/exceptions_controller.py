from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse

app = FastAPI()
router = APIRouter()

class NotFoundException(Exception):
    def __init__(self, message="Not Found"):
        self.message = message

# Custom exception for 400 errors
class BadRequestException(Exception):
    def __init__(self, message="Bad Request"):
        self.message = message

class InternalServerErrorException(Exception):
    def __init__(self, message="Internal Server Error"):
        self.message = message

# Exception handlers
@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    return JSONResponse(
        status_code=404,
        content={"message": "Resource not found"}
    )

@app.exception_handler(BadRequestException)
async def bad_request_exception_handler(request: Request, exc: BadRequestException):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)}
    )

@app.exception_handler(InternalServerErrorException)
async def internal_server_error_exception_handler(request: Request, exc: InternalServerErrorException):
    return JSONResponse(
        status_code=500,
        content={"message": str(exc)}
    )

