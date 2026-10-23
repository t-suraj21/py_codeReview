from fastapi import APIRouter
from app.api.v1.reviews import reviews_router
from app.api.v1.runner import runner_router
from app.api.v1.websocket import ws_router

api_router = APIRouter()

api_router.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(runner_router, prefix="/runner", tags=["Sandbox Runner"])
api_router.include_router(ws_router, tags=["WebSockets"])

@api_router.get("/health", tags=["Health"])
async def api_health():
    return {
        "status": "healthy",
        "engine": "FastAPI Python 3.13+",
        "features": [
            "Tree-Sitter Multi-Language AST",
            "Google Gemini 2.5 Flash Structured Engine",
            "Sandboxed Process Test Runner",
            "Realtime WebSocket Diagnostics",
            "Beanie ODM / MongoDB Persistence"
        ]
    }
