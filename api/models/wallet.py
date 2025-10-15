from pydantic import BaseModel

class WalletBody(BaseModel):
    wallet: str

