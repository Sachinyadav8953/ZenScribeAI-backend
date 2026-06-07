from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from models.user import User
from schemas.user import UserCreate
from utils.password import hash_password
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