import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _get_prehashed_password(plain_password: str) -> str:
    """Pre-hashes password using SHA-256 to guarantee a fixed 64-character string (strictly < 72 bytes for bcrypt)."""
    if not plain_password:
        plain_password = ""
    return hashlib.sha256(plain_password.encode("utf-8")).hexdigest()


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(_get_prehashed_password(plain_password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(_get_prehashed_password(plain_password), hashed_password)