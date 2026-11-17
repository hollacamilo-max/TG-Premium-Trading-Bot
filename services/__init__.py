# Local token service
from .token_service import TokenService, token_service

# Try to import trading_bot services (optional - requires additional dependencies)
try:
    from trading_bot.services.wallet_service import WalletService
    from trading_bot.services.trading_service import TradingService
    from trading_bot.services.admin_service import AdminService
    from trading_bot.services.referral_service import ReferralService
    _HAS_TRADING_SERVICES = True
except ImportError:
    # Trading services not available (missing dependencies)
    WalletService = None
    TradingService = None
    AdminService = None
    ReferralService = None
    _HAS_TRADING_SERVICES = False

__all__ = [
    "TokenService",
    "token_service",
]

if _HAS_TRADING_SERVICES:
    __all__.extend([
        "WalletService",
        "TradingService",
        "AdminService",
        "ReferralService",
    ])
