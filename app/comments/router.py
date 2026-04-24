from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_user
from app.db.database import get_db
from app.comments.schemas import CommentCreate, CommentRead, CommentUpdate
from app.comments import crud

router = APIRouter(tags=["comments"])

@router.post("/{report_id}/comments", response_model=CommentRead)
async def create_comment(
    report_id: int,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    return await crud.create_comment(db, data, user.id, report_id)

@router.get("/{report_id}/comments", response_model=list[CommentRead])
async def get_comments(
    report_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await crud.get_comments_by_report(db, report_id)

@router.patch("/comments/{comment_id}", response_model=CommentRead)
async def update_comment(
    comment_id: int,
    data: CommentUpdate,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    comment = await crud.get_comment_by_id(db, comment_id)
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return await crud.update_comment(db, comment, data)
    

@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    comment = await crud.get_comment_by_id(db, comment_id)
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    await crud.delete_comment(db, comment)
    
