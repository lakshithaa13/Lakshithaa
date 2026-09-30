import json
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import RecommendationHistory
from app.utils.auth import get_optional_current_user

router = APIRouter(tags=["History"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/history", response_class=HTMLResponse)
async def history_page(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_optional_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login?next=/history", status_code=status.HTTP_303_SEE_OTHER)

    records = (
        db.query(RecommendationHistory)
        .filter(RecommendationHistory.user_id == user.id)
        .order_by(RecommendationHistory.created_at.desc())
        .all()
    )

    formatted_records = []
    for r in records:
        try:
            parsed = json.loads(r.result_json)
        except Exception:
            parsed = {}
        formatted_records.append({
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
        name="history.html",
        context={
            "current_user": user,
            "plans": formatted_records,
            "total_count": len(formatted_records)
        }
    )


@router.get("/history/{plan_id}", response_class=HTMLResponse)
async def view_historical_plan(
    plan_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_optional_current_user(request, db)
    if not user:
        return RedirectResponse(url=f"/login?next=/history/{plan_id}", status_code=status.HTTP_303_SEE_OTHER)

    record = (
        db.query(RecommendationHistory)
        .filter(RecommendationHistory.id == plan_id, RecommendationHistory.user_id == user.id)
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="Saved plan not found.")

    try:
        result_data = json.loads(record.result_json)
    except Exception:
        result_data = {}

    if record.planner_type == "home":
        return templates.TemplateResponse(
            request=request,
            name="home_results.html",
            context={
                "current_user": user,
                "data": result_data,
                "is_history_view": True,
                "created_at": record.created_at
            }
        )
    elif record.planner_type == "party":
        return templates.TemplateResponse(
            request=request,
            name="party_results.html",
            context={
                "current_user": user,
                "data": result_data,
                "is_history_view": True,
                "created_at": record.created_at
            }
        )
    elif record.planner_type == "jewelry":
        return templates.TemplateResponse(
            request=request,
            name="jewelry_results.html",
            context={
                "current_user": user,
                "data": result_data,
                "is_history_view": True,
                "created_at": record.created_at
            }
        )

    return RedirectResponse(url="/history", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/history/{plan_id}/delete")
async def delete_historical_plan(
    plan_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_optional_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    record = (
        db.query(RecommendationHistory)
        .filter(RecommendationHistory.id == plan_id, RecommendationHistory.user_id == user.id)
        .first()
    )

    if record:
        db.delete(record)
        db.commit()

    return RedirectResponse(url="/history", status_code=status.HTTP_303_SEE_OTHER)
