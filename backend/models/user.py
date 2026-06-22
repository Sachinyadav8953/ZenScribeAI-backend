import uuid as uuid_module
import enum
from datetime import datetime
from sqlalchemy import (
    String, Boolean,
    DateTime, Enum as SAEnum, Integer, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped,mapped_column
from db.session import Base
from typing import Optional
 
class UserRole(str, enum.Enum):
    DOCTOR      = "doctor"
 
class Specialization(str, enum.Enum):
    GENERAL_PHYSICIAN = "general_physician"
    CARDIOLOGIST      = "cardiologist"
    NEUROLOGIST       = "neurologist"
    PEDIATRICIAN      = "pediatrician"
    ORTHOPEDIC        = "orthopedic"
    DERMATOLOGIST     = "dermatologist"
    PSYCHIATRIST      = "psychiatrist"
    GYNECOLOGIST      = "gynecologist"
    ONCOLOGIST        = "oncologist"
    OTHER             = "other"
 
 


class User(Base):
    __tablename__ = "users"

    id              : Mapped[int]           = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    uuid            : Mapped[uuid_module.UUID]     = mapped_column(UUID(as_uuid=True), default=uuid_module.uuid4, unique=True)
    full_name       : Mapped[str]           = mapped_column(String(100), nullable=False)
    email           : Mapped[str]           = mapped_column(String(255), nullable=False, unique=True, index=True)
    hashed_password : Mapped[str]           = mapped_column(String(255), nullable=False)
    role            : Mapped[UserRole]      = mapped_column(SAEnum(UserRole, native_enum=False), nullable=False, default=UserRole.DOCTOR)
    specialization  : Mapped[Optional[Specialization]] = mapped_column(SAEnum(Specialization, native_enum=False), nullable=True)
    license_number  : Mapped[Optional[str]]  = mapped_column(String(50), nullable=True, unique=True)
    license_verified: Mapped[bool]           = mapped_column(Boolean, default=False, nullable=False)
    hospital_name   : Mapped[Optional[str]]  = mapped_column(String(150), nullable=True)
    phone_number    : Mapped[Optional[str]]  = mapped_column(String(20), nullable=True)
    profile_image   : Mapped[Optional[str]]  = mapped_column(String(500), nullable=True)
    is_email_verified          : Mapped[bool]              = mapped_column(Boolean, default=False, nullable=False)
    email_verification_token   : Mapped[Optional[str]]     = mapped_column(String(255), nullable=True)
    email_verification_expires : Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reset_password_token       : Mapped[Optional[str]]     = mapped_column(String(255), nullable=True)
    reset_password_expires     : Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_2fa_enabled             : Mapped[bool]              = mapped_column(Boolean, default=False, nullable=False)
    two_factor_secret          : Mapped[Optional[str]]     = mapped_column(String(255), nullable=True)
    is_active                  : Mapped[bool]              = mapped_column(Boolean, default=True, nullable=False)
    is_deleted                 : Mapped[bool]              = mapped_column(Boolean, default=False, nullable=False)
    deleted_at                 : Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login                 : Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip              : Mapped[Optional[str]]     = mapped_column(String(45), nullable=True)
    last_login_device          : Mapped[Optional[str]]     = mapped_column(String(255), nullable=True)
    created_at                 : Mapped[datetime]          = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at                 : Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by                 : Mapped[Optional[uuid_module.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.uuid", ondelete="SET NULL"), nullable=True)
    updated_by                 : Mapped[Optional[uuid_module.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.uuid", ondelete="SET NULL"), nullable=True)   
 
    def __repr__(self):
        return f"<User uuid={self.uuid} email={self.email} role={self.role}>"