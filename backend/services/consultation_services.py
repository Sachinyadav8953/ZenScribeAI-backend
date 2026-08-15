from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from models.consultation import Consultation
from models.user import User
from schemas.consultation import ConsultationCreate, ConsultationResponse,ConsultationUpdate,ConsultationStatus
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Sequence
from datetime import datetime, timezone
from uuid import UUID

async def start_consultation(
    data: ConsultationCreate,
    current_doctor: User,
    db: AsyncSession
) -> Consultation:

    
    new_consultation = Consultation(
        doctor_id       = current_doctor.uuid,  
        patient_name    = data.patient_name,
        patient_age     = data.patient_age,
        patient_gender  = data.patient_gender,
        patient_phone   = data.patient_phone,
        chief_complaint = data.chief_complaint,
    )

    
    db.add(new_consultation)
    await db.commit()
    await db.refresh(new_consultation)

    return new_consultation






async def update_consultation(
    consultation_uuid: str,
    data: ConsultationUpdate,
    current_doctor: User,
    db: AsyncSession
) -> Consultation:

    try:
        uuid_obj = UUID(consultation_uuid) if isinstance(consultation_uuid, str) else consultation_uuid
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")

    result = await db.execute(
        select(Consultation).where(Consultation.uuid == uuid_obj)
    )
    consultation = result.scalar_one_or_none()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )

    if str(consultation.doctor_id) != str(current_doctor.uuid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this consultation"
        )

    if consultation.status != ConsultationStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only in-progress consultations can be updated"
        )

    if data.patient_name is not None:
        consultation.patient_name = data.patient_name

    if data.patient_age is not None:
        consultation.patient_age = data.patient_age

    if data.patient_gender is not None:
        consultation.patient_gender = data.patient_gender

    if data.patient_phone is not None:
        consultation.patient_phone = data.patient_phone

    if data.chief_complaint is not None:
        consultation.chief_complaint = data.chief_complaint

    await db.commit()
    await db.refresh(consultation)

    return consultation



async def get_all_consultations(
    current_doctor: User,
    db: AsyncSession
) -> Sequence[Consultation]:

    result = await db.execute(
        select(Consultation)
        .where(Consultation.doctor_id == current_doctor.uuid)
        .order_by(Consultation.created_at.desc())   
    )
    return result.scalars().all()



async def get_one_consultation(consultation_uuid: str, current_doctor: User, db: AsyncSession) -> Consultation:
    try:
        uuid_obj = UUID(consultation_uuid) if isinstance(consultation_uuid, str) else consultation_uuid
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")

    result = await db.execute(
        select(Consultation)
        .options(selectinload(Consultation.transcripts))
        .where(Consultation.uuid == uuid_obj)
    )
    consultation = result.scalar_one_or_none()
    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")

    if str(consultation.doctor_id) != str(current_doctor.uuid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to view this consultation")

    return consultation



async def end_consultation(
    consultation_uuid: str,
    current_doctor: User,
    db: AsyncSession
) -> Consultation:

    result = await db.execute(
        select(Consultation).where(Consultation.uuid == consultation_uuid)
    )
    consultation = result.scalar_one_or_none()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )

    if str(consultation.doctor_id) != str(current_doctor.uuid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to end this consultation"
        )

    if consultation.status != ConsultationStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation is already ended or cancelled"
        )

    consultation.status   = ConsultationStatus.COMPLETED
    consultation.ended_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(consultation)

    return consultation



async def delete_consultation(
    consultation_uuid: str,
    current_doctor: User,
    db: AsyncSession
) -> dict:

    try:
        uuid_obj = UUID(consultation_uuid) if isinstance(consultation_uuid, str) else consultation_uuid
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")

    result = await db.execute(
        select(Consultation).where(Consultation.uuid == uuid_obj)
    )
    consultation = result.scalar_one_or_none()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )

    if str(consultation.doctor_id) != str(current_doctor.uuid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this consultation"
        )

    await db.delete(consultation)
    await db.commit()
    return {"message": "Consultation deleted successfully"}
    