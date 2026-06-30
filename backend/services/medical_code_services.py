import json
import logging
from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from schemas.medical_code import MedicalCodeSelect
from models.medical_code import MedicalCode, CodeType
from models.soap_note import SoapNote
from models.consultation import Consultation, ConsultationStatus
from utils.gemini_client import get_gemini_client
from config import settings
from models.user import User

logger = logging.getLogger("doctor_zenz.medical_code_services")    
 

def build_coding_prompt(assessment: str, plan: str) -> str:
    return f"""
    You are an expert clinical documentation specialist and certified ICD-10-CM medical coder.

    Your task is to assign ICD-10-CM diagnosis codes ONLY from the documented clinical information below.

    Clinical Assessment:
    {assessment}

    Treatment Plan:
    {plan}

    Coding Rules:

    1. Code ONLY diagnoses, conditions, signs, or symptoms explicitly documented.
    2. Never infer diagnoses from medications, laboratory tests, imaging orders, or treatments.
    3. Never assume severity, etiology, organism, laterality, or complications unless explicitly documented.
    4. If a diagnosis is uncertain (suspected, probable, possible, likely, rule out, query, differential diagnosis), DO NOT code the diagnosis. Instead code documented signs or symptoms when appropriate.
    5. Use the highest level of specificity supported by the documentation.
    6. Do not assign unspecified codes if a more specific documented code exists.
    7. Do not assign symptom codes that are routinely associated with a confirmed diagnosis unless they are independently significant.
    8. Include chronic conditions only if they are documented as active, assessed, monitored, treated, or affecting today's encounter.
    9. Remove duplicate diagnoses.
    10. Rank diagnoses by clinical importance:
    - Primary = chief reason for today's encounter.
    - Secondary = additional active diagnoses affecting management.
    11. Maximum 5 diagnosis codes.
    12. If no supported diagnosis exists, return:
    {{"codes":[]}}

    Output ONLY valid JSON.

    Schema:

    {{
    "codes":[
        {{
        "code":"string",
        "description":"string",
        "type":"primary|secondary"
        }}
    ]
    }}
    """
async def generate_medical_codes(
    consultation_uuid: str,
    current_doctor: User,
    db: AsyncSession
) -> list[MedicalCode]:

    result = await db.execute(
        select(Consultation).where(Consultation.uuid == consultation_uuid)
    )
    consultation = result.scalar_one_or_none()

    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")

    if str(consultation.doctor_id) != str(current_doctor.uuid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorised")

    if consultation.status != ConsultationStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consultation must be completed before generating medical codes"
        )

    soap_note_res = await db.execute(
        select(SoapNote).where(SoapNote.consultation_id == consultation.uuid)
    )
    soap_note = soap_note_res.scalar_one_or_none()

    if not soap_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SOAP note not found")

    if not soap_note.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOAP note must be approved before generating medical codes"
        )

    parsed_text :str|None=None

    try:
        gemini   = get_gemini_client()
        response = gemini.models.generate_content(
            model    = settings.GEMINI_MODEL,
            contents = build_coding_prompt(soap_note.assessment, soap_note.plan),
            config   = types.GenerateContentConfig(
                temperature        = 0.1,
                max_output_tokens  = 2048,
                response_mime_type = "application/json",
            )
        )
        
        parsed_text=response.text
        if parsed_text is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini returned an empty response."
            )
        parsed_response = json.loads(parsed_text)

    except Exception as e:
        logger.error(f"Error generating medical codes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate medical codes"
        )

    if not parsed_response or "codes" not in parsed_response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Invalid response from AI"
        )

    medical_codes = []

    for code_data in parsed_response["codes"]:
        code = MedicalCode(
            consultation_id = consultation.uuid,
            soap_note_id    = soap_note.uuid,
            code            = code_data["code"],
            description     = code_data["description"],
            code_type       = CodeType.PRIMARY if code_data["type"] == "primary" else CodeType.SECONDARY,
            is_selected     = False,
        )
        db.add(code)
        medical_codes.append(code)

    await db.commit()

    return medical_codes



async def get_medical_codes(
    consultation_uuid: str,
    current_doctor: User,
    db: AsyncSession
) -> list[MedicalCode]:

    consultation_res = await db.execute(
        select(Consultation).where(Consultation.uuid == consultation_uuid)
    )
    consultation = consultation_res.scalar_one_or_none()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )

    if str(consultation.doctor_id) != str(current_doctor.uuid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorised"
        )

    result = await db.execute(
        select(MedicalCode)
        .where(MedicalCode.consultation_id == consultation_uuid)
        .order_by(MedicalCode.code_type)
    )
    return list(result.scalars().all())


async def select_medical_code(
    code_uuid: str,
    data: MedicalCodeSelect,
    current_doctor: User,
    db: AsyncSession
) -> MedicalCode:

    result = await db.execute(
        select(MedicalCode).where(MedicalCode.uuid == code_uuid)
    )
    medical_code = result.scalar_one_or_none()

    if not medical_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical code not found"
        )

    consultation_res = await db.execute(
        select(Consultation).where(Consultation.uuid == medical_code.consultation_id)
    )
    consultation = consultation_res.scalar_one_or_none()

    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found"
        )

    if str(consultation.doctor_id) != str(current_doctor.uuid):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not Authorised"
        )

    medical_code.is_selected = data.is_selected
    await db.commit()
    await db.refresh(medical_code)

    return medical_code