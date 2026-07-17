# api/routes/auth.py

import os
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from typing import List, Optional

from database.connection import get_db
from database import crud

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ─── Schemas ───────────────────────────────────────────────

class SkillInput(BaseModel):
    name: str
    proficiency: int


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    company_name: Optional[str] = ""
    company_type: str  # service/product/startup
    role: str
    tech_stack: Optional[List[str]] = []
    personal_goal: str
    joined_company_date: Optional[str] = None
    skills: Optional[List[SkillInput]] = []


class Token(BaseModel):
    access_token: str
    token_type: str
    user_name: str
    user_id: str


# ─── Helpers ───────────────────────────────────────────────

def create_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=EXPIRE_DAYS)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise credentials_exception
    return user


# ─── Routes ────────────────────────────────────────────────

@router.post("/register", response_model=Token)
def register(data: UserRegister, db: Session = Depends(get_db)):
    existing = crud.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    from datetime import date
    joined_date = None
    if data.joined_company_date:
        try:
            joined_date = date.fromisoformat(data.joined_company_date)
        except ValueError:
            joined_date = date.today()

    user = crud.create_user(db, {
        "name": data.name,
        "email": data.email,
        "password": data.password,
        "company_name": data.company_name,
        "company_type": data.company_type,
        "role": data.role,
        "tech_stack": data.tech_stack,
        "personal_goal": data.personal_goal,
        "joined_company_date": joined_date
    })

    if data.skills:
        crud.add_user_skills(
            db, str(user.id),
            [{"name": s.name, "proficiency": s.proficiency}
             for s in data.skills]
        )

    token = create_token(str(user.id))
    return Token(
        access_token=token,
        token_type="bearer",
        user_name=user.name,
        user_id=str(user.id)
    )


@router.post("/login", response_model=Token)
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user_by_email(db, form.username)
    if not user or not crud.verify_password(
        form.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    token = create_token(str(user.id))
    return Token(
        access_token=token,
        token_type="bearer",
        user_name=user.name,
        user_id=str(user.id)
    )


@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "company_type": current_user.company_type,
        "days_at_company": current_user.days_at_company,
        "personal_goal": current_user.personal_goal
    }