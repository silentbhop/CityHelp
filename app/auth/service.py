from app.users import crud
from app.core.security import verify_password
from app.auth.jwt import create_access_token


async def authenticate_user(db, username: str, password: str):
    user = await crud.get_user_by_username(db, username)
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user



async def login_user(db, username: str, password: str):
    user = await authenticate_user(db, username, password)
    
    if not user:
        return None

    token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value
    })
    
    return token