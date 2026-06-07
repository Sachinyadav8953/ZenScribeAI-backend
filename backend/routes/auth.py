from fastapi import APIRouter, Depends,status
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, UserResponse
from services.auth_services import register_user
from db.session import get_db

router=APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/register",status_code=status.HTTP_201_CREATED,response_model=UserResponse)


async def register(user_data:UserCreate,db:AsyncSession=Depends(get_db)):

    return await register_user(user_data,db)

