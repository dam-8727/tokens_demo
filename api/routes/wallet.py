from fastapi import APIRouter, Query, HTTPException
from api.models.wallet import WalletBody
from api.services.token_service import token_service
from api.services.points_service import points_service

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.get("/eligible")
def eligible(wallet: str = Query(..., description="User devnet public key")):
    """Get points for a wallet"""
    return {"wallet": wallet, "points": points_service.get_points(wallet)}

@router.get("/balance")
def get_balance(wallet: str = Query(..., description="User devnet public key")):
    """Get token balance for a wallet"""
    return token_service.get_token_balance(wallet)

@router.get("/treasury")
def get_treasury_info():
    """Get treasury wallet information"""
    return token_service.get_treasury_info()

@router.post("/checkin")
def checkin(body: WalletBody):
    """Check in and earn points"""
    w = body.wallet
    if not token_service.is_valid_pubkey(w):
        raise HTTPException(400, "Invalid wallet")
    
    # Toggle: check-in ko instant reward banana ho to True karo
    INSTANT_CHECKIN = False
    
    if INSTANT_CHECKIN:
        sig = token_service.transfer_tokens_now(w, 10)
        return {"ok": True, "mode": "instant", "tx": sig, "reward": 10}
    
    # batched: just accumulate
    new_points = points_service.add_points(w, 10)
    return {"ok": True, "mode": "batched", "points": new_points}

@router.post("/claim")
def claim(body: WalletBody):
    """Claim accumulated points as tokens"""
    w = body.wallet
    if not token_service.is_valid_pubkey(w):
        raise HTTPException(400, "Invalid wallet")
    
    amt = points_service.claim_points(w)
    if amt <= 0:
        raise HTTPException(400, "Nothing to claim")
    
    sig = token_service.transfer_tokens_now(w, amt)
    return {"ok": True, "tx": sig, "amount_tokens": amt}

@router.post("/reset-points")
def reset_points(body: WalletBody):
    """Reset points for a specific wallet"""
    w = body.wallet
    if not token_service.is_valid_pubkey(w):
        raise HTTPException(400, "Invalid wallet")
    
    points_service.reset_points(w)
    return {"ok": True, "message": "Points reset to 0", "wallet": w}

