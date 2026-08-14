import bcrypt
import hashlib


def _get_prehashed_bytes(plain_password: str) -> bytes:
    """Pre-hashes plain_password using SHA-256 to guarantee a 64-byte string (strictly < 72 bytes for bcrypt)."""
    if not plain_password:
        plain_password = ""
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest().encode("utf-8")


def hash_password(plain_password: str) -> str:
    prehashed = _get_prehashed_bytes(plain_password)
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(prehashed, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False
    prehashed = _get_prehashed_bytes(plain_password)
    try:
        return bcrypt.checkpw(prehashed, hashed_password.encode("utf-8"))
    except Exception:
        return False