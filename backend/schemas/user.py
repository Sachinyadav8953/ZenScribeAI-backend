from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from uuid import UUID
from datetime import datetime
from models.user import UserRole, Specialization
from utils.passwordValidators import validate_password_strength, validate_password_match

#signup
class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=64)
    confirm_password: str
    role: UserRole                           = UserRole.DOCTOR
    specialization: Optional[Specialization] = Field(default=None, validate_default=True)
    license_number: Optional[str]            = Field(default=None, min_length=5, max_length=50)
    hospital_name: Optional[str]             = Field(default=None, max_length=150)
    phone_number: Optional[str]              = Field(default=None, pattern=r"^\+?[1-9]\d{9,14}$")

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

    @field_validator("specialization")
    @classmethod
    def doctor_needs_specialization(cls, v, info):
        if info.data.get("role") == UserRole.DOCTOR and v is None:
            raise ValueError("Specialization is required for doctors")
        return v


#signin
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


#ForgotPassword

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


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
    email: EmailStr
    role: UserRole

#User Response

class UserResponse(BaseModel):
    id: int
    uuid: UUID
    full_name: str
    email: EmailStr
    role: UserRole
    specialization: Optional[Specialization] = None
    license_number: Optional[str]            = None
    license_verified: bool
    hospital_name: Optional[str]             = None
    phone_number: Optional[str]              = None
    is_email_verified: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}