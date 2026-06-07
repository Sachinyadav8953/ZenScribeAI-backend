def validate_password_strength(password: str) -> str:
    if not any(c.isupper() for c in password):
            raise ValueError("Password must contain at least one uppercase letter")
    if not any(c.isdigit() for c in password):
            raise ValueError("Password must contain at least one number")
    if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
            raise ValueError("Password must contain at least one special character")
    return password

def validate_password_match(password: str, confirm_password: str) -> str:
    if password != confirm_password:
        raise ValueError("Passwords do not match")
    return confirm_password