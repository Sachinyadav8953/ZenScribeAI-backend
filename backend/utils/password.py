from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False,
)


def hash_password(plain_password: str) -> str:
    safe_pw = plain_password[:72] if plain_password else ""
    return pwd_context.hash(safe_pw)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    safe_pw = plain_password[:72] if plain_password else ""
    return pwd_context.verify(safe_pw, hashed_password)