from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.categories.models import Category
from app.categories.schemas import CategoryCreate, CategoryUpdate


async def create_category(
    db: AsyncSession,
    data: CategoryCreate
) -> Category:
    category = Category(
        name = data.name
    )
    
    db.add(category)
    await db.commit()
    await db.refresh(category)
    
    return category

async def get_category_by_id(
    db: AsyncSession,
    category_id: int
) -> Category | None:
    result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    return result.scalar_one_or_none()

async def get_categories(
    db: AsyncSession
) -> list[Category]:
    result = await db.execute(select(Category))
    return list(result.scalars().all())

async def update_category(
    db: AsyncSession,
    category: Category,
    data: CategoryUpdate
) -> Category:
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(category, field, value)
        
    await db.commit()
    await db.refresh(category)
    
    return category

async def delete_category(
    db: AsyncSession,
    category: Category
) -> None:
    await db.delete(category)
    await db.commit()