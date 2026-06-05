import uuid
import enum
from sqlalchemy import (
    Column, String, Boolean,
    DateTime, Enum as SAEnum, Integer
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
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
 
    id      = Column(Integer, primary_key=True, autoincrement=True, index=True)
    uuid    = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False, index=True)
 
    full_name       = Column(String(100), nullable=False)
    email           = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
 
    role             = Column(SAEnum(UserRole),        nullable=False, default=UserRole.DOCTOR)
    specialization   = Column(SAEnum(Specialization),  nullable=True)
    license_number   = Column(String(50),  nullable=True, unique=True)
    license_verified = Column(Boolean,     default=False, nullable=False)
    hospital_name    = Column(String(150), nullable=True)
    phone_number     = Column(String(20),  nullable=True)
    profile_image    = Column(String(500), nullable=True)      
 
  
    is_email_verified          = Column(Boolean,                default=False, nullable=False)
    email_verification_token   = Column(String(255),            nullable=True)
    email_verification_expires = Column(DateTime(timezone=True), nullable=True)
 
    reset_password_token   = Column(String(255),            nullable=True)
    reset_password_expires = Column(DateTime(timezone=True), nullable=True)
 
    is_2fa_enabled    = Column(Boolean,     default=False, nullable=False)
    two_factor_secret = Column(String(255), nullable=True)  
 
    is_active  = Column(Boolean, default=True,  nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)     
    deleted_at = Column(DateTime(timezone=True), nullable=True)
 
    last_login        = Column(DateTime(timezone=True), nullable=True)
    last_login_ip     = Column(String(45),  nullable=True)      
    last_login_device = Column(String(255), nullable=True)      
 

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