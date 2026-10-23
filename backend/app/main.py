import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings
from app.api.v1.router import api_router
from app.api.v1.websocket import ws_router
from app.models.review import ReviewDocument

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("PyCodeReview")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MongoDB and Beanie ODM
    client = None
    try:
        logger.info(f"Connecting to MongoDB at {settings.MONGODB_URL}...")
        client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
        # Verify connection
        await client.server_info()
        await init_beanie(database=client.get_database("codereview"), document_models=[ReviewDocument])
        logger.info("Successfully initialized MongoDB & Beanie ODM.")
    except Exception as e:
        logger.warning(f"MongoDB connection skipped or unavailable ({e}). Running with in-memory review storage.")

    yield

    # Shutdown
    if client:
        client.close()
        logger.info("MongoDB client closed.")

app = FastAPI(
    title="PyCodeReview AI API",
    version="1.0.0",
    description="Enterprise Multi-Language Code Review, AST Analysis, and Sandboxed Execution Engine",
    lifespan=lifespan
)

# CORS Middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 routers
app.include_router(api_router, prefix="/api/v1")
# Also mount websocket at root for direct ws://localhost:8000/ws/realtime-analysis
app.include_router(ws_router)

@app.get("/health", tags=["Health"])
async def root_health():
    return {
        "status": "online",
        "service": "PyCodeReview AI Engine",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
