from fastapi import APIRouter, Depends,status,Request,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.user import UserCreate, UserResponse,UserLogin,TokenResponse
from services.auth_services import register_user,login_user
from db.session import get_db
from schemas.user import ForgotPasswordRequest, ResetPasswordRequest
from services.auth_services import forgot_password, reset_password,verify_email
from fastapi.security import OAuth2PasswordRequestForm
from models.user import User
from config import settings
from datetime import datetime,timezone,timedelta
from utils.email import send_verification_email
import secrets

router=APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/register",status_code=status.HTTP_201_CREATED,response_model=UserResponse)


async def register(user_data:UserCreate,db:AsyncSession=Depends(get_db)):

    return await register_user(user_data,db)


@router.post("/token", response_model=TokenResponse)
async def swagger_login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    ip = request.client.host if request.client else None
    device = request.headers.get("user-agent")

    user_data = UserLogin(
        email=form_data.username,
        password=form_data.password,
    )

    return await login_user(user_data, db, ip, device)
@router.post("/login",status_code=status.HTTP_200_OK,response_model=TokenResponse)


async def login(user_data:UserLogin,request: Request,db:AsyncSession=Depends(get_db)):
    ip     = request.client.host if request.client else None
    device = request.headers.get("user-agent")
    if not ip and not device:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Request"    )
    return await login_user(user_data,db,ip,device  )



@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password_route(
    request_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    return await forgot_password(request_data.email, db)


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_route(
    request_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    return await reset_password(request_data, db) 






@router.get("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email_route(
    token: str,                         
    db: AsyncSession = Depends(get_db)
):
    return await verify_email(token, db)


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification(
    request_data: ForgotPasswordRequest,    
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.email == request_data.email)
    )
    user = result.scalar_one_or_none()

    if not user or user.is_email_verified:
        return {"message": "If this email exists and is unverified you will receive a new link"}

    new_token = secrets.token_urlsafe(32)
    user.email_verification_token   = new_token
    user.email_verification_expires = datetime.now(timezone.utc) + timedelta(
        hours=settings.EMAIL_VERIFY_EXPIRE_HOURS
    )
    await db.commit()

    await send_verification_email(user.email, new_token)
    return {"message": "If this email exists and is unverified you will receive a new link"}