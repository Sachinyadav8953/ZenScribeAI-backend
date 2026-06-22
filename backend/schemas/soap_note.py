

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class SoapNoteResponse(BaseModel):
    id:              int
    uuid:            UUID
    consultation_id: UUID
    subjective:      str
    objective:       str
    assessment:      str
    plan:            str
    is_approved:     bool
    approved_at:     Optional[datetime] = None
    created_at:      datetime
    updated_at:      Optional[datetime] = None

    model_config = {"from_attributes": True}


class SoapNoteUpdate(BaseModel):
    subjective:  Optional[str] = None
    objective:   Optional[str] = None
    assessment:  Optional[str] = None
    plan:        Optional[str] = None