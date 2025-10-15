from fastapi import APIRouter
from api.routes.wallet import router as wallet_router
from api.routes.quest import router as quest_router
from api.routes.upload import router as upload_router

# Create main API router that combines all route modules
api_router = APIRouter()

# Include all route modules
api_router.include_router(wallet_router)
api_router.include_router(quest_router)
api_router.include_router(upload_router)
