import uuid as uuid_module
import enum
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Integer, DateTime,
    Enum as SAEnum, ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.session import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .transcript import Transcript

    
class ConsultationStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED   = "completed"
    CANCELLED   = "cancelled"


class GenderEnum(str, enum.Enum):
    MALE   = "male"
    FEMALE = "female"
    OTHER  = "other"


class Consultation(Base):
    __tablename__ = "consultations"

    id:   Mapped[int]       = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    uuid: Mapped[uuid_module.UUID] = mapped_column(UUID(as_uuid=True), default=uuid_module.uuid4, unique=True, nullable=False)

    doctor_id: Mapped[uuid_module.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )


    patient_name:   Mapped[str]                = mapped_column(String(100), nullable=False)
    patient_age:    Mapped[Optional[int]]      = mapped_column(Integer, nullable=True)
    patient_gender: Mapped[Optional[GenderEnum]] = mapped_column(SAEnum(GenderEnum, native_enum=False), nullable=True)
    patient_phone:  Mapped[Optional[str]]      = mapped_column(String(20), nullable=True)


    chief_complaint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ConsultationStatus] = mapped_column(
        SAEnum(ConsultationStatus, native_enum=False),
        nullable=False,
        default=ConsultationStatus.IN_PROGRESS,
        index=True
    )

    
    started_at: Mapped[datetime]            = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ended_at:   Mapped[Optional[datetime]]  = mapped_column(DateTime(timezone=True), nullable=True)

    
    created_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    
    doctor = relationship(
        "User",
        foreign_keys=[doctor_id],
        primaryjoin="Consultation.doctor_id == User.uuid",
    )

    transcripts: Mapped[List["Transcript"]] = relationship(
        "Transcript",
        back_populates="consultation",
        cascade="all, delete-orphan",
        order_by="Transcript.timestamp_start"
    )

    def __repr__(self):
        return f"<Consultation uuid={self.uuid} doctor={self.doctor_id} status={self.status}>"