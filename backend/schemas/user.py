from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from models.user import UserRole, Specialization
from utils.passwordValidators import validate_password_strength, validate_password_match

#signup — email removed, license_number is now required
class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    # email: EmailStr  # REMOVED — no longer collected from user
    password: str = Field(..., min_length=8, max_length=64)
    confirm_password: str
    role: UserRole                           = UserRole.DOCTOR
    specialization: Optional[Specialization] = None
    license_number: str                      = Field(..., min_length=5, max_length=50)
    hospital_name: Optional[str]             = None
    phone_number: Optional[str]              = None

    @field_validator("phone_number", "hospital_name", mode="before")
    @classmethod
    def clean_empty_strings(cls, v):
        if not v or (isinstance(v, str) and not v.strip()):
            return None
        return v

    @field_validator("specialization", mode="before")
    @classmethod
    def clean_specialization(cls, v):
        if not v or (isinstance(v, str) and not v.strip()):
            return Specialization.GENERAL_PHYSICIAN
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_must_match(cls, v, info):
        if "password" in info.data:
            validate_password_match(info.data["password"], v) 
        return v  

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        validate_password_strength(v)   
        return v


#signin — uses license_number instead of email
class UserLogin(BaseModel):
    license_number: str = Field(..., min_length=5, max_length=50)
    password: str = Field(..., min_length=8)


# #ForgotPassword — COMMENTED OUT (email-based)
# class ForgotPasswordRequest(BaseModel):
#     email: EmailStr


#Reset Password
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str     = Field(..., min_length=8, max_length=64)
    confirm_new_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        validate_password_strength(v)
        return v

    @field_validator("confirm_new_password")
    @classmethod
    def passwords_must_match(cls, v, info):
        if "new_password" in info.data:
            validate_password_match(info.data["new_password"], v)
        return v


#Token Response

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


#Token Data

class TokenData(BaseModel):
    user_id: int
    uuid: UUID
    email: str  # kept as str for internal dummy email
    role: UserRole

#User Response

class UserResponse(BaseModel):
    id: int
    uuid: UUID
    full_name: str
    # email: EmailStr  # REMOVED — not exposed to frontend
    role: UserRole
    specialization: Optional[Specialization] = None
    license_number: Optional[str]            = None
    license_verified: bool
    hospital_name: Optional[str]             = None
    phone_number: Optional[str]              = None
    # is_email_verified: bool  # REMOVED — no longer relevant
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


#Refresh Token Request
class RefreshTokenRequest(BaseModel):
    refresh_token: str