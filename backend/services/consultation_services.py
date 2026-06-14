from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from models.consultation import Consultation
from models.user import User
from schemas.consultation import ConsultationCreate, ConsultationResponse,ConsultationUpdate,ConsultationStatus


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





from sqlalchemy import select


async def update_consultation(
    consultation_uuid: str,
    data: ConsultationUpdate,
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
            detail="You are not authorized to update this consultation"
        )

    
    if consultation.status != ConsultationStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only in progress consultations can be updated"
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