from fastapi import APIRouter,Depends,status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.user import User
from schemas.medical_code import  MedicalCodeResponse,MedicalCodeSelect

from services.medical_code_services import generate_medical_codes,get_medical_codes,select_medical_code
from utils.dependencies import get_current_doctor
router=APIRouter(prefix="/coding",tags=["MedicalCoding"])


@router.post("/{consultation_uuid}/generate",
    status_code=status.HTTP_201_CREATED,
    response_model=list[MedicalCodeResponse])


async def create_medical_codes(
    consultation_uuid:str,
    db: AsyncSession = Depends(get_db),
    current_doctor : User = Depends(get_current_doctor)):
    return  await generate_medical_codes(consultation_uuid,current_doctor,db)


@router.get("/{consultation_uuid}",status_code=status.HTTP_200_OK,response_model=list[MedicalCodeResponse])


async def get_medical_code (consultation_uuid:str,db:AsyncSession=Depends(get_db),current_doctor:User=Depends(get_current_doctor)):
    return await get_medical_codes(consultation_uuid,current_doctor,db)


@router.patch("/{code_uuid}/select",status_code=status.HTTP_200_OK,response_model=MedicalCodeResponse)


async def select_code(code_uuid:str,data:MedicalCodeSelect,db:AsyncSession=Depends(get_db),current_doctor:User=Depends(get_current_doctor)):
    return await select_medical_code(code_uuid,data,current_doctor,db)
