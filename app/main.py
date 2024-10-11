from app.db.startup import create_database_if_not_exists
import uvicorn
from fastapi import FastAPI
from app.api import router
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    
    create_database_if_not_exists()
    
    yield
    
    # # Shutdown
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
