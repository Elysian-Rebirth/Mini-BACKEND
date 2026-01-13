from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select
from database import get_session
from models import User
import uuid

router = APIRouter()

class LoginRequest(BaseModel):
    user_name: str
    password: str
    captcha_key: str | None = None
    captcha: str | None = None

class LoginResponse(BaseModel):
    status_code: int = 200
    status_message: str = "success"
    data: dict

class UserInfoResponse(BaseModel):
    status_code: int = 200
    data: dict

@router.post("/login")
def login(request: LoginRequest, session: Session = Depends(get_session)):
    # Simple mock login for MVP
    # In real app, hash password and verify
    user = session.exec(select(User).where(User.username == request.user_name)).first()
    if not user:
        # Auto-register for MVP convenience
        user = User(username=request.user_name, password=request.password)
        session.add(user)
        session.commit()
        session.refresh(user)
    
    token = "mock-token-" + str(uuid.uuid4())
    return {
        "status_code": 200,
        "status_message": "success",
        "data": {
            "access_token": token,
            "user_id": user.id,
            "user_name": user.username
        }
    }

@router.get("/info", response_model=UserInfoResponse)
def get_user_info():
    # Return dummy user info
    return {
        "status_code": 200,
        "data": {
            "user_id": 1,
            "user_name": "admin",
            "role": "admin"
        }
    }

@router.post("/logout")
def logout():
    return {"status_code": 200, "status_message": "success"}

@router.get("/get_captcha")
def get_captcha():
    # Mock captcha response
    return {
        "status_code": 200,
        "data": {
            "captcha_id": "mock-captcha-id",
            "image": "" # Frontend might expect base64, leaving empty for now or valid minimal base64 if needed
        }
    }

