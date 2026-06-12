from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from models.consultation import ConsultationStatus, GenderEnum
from models.transcript import SpeakerEnum




class ConsultationCreate(BaseModel):
    patient_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Ramesh Yadav"]
    )
    patient_age: Optional[int] = Field(
        default=None,
        ge=0,
        le=120,
        description="Patient age in years"
    )
    patient_gender: Optional[GenderEnum] = None
    patient_phone: Optional[str] = Field(
        default=None,
        pattern=r"^\+?[1-9]\d{9,14}$"
    )
    chief_complaint: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Short note on reason for visit",
        examples=["Fever and chest pain since 2 days"]
    )



class ConsultationUpdate(BaseModel):
    patient_name: Optional[str]          = Field(default=None, min_length=2, max_length=100)
    patient_age: Optional[int]           = Field(default=None, ge=0, le=120)
    patient_gender: Optional[GenderEnum] = None
    patient_phone: Optional[str]         = Field(default=None, pattern=r"^\+?[1-9]\d{9,14}$")
    chief_complaint: Optional[str]       = Field(default=None, max_length=500)



class TranscriptResponse(BaseModel):
    id: int
    uuid: UUID
    speaker: SpeakerEnum
    text: str
    timestamp_start: float
    timestamp_end: Optional[float] = None
    confidence: Optional[float]    = None
    created_at: datetime

    model_config = {"from_attributes": True}





class ConsultationResponse(BaseModel):
    id: int
    uuid: UUID
    doctor_id: UUID
    patient_name: str
    patient_age: Optional[int]           = None
    patient_gender: Optional[GenderEnum] = None
    patient_phone: Optional[str]         = None
    chief_complaint: Optional[str]       = None
    status: ConsultationStatus
    started_at: datetime
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}




class ConsultationDetailResponse(ConsultationResponse):
    transcripts: List[TranscriptResponse] = []




class ConsultationListResponse(BaseModel):
    id: int
    uuid: UUID
    patient_name: str
    chief_complaint: Optional[str] = None
    status: ConsultationStatus
    started_at: datetime
    ended_at: Optional[datetime] = None

    model_config = {"from_attributes": True}