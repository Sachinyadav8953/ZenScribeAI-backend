import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean,
    DateTime, Enum as SAEnum, Integer, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from db.session import Base
 
 
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
 
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True, index=True)  # type: ignore
    uuid: Mapped[uuid.UUID] = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)  # type: ignore
 
    full_name: Mapped[str] = Column(String(100), nullable=False)  # type: ignore
    email: Mapped[str] = Column(String(255), nullable=False, unique=True, index=True)  # type: ignore
    hashed_password: Mapped[str] = Column(String(255), nullable=False)  # type: ignore
 
    role: Mapped[UserRole] = Column(SAEnum(UserRole),        nullable=False, default=UserRole.DOCTOR)  # type: ignore
    specialization: Mapped[Specialization | None] = Column(SAEnum(Specialization),  nullable=True)  # type: ignore
    license_number: Mapped[str | None] = Column(String(50),  nullable=True, unique=True)  # type: ignore
    license_verified: Mapped[bool] = Column(Boolean,     default=False, nullable=False)  # type: ignore
    hospital_name    = Column(String(150), nullable=True)
    phone_number     = Column(String(20),  nullable=True)
    profile_image    = Column(String(500), nullable=True)      
 
  
    is_email_verified: Mapped[bool] = Column(Boolean,                default=False, nullable=False)  # type: ignore
    email_verification_token: Mapped[str | None] = Column(String(255),            nullable=True)  # type: ignore
    email_verification_expires: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)  # type: ignore
 
    reset_password_token: Mapped[str | None] = Column(String(255),            nullable=True)  # type: ignore
    reset_password_expires: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)  # type: ignore
 
    is_2fa_enabled: Mapped[bool] = Column(Boolean,     default=False, nullable=False)  # type: ignore
    two_factor_secret: Mapped[str | None] = Column(String(255), nullable=True)  # type: ignore
 
    is_active: Mapped[bool] = Column(Boolean, default=True,  nullable=False)  # type: ignore
    is_deleted: Mapped[bool] = Column(Boolean, default=False, nullable=False)  # type: ignore
    deleted_at: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)  # type: ignore
 
    last_login: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)  # type: ignore
    last_login_ip: Mapped[str | None] = Column(String(45),  nullable=True)  # type: ignore
    last_login_device: Mapped[str | None] = Column(String(255), nullable=True)  # type: ignore      
 

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
 

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.uuid", ondelete="SET NULL"),
        nullable=True
    )
    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.uuid", ondelete="SET NULL"),
        nullable=True
    )      
 
    def __repr__(self):
        return f"<User uuid={self.uuid} email={self.email} role={self.role}>"