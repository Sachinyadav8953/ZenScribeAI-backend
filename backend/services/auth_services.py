from datetime import datetime, timezone,timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from models.user import User
from schemas.user import UserCreate,UserLogin,TokenResponse,ResetPasswordRequest
from utils.password import hash_password,verify_password
from utils.token import create_access_token,create_refresh_token
from utils.email import send_reset_password_email
import secrets
from config import settings
#Sign Up
async def register_user(user_data:UserCreate, db: AsyncSession)->User:
    result=await db.execute(select(User).where(User.email==user_data.email))
    existing_user=result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exit with this email,Please try with another email !")

    hashedPassword=hash_password(user_data.password)


    new_user=User(
        full_name        = user_data.full_name,
        email            = user_data.email,
        hashed_password  = hashedPassword,
        role             = user_data.role,
        specialization   = user_data.specialization,
        license_number   = user_data.license_number,
        hospital_name    = user_data.hospital_name,
        phone_number     = user_data.phone_number, 
    )
    

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


#Sign In
async def login_user(
    user_data: UserLogin,
    db: AsyncSession,
    request_ip: str | None = None,
    request_device: str | None = None 
) -> TokenResponse:

    result =await db.execute(select(User).where(User.email==user_data.email))
    user=result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Credentials")
    if not verify_password(user_data.password,user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Credentials")

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Contact support."
        )
    

    if user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account no longer exists."
        )
    

    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in."
        )
    token_data = {
            "user_id" : user.id,
            "uuid"    : str(user.uuid),
            "email"   : user.email,
            "role"    : user.role
        }

    access_token  = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)


    user.last_login        = datetime.now(timezone.utc)
    user.last_login_ip     = request_ip
    user.last_login_device = request_device


    await db.commit()


    return TokenResponse(
        access_token  = access_token,
        refresh_token = refresh_token,
        token_type    = "bearer"
    )


#forget Password

async def forgot_password(email: str, db: AsyncSession) -> dict:
    result =await db.execute(select(User).where(User.email==email))
    user=result.scalar_one_or_none()
    if not user:
        return {"message": "If this email exists you will receive a reset link"}
    
    reset_token = secrets.token_urlsafe(32)
    user.reset_password_token   = reset_token
    user.reset_password_expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES
    )
    await db.commit()
    await send_reset_password_email(user.email,reset_token)
    return {"message": "If this email exists you will receive a reset link"}


async def reset_password(reset_data: ResetPasswordRequest, db: AsyncSession) -> dict:
    result =await db.execute(select(User).where(User.reset_password_token==reset_data.token))
    user=result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid or expired reset token")
    
    if user.reset_password_expires is None or datetime.now(timezone.utc) > user.reset_password_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired. Please request a new one."
        ) 

    user.hashed_password = hash_password(reset_data.new_password)

   
    user.reset_password_token   = None
    user.reset_password_expires = None

    await db.commit()
    return {"message":"Your password has been reset please login again"}        
    
