from typing import Optional
from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_optional_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(tags=["Authentication"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    next: Optional[str] = None,
    db: Session = Depends(get_db)
):
    current_user = get_optional_current_user(request, db)
    if current_user:
        return RedirectResponse(url=next or "/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "current_user": None,
            "next": next or "/dashboard",
            "error": None
        }
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    db: Session = Depends(get_db)
):
    current_user = get_optional_current_user(request, db)
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "current_user": None,
            "error": None
        }
    )


@router.post("/register")
async def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    name = name.strip()
    email = email.strip().lower()

    # Form Validation
    error = None
    if not name or len(name) < 2:
        error = "Name must be at least 2 characters long."
    elif "@" not in email or "." not in email:
        error = "Please provide a valid email address."
    elif len(password) < 6:
        error = "Password must be at least 6 characters long."
    elif password != confirm_password:
        error = "Passwords do not match."
    
    if error:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "current_user": None,
                "error": error,
                "name": name,
                "email": email
            },
            status_code=400
        )

    # Check existing user
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "current_user": None,
                "error": "An account with this email already exists. Please log in.",
                "name": name,
                "email": email
            },
            status_code=400
        )

    # Create new user
    hashed = hash_password(password)
    user = User(name=name, email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate token and set cookie
    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return response


@router.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    next: Optional[str] = Form(default="/dashboard"),
    db: Session = Depends(get_db)
):
    email = email.strip().lower()
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "current_user": None,
                "error": "Invalid email or password. Please try again.",
                "email": email,
                "next": next or "/dashboard"
            },
            status_code=401
        )

    # Generate token and set cookie
    token = create_access_token(data={"sub": str(user.id), "email": user.email})
    target_url = next if next and next.startswith("/") else "/dashboard"
    response = RedirectResponse(url=target_url, status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    return response


@router.get("/logout")
async def logout(request: Request):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response


@router.get("/session-info")
async def session_info(
    request: Request,
    db: Session = Depends(get_db)
):
    user = get_optional_current_user(request, db)
    if user:
        return {
            "authenticated": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }
    return {"authenticated": False, "user": None}
