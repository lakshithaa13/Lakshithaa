from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.auth import get_optional_current_user
from app.services.budget_service import validate_budget
from app.services.recommendation_service import process_party_plan

router = APIRouter(tags=["Party & Event Planner"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/party-planner", response_class=HTMLResponse)
async def party_planner_page(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_optional_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login?next=/party-planner", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="party_planner.html",
        context={
            "current_user": user,
            "error": None
        }
    )


@router.post("/generate-party")
async def generate_party_submit(
    request: Request,
    budget: float = Form(...),
    currency: str = Form(default="₹"),
    event_type: str = Form(...),
    guest_count: int = Form(...),
    location: str = Form(...),
    venue_requirement: str = Form(default="Needed"),
    food_preference: str = Form(default="Both"),
    decoration_level: str = Form(default="Standard"),
    entertainment: str = Form(default="Basic"),
    additional_requirements: Optional[str] = Form(default=None),
    db: Session = Depends(get_db)
):
    user = get_optional_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login?next=/party-planner", status_code=status.HTTP_303_SEE_OTHER)

    try:
        valid_budget = validate_budget(budget, min_budget=1000)
    except ValueError as ve:
        return templates.TemplateResponse(
            request=request,
            name="party_planner.html",
            context={
                "current_user": user,
                "error": str(ve)
            },
            status_code=400
        )

    if guest_count < 1:
        return templates.TemplateResponse(
            request=request,
            name="party_planner.html",
            context={
                "current_user": user,
                "error": "Number of guests must be at least 1."
            },
            status_code=400
        )

    input_data = {
        "budget": valid_budget,
        "currency": currency,
        "event_type": event_type,
        "guest_count": guest_count,
        "location": location.strip(),
        "venue_requirement": venue_requirement,
        "food_preference": food_preference,
        "decoration_level": decoration_level,
        "entertainment": entertainment,
        "additional_requirements": (additional_requirements or "").strip()
    }

    result = process_party_plan(input_data, db=db, user=user)

    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse(content=result)

    return templates.TemplateResponse(
        request=request,
        name="party_results.html",
        context={
            "current_user": user,
            "data": result,
            "input_data": input_data
        }
    )
