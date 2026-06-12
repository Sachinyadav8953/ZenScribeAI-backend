import uuid as uuid_module  
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Integer, DateTime,
    Enum as SAEnum, ForeignKey, Text, Float
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.session import Base


class SpeakerEnum(str, enum.Enum):
    DOCTOR  = "doctor"
    PATIENT = "patient"
    UNKNOWN = "unknown"



class Transcript(Base):
    __tablename__ = "transcripts"

    
    id:   Mapped[int]       = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    uuid: Mapped[uuid_module.UUID] = mapped_column(UUID(as_uuid=True), default=uuid_module.uuid4, unique=True, nullable=False, index=True)

    
    consultation_id: Mapped[uuid_module.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("consultations.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    speaker: Mapped[SpeakerEnum] = mapped_column(
        SAEnum(SpeakerEnum, native_enum=False), nullable=False, default=SpeakerEnum.UNKNOWN
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)

    timestamp_start: Mapped[float]           = mapped_column(Float, nullable=False)
    timestamp_end:   Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    consultation = relationship(
        "Consultation",
        back_populates="transcripts",
        foreign_keys=[consultation_id],
        primaryjoin="Transcript.consultation_id == Consultation.uuid",
    )

    def __repr__(self):
        return f"<Transcript uuid={self.uuid} speaker={self.speaker} text={self.text[:30]}...>"