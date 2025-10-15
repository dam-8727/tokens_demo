# SPL Token Backend Demo

A FastAPI backend for SPL token rewards system with real Solana blockchain integration.

## Features

- ✅ Real SPL token transfers using Solana blockchain
- ✅ Token balance checking
- ✅ Treasury management
- ✅ Points-based reward system
- ✅ File upload to IPFS (Pinata)
- ✅ RESTful API endpoints

## Prerequisites

1. **Solana CLI tools installed** (for token minting)
2. **Python 3.8+**
3. **Pinata account** (optional, for file uploads)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Mint Your SPL Token

First, create and mint your SPL token using Solana CLI:

```bash
# Create a new keypair for your mint authority
solana-keygen new --outfile mint-authority.json

# Create the token mint
spl-token create-token mint-authority.json

# Create a token account for the mint authority
spl-token create-account <MINT_ADDRESS> mint-authority.json

# Mint initial supply (e.g., 1,000,000 tokens)
spl-token mint <MINT_ADDRESS> 1000000 mint-authority.json
```

### 3. Configure Environment

Copy the `.env` file and update it with your values:

```bash
cp .env .env.local
```

Update `.env.local` with:
- `MINT`: Your mint address from step 2
- `TREASURY_SECRET_KEY`: Your mint authority keypair as JSON array
- `PINATA_JWT`: Your Pinata JWT (optional)

### 4. Test Your Setup

Run the demo script to verify everything works:

```bash
python demo_mint.py
```

### 5. Start the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Token Management

- `GET /balance?wallet=<WALLET>` - Get token balance for a wallet
- `GET /treasury` - Get treasury wallet information

### Rewards System

- `GET /eligible?wallet=<WALLET>` - Check user's points
- `POST /checkin` - Check in and earn points
- `POST /claim` - Claim accumulated points as tokens
- `POST /upload` - Upload file to IPFS and earn points

### Example Usage

```bash
# Check balance
curl "http://localhost:8000/balance?wallet=YOUR_WALLET_ADDRESS"

# Check in
curl -X POST "http://localhost:8000/checkin" \
  -H "Content-Type: application/json" \
  -d '{"wallet": "YOUR_WALLET_ADDRESS"}'

# Claim tokens
curl -X POST "http://localhost:8000/claim" \
  -H "Content-Type: application/json" \
  -d '{"wallet": "YOUR_WALLET_ADDRESS"}'
```

## Project Structure

```
tokens_backend/
├── main.py              # FastAPI application
├── spl_token_utils.py   # SPL token utilities
├── demo_mint.py         # Demo and testing script
├── requirements.txt     # Python dependencies
├── .env                 # Environment configuration
└── README.md           # This file
```

## Configuration

### Environment Variables

- `RPC_URL`: Solana RPC endpoint (default: devnet)
- `MINT`: Your SPL token mint address
- `DECIMALS`: Token decimals (default: 6)
- `TREASURY_SECRET_KEY`: Treasury wallet keypair as JSON array
- `PINATA_JWT`: Pinata API JWT for file uploads
- `MAX_UPLOAD_MB`: Maximum file upload size

### Treasury Setup

The treasury wallet needs:
1. SOL for transaction fees
2. Tokens to distribute as rewards

To fund your treasury:
```bash
# Get SOL from devnet faucet
solana airdrop 2 <TREASURY_WALLET>

# Transfer tokens to treasury
spl-token transfer <MINT_ADDRESS> <AMOUNT> <TREASURY_WALLET>
```

## Development

### Adding New Features

1. Add new endpoints in `main.py`
2. Add utility functions in `spl_token_utils.py`
3. Test with `demo_mint.py`

### Testing

Use the demo script to test token operations:

```bash
python demo_mint.py
```

This will:
- Verify your mint configuration
- Check treasury balance
- Test token transfers
- Provide setup guidance

## Troubleshooting

### Common Issues

1. **"Mint not found"**: Check your MINT address in .env
2. **"Insufficient funds"**: Add SOL to treasury wallet
3. **"No tokens in treasury"**: Transfer tokens to treasury
4. **"Invalid keypair"**: Check TREASURY_SECRET_KEY format

### Getting Help

- Check Solana logs: `solana logs`
- Verify transactions on Solana Explorer
- Use `demo_mint.py` for debugging

## Next Steps

- Add user authentication
- Implement batch processing
- Add more reward mechanisms
- Deploy to production
- Add monitoring and analytics
