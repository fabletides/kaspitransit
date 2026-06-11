from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User
from app.schemas import UserCreate, UserOut, Token
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user, get_demo_user, DEMO_USERS
from app.core.config import settings

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login endpoint supporting both demo and JWT modes.
    In demo mode, accepts any demo user with password 'demo123'.
    """
    email = form_data.username
    password = form_data.password
    
    # DEMO MODE: Accept hardcoded demo users
    if settings.is_demo_mode and email in DEMO_USERS:
        # In demo mode, accept "demo123" password for all demo users
        if password == "demo123":
            user = get_demo_user(email)
            token = create_access_token(data={"sub": str(user.id), "role": user.role, "email": email})
            # Ensure response includes all fields expected by UserOut schema
            from datetime import datetime
            user_data = {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "company": user.company,
                "phone": user.phone,
                "is_active": (user.is_active if getattr(user, "is_active", None) is not None else True),
                "created_at": (user.created_at if getattr(user, "created_at", None) is not None else datetime.utcnow())
            }
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": user_data
            }
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password (use 'demo123')")
    
    # NORMAL MODE: Check database
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registration endpoint (disabled in demo mode)"""
    if settings.is_demo_mode:
        raise HTTPException(status_code=403, detail="Registration disabled in demo mode")
    
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=get_password_hash(user_data.password),
        role=user_data.role,
        company=user_data.company,
        phone=user_data.phone
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@router.get("/demo-credentials")
async def demo_credentials():
    """Return demo credentials available in demo mode"""
    if not settings.is_demo_mode:
        raise HTTPException(status_code=403, detail="Not in demo mode")
    
    return {
        "auth_mode": settings.AUTH_MODE,
        "demo_accounts": [
            {"email": email, "password": "demo123", "role": data["role"]}
            for email, data in DEMO_USERS.items()
        ]
    }
