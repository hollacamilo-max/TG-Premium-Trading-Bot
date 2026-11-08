from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from config import get_settings
from services.referral_service import ReferralService
from keyboards import get_main_keyboard

router = Router()
settings = get_settings()
referral_service = ReferralService()


@router.callback_query(F.data == "referral_menu")
async def callback_referral_menu(callback: CallbackQuery):
    """Show referral menu."""
    user_id = callback.from_user.id
    
    # Get bot username for referral link
    bot_info = await callback.bot.get_me()
    bot_username = bot_info.username
    
    referral_link = await referral_service.get_referral_link(user_id, bot_username)
    stats = await referral_service.get_referral_stats(user_id)
    
    text = (
        "👥 <b>Referral Program</b>\n\n"
        "Share your referral link and earn commissions!\n\n"
        "🔗 <b>Your Link:</b>\n<code>" + referral_link + "</code>\n\n"
        "📊 <b>Your Stats:</b>\n"
        "Direct Referrals: " + str(stats["direct_referrals"]) + "\n"
        "Indirect Referrals: " + str(stats["indirect_referrals"]) + "\n"
        "Total Commission: " + format_usd(stats["total_commission_usd"]) + "\n\n"
        "💰 <b>Commission Rates:</b>\n"
        "• Tier 1 (Direct): " + str(settings.REFERRAL_COMMISSION_BPS / 100) + "% of trading fees\n"
        "• Tier 2 (Indirect): " + str(settings.REFERRAL_TIER_2_BPS / 100) + "% of trading fees"
    )
    
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_main_keyboard()
    )
    await callback.answer()


def format_usd(amount):
    return "${:,.2f}".format(float(amount or 0))
