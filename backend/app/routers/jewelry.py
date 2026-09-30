import os
import uuid
from typing import Optional
from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.auth import get_optional_current_user
from app.services.budget_service import validate_budget
from app.services.recommendation_service import process_jewelry_plan

router = APIRouter(tags=["Jewelry & Outfit Styling Planner"])
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


@router.get("/jewelry-planner", response_class=HTMLResponse)
async def jewelry_planner_page(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_optional_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login?next=/jewelry-planner", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="jewelry_planner.html",
        context={
            "current_user": user,
            "error": None
        }
    )


@router.post("/generate-jewelry")
async def generate_jewelry_submit(
    request: Request,
    budget: float = Form(...),
    currency: str = Form(default="₹"),
    occasion: str = Form(...),
    style: str = Form(...),
    jewelry_type: str = Form(...),
    preferred_color_material: Optional[str] = Form(default=None),
    outfit_description: Optional[str] = Form(default=None),
    outfit_image: Optional[UploadFile] = File(default=None),
    db: Session = Depends(get_db)
):
    user = get_optional_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login?next=/jewelry-planner", status_code=status.HTTP_303_SEE_OTHER)

    try:
        valid_budget = validate_budget(budget, min_budget=500)
    except ValueError as ve:
        return templates.TemplateResponse(
            request=request,
            name="jewelry_planner.html",
            context={
                "current_user": user,
                "error": str(ve)
            },
            status_code=400
        )

    saved_image_path = None
    image_web_url = None

    if outfit_image and outfit_image.filename:
        ext = os.path.splitext(outfit_image.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            return templates.TemplateResponse(
                request=request,
                name="jewelry_planner.html",
                context={
                    "current_user": user,
                    "error": f"Invalid file format '{ext}'. Allowed formats: JPG, PNG, WEBP."
                },
                status_code=400
            )

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        unique_name = f"{uuid.uuid4().hex}{ext}"
        target_path = os.path.join(UPLOAD_DIR, unique_name)

        file_size = 0
        with open(target_path, "wb") as buffer:
            while chunk := await outfit_image.read(1024 * 64):
                file_size += len(chunk)
                if file_size > MAX_FILE_SIZE_BYTES:
                    buffer.close()
                    if os.path.exists(target_path):
                        os.remove(target_path)
                    return templates.TemplateResponse(
                        request=request,
                        name="jewelry_planner.html",
                        context={
                            "current_user": user,
                            "error": "Uploaded image is too large. Maximum file size is 5MB."
                        },
                        status_code=400
                    )
                buffer.write(chunk)

        saved_image_path = target_path
        image_web_url = f"/uploads/{unique_name}"

    input_data = {
        "budget": valid_budget,
        "currency": currency,
        "occasion": occasion,
        "style": style,
        "jewelry_type": jewelry_type,
        "preferred_color_material": (preferred_color_material or "").strip(),
        "outfit_description": (outfit_description or "").strip(),
        "has_image": bool(saved_image_path),
        "image_url": image_web_url
    }

    result = process_jewelry_plan(input_data, db=db, user=user, image_path=saved_image_path)
    result["image_url"] = image_web_url

    if "application/json" in request.headers.get("accept", ""):
        return JSONResponse(content=result)

    return templates.TemplateResponse(
        request=request,
        name="jewelry_results.html",
        context={
            "current_user": user,
            "data": result,
            "input_data": input_data
        }
    )
