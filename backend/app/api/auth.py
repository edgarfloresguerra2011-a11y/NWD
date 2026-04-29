from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate
from app.core.security import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email ya registrado")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        company=data.company,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_me(data: UserUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if data.full_name is not None:
        current_user.full_name = data.full_name
    if data.company is not None:
        current_user.company = data.company
    await db.commit()
    await db.refresh(current_user)
    return UserResponse.model_validate(current_user)
