import json
import logging
from uuid import UUID
from datetime import datetime, timezone
from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from models.consultation import Consultation, ConsultationStatus
from models.transcript import Transcript
from models.soap_note import SoapNote
from schemas.soap_note import SoapNoteUpdate
from models.user import User
from utils.gemini_client import get_gemini_client
from config import settings
logger = logging.getLogger("doctor_zenz.soap")


def build_prompt(transcript_text: str) -> str:
    return f"""
You are an expert medical scribe assistant for Indian doctors.

Below is a conversation between a doctor and patient during
a medical consultation. The conversation has been translated
to English from Hinglish (Hindi + English mixed).

Generate a professional SOAP note from this conversation.

CONVERSATION:
{transcript_text}

Rules:
- Use proper medical terminology
- Be concise and clinically accurate
- Only include information mentioned in the conversation
- Do not add or assume information not discussed
- Return ONLY valid JSON — no extra text, no markdown

Return exactly this JSON format:
{{
    "subjective": "what patient reported about symptoms, history, complaints",
    "objective": "what doctor observed, examined, vital signs if mentioned",
    "assessment": "doctor diagnosis or clinical impression",
    "plan": "treatment plan, medicines prescribed, follow up, investigations ordered"
}}
"""


async def generate_soap_note(
    consultation_uuid: str,
    current_doctor: User,
    db: AsyncSession
) -> SoapNote:

    try:
        uuid_obj = UUID(consultation_uuid) if isinstance(consultation_uuid, str) else consultation_uuid
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")

    result = await db.execute(
        select(Consultation).where(Consultation.uuid == uuid_obj)
    )
    consultation = result.scalar_one_or_none()

    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")

    if str(consultation.doctor_id) != str(current_doctor.uuid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    existing = await db.execute(
        select(SoapNote).where(SoapNote.consultation_id == consultation.uuid)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOAP note already generated for this consultation"
        )

    transcripts_result = await db.execute(
        select(Transcript)
        .where(Transcript.consultation_id == consultation.uuid)
        .order_by(Transcript.timestamp_start)
    )
    transcripts = transcripts_result.scalars().all()

    if not transcripts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transcript found for this consultation. Please record some audio first."
        )

    transcript_text = "\n".join([
        f"{chunk.speaker.upper()}: {chunk.text}"
        for chunk in transcripts
    ])

    response_text: str | None = None
    try:
        gemini = get_gemini_client()

        model_name = settings.GEMINI_MODEL or "gemini-3.6-flash"
        if "2.0-flash" in model_name:
            model_name = "gemini-3.6-flash"

        try:
            response = gemini.models.generate_content(
                model    = model_name,       
                contents = build_prompt(transcript_text),
                config   = types.GenerateContentConfig(
                    temperature      = 0.1,             
                    max_output_tokens = 2048,
                    response_mime_type = "application/json",  
                )
            )
        except Exception as model_err:
            if "2.0-flash" in str(model_err) or "404" in str(model_err):
                logger.warning(f"Model {model_name} failed, falling back to gemini-3.6-flash: {model_err}")
                response = gemini.models.generate_content(
                    model    = "gemini-3.6-flash",
                    contents = build_prompt(transcript_text),
                    config   = types.GenerateContentConfig(
                        temperature      = 0.1,
                        max_output_tokens = 2048,
                        response_mime_type = "application/json",
                    )
                )
            else:
                raise model_err

        response_text = response.text 

        if response_text is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Gemini returned an empty response."
            )

        # Clean markdown codeblocks if returned
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```"):
            lines = cleaned_text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned_text = "\n".join(lines).strip()

        soap_data = json.loads(cleaned_text)

    except json.JSONDecodeError:
        logger.error(f"Gemini returned invalid JSON: {response_text}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI returned invalid response format. Please try again."
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SOAP note via AI: {str(e)}"
        )

    soap_note = SoapNote(
        consultation_id = consultation.uuid,
        subjective      = soap_data.get("subjective", ""),
        objective       = soap_data.get("objective", ""),
        assessment      = soap_data.get("assessment", ""),
        plan            = soap_data.get("plan", ""),
        raw_transcript  = transcript_text,
    )

    db.add(soap_note)
    await db.commit()
    await db.refresh(soap_note)

    logger.info(f"SOAP note generated for consultation {consultation_uuid}")
    return soap_note


async def get_soap_note(
    consultation_uuid: str,
    current_doctor: User,
    db: AsyncSession
) -> SoapNote | None:

    try:
        uuid_obj = UUID(consultation_uuid) if isinstance(consultation_uuid, str) else consultation_uuid
    except ValueError:
        return None

    result = await db.execute(
        select(SoapNote).where(SoapNote.consultation_id == uuid_obj)
    )
    soap_note = result.scalar_one_or_none()

    return soap_note


async def update_soap_note(
    consultation_uuid: str,
    data: SoapNoteUpdate,
    current_doctor: User,
    db: AsyncSession
) -> SoapNote:

    try:
        uuid_obj = UUID(consultation_uuid) if isinstance(consultation_uuid, str) else consultation_uuid
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SOAP note not found")

    result = await db.execute(
        select(SoapNote).where(SoapNote.consultation_id == uuid_obj)
    )
    soap_note = result.scalar_one_or_none()
    if not soap_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SOAP note not found")

    # Fetch consultation to check authorization
    cons_res = await db.execute(select(Consultation).where(Consultation.uuid == soap_note.consultation_id))
    cons = cons_res.scalar_one_or_none()
    if cons and str(cons.doctor_id) != str(current_doctor.uuid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this operation")

    if data.subjective is not None:
        soap_note.subjective = data.subjective
    if data.objective is not None:
        soap_note.objective = data.objective
    if data.assessment is not None:
        soap_note.assessment = data.assessment
    if data.plan is not None:
        soap_note.plan = data.plan

    await db.commit()
    await db.refresh(soap_note)
    return soap_note


async def approve_soap_note(
    consultation_uuid: str,
    current_doctor: User,
    db: AsyncSession
) -> SoapNote:

    try:
        uuid_obj = UUID(consultation_uuid) if isinstance(consultation_uuid, str) else consultation_uuid
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SOAP note not found")

    result = await db.execute(
        select(SoapNote).where(SoapNote.consultation_id == uuid_obj)
    )
    soap_note = result.scalar_one_or_none()
    if not soap_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="SOAP note not found")

    # Fetch consultation to check authorization
    cons_res = await db.execute(select(Consultation).where(Consultation.uuid == soap_note.consultation_id))
    cons = cons_res.scalar_one_or_none()
    if cons and str(cons.doctor_id) != str(current_doctor.uuid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform this operation")

    soap_note.is_approved = True
    soap_note.approved_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(soap_note)
    return soap_note