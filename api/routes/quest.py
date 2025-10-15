from fastapi import APIRouter, Query, HTTPException
from api.models.wallet import WalletBody
from api.services.token_service import token_service
from api.services.points_service import points_service

router = APIRouter(prefix="/quest", tags=["quest"])

@router.post("/complete")
def quest_complete(body: WalletBody, quest_type: str = Query(..., description="Type of quest completed")):
    """Award points for completing different types of quests"""
    w = body.wallet
    if not token_service.is_valid_pubkey(w):
        raise HTTPException(400, "Invalid wallet")
    
    # Define point rewards for different quest types
    quest_rewards = {
        "daily": 10,
        "upload": 50,
        "social": 25,
        "referral": 100,
        "profile": 30
    }
    
    if quest_type not in quest_rewards:
        raise HTTPException(400, "Invalid quest type")
    
    reward_points = quest_rewards[quest_type]
    total_points = points_service.add_points(w, reward_points)
    
    return {
        "ok": True, 
        "quest_type": quest_type,
        "points_awarded": reward_points,
        "total_points": total_points
    }

