import uuid as uuid_module
import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.session import Base


class CodeType(str, enum.Enum):
    PRIMARY   = "primary"
    SECONDARY = "secondary"


class MedicalCode(Base):
    __tablename__ = "medical_codes"

    id:   Mapped[int]            = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    uuid: Mapped[uuid_module.UUID] = mapped_column(UUID(as_uuid=True), default=uuid_module.uuid4, unique=True, nullable=False, index=True)

    consultation_id: Mapped[uuid_module.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("consultations.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    soap_note_id: Mapped[uuid_module.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("soap_notes.uuid", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    code:        Mapped[str]      = mapped_column(String(10), nullable=False, index=True)
    description: Mapped[str]      = mapped_column(Text, nullable=False)
    code_type:   Mapped[CodeType] = mapped_column(SAEnum(CodeType, native_enum=False), default=CodeType.PRIMARY, nullable=False, index=True)
    is_selected: Mapped[bool]     = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    consultation = relationship(
        "Consultation",
        foreign_keys=[consultation_id],
        primaryjoin="MedicalCode.consultation_id == Consultation.uuid"
    )
    soap_note = relationship(
        "SoapNote",
        foreign_keys=[soap_note_id],
        primaryjoin="MedicalCode.soap_note_id == SoapNote.uuid"
    )

    def __repr__(self):
        return f"<MedicalCode uuid={self.uuid} code={self.code} type={self.code_type}>"