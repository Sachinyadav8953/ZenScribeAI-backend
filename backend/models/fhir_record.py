import uuid as uuid_module
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from db.session import Base


class FHIRRecord(Base):
    __tablename__ = "fhir_records"

    id:   Mapped[int]            = mapped_column(autoincrement=True, primary_key=True, index=True)
    uuid: Mapped[uuid_module.UUID] = mapped_column(UUID(as_uuid=True), default=uuid_module.uuid4, unique=True, nullable=False)

    consultation_id: Mapped[uuid_module.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("consultations.uuid", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    fhir_patient_id     : Mapped[str] = mapped_column(String(100), nullable=True)
    fhir_practitioner_id: Mapped[str] = mapped_column(String(100), nullable=True)
    fhir_encounter_id   : Mapped[str] = mapped_column(String(100), nullable=True)
    fhir_document_id    : Mapped[str] = mapped_column(String(100), nullable=True)

    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    consultation = relationship(
        "Consultation",
        foreign_keys=[consultation_id],
        primaryjoin="FHIRRecord.consultation_id == Consultation.uuid"
    )

    def __repr__(self):
        return f"<FHIRRecord consultation={self.consultation_id} encounter={self.fhir_encounter_id}>"