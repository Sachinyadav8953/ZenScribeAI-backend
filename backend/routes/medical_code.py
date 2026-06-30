from fastapi import APIRouter,Depends,status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.user import User
from schemas.medical_code import  MedicalCodeResponse

from services.medical_code_services import generate_medical_codes
from utils.dependencies import get_current_doctor
router=APIRouter(prefix="/medical_code",tags=["MedicalCoding"])


@router.post("/{consultation_uuid}",
    status_code=status.HTTP_201_CREATED,
    response_model=MedicalCodeResponse)


async def create_medical_codes(
    consultation_uuid:str,
    db: AsyncSession = Depends(get_db),
    current_doctor : User = Depends(get_current_doctor)):
    return  generate_medical_codes(consultation_uuid,current_doctor,db)


@router.get()
