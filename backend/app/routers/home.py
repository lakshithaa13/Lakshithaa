from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.auth import get_optional_current_user
from app.services.budget_service import validate_budget
from app.services.recommendation_service import process_home_plan

router = APIRouter(tags=["Home Interior Planner"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/home-planner", response_class=HTMLResponse)
async def home_planner_page(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_optional_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login?next=/home-planner", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="home_planner.html",
        context={
            "current_user": user,
            "error": None
        }
    )


@router.post("/generate-home")
async def generate_home_submit(
    request: Request,
    budget: float = Form(...),
    currency: str = Form(default="₹"),
    room_type: str = Form(...),
    style: str = Form(...),
    sofa_qty: int = Form(default=0),
    bed_qty: int = Form(default=0),
    dining_table_qty: int = Form(default=0),
    chairs_qty: int = Form(default=0),
    lights_qty: int = Form(default=0),
    ceiling_fan_qty: int = Form(default=0),
    curtains_qty: int = Form(default=0),
    storage_qty: int = Form(default=0),
    decor_qty: int = Form(default=0),
    custom_requirements: Optional[str] = Form(default=None),
    db: Session = Depends(get_db)
):
    user = get_optional_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login?next=/home-planner", status_code=status.HTTP_303_SEE_OTHER)

    # Validate budget
    try:
        valid_budget = validate_budget(budget, min_budget=1000)
    except ValueError as ve:
        return templates.TemplateResponse(
            request=request,
            name="home_planner.html",
            context={
                "current_user": user,
                "error": str(ve),
                "prev_data": {
                    "budget": budget,
                    "currency": currency,
                    "room_type": room_type,
                    "style": style
                }
            },
            status_code=400
        )

    input_data = {
        "budget": valid_budget,
        "currency": currency,
        "room_type": room_type,
        "style": style,
        "sofa_qty": max(0, sofa_qty),
        "bed_qty": max(0, bed_qty),
        "dining_table_qty": max(0, dining_table_qty),
        "chairs_qty": max(0, chairs_qty),
        "lights_qty": max(0, lights_qty),
        "ceiling_fan_qty": max(0, ceiling_fan_qty),
        "curtains_qty": max(0, curtains_qty),
        "storage_qty": max(0, storage_qty),
        "decor_qty": max(0, decor_qty),
        "custom_requirements": (custom_requirements or "").strip()
    }

    result = process_home_plan(input_data, db=db, user=user)

    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse(content=result)

    return templates.TemplateResponse(
        request=request,
        name="home_results.html",
        context={
            "current_user": user,
            "data": result,
            "input_data": input_data
        }
    )
