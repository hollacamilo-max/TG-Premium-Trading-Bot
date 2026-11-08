@from .main import router as main_router
from .wallet import router as wallet_router
from .trading import router as trading_router
from .admin import router as admin_router
from .referral import router as referral_router

__all__ = [
    "main_router",
    "wallet_router",
    "trading_router",
    "admin_router",
    "referral_router",
]
