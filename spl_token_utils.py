import json
import base64
from typing import Optional, Union
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solana.rpc.commitment import Commitment
from solders.instruction import Instruction
from solders.system_program import create_account, CreateAccountParams
from solders.transaction import VersionedTransaction
from solders.message import MessageV0
from solders.address_lookup_table_account import AddressLookupTableAccount
from spl.token.instructions import (
    transfer,
    get_associated_token_address,
    create_associated_token_account,
    TransferParams
)
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID


class SPLTokenManager:
    """Manages SPL token operations on Solana blockchain."""
    
    def __init__(self, rpc_url: str, mint_address: str, decimals: int = 6):
        self.client = Client(rpc_url)
        self.mint_address = Pubkey.from_string(mint_address)
        self.decimals = decimals
        # SPL Token Program ID
        self.token_program_id = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        # Associated Token Program ID
        self.associated_token_program_id = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
    
    def get_token_balance(self, wallet_address: str) -> int:
        """Get token balance for a wallet address."""
        try:
            wallet_pubkey = Pubkey.from_string(wallet_address)
            
            # Get the associated token account address
            ata_address = get_associated_token_address(wallet_pubkey, self.mint_address)
            
            # Get account info
            account_info = self.client.get_account_info(ata_address, commitment=Commitment("confirmed"))
            
            if not account_info.value:
                # No associated token account exists
                return 0
            
            # Parse the token account data
            account_data = account_info.value.data
            if len(account_data) < 64:
                return 0
                
            # Token account balance is stored at offset 64-72 (8 bytes, little endian)
            balance_bytes = account_data[64:72]
            balance = int.from_bytes(balance_bytes, byteorder='little')
            
            return balance
            
        except Exception as e:
            print(f"Error getting token balance: {e}")
            return 0
    
    def create_associated_token_account(self, payer: Keypair, owner: Pubkey) -> str:
        """Create an associated token account for the given owner."""
        try:
            # Get the associated token account address
            ata_address = get_associated_token_address(owner, self.mint_address)
            
            # Check if ATA already exists
            account_info = self.client.get_account_info(ata_address)
            if account_info.value:
                print(f"ATA already exists: {ata_address}")
                return str(ata_address)
            
            # Create the instruction to create the ATA
            instruction = create_associated_token_account(
                payer=payer.pubkey(),
                owner=owner,
                mint=self.mint_address
            )
            
            # Get recent blockhash
            recent_blockhash = self.client.get_latest_blockhash(commitment=Commitment("confirmed"))
            
            # Create transaction
            transaction = Transaction()
            transaction.add(instruction)
            transaction.recent_blockhash = recent_blockhash.value.blockhash
            transaction.fee_payer = payer.pubkey()
            
            # Sign and send transaction
            transaction.sign(payer)
            
            # Send transaction
            result = self.client.send_transaction(transaction, opts=TxOpts(skip_preflight=False, preflight_commitment=Commitment("confirmed")))
            
            print(f"✅ Created ATA: {ata_address}")
            print(f"📝 Transaction: {result.value}")
            
            return str(ata_address)
            
        except Exception as e:
            raise Exception(f"Failed to create ATA: {str(e)}")
    
    def transfer_tokens(self, from_keypair: Keypair, to_wallet: str, amount: int) -> str:
        """Transfer tokens from treasury to user wallet."""
        try:
            to_wallet_pubkey = Pubkey.from_string(to_wallet)
            
            # Get ATA addresses
            from_ata = get_associated_token_address(from_keypair.pubkey(), self.mint_address)
            to_ata = get_associated_token_address(to_wallet_pubkey, self.mint_address)
            
            # Check if destination ATA exists, create if not
            to_account_info = self.client.get_account_info(to_ata)
            if not to_account_info.value:
                print(f"Creating ATA for destination: {to_ata}")
                self.create_associated_token_account(from_keypair, to_wallet_pubkey)
            
            # Create transfer instruction
            transfer_params = TransferParams(
                source=from_ata,
                dest=to_ata,
                owner=from_keypair.pubkey(),
                amount=amount,
                program_id=TOKEN_PROGRAM_ID
            )
            transfer_instruction = transfer(transfer_params)
            
            # Get recent blockhash
            recent_blockhash = self.client.get_latest_blockhash(commitment=Commitment("confirmed"))
            
            # Create transaction
            transaction = Transaction()
            transaction.add(transfer_instruction)
            transaction.recent_blockhash = recent_blockhash.value.blockhash
            transaction.fee_payer = from_keypair.pubkey()
            
            # Sign and send transaction
            transaction.sign(from_keypair)
            
            # Send transaction
            result = self.client.send_transaction(transaction, opts=TxOpts(skip_preflight=False, preflight_commitment=Commitment("confirmed")))
            
            print(f"✅ Transferred {amount} tokens from {from_ata} to {to_ata}")
            print(f"📝 Transaction: {result.value}")
            
            return str(result.value)
            
        except Exception as e:
            raise Exception(f"Transfer failed: {str(e)}")
    
    def get_mint_info(self) -> dict:
        """Get mint information."""
        try:
            # Get mint account info
            mint_info = self.client.get_account_info(self.mint_address, commitment=Commitment("confirmed"))
            
            if not mint_info.value:
                raise Exception("Mint account not found")
            
            # Parse mint data (simplified - in production you'd use proper parsing)
            account_data = mint_info.value.data
            if len(account_data) < 82:  # Minimum size for mint account
                raise Exception("Invalid mint account data")
            
            # Extract supply (bytes 36-44, little endian)
            supply_bytes = account_data[36:44]
            supply = int.from_bytes(supply_bytes, byteorder='little')
            
            # Extract decimals (byte 44)
            decimals = account_data[44]
            
            # Extract mint authority (bytes 4-36)
            mint_authority_bytes = account_data[4:36]
            mint_authority = Pubkey.from_bytes(mint_authority_bytes) if any(mint_authority_bytes) else None
            
            # Extract freeze authority (bytes 68-100)
            freeze_authority_bytes = account_data[68:100]
            freeze_authority = Pubkey.from_bytes(freeze_authority_bytes) if any(freeze_authority_bytes) else None
            
            return {
                "mint_address": str(self.mint_address),
                "supply": supply,
                "decimals": decimals,
                "mint_authority": str(mint_authority) if mint_authority else None,
                "freeze_authority": str(freeze_authority) if freeze_authority else None,
            }
        except Exception as e:
            raise Exception(f"Failed to get mint info: {str(e)}")


def load_keypair_from_env(env_var: str) -> Keypair:
    """Load keypair from environment variable containing JSON array."""
    import os
    keypair_json = os.getenv(env_var)
    if not keypair_json:
        raise Exception(f"Environment variable {env_var} not set")
    
    try:
        # Parse JSON array and create keypair
        keypair_data = json.loads(keypair_json)
        if not isinstance(keypair_data, list) or len(keypair_data) != 64:
            raise Exception("Invalid keypair format")
        
        # Convert to bytes and create keypair
        keypair_bytes = bytes(keypair_data)
        return Keypair.from_bytes(keypair_bytes)
        
    except Exception as e:
        raise Exception(f"Failed to load keypair from {env_var}: {str(e)}")


def create_demo_keypair() -> tuple[Keypair, str]:
    """Create a demo keypair and return both keypair and JSON string."""
    keypair = Keypair()
    # Convert keypair to bytes array for JSON serialization
    keypair_bytes = bytes(keypair)
    keypair_json = json.dumps(list(keypair_bytes))
    return keypair, keypair_json
