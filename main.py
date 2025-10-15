from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Import API routes
from api.routes.api_router import api_router

# ============== ENV / SETUP ==============
load_dotenv()

# ============== APP ==============
app = FastAPI(title="LYFLYNK Demo (FastAPI + Pinata + Solana)")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Include API routes
app.include_router(api_router)

# ============== ROOT ENDPOINT ==============
@app.get("/")
def read_root():
    return {
        "message": "LYFLYNK Demo API", 
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "wallet": "/wallet/",
            "quest": "/quest/", 
            "upload": "/upload/"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)