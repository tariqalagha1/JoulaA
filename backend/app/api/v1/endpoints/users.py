from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_users():
    """Get users endpoint - placeholder"""
    return {"message": "Users endpoint - to be implemented"} 