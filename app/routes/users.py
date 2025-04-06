from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.database import get_db
from app.models import User
from app.auth import verify_password, hash_password

router = APIRouter(prefix="/users", tags=["Users"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/logout")
def logout():
    return RedirectResponse(url="/users/login?message=Logged%20out%20successfully", status_code=303)


@router.get("/login")
def show_login_page(request: Request, message: str = ""):
    return templates.TemplateResponse("login.html", {"request": request, "message": message})


@router.post("/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return RedirectResponse(url="/users/login?message=Invalid%20email%20or%20password", status_code=303)

    response = RedirectResponse(url="/tasks/dashboard", status_code=303)
    response.set_cookie(key="user_id", value=user.id)  # Store user ID in a cookie
    return response


async def send_email(param, param1, param2):
    pass


@router.get("/test-email")
async def test_email():
    await send_email("test@example.com", "Test Email", "This is a Mailtrap test!")
    return {"message": "Email sent to Mailtrap!"}


@router.get("/register")
def show_register_page(request: Request, message: str = ""):
    return templates.TemplateResponse("register.html", {"request": request, "message": message})


@router.post("/register")
def create_user(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return RedirectResponse(url="/users/register?message=Email%20already%20registered", status_code=303)

    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return RedirectResponse(url="/users/login?message=Account%20created%20successfully", status_code=303)
