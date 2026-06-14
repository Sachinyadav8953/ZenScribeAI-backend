# routes/consultation.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.user import User
from schemas.consultation import ConsultationCreate, ConsultationResponse,ConsultationUpdate
from services.consultation_services import start_consultation,update_consultation
from utils.dependencies import get_current_doctor




router = APIRouter(prefix="/consultations", tags=["Consultations"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ConsultationResponse
)
async def create_consultation(
    data: ConsultationCreate,
    db: AsyncSession = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)  
):
    return await start_consultation(data, current_doctor, db)







@router.patch(
    "/{consultation_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=ConsultationResponse
)
async def update_consultation_route(
    consultation_uuid: str,
    data: ConsultationUpdate,
    db: AsyncSession = Depends(get_db),
    current_doctor: User = Depends(get_current_doctor)
):
    return await update_consultation(consultation_uuid, data, current_doctor, db)