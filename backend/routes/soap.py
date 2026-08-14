from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.user import User
from schemas.soap_note import SoapNoteResponse, SoapNoteUpdate
from services.soap_services import (
    generate_soap_note,
    get_soap_note,
    update_soap_note,
    approve_soap_note
)
from utils.dependencies import get_current_doctor

router = APIRouter(prefix="/soap", tags=["SOAP Notes"])


@router.post("/{consultation_uuid}/generate",
    status_code=status.HTTP_201_CREATED,
    response_model=SoapNoteResponse
)
async def generate(
    consultation_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)
):
    return await generate_soap_note(consultation_uuid, current_doctor, db)


from typing import Optional

@router.get("/{consultation_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[SoapNoteResponse]
)
async def get_note(
    consultation_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)
):
    return await get_soap_note(consultation_uuid, current_doctor, db)


@router.patch("/{consultation_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=SoapNoteResponse
)
async def update_note(
    consultation_uuid: str,
    data: SoapNoteUpdate,
    db: AsyncSession = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)
):
    return await update_soap_note(consultation_uuid, data, current_doctor, db)


@router.patch("/{consultation_uuid}/approve",
    status_code=status.HTTP_200_OK,
    response_model=SoapNoteResponse
)
async def approve_note(
    consultation_uuid: str,
    db: AsyncSession = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)
):
    return await approve_soap_note(consultation_uuid, current_doctor, db)