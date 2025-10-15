import os
from typing import Dict
from fastapi import HTTPException
from solders.pubkey import Pubkey
from spl_token_utils import SPLTokenManager, load_keypair_from_env
from solders.keypair import Keypair

class TokenService:
    def __init__(self):
        # Load configuration
        self.RPC_URL = os.getenv("RPC_URL", "https://api.devnet.solana.com")
        self.MINT_ADDRESS = os.getenv("MINT", "11111111111111111111111111111111")
        self.DECIMALS = int(os.getenv("DECIMALS", "6"))
        
        # Initialize SPL Token Manager
        self.token_manager = SPLTokenManager(self.RPC_URL, self.MINT_ADDRESS, self.DECIMALS)
        
        # Load treasury keypair
        try:
            self.treasury = load_keypair_from_env("TREASURY_SECRET_KEY")
            print(f"✅ Loaded treasury wallet: {self.treasury.pubkey()}")
        except Exception as e:
            print(f"❌ Error loading treasury keypair: {e}")
            print("   Please set TREASURY_SECRET_KEY in your .env file")
            # Generate a random keypair for demo
            self.treasury = Keypair()
            print(f"   Using demo keypair: {self.treasury.pubkey()}")
    
    def is_valid_pubkey(self, s: str) -> bool:
        """Check if string is a valid Solana public key"""
        try:
            Pubkey.from_string(s)
            return True
        except Exception:
            return False
    
    def transfer_tokens_now(self, to_wallet: str, whole_tokens: int) -> str:
        """Send SPL tokens from treasury to user ATA immediately."""
        if whole_tokens <= 0:
            raise HTTPException(400, "amount must be > 0")
        if not self.is_valid_pubkey(to_wallet):
            raise HTTPException(400, "Invalid wallet address")

        try:
            # Convert whole tokens to raw units (considering decimals)
            raw_amount = whole_tokens * (10 ** self.DECIMALS)
            
            # Use real SPL token transfer
            tx_signature = self.token_manager.transfer_tokens(
                self.treasury, 
                to_wallet, 
                raw_amount
            )
            
            print(f"✅ Transferred {whole_tokens} tokens to {to_wallet}")
            print(f"📝 Transaction: {tx_signature}")
            return tx_signature
            
        except Exception as e:
            print(f"❌ Transfer failed: {e}")
            raise HTTPException(500, f"Token transfer failed: {str(e)}")
    
    def get_token_balance(self, wallet: str):
        """Get token balance for a wallet"""
        if not self.is_valid_pubkey(wallet):
            raise HTTPException(400, "Invalid wallet address")
        
        try:
            balance = self.token_manager.get_token_balance(wallet)
            # Convert raw balance to whole tokens
            whole_tokens = balance / (10 ** self.DECIMALS)
            return {
                "wallet": wallet,
                "balance": whole_tokens,
                "raw_balance": balance,
                "decimals": self.DECIMALS
            }
        except Exception as e:
            raise HTTPException(500, f"Failed to get balance: {str(e)}")
    
    def get_treasury_info(self):
        """Get treasury wallet information"""
        try:
            treasury_balance = self.token_manager.get_token_balance(str(self.treasury.pubkey()))
            whole_tokens = treasury_balance / (10 ** self.DECIMALS)
            
            return {
                "treasury_wallet": str(self.treasury.pubkey()),
                "balance": whole_tokens,
                "raw_balance": treasury_balance,
                "decimals": self.DECIMALS,
                "mint_address": self.MINT_ADDRESS
            }
        except Exception as e:
            raise HTTPException(500, f"Failed to get treasury info: {str(e)}")

# Global instance
token_service = TokenService()

