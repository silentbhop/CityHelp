from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.comments.models import Comment
from app.comments.schemas import CommentCreate, CommentUpdate


async def create_comment(
    db: AsyncSession,
    data: CommentCreate,
    user_id: int,
    report_id: int
) -> Comment:
    comment = Comment(
        text = data.text,
        report_id = report_id,
        user_id = user_id
    )
    
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    
    return comment

async def get_comment_by_id(
    db: AsyncSession,
    comment_id: int
) -> Comment | None:
    result = await db.execute(
        select(Comment).where(Comment.id == comment_id)
    )
    return result.scalar_one_or_none()

async def get_comments(
    db: AsyncSession
) -> list[Comment]:
    result = await db.execute(select(Comment))
    return list(result.scalars().all())

async def get_comments_by_report(
    db: AsyncSession,
    report_id: int
) -> list[Comment]:
    result = await db.execute(
        select(Comment)
        .options(joinedload(Comment.users))
        .where(Comment.report_id == report_id)
        .order_by(Comment.created_at.asc())
    )
    return list(result.scalars().all())


async def update_comment(
    db: AsyncSession,
    comment: Comment,
    data: CommentUpdate
) -> Comment:
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(comment, field, value)
        
    await db.commit()
    await db.refresh(comment)
    
    return comment

async def delete_comment(
    db: AsyncSession,
    comment: Comment
) -> None:
    await db.delete(comment)
    await db.commit()