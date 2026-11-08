# Premium Telegram Trading Bot

A feature-rich Telegram trading bot supporting **EVM chains (Ethereum, Base, Arbitrum, BSC, Polygon, Avalanche)** and **Solana**, with wallet import, admin monitoring, and broadcast messaging.

## Features

### 🔐 Wallet Management
- **Import-only wallets** (no auto-generation)
- Support for **Seed Phrases** (12/24 words BIP39)
- Support for **Private Keys** (EVM hex, Solana base58/hex)
- Multi-chain support: Ethereum, Base, Arbitrum, BSC, Polygon, Avalanche, Solana
- Encrypted storage (AES-GCM)

### 💰 Trading
- Buy/Sell/Swap tokens
- Limit orders (planned)
- Multi-DEX support: Uniswap V2/V3, 1inch, Jupiter, Raydium, Orca
- Slippage control
- Gas priority fees

### 👥 Referral System
- Tier 1 (direct) and Tier 2 (indirect) commissions
- Custom referral links
- Commission tracking

### 🔧 Admin Panel
- **Full activity monitoring** - see all user actions including wallet imports
- View user wallets, trades, and referral stats
- Ban/unban users
- **Broadcast messaging** to all users, premium users, or specific users
- System statistics

### 🚀 Deployment
- Optimized for **Railway** (Python 3.12)
- Docker support
- PostgreSQL + Redis
- Horizontal scaling ready

## Quick Start

### 1. Clone and Configure

```bash
cd trading_bot
cp .env.example .env
# Edit .env with your settings
```

### 2. Generate Encryption Key

```bash
python -c "import base64, os; print(base64.b64encode(os.urandom(32)).decode())"
```

Add the output to `ENCRYPTION_KEY` in `.env`.

### 3. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis (using Docker)
docker-compose up -d postgres redis

# Run bot
python main.py
```

### 4. Railway Deployment

1. Push to GitHub
2. Connect repository to Railway
3. Add PostgreSQL and Redis services
4. Set environment variables in Railway dashboard
5. Deploy!

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `BOT_TOKEN` | Telegram Bot Token from @BotFather | Yes |
| `ADMIN_IDS` | Comma-separated admin user IDs | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `REDIS_URL` | Redis connection string | Yes |
| `ENCRYPTION_KEY` | Base64-encoded 32-byte key for wallet encryption | Yes |
| `SESSION_SECRET` | Secret for session signing | Yes |
| `ETHEREUM_RPC` | Ethereum RPC URL | No (has defaults) |
| `BASE_RPC` | Base RPC URL | No |
| `ARBITRUM_RPC` | Arbitrum RPC URL | No |
| `SOLANA_RPC` | Solana RPC URL | No |
| `DEFAULT_SLIPPAGE` | Default slippage % | No (1.0) |
| `REFERRAL_COMMISSION_BPS` | Tier 1 commission in basis points | No (100) |

## Project Structure

```
trading_bot/
├── main.py                 # Entry point
├── config/                 # Configuration
│   └── settings.py        # Pydantic settings
├── database/              # Database layer
│   ├── base.py           # SQLAlchemy setup
│   └── models.py         # ORM models
├── handlers/             # Telegram handlers
│   ├── main.py          # Main menu, /start
│   ├── wallet.py        # Wallet import/management
│   ├── trading.py       # Trading operations
│   ├── admin.py         # Admin panel
│   └── referral.py      # Referral system
├── middlewares/         # Aiogram middlewares
├── keyboards/           # Inline keyboards
├── services/            # Business logic
│   ├── wallet_service.py
│   ├── trading_service.py
│   ├── admin_service.py
│   └── referral_service.py
├── utils/               # Utilities
│   ├── encryption.py    # AES-GCM encryption
│   ├── validators.py    # Input validation
│   └── helpers.py       # Formatting helpers
└── requirements.txt
```

## Security Notes

⚠️ **IMPORTANT SECURITY WARNINGS:**

1. **Admin can see private keys/seed phrases** - This is by design per requirements but is a MAJOR security risk. Any admin with access can steal ALL user funds.

2. **Use strong encryption key** - Generate a new 32-byte key for production.

3. **Secure your admin IDs** - Only add trusted administrators.

4. **Use HTTPS RPC endpoints** - For production, use your own RPC nodes.

5. **Enable 2FA** on Telegram accounts.

## Railway Deployment Details

### Supported Python Versions
- Python 3.11 ✅
- Python 3.12 ✅ (recommended)
- Python 3.13 ✅

### Services Needed
1. **PostgreSQL** - Primary database
2. **Redis** - FSM storage, caching, sessions

### Environment Variables in Railway
Set all variables from `.env.example` in Railway dashboard.

### Health Checks
The bot uses long polling, so health checks just verify the process is running.

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## License

MIT License - See LICENSE file for details.

## Disclaimer

This software is for educational purposes. Trading cryptocurrencies involves substantial risk. The admin monitoring feature that exposes private keys is a severe security vulnerability - use at your own risk.
