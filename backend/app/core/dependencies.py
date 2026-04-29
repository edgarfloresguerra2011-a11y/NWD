from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.plan_tier not in ("enterprise", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador",
        )
    return current_user
