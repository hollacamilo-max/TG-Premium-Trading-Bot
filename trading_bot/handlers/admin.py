from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import get_settings
from services.admin_service import AdminService
from services.wallet_service import WalletService
from keyboards import get_admin_keyboard, get_admin_user_keyboard, get_broadcast_keyboard, get_admin_activity_keyboard
from database.models import User
from database.base import get_db
from sqlalchemy import select, desc

router = Router()
settings = get_settings()
admin_service = AdminService()
wallet_service = WalletService()


class AdminStates(StatesGroup):
    panel = State()
    broadcast_message = State()
    broadcast_target = State()
    user_message = State()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    """Admin panel command."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Access denied.")
        return
    
    await state.set_state(AdminStates.panel)
    await message.answer(
        "🔧 <b>Admin Panel</b>\n\nWelcome to the admin control panel.",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )


@router.callback_query(F.data == "admin_panel")
async def callback_admin_panel(callback: CallbackQuery, state: FSMContext):
    """Open admin panel."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🔧 <b>Admin Panel</b>\n\nSelect an option:",
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def callback_admin_stats(callback: CallbackQuery):
    """Show system statistics."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    stats = await admin_service.get_system_stats()
    
    text = (
        "📊 <b>System Statistics</b>\n\n"
        "👥 Total Users: " + str(stats["total_users"]) + "\n"
        "✅ Active Users: " + str(stats["active_users"]) + "\n"
        "🚫 Banned Users: " + str(stats["banned_users"]) + "\n"
        "💰 Total Trades: " + str(stats["total_trades"]) + "\n"
        "📈 Total Volume: $" + format_usd(stats["total_volume"]) + "\n"
        "👛 Total Wallets: " + str(stats["total_wallets"]) + "\n"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def callback_admin_users(callback: CallbackQuery):
    """List all users."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    users_stats = await admin_service.get_all_users_stats(limit=20)
    
    if not users_stats:
        await callback.message.edit_text(
            "👥 <b>All Users</b>\n\nNo users found.",
            parse_mode="HTML",
            reply_markup=get_admin_keyboard()
        )
        await callback.answer()
        return
    
    text = "👥 <b>All Users (Latest 20)</b>\n\n"
    for user in users_stats:
        banned = " 🚫" if user.get("is_banned") else ""
        premium = " 💎" if user.get("is_premium") else ""
        admin_badge = " 🔧" if user.get("is_admin") else ""
        text += (
            "ID: <code>" + str(user["user_id"]) + "</code>" + banned + premium + admin_badge + "\n"
            "  @" + (user["username"] or "N/A") + " | " + (user["first_name"] or "") + "\n"
            "  Trades: " + str(user["total_trades"]) + " | Volume: " + format_usd(user["total_volume_usd"]) + "\n"
            "  Wallets: " + str(user["wallet_count"]) + " | Commission: " + format_usd(user["commission_earned_usd"]) + "\n\n"
        )
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_user_"))
async def callback_admin_user_detail(callback: CallbackQuery):
    """Show user detail."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    parts = callback.data.split("_")
    if len(parts) < 3:
        return
    
    action = parts[2]
    user_id = int(parts[3])
    
    if action == "wallets":
        wallets = await wallet_service.get_user_wallets(user_id)
        text = "👛 <b>User Wallets</b>\n\n"
        for w in wallets:
            text += "Chain: " + w.chain.value + " | " + w.address[:10] + "...\n"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_user_keyboard(user_id))
    
    elif action == "trades":
        from services.trading_service import TradingService
        trading_service = TradingService()
        trades = await trading_service.get_user_trades(user_id, limit=10)
        text = "📈 <b>User Trades</b>\n\n"
        for t in trades:
            text += t.trade_type.value + " " + t.token_in_symbol + "→" + t.token_out_symbol + " | " + t.status.value + "\n"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_user_keyboard(user_id))
    
    elif action == "activity":
        logs = await admin_service.get_user_activity(user_id, limit=20)
        text = "📝 <b>User Activity</b>\n\n"
        for log in logs:
            text += log.action + " | " + str(log.details)[:100] + "\n"
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_user_keyboard(user_id))
    
    elif action == "referrals":
        from services.referral_service import ReferralService
        referral_service = ReferralService()
        stats = await referral_service.get_referral_stats(user_id)
        text = "👥 <b>Referral Stats</b>\n\nDirect: " + str(stats["direct_referrals"]) + "\nIndirect: " + str(stats["indirect_referrals"]) + "\nCommission: " + format_usd(stats["total_commission_usd"])
        await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_admin_user_keyboard(user_id))
    
    elif action == "ban":
        await admin_service.ban_user(user_id, callback.from_user.id, "Banned by admin")
        await callback.answer("🚫 User banned", show_alert=True)
    
    elif action == "unban":
        await admin_service.unban_user(user_id, callback.from_user.id)
        await callback.answer("✅ User unbanned", show_alert=True)
    
    elif action == "message":
        from aiogram.fsm.context import FSMContext
        # Would need state to store target user_id
        await callback.message.edit_text(
            "📩 <b>Send Message to User</b>\n\nEnter message:",
            parse_mode="HTML",
            reply_markup=None
        )
    
    await callback.answer()


@router.callback_query(F.data == "admin_activity")
async def callback_admin_activity(callback: CallbackQuery):
    """Show activity log."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📝 <b>Activity Log</b>\n\nFilter by action:",
        parse_mode="HTML",
        reply_markup=get_admin_activity_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_activity_"))
async def callback_admin_activity_filter(callback: CallbackQuery):
    """Filter activity log."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    action = callback.data.replace("admin_activity_", "")
    if action == "all":
        action = None
    
    logs = await admin_service.get_all_activity(action=action, limit=50)
    
    text = "📝 <b>Activity Log" + (" - " + action if action else "") + "</b>\n\n"
    for log in logs:
        text += "#" + str(log.user_id) + " | " + log.action + " | " + str(log.details)[:150] + "\n"
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_admin_activity_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_broadcast")
async def callback_admin_broadcast(callback: CallbackQuery, state: FSMContext):
    """Broadcast message menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    await callback.message.edit_text(
        "📢 <b>Broadcast Message</b>\n\nSelect target audience:",
        parse_mode="HTML",
        reply_markup=get_broadcast_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("broadcast_"))
async def callback_broadcast_target(callback: CallbackQuery, state: FSMContext):
    """Handle broadcast target selection."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Access denied.", show_alert=True)
        return
    
    target = callback.data.replace("broadcast_", "")
    await state.update_data(broadcast_target=target)
    await state.set_state(AdminStates.broadcast_message)
    
    target_names = {
        "all": "All Users",
        "user": "Specific User",
        "premium": "Premium Users",
        "new": "New Users (24h)",
    }
    
    await callback.message.edit_text(
        "📢 <b>Broadcast to " + target_names.get(target, target) + "</b>\n\nEnter message to send:",
        parse_mode="HTML",
        reply_markup=None
    )
    await callback.answer()


@router.message(AdminStates.broadcast_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    """Process broadcast message."""
    if not is_admin(message.from_user.id):
        return
    
    data = await state.get_data()
    target = data.get("broadcast_target", "all")
    msg_text = message.text
    
    # Get target users
    async with get_db() as session:
        query = select(User).where(User.is_banned == False)
        if target == "premium":
            query = query.where(User.is_premium == True)
        # Add more filters as needed
        
        result = await session.execute(query)
        users = list(result.scalars().all())
    
    sent = 0
    failed = 0
    for user in users:
        try:
            await message.bot.send_message(user.id, msg_text, parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
    
    await message.answer(
        "📢 <b>Broadcast Complete</b>\n\n"
        "Target: " + target + "\n"
        "Sent: " + str(sent) + "\n"
        "Failed: " + str(failed),
        parse_mode="HTML",
        reply_markup=get_admin_keyboard()
    )
    
    await state.clear()


def format_usd(amount):
    return "${:,.2f}".format(float(amount or 0))
