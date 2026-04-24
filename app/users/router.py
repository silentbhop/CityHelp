from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.db.database import get_db
from app.users.schemas import PasswordUpdate, UserCreate, UserRead, UserUpdate
from app.users import crud
from app.core.security import verify_password, hash_password

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserRead)
async def get_me(user = Depends(get_current_user)):
    return user

@router.patch("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    return await crud.update_user(db, user, data)

@router.patch("/me/password")
async def change_password(
    data: PasswordUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    if not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    new_password_hash = hash_password(data.new_password)
    
    return await crud.update_user_password(db, user, new_password_hash)