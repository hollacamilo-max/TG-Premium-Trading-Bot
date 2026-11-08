import re
from typing import Tuple
from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip39MnemonicValidator
from eth_account import Account
from solders.keypair import Keypair
from solders.pubkey import Pubkey


# Initialize mnemonic validators
_mnemonic_english = Mnemonic("english")
_bip39_validator = Bip39MnemonicValidator()


def validate_seed_phrase(phrase: str) -> Tuple[bool, str]:
    """
    Validate a BIP39 seed phrase (12 or 24 words).
    Returns (is_valid, error_message)
    """
    if not phrase or not phrase.strip():
        return False, "Seed phrase cannot be empty"
    
    words = phrase.strip().split()
    if len(words) not in [12, 15, 18, 21, 24]:
        return False, f"Seed phrase must be 12, 15, 18, 21, or 24 words (got {len(words)})"
    
    # Check with mnemonic library
    if not _mnemonic_english.check(phrase.strip()):
        return False, "Invalid seed phrase: checksum failed"
    
    # Additional BIP39 validation
    try:
        _bip39_validator.Validate(phrase.strip())
    except Exception as e:
        return False, f"Invalid seed phrase: {str(e)}"
    
    return True, ""


def validate_private_key_evm(private_key: str) -> Tuple[bool, str, str]:
    """
    Validate an EVM private key (hex format, 64 chars).
    Returns (is_valid, address, error_message)
    """
    if not private_key or not private_key.strip():
        return False, "", "Private key cannot be empty"
    
    pk = private_key.strip()
    # Remove 0x prefix if present
    if pk.startswith("0x"):
        pk = pk[2:]
    
    # Check hex format
    if not re.match(r"^[0-9a-fA-F]{64}$", pk):
        return False, "", "Invalid EVM private key: must be 64 hex characters"
    
    try:
        account = Account.from_key("0x" + pk)
        return True, account.address, ""
    except Exception as e:
        return False, "", f"Invalid private key: {str(e)}"


def validate_private_key_solana(private_key: str) -> Tuple[bool, str, str]:
    """
    Validate a Solana private key (base58 or hex format).
    Returns (is_valid, address, error_message)
    """
    if not private_key or not private_key.strip():
        return False, "", "Private key cannot be empty"
    
    pk = private_key.strip()
    
    try:
        # Try base58 first (most common for Solana)
        keypair = Keypair.from_base58_string(pk)
        return True, str(keypair.pubkey()), ""
    except Exception:
        pass
    
    try:
        # Try hex format
        if re.match(r"^[0-9a-fA-F]{64}$", pk):
            keypair = Keypair.from_bytes(bytes.fromhex(pk))
            return True, str(keypair.pubkey()), ""
        elif re.match(r"^[0-9a-fA-F]{128}$", pk):  # 64 bytes = 128 hex chars (seed)
            keypair = Keypair.from_seed(bytes.fromhex(pk))
            return True, str(keypair.pubkey()), ""
    except Exception as e:
        return False, "", f"Invalid Solana private key: {str(e)}"
    
    return False, "", "Invalid Solana private key format (must be base58 or 64/128 hex chars)"


def validate_wallet_import(chain: str, wallet_type: str, data: str) -> Tuple[bool, str, str]:
    """
    Validate wallet import data based on chain and type.
    Returns (is_valid, address, error_message)
    """
    chain = chain.lower()
    wallet_type = wallet_type.lower()
    
    if wallet_type == "seed_phrase":
        is_valid, error = validate_seed_phrase(data)
        if not is_valid:
            return False, "", error
        # For seed phrase, we derive address based on chain
        # This is a simplified check - actual derivation happens in wallet service
        return True, "derived_from_seed", ""
    
    elif wallet_type == "private_key":
        if chain in ["evm", "ethereum", "eth", "base", "arbitrum", "arb", "bsc", "polygon", "matic", "avalanche", "avax"]:
            return validate_private_key_evm(data)
        elif chain in ["solana", "sol"]:
            return validate_private_key_solana(data)
        else:
            return False, "", f"Unsupported chain: {chain}"
    
    return False, "", f"Unknown wallet type: {wallet_type}"
