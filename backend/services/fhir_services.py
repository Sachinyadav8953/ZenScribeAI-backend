import base64
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from models.consultation import Consultation
from models.soap_note import SoapNote
from models.medical_code import MedicalCode
from models.user import User
from models.fhir_record import FHIRRecord
from utils.fhir_clients import fhir_client

logger = logging.getLogger("doctor_zenz.fhir")


def build_patient_resource(consultation: Consultation) -> dict:
    # converts your patient fields into FHIR Patient resource
    resource = {
        "resourceType": "Patient",
        "name": [{"text": consultation.patient_name}],
    }

    if consultation.patient_gender:
        # FHIR expects lowercase: male, female, other
        resource["gender"] = consultation.patient_gender.value

    if consultation.patient_phone:
        resource["telecom"] = [{
            "system": "phone",
            "value" : consultation.patient_phone
        }]

    return resource


def build_practitioner_resource(doctor: User) -> dict:
    # converts your doctor User into FHIR Practitioner resource
    return {
        "resourceType": "Practitioner",
        "name": [{"text": doctor.full_name}],
        "telecom": [{
            "system": "email",
            "value" : doctor.email
        }]
    }


def build_encounter_resource(
    consultation: Consultation,
    patient_fhir_id: str,
    practitioner_fhir_id: str
) -> dict:
    return {
        "resourceType": "Encounter",
        "status": "finished",       
        "class": {
            "system" : "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code"   : "AMB",        
            "display": "ambulatory"
        },
        "subject": {
            "reference": f"Patient/{patient_fhir_id}"
        },
        "participant": [{
            "individual": {
                "reference": f"Practitioner/{practitioner_fhir_id}"
            }
        }],
        "reasonCode": [{
            "text": consultation.chief_complaint or "Not specified"
        }],
        "period": {
            "start": consultation.started_at.isoformat(),
            "end"  : consultation.ended_at.isoformat() if consultation.ended_at else None
        }
    }


def build_condition_resources(
    medical_codes: list[MedicalCode],
    patient_fhir_id: str,
    encounter_fhir_id: str
) -> list[dict]:
    
    conditions = []

    for code in medical_codes:
        if not code.is_selected:
            continue   

        conditions.append({
            "resourceType": "Condition",
            "code": {
                "coding": [{
                    "system" : "http://hl7.org/fhir/sid/icd-10-cm",
                    "code"   : code.code,
                    "display": code.description
                }],
                "text": code.description
            },
            "subject": {
                "reference": f"Patient/{patient_fhir_id}"
            },
            "encounter": {
                "reference": f"Encounter/{encounter_fhir_id}"
            },
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code"  : "active"
                }]
            }
        })

    return conditions


def build_document_reference(
    soap_note: SoapNote,
    patient_fhir_id: str,
    encounter_fhir_id: str
) -> dict:
    

    soap_text = f"""
SUBJECTIVE:
{soap_note.subjective}

OBJECTIVE:
{soap_note.objective}

ASSESSMENT:
{soap_note.assessment}

PLAN:
{soap_note.plan}
"""

    encoded_content = base64.b64encode(soap_text.encode("utf-8")).decode("utf-8")

    return {
        "resourceType": "DocumentReference",
        "status": "current",
        "type": {
            "coding": [{
                "system" : "http://loinc.org",
                "code"   : "11506-3",         
                "display": "Progress note"
            }]
        },
        "subject": {
            "reference": f"Patient/{patient_fhir_id}"
        },
        "context": {
            "encounter": [{
                "reference": f"Encounter/{encounter_fhir_id}"
            }]
        },
        "content": [{
            "attachment": {
                "contentType": "text/plain",
                "data"       : encoded_content
            }
        }]
    }


async def sync_consultation_to_fhir(
    consultation_uuid: str,
    current_doctor: User,
    db: AsyncSession
) -> FHIRRecord:

    result = await db.execute(
        select(Consultation).where(Consultation.uuid == consultation_uuid)
    )
    consultation = result.scalar_one_or_none()

    if not consultation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consultation not found")

    if str(consultation.doctor_id) != str(current_doctor.uuid):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    existing = await db.execute(
        select(FHIRRecord).where(FHIRRecord.consultation_id == consultation.uuid)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already synced to FHIR")

    soap_result = await db.execute(
        select(SoapNote).where(SoapNote.consultation_id == consultation.uuid)
    )
    soap_note = soap_result.scalar_one_or_none()

    if not soap_note or not soap_note.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SOAP note must be generated and approved first"
        )

    codes_result = await db.execute(
        select(MedicalCode).where(MedicalCode.consultation_id == consultation.uuid)
    )
    medical_codes = list(codes_result.scalars().all())

    try:
#create Patient on FHIR server
        patient_payload  = build_patient_resource(consultation)
        patient_response = await fhir_client.create_resource("Patient", patient_payload)
        patient_fhir_id   = patient_response["id"]

        # create Practitioner on FHIR server
        practitioner_payload  = build_practitioner_resource(current_doctor)
        practitioner_response = await fhir_client.create_resource("Practitioner", practitioner_payload)
        practitioner_fhir_id   = practitioner_response["id"]

        #create Encounter on FHIR server 
        encounter_payload  = build_encounter_resource(consultation, patient_fhir_id, practitioner_fhir_id)
        encounter_response = await fhir_client.create_resource("Encounter", encounter_payload)
        encounter_fhir_id   = encounter_response["id"]

        #create Condition resources for each selected code 
        condition_payloads = build_condition_resources(medical_codes, patient_fhir_id, encounter_fhir_id)
        for payload in condition_payloads:
            await fhir_client.create_resource("Condition", payload)

        #create DocumentReference for SOAP note 
        document_payload  = build_document_reference(soap_note, patient_fhir_id, encounter_fhir_id)
        document_response = await fhir_client.create_resource("DocumentReference", document_payload)
        document_fhir_id   = document_response["id"]

    except Exception as e:
        logger.error(f"FHIR sync failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to sync with FHIR server"
        )

    #save FHIR IDs to our database
    fhir_record = FHIRRecord(
        consultation_id      = consultation.uuid,
        fhir_patient_id      = patient_fhir_id,
        fhir_practitioner_id = practitioner_fhir_id,
        fhir_encounter_id    = encounter_fhir_id,
        fhir_document_id     = document_fhir_id,
    )
    db.add(fhir_record)
    await db.commit()
    await db.refresh(fhir_record)

    logger.info(f"Consultation {consultation_uuid} synced to FHIR successfully")
    return fhir_record


async def get_fhir_record(
    consultation_uuid: str,
    current_doctor: User,
    db: AsyncSession
) -> FHIRRecord:

    result = await db.execute(
        select(FHIRRecord).where(FHIRRecord.consultation_id == consultation_uuid)
    )
    fhir_record = result.scalar_one_or_none()

    if not fhir_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not synced to FHIR yet")

    return fhir_record