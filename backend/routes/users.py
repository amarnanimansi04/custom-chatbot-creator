from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
import models
from auth import hash_password, verify_password, create_access_token

router = APIRouter()

# --- Request body shapes ---
class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

# --- Register ---
@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = db.query(models.User).filter(models.User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the password and save user
    user = models.User(
        email=data.email,
        hashed_password=hash_password(data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Return JWT token
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "email": user.email}

# --- Login ---
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Return JWT token
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "email": user.email}