from fastapi import APIRouter, Depends,status,Request,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import UserCreate, UserResponse,UserLogin,TokenResponse
from services.auth_services import register_user,login_user
from db.session import get_db
from schemas.user import ForgotPasswordRequest, ResetPasswordRequest
from services.auth_services import forgot_password, reset_password
from fastapi.security import OAuth2PasswordRequestForm

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