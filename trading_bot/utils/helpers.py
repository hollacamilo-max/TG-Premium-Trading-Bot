import secrets
import string
from decimal import Decimal, ROUND_DOWN
from typing import Optional


def format_usd(amount: float | Decimal | int | str, decimals: int = 2) -> str:
    if amount is None:
        return "$0.00"
    d = Decimal(str(amount))
    quantize_exp = Decimal("0.1") ** decimals
    formatted = d.quantize(quantize_exp, rounding=ROUND_DOWN)
    return f"${formatted:,.{decimals}f}"


def format_token_amount(amount: float | Decimal | int | str, decimals: int = 4, trim_zeros: bool = True) -> str:
    if amount is None:
        return "0"
    d = Decimal(str(amount))
    if trim_zeros:
        s = format(d, "f")
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return s
    quantize_exp = Decimal("0.1") ** decimals
    return str(d.quantize(quantize_exp, rounding=ROUND_DOWN))


def generate_referral_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    alphabet = alphabet.replace("O", "").replace("0", "").replace("I", "").replace("1", "")
    return "".join(secrets.choice(alphabet) for _ in range(length))


def truncate_address(address: str, start: int = 6, end: int = 4) -> str:
    if not address:
        return ""
    if len(address) <= start + end:
        return address
    return f"{address[:start]}...{address[-end:]}"


def parse_amount_input(text: str) -> Optional[Decimal]:
    if not text:
        return None
    text = text.strip().lower()
    if text in ["all", "max", "100%"]:
        return Decimal("-1")
    if text.endswith("%"):
        try:
            pct = Decimal(text[:-1]) / Decimal("100")
            return pct
        except Exception:
            return None
    try:
        return Decimal(text)
    except Exception:
        return None


def escape_markdown(text: str) -> str:
    if not text:
        return ""
    special_chars = r"_*[]()~`>#+-=|{}.!"
    return "".join(f"\\{c}" if c in special_chars else c for c in text)


def format_number(num: float | Decimal | int, decimals: int = 2) -> str:
    if num is None:
        return "0"
    n = float(num)
    if abs(n) >= 1_000_000_000:
        return f"{n / 1_000_000_000:.{decimals}f}B"
    elif abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.{decimals}f}M"
    elif abs(n) >= 1_000:
        return f"{n / 1_000:.{decimals}f}K"
    else:
        return f"{n:.{decimals}f}"
