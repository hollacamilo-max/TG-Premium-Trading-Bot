import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from config import get_settings


_aesgcm = None


def _get_cipher():
    global _aesgcm
    if _aesgcm is None:
        settings = get_settings()
        key = base64.b64decode(settings.ENCRYPTION_KEY)
        _aesgcm = AESGCM(key)
    return _aesgcm


def generate_encryption_key() -> str:
    key = os.urandom(32)
    return base64.b64encode(key).decode()


def encrypt_data(plaintext: str) -> str:
    if not plaintext:
        return ""
    cipher = _get_cipher()
    nonce = os.urandom(12)
    ciphertext = cipher.encrypt(nonce, plaintext.encode(), None)
    encrypted = nonce + ciphertext
    return base64.b64encode(encrypted).decode()


def decrypt_data(encrypted_b64: str) -> str:
    if not encrypted_b64:
        return ""
    cipher = _get_cipher()
    encrypted = base64.b64decode(encrypted_b64)
    if len(encrypted) < 12:
        raise ValueError("Invalid encrypted data: too short")
    nonce = encrypted[:12]
    ciphertext = encrypted[12:]
    plaintext = cipher.decrypt(nonce, ciphertext, None)
    return plaintext.decode()


def encrypt_dict(data: dict) -> str:
    import json
    return encrypt_data(json.dumps(data, separators=(",", ":")))


def decrypt_dict(encrypted_b64: str) -> dict:
    import json
    decrypted = decrypt_data(encrypted_b64)
    if not decrypted:
        return {}
    return json.loads(decrypted)
