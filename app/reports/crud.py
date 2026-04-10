from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.reports.models import Report
from app.reports.schemas import ReportCreate, ReportStatusUpdate, ReportUpdate
from app.reports.enums import ReportStatus


async def create_report(
    db: AsyncSession,
    data: ReportCreate,
    user_id: int,
) -> Report:
    report = Report(
        title = data.title,
        description = data.description,
        address = data.address,
        user_id = user_id,
        status = ReportStatus.REVIEW
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return report

async def get_report_by_id(
    db: AsyncSession,
    report_id: int
) -> Report | None:
    result = await db.execute(
        select(Report).where(Report.id == report_id)
    )
    return result.scalar_one_or_none()

async def get_reports(
    db: AsyncSession
) -> list[Report]:
    result = await db.execute(select(Report))
    return list(result.scalars().all())

async def update_report(
    db: AsyncSession,
    report: Report,
    data: ReportUpdate
) -> Report:
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(report, field, value)
        
    await db.commit()
    await db.refresh(report)
    
    return report

async def update_report_status(
    db: AsyncSession,
    report: Report,
    data: ReportStatusUpdate
) -> Report:
    report.status = data.status
    
    await db.commit()
    await db.refresh(report)
    
    return report

async def delete_report(
    db: AsyncSession,
    report: Report
) -> None:
    await db.delete(report)
    await db.commit()