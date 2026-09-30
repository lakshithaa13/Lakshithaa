import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import init_db, get_db
from app.models import User, RecommendationHistory
from app.utils.auth import get_optional_current_user
from app.routers import auth, home, party, jewelry, history

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite database and upload folder
    os.makedirs("uploads", exist_ok=True)
    init_db()
    yield


app = FastAPI(
    title="PocketSmart AI",
    description="Your Smart Budget Recommendation Assistant",
    version="1.0.0",
    lifespan=lifespan
)

# Ensure uploads directory exists and mount for serving uploaded outfit images
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Include Modular Routers
app.include_router(auth.router)
app.include_router(home.router)
app.include_router(party.router)
app.include_router(jewelry.router)
app.include_router(history.router)


@app.get("/", response_class=HTMLResponse)
async def landing_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """Polished SaaS landing page for PocketSmart AI."""
    current_user = get_optional_current_user(request, db)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"current_user": current_user}
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """User dashboard showing stats, quick planner shortcuts, and recent recommendation plans."""
    current_user = get_optional_current_user(request, db)
    if not current_user:
        return RedirectResponse(url="/login?next=/dashboard", status_code=status.HTTP_303_SEE_OTHER)

    # Fetch recent plans for this user
    recent_plans_records = (
        db.query(RecommendationHistory)
        .filter(RecommendationHistory.user_id == current_user.id)
        .order_by(RecommendationHistory.created_at.desc())
        .limit(5)
        .all()
    )

    total_plans_count = (
        db.query(RecommendationHistory)
        .filter(RecommendationHistory.user_id == current_user.id)
        .count()
    )

    recent_plans = []
    for r in recent_plans_records:
        try:
            parsed = json.loads(r.result_json)
        except Exception:
            parsed = {}
        recent_plans.append({
            "id": r.id,
            "planner_type": r.planner_type,
            "budget": r.budget,
            "currency": r.currency,
            "input_summary": r.input_summary,
            "created_at": r.created_at,
            "result_data": parsed
        })

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "current_user": current_user,
            "recent_plans": recent_plans,
            "total_plans_count": total_plans_count
        }
    )


# Friendly error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    current_user = get_optional_current_user(request, next(get_db()))
    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={
            "current_user": current_user,
            "custom_error": "404 - Page Not Found. The requested page could not be located."
        },
        status_code=404
    )


@app.exception_handler(500)
async def server_error_handler(request: Request, exc):
    current_user = get_optional_current_user(request, next(get_db()))
    return templates.TemplateResponse(
        request=request,
        name="base.html",
        context={
            "current_user": current_user,
            "custom_error": "500 - An unexpected internal error occurred. Please try again."
        },
        status_code=500
    )
