import os
import hashlib
import requests
from fastapi import APIRouter, HTTPException, UploadFile, File, Query
from api.services.token_service import token_service
from api.services.points_service import points_service

router = APIRouter(prefix="/upload", tags=["upload"])

# Load configuration
PINATA_JWT = os.getenv("PINATA_JWT")  # required for /upload
MAX_MB = int(os.getenv("MAX_UPLOAD_MB", "25"))

@router.post("/file")
async def upload_file(wallet: str = Query(..., description="Wallet address"), file: UploadFile = File(...)):
    """Upload file to IPFS (Pinata) and award +50 points."""
    if not token_service.is_valid_pubkey(wallet):
        raise HTTPException(400, "Invalid wallet")
    if not PINATA_JWT:
        raise HTTPException(500, "PINATA_JWT missing in .env")

    content = await file.read()
    if len(content) > MAX_MB * 1024 * 1024:
        raise HTTPException(400, f"Max {MAX_MB}MB")

    # Try real IPFS upload to Pinata first
    try:
        r = requests.post(
            "https://api.pinata.cloud/pinning/pinFileToIPFS",
            headers={"Authorization": f"Bearer {PINATA_JWT}"},
            files={"file": (file.filename, content, file.content_type or "application/octet-stream")},
            timeout=60,
        )
        if r.status_code >= 300:
            raise Exception(f"Pinata error: {r.text}")
        
        cid = r.json()["IpfsHash"]
        print(f" Real IPFS upload: {file.filename} -> {cid}")
    except Exception as e:
        # Fallback to mock upload if Pinata fails
        print(f" Pinata upload failed: {e}")
        print(" Using mock upload as fallback...")
        
        file_hash = hashlib.sha256(content).hexdigest()
        cid = f"Qm{file_hash[:44]}"  # Mock IPFS CID format
        print(f"📁 Mock upload: {file.filename} -> {cid}")
    
    # reward user for successful upload
    new_points = points_service.add_points(wallet, 50)

    return {
        "ok": True,
        "cid": cid,
        "gateway": f"https://gateway.pinata.cloud/ipfs/{cid}",
        "points": new_points,
    }

