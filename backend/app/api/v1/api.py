from fastapi import APIRouter
from .endpoints import auth, users, organizations, agents, conversations, integrations, websocket

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(agents.router, prefix="/agents", tags=["ai-agents"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["enterprise-integrations"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])