
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from models.medical_code import CodeType


class MedicalCodeSelect(BaseModel):
    is_selected: bool



class MedicalCodeResponse(BaseModel):
    id:              int
    uuid:            UUID
    consultation_id: UUID
    soap_note_id:    UUID
    code:            str
    description:     str
    code_type:       CodeType
    is_selected:     bool
    created_at:      datetime

    model_config = {"from_attributes": True}


class MedicalCodeListResponse(BaseModel):
    codes: list[MedicalCodeResponse]
    total: int