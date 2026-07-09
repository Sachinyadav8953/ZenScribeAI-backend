from datetime import datetime, timezone,timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status
from models.user import User
from schemas.user import UserCreate,UserLogin,TokenResponse,ResetPasswordRequest,RefreshTokenRequest
from utils.password import hash_password,verify_password
from utils.token import create_access_token,create_refresh_token
from utils.email import send_reset_password_email,send_verification_email
from utils.token import decode_token
import secrets
from config import settings
from jose import JWTError
from fastapi import Request


#Sign Up
async def register_user(user_data:UserCreate, db: AsyncSession)->User:
    result=await db.execute(select(User).where(User.email==user_data.email))
    existing_user=result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exit with this email,Please try with another email !")

    hashedPassword=hash_password(user_data.password)
    verification_token = secrets.token_urlsafe(32)
    token_expiry = datetime.now(timezone.utc) + timedelta(
        hours=settings.EMAIL_VERIFY_EXPIRE_HOURS
    )

    new_user=User(
        full_name        = user_data.full_name,
        email            = user_data.email,
        hashed_password  = hashedPassword,
        role             = user_data.role,
        specialization   = user_data.specialization,
        license_number   = user_data.license_number,
        hospital_name    = user_data.hospital_name,
        phone_number     = user_data.phone_number, 
        is_email_verified          = False,
        email_verification_token   = verification_token,
        email_verification_expires = token_expiry,
    )
    

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    await send_verification_email(new_user.email, verification_token)
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

#Logged out

async def logged_out(current_user:User,db:AsyncSession,request:Request)->dict:
    
    current_user.last_login=datetime.now(timezone.utc)
    current_user.last_login_ip=request.client.host if request.client else None
    current_user.last_login_device=request.headers.get("User-Agent",None)
    await db.commit()
    return {"message":"User logged out successfully"}


#forget Password

async def forgot_password(email: str, db: AsyncSession) -> dict:
    result =await db.execute(select(User).where(User.email==email))
    user=result.scalar_one_or_none()
    if not user:
        return {"message": "If this email exists you will receive a reset link"}
    
    reset_token = secrets.token_urlsafe(32)
    user.reset_password_token   = reset_token
    user.reset_password_expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.EMAIL_RESET_EXPIRE_MINUTES
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
    



async def verify_email(token: str, db: AsyncSession) -> dict:

    result = await db.execute(
        select(User).where(User.email_verification_token == token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )

    if user.is_email_verified:
        return {"message": "Email already verified. Please login."}

    if user.email_verification_expires is None or datetime.now(timezone.utc) > user.email_verification_expires:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token expired. Please register again or request a new link."
        )

    user.is_email_verified          = True
    user.email_verification_token   = None      
    user.email_verification_expires = None

    await db.commit()

    return {"message": "Email verified successfully. You can now login."}



async def refresh_token_service(refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type — must be refresh token"
            )

        new_access_token = create_access_token(payload)

        return TokenResponse(
            access_token  = new_access_token,
            refresh_token = refresh_token,     
            token_type    = "bearer",
            expires_in    = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or expired"
        )
    except HTTPException:
        raise                   
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    


    
    
