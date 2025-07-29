from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_conversations():
    """Get conversations endpoint - placeholder"""
    return {"message": "Conversations endpoint - to be implemented"} 