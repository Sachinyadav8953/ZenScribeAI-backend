from fastapi import APIRouter, Depends,status,Request,HTTPException,Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas.user import UserCreate, UserResponse,UserLogin,TokenResponse,RefreshTokenRequest
from services.auth_services import register_user,login_user,refresh_token_service
from db.session import get_db
from schemas.user import ResetPasswordRequest
from services.auth_services import reset_password, logged_out

from models.user import User
from config import settings
from datetime import datetime,timezone,timedelta
# from utils.email import send_verification_email  # COMMENTED OUT — email disabled
from utils.dependencies import get_current_doctor
import secrets

router=APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/register",status_code=status.HTTP_201_CREATED,response_model=UserResponse)
async def register(user_data:UserCreate,db:AsyncSession=Depends(get_db)):
    try:
        return await register_user(user_data,db)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@router.get("/me",response_model=UserResponse)
async def get_profile(current_doctor:User=Depends(get_current_doctor)):
    return current_doctor


@router.post("/login",status_code=status.HTTP_200_OK,response_model=TokenResponse)
async def login(user_data:UserLogin,request: Request,db:AsyncSession=Depends(get_db)):
    ip     = request.client.host if request.client else "127.0.0.1"
    device = request.headers.get("user-agent") or "Unknown Device"
    try:
        return await login_user(user_data,db,ip,device)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Login error: {str(e)}")


@router.post("/logout",status_code=status.HTTP_200_OK)
async def log_out(request:Request,current_doctor:User=Depends(get_current_doctor),db:AsyncSession=Depends(get_db)):
    return await logged_out(current_doctor,db,request)


# COMMENTED OUT — email-based forgot password
# @router.post("/forgot-password", status_code=status.HTTP_200_OK)
# async def forgot_password_route(
#     request_data: ForgotPasswordRequest,
#     db: AsyncSession = Depends(get_db)
# ):
#     return await forgot_password(request_data.email, db)


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password_route(
    request_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    return await reset_password(request_data, db) 


# COMMENTED OUT — email verification endpoints
# @router.get("/verify-email", status_code=status.HTTP_200_OK)
# async def verify_email_route(
#     token: str,                         
#     db: AsyncSession = Depends(get_db)
# ):
#     return await verify_email(token, db)


# @router.post("/resend-verification", status_code=status.HTTP_200_OK)
# async def resend_verification(
#     request_data: ForgotPasswordRequest,    
#     db: AsyncSession = Depends(get_db)
# ):
#     result = await db.execute(
#         select(User).where(User.email == request_data.email)
#     )
#     user = result.scalar_one_or_none()
#     if not user or user.is_email_verified:
#         return {"message": "If this email exists and is unverified you will receive a new link"}
#     new_token = secrets.token_urlsafe(32)
#     user.email_verification_token   = new_token
#     user.email_verification_expires = datetime.now(timezone.utc) + timedelta(
#         hours=settings.EMAIL_VERIFY_EXPIRE_HOURS
#     )
#     await db.commit()
#     await send_verification_email(user.email, new_token)
#     return {"message": "If this email exists and is unverified you will receive a new link"}


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse
)
async def refresh_token(request_data: RefreshTokenRequest):
    return await refresh_token_service(request_data.refresh_token)