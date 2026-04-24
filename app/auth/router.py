from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.db.database import get_db
from app.auth.service import login_user
from app.users.schemas import UserCreate, UserLogin, UserRead
from app.users import crud

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead)
async def register(
    data: UserCreate,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    existing_user = await crud.get_user_by_username(db, data.username)
    
    if existing_user:
        raise HTTPException(400, "Username already taken")
    
    user = await crud.create_user(db, data)
    
    token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value
    })
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60
    )
    
    return user
    




@router.post("/login")
async def login(
    data: UserLogin,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    token = await login_user(db, data.username, data.password)
    
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60
    )
    
    return {"message": "login successful"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "logged out"}