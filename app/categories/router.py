from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_admin
from app.db.database import get_db
from app.categories.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from app.categories import crud


router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.post("/", response_model=CategoryRead)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db), user = Depends(get_current_admin)):
    return await crud.create_category(db, data)

@router.get("/", response_model=list[CategoryRead])
async def get_categories(db: AsyncSession = Depends(get_db)):
    return await crud.get_categories(db)

@router.get("/{category_id}", response_model=CategoryRead)
async def get_category_by_id(category_id: int, db: AsyncSession = Depends(get_db)):
    category = await crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_admin)
):
    category = await crud.get_category_by_id(db, category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return await crud.update_category(db, category, data)

@router.delete("/{category_id}")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_admin)
):
    category = await crud.get_category_by_id(db, category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    await crud.delete_category(db, category)
    
