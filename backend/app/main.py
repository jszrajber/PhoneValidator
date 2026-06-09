from fastapi import FastAPI
from backend.api.v1.endpoints import check
from backend.core.logging import setup_logging, logger
from contextlib import asynccontextmanager
from backend.services.numverify import close_client

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # App is working
    yield
    # Clean up the _client before closing
    await close_client()

app = FastAPI(lifespan=lifespan)

app.include_router(check.router, prefix="/api/v1", tags=["Number Check"])


@app.get("/")
def home():
    logger.info("App is running")
    return {"message": "API is running"}

