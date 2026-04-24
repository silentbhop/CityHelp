from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.reports.router import router as reports_router
from app.comments.router import router as comments_router
from app.categories.router import router as categories_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(reports_router)
app.include_router(comments_router)
app.include_router(categories_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}