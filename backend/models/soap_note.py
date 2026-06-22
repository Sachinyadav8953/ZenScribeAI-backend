import uuid as uuid_module
from datetime import datetime
from typing import Optional
from sqlalchemy import  Boolean, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from db.session import Base


class SoapNote(Base):
    __tablename__ = "soap_notes"

    id:   Mapped[int]       = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    uuid: Mapped[uuid_module.UUID] = mapped_column(UUID(as_uuid=True), default=uuid_module.uuid4, unique=True, nullable=False, index=True)

    
    consultation_id: Mapped[uuid_module.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("consultations.uuid", ondelete="CASCADE"),
        nullable=False,
        unique=True,      
        index=True
    )

    subjective:  Mapped[str]           = mapped_column(Text, nullable=False)
    objective:   Mapped[str]           = mapped_column(Text, nullable=False)
    assessment:  Mapped[str]           = mapped_column(Text, nullable=False)
    plan:        Mapped[str]           = mapped_column(Text, nullable=False)

    raw_transcript: Mapped[str]        = mapped_column(Text, nullable=False)

    is_approved:  Mapped[bool]              = mapped_column(Boolean, default=False, nullable=False)
    approved_at:  Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime]           = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    consultation = relationship(
        "Consultation",
        foreign_keys=[consultation_id],
        primaryjoin="SoapNote.consultation_id == Consultation.uuid"
    )

    def __repr__(self):
        return f"<SoapNote uuid={self.uuid} consultation={self.consultation_id}>"