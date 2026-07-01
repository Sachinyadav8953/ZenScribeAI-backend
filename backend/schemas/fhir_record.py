from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class FHIRRecordResponse(BaseModel):
    id: int
    uuid: UUID
    consultation_id: UUID
    fhir_patient_id: Optional[str]      = None
    fhir_practitioner_id: Optional[str] = None
    fhir_encounter_id: Optional[str]    = None
    fhir_document_id: Optional[str]     = None
    synced_at: datetime

    model_config = {"from_attributes": True}