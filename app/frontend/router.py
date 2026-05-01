from fastapi import APIRouter, Depends, Form, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.auth.service import login_user
from app.comments.schemas import CommentCreate
from app.users.schemas import UserCreate
from app.db.database import get_db
from app.reports import crud as reports_crud
from app.comments import crud as comments_crud
from app.users import crud as users_crud
from app.auth.dependencies import get_current_user, get_current_user_optional
from fastapi.templating import Jinja2Templates


router = APIRouter()

templates = Jinja2Templates(directory="app/frontend/templates")

@router.get("/reports")
async def reports_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user_optional)
):
    print(templates.env.loader)
    
    reports = await reports_crud.get_reports_with_comment_count(db)
    
    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={
            "reports": reports,
            "user": user
        }
    )
    
@router.get("/reports/{report_id}")
async def report_detail(
    request: Request,
    report_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user_optional)
):
    report = await reports_crud.get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    comments = await comments_crud.get_comments_by_report(db, report_id)
    
    return templates.TemplateResponse(
        request=request,
        name="report.html",
        context={
            "report": report,
            "comments": comments,
            "user": user
        }
    )
    
@router.post("/reports/{report_id}/comments")
async def add_comment(
    request: Request,
    report_id: int,
    text: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    report = await reports_crud.get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    comment_data = CommentCreate(text=text)
    await comments_crud.create_comment(db, comment_data, user.id, report_id)
    
    return RedirectResponse(url=f"/reports/{report_id}", status_code=303)

@router.get("/login")
async def login_page(
    request: Request,
    user = Depends(get_current_user_optional)
):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"user": user}
    )
    
@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    token = await login_user(db, username, password)
    
    if not token:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Неверное имя пользователя или пароль"}
        )
        
    redirect = RedirectResponse(url="/reports", status_code=303)
        
    redirect.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60
    )
    
    return redirect

@router.get("/register")
async def register_page(
    request: Request,
    user = Depends(get_current_user_optional)
):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"user": user}
    )
    
@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)    
):
    existing_user = await users_crud.get_user_by_username(db, username)
    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Имя пользователя уже занято"}
        )
    
    user_data = UserCreate(username=username, password=password)
    
    user = await users_crud.create_user(db, user_data)
    
    token = create_access_token({
        "sub": str(user.id),
        "role": user.role.value
    })
    
    redirect = RedirectResponse(url="/reports", status_code=303)
    
    redirect.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60
    )
    
    return redirect

@router.get("/logout")
async def logout():
    redirect = RedirectResponse(url="/reports", status_code=303)
    redirect.delete_cookie("access_token")
    return redirect