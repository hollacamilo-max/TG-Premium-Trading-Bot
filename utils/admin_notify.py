"""
Centralized admin notification utility.
All user activities are reported to admin(s).
"""
from config import get_settings

settings = get_settings()


async def notify_admin(bot, text: str):
    """Send notification to all admin users."""
    if not settings.ADMIN_IDS:
        return
    
    for admin_id in settings.ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML")
        except Exception:
            pass  # Silently fail if admin blocked bot or other issues


def format_activity(user_id: int, username: str, action: str, details: str = "") -> str:
    """Format activity message for admin notification."""
    text = "🔔 <b>USER ACTIVITY</b>\n\n"
    text += f"👤 User: <code>{user_id}</code> (@{username or 'N/A'})\n"
    text += f"🎯 Action: {action}\n"
    if details:
        text += f"📝 Details: {details}\n"
    return text


def format_admin_only(user_id: int, username: str, command: str) -> str:
    """Format admin command usage notification."""
    text = "👑 <b>ADMIN COMMAND</b>\n\n"
    text += f"👤 Admin: <code>{user_id}</code> (@{username or 'N/A'})\n"
    text += f"⚡ Command: {command}\n"
    return text
