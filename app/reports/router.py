from fastapi import APIRouter, Depends, HTTPException
from app.comments.router import router as comments_router
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.dependencies import get_current_admin, get_current_user
from app.db.database import get_db
from app.reports.schemas import ReportCreate, ReportRead, ReportUpdate, ReportStatusUpdate
from app.reports import crud


router = APIRouter(prefix="/api/reports", tags=["reports"])
router.include_router(comments_router)

@router.post("/", response_model=ReportRead)
async def create_report(
    data: ReportCreate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    return await crud.create_report(db, data, user.id)

@router.get("/", response_model=list[ReportRead])
async def get_reports(db: AsyncSession = Depends(get_db)):
    return await crud.get_reports(db)

@router.get("/{report_id}", response_model=ReportRead)
async def get_report_by_id(report_id: int, db: AsyncSession = Depends(get_db)):
    report =  await crud.get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.patch("/{report_id}", response_model=ReportRead)
async def update_report(
    report_id: int,
    data: ReportUpdate,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    report = await crud.get_report_by_id(db, report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if report.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    return await crud.update_report(db, report, data)

@router.patch("/{report_id}/status", response_model=ReportRead)
async def update_report_status(
    report_id: int,
    data: ReportStatusUpdate,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_admin)
):
    report = await crud.get_report_by_id(db, report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")    
    return await crud.update_report_status(db, report, data)

@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    report = await crud.get_report_by_id(db, report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    await crud.delete_report(db, report)
