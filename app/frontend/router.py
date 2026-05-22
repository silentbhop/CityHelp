from math import ceil

from fastapi import APIRouter, Depends, Form, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token
from app.auth.service import login_user
from app.categories.schemas import CategoryCreate, CategoryUpdate
from app.comments.schemas import CommentCreate
from app.core.security import hash_password, verify_password
from app.reports.enums import ReportStatus
from app.reports.schemas import ReportCreate, ReportStatusUpdate
from app.users.enums import UserRole
from app.users.schemas import UserCreate
from app.db.database import get_db
from app.reports import crud as reports_crud
from app.comments import crud as comments_crud
from app.categories import crud as categories_crud
from app.users import crud as users_crud
from app.auth.dependencies import get_current_admin, get_current_user, get_current_user_optional
from fastapi.templating import Jinja2Templates


router = APIRouter()

templates = Jinja2Templates(directory="app/frontend/templates")

PER_PAGE = 4

@router.get("/")
async def home(
    request: Request,
    user = Depends(get_current_user_optional)
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"user": user}
    )

@router.get("/reports")
async def reports_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user_optional),
    search: str = "",
    status: str = "",
    category_id: int = 0,
    page: int = 1
):
    categories = await categories_crud.get_categories(db)
    
    reports, total = await reports_crud.get_reports_with_comment_count(
        db,
        search=search or None,
        status=status or None,
        category_id=category_id or None,
        is_admin=user is not None and user.role.value == "admin",
        page=page,
        per_page=PER_PAGE,
    )
    
    total_pages = ceil(total / PER_PAGE) if total else 1
    
    qs_parts = []
    if search:
        qs_parts.append(f"search={search}")
    if status:
        qs_parts.append(f"status={status}")
    if category_id:
        qs_parts.append(f"category_id={category_id}")
    qs = "&".join(qs_parts)
    
    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={
            "reports": reports,
            "user": user,
            "categories": categories,
            "statuses": ReportStatus,
            "search": search,
            "status": status,
            "category_id": category_id,
            "page": page,
            "total_pages": total_pages,
            "total": total,
            "qs": qs,
        },
    )
    
@router.get("/reports/my")
async def my_reports(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
    search: str = "",
    status: str = "",
    category_id: int = 0,
    page: int = 1
):
    categories = await categories_crud.get_categories(db)
    
    reports, total = await reports_crud.get_reports_with_comment_count(
        db,
        search=search or None,
        status=status or None,
        category_id=category_id or None,
        user_id = user.id,
        is_admin=user is not None and user.role.value == "admin",
        page=page,
        per_page=PER_PAGE,
    )
    
    total_pages = ceil(total / PER_PAGE) if total else 1
    
    return templates.TemplateResponse(
        request=request,
        name="my_reports.html",
        context={
            "reports": reports,
            "user": user,
            "categories": categories,
            "statuses": ReportStatus,
            "search": search,
            "status": status,
            "category_id": category_id,
            "page": page,
            "total_pages": total_pages,
            "total": total,
        },
    )


@router.get("/reports/create")
async def create_report_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user_optional)
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    
    categories = await categories_crud.get_categories(db)
    
    return templates.TemplateResponse(
        request=request,
        name="create_report.html",
        context={
            "user": user,
            "categories": categories
        }
    )
    
@router.post("/reports/create")
async def create_report(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    address: str = Form(...),
    category_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user_optional)
):
    if not user:
        return RedirectResponse("/login", status_code=303)
    
    errors = []
    
    if len(title) < 3 or len(title) > 100:
        errors.append("Заголовок должен быть от 3 до 100 символов")
    if len(description) < 5 or len(description) > 1500:
        errors.append("Описание должно быть от 5 до 1500 символов")
    if len(address) < 5 or len(address) > 255:
        errors.append("Адрес должен быть от 5 до 255 символов")
        
    category = await categories_crud.get_category_by_id(db, category_id)
    if not category:
        errors.append("Выбранная категория не существует")
    
    if errors:
        categories = await categories_crud.get_categories(db)
        return templates.TemplateResponse(
            request=request,
            name="create_report.html",
            context={
                "user": user,
                "categories": categories,
                "errors": errors,
                "form": {
                    "title": title,
                    "description": description,
                    "address": address,
                    "category_id": category_id
                }
            }
        )
        
    report_data = ReportCreate(
        title=title,
        description=description,
        address = address,
        category_id=category_id
    )
    
    report = await reports_crud.create_report(db, report_data, user.id)
    
    return RedirectResponse(url=f"/reports/{report.id}", status_code=303)

@router.get("/reports/{report_id}/edit")
async def edit_report_page(
    request: Request,
    report_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    report = await reports_crud.get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.user_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    categories = await categories_crud.get_categories(db)

    return templates.TemplateResponse(
        request=request,
        name="edit_report.html",
        context={
            "user": user,
            "report": report,
            "categories": categories,
        }
    )


@router.post("/reports/{report_id}/edit")
async def edit_report(
    request: Request,
    report_id: int,
    title: str = Form(...),
    description: str = Form(...),
    address: str = Form(...),
    category_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    report = await reports_crud.get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.user_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    errors = []

    if len(title) < 3 or len(title) > 100:
        errors.append("Заголовок должен быть от 3 до 100 символов")
    if len(description) < 5 or len(description) > 1500:
        errors.append("Описание должно быть от 5 до 1500 символов")
    if len(address) < 5 or len(address) > 255:
        errors.append("Адрес должен быть от 5 до 255 символов")

    category = await categories_crud.get_category_by_id(db, category_id)
    if not category:
        errors.append("Выбранная категория не существует")

    if errors:
        categories = await categories_crud.get_categories(db)
        return templates.TemplateResponse(
            request=request,
            name="edit_report.html",
            context={
                "user": user,
                "report": report,
                "categories": categories,
                "errors": errors,
                "form": {
                    "title": title,
                    "description": description,
                    "address": address,
                    "category_id": category_id,
                }
            }
        )

    from app.reports.schemas import ReportUpdate
    update_data = ReportUpdate(
        title=title,
        description=description,
        address=address,
        category_id=category_id,
    )
    await reports_crud.update_report(db, report, update_data)

    return RedirectResponse(url=f"/reports/{report_id}", status_code=303)


@router.post("/reports/{report_id}/delete")
async def delete_report(
    report_id: int,
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user)
):
    report = await reports_crud.get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    if report.user_id != user.id and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    await reports_crud.delete_report(db, report)

    return RedirectResponse(url="/reports/my", status_code=303)
    
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
    token, error = await login_user(db, username, password)
    
    if error == "blocked":
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Ваш аккаунт заблокирован"}
        )
    
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


@router.get("/profile")
async def profile_page(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse(
        request=request, name="profile.html", context={"user": user}
    )
    
@router.post("/profile/username")
async def update_username(
    request: Request,
    username: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    existing = await users_crud.get_user_by_username(db, username)
    if existing and existing.id != user.id:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={"user": user, "username_error": "Это имя уже занято"},
        )

    from app.users.schemas import UserUpdate
    await users_crud.update_username(db, user, UserUpdate(username=username))
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"user": user, "username_success": "Имя пользователя обновлено"},
    )    

@router.post("/profile/password")
async def update_password(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
):
    if not verify_password(old_password, user.password_hash):
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={"user": user, "password_error": "Неверный текущий пароль"},
        )

    if len(new_password) < 6:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={"user": user, "password_error": "Пароль должен быть не менее 6 символов"},
        )

    new_hash = hash_password(new_password)
    await users_crud.update_user_password(db, user, new_hash)
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={"user": user, "password_success": "Пароль успешно изменён"},
    )
    
@router.get("/admin")
async def admin_panel(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_admin),
    tab: str = "reports",
    status_filter: str = "",
    page: int = 1,
):
    reports = []
    total_pages = 1
    users = []
    categories = []

    if tab == "reports":
        reports, total = await reports_crud.get_reports_with_comment_count(
            db,
            status=status_filter or None,
            page=page,
            per_page=20,
            is_admin=True,
        )
        total_pages = ceil(total / 20) if total else 1

    elif tab == "users":
        users = await users_crud.get_users(db)
        
    elif tab == "categories":
        categories = await categories_crud.get_categories(db)

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "user": user,
            "tab": tab,
            "reports": reports,
            "users": users,
            "categories": categories,
            "statuses": ReportStatus,
            "status_filter": status_filter,
            "page": page,
            "total_pages": total_pages,
        },
    )
    
@router.post("/admin/reports/{report_id}/status")
async def admin_update_status(
    report_id: int,
    new_status: str = Form(...),
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_admin),
):
    report = await reports_crud.get_report_by_id(db, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Not found")

    status_data = ReportStatusUpdate(status=ReportStatus(new_status))
    await reports_crud.update_report_status(db, report, status_data)
    return RedirectResponse(url="/admin?tab=reports", status_code=303)

@router.post("/admin/users/{user_id}/block")
async def admin_block_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    target = await users_crud.get_user_by_id(db, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot block yourself")
    await users_crud.block_user(db, target)
    return RedirectResponse(url="/admin?tab=users", status_code=303)

@router.post("/admin/users/{user_id}/unblock")
async def admin_unblock_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    target = await users_crud.get_user_by_id(db, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    await users_crud.unblock_user(db, target)
    return RedirectResponse(url="/admin?tab=users", status_code=303)

@router.post("/admin/categories/create")
async def admin_create_category(
    request: Request,
    name: str = Form(...),
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    name = name.strip()

    if len(name) < 3 or len(name) > 50:
        categories = await categories_crud.get_categories(db)
        return templates.TemplateResponse(
            request=request,
            name="admin.html",
            context={
                "user": admin,
                "tab": "categories",
                "reports": [],
                "users": [],
                "categories": categories,
                "statuses": ReportStatus,
                "status_filter": "",
                "page": 1,
                "total_pages": 1,
                "category_error": "Название должно быть от 3 до 50 символов",
                "form_name": name,
            },
        )


    existing = await categories_crud.get_categories(db)
    if any(c.name.lower() == name.lower() for c in existing):
        return templates.TemplateResponse(
            request=request,
            name="admin.html",
            context={
                "user": admin,
                "tab": "categories",
                "reports": [],
                "users": [],
                "categories": existing,
                "statuses": ReportStatus,
                "status_filter": "",
                "page": 1,
                "total_pages": 1,
                "category_error": "Категория с таким названием уже существует",
                "form_name": name,
            },
        )

    await categories_crud.create_category(db, CategoryCreate(name=name))
    return RedirectResponse(url="/admin?tab=categories", status_code=303)


@router.post("/admin/categories/{category_id}/update")
async def admin_update_category(
    category_id: int,
    name: str = Form(...),
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    category = await categories_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await categories_crud.update_category(db, category, CategoryUpdate(name=name.strip()))
    return RedirectResponse(url="/admin?tab=categories", status_code=303)


@router.post("/admin/categories/{category_id}/delete")
async def admin_delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    admin=Depends(get_current_admin),
):
    category = await categories_crud.get_category_by_id(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await categories_crud.delete_category(db, category)
    return RedirectResponse(url="/admin?tab=categories", status_code=303)
