from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate
from app.users.enums import UserRole


async def create_user(
    db: AsyncSession,
    data: UserCreate
) -> User:
    password_hash = hash_password(data.password)
    
    user = User(
        username = data.username,
        password_hash = password_hash,
        role = UserRole.USER
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user

async def get_user_by_id(
    db: AsyncSession,
    user_id: int
) -> User | None:
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

async def get_users(
    db: AsyncSession
) -> list[User]:
    result = await db.execute(select(User))
    return list(result.scalars().all())

async def get_user_by_username(
    db: AsyncSession,
    username: str
) -> User | None:
    result = await db.execute(
        select(User).where(User.username == username)
    )
    return result.scalar_one_or_none()

async def update_user(
    db: AsyncSession,
    user: User,
    data: UserUpdate
) -> User:
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(user, field, value)
        
    await db.commit()
    await db.refresh(user)
    
    return user

async def update_user_password(
    db: AsyncSession,
    user: User,
    new_password_hash: str
):
    user.password_hash = new_password_hash
    
    await db.commit()
    await db.refresh(user)
    
    return user

async def delete_user(
    db: AsyncSession,
    user: User
) -> None:
    await db.delete(user)
    await db.commit()