from fastapi import Depends, HTTPException, Request
from app.auth.jwt import decode_token
from sqlalchemy.ext.asyncio import AsyncSession
from app.users import crud
from app.db.database import get_db
from app.users.enums import UserRole
from app.users.models import User


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    sub = payload.get("sub")
    
    if sub is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    try:
        user_id = int(sub)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user id")
    
    user = await crud.get_user_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

async def get_current_admin(
    user: User = Depends(get_current_user)
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user