import hashlib
import bcrypt


def _prehash(plain_password: str) -> bytes:
    """SHA-256 pre-hash to bypass bcrypt's 72-byte limit."""
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest().encode("utf-8")


def hash_password(plain_password: str) -> str:
    """Hash a password using SHA-256 pre-hash + bcrypt."""
    hashed = bcrypt.hashpw(_prehash(plain_password), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.
    Supports both:
      1. New format: SHA-256 pre-hashed passwords (created by this module)
      2. Legacy format: direct bcrypt passwords (created by old passlib code)
    """
    hashed_bytes = hashed_password.encode("utf-8")

    # Try new format first (SHA-256 pre-hashed)
    try:
        if bcrypt.checkpw(_prehash(plain_password), hashed_bytes):
            return True
    except Exception:
        pass

    # Fall back to legacy direct bcrypt (passlib-compatible)
    try:
        if bcrypt.checkpw(plain_password.encode("utf-8"), hashed_bytes):
            return True
    except Exception:
        pass

    return False