from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.user import User

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

# Demo users for hackathon mode
DEMO_USERS = {
    "admin@keruen.local": {
        "full_name": "Admin User",
        "role": "admin",
        "company": "Keruen",
        "phone": "+7 7292 000001"
    },
    "analyst@keruen.local": {
        "full_name": "Analyst User",
        "role": "analyst",
        "company": "Analytics Team",
        "phone": "+7 7292 000002"
    },
    "shipper@keruen.local": {
        "full_name": "Shipper User",
        "role": "shipper",
        "company": "Shipping Co",
        "phone": "+7 7292 000003"
    },
    "driver@keruen.local": {
        "full_name": "Driver User",
        "role": "driver",
        "company": "Transport Co",
        "phone": "+7 7292 000004"
    },
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=30))  # 30 days for demo
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_demo_user(email: str) -> Optional[User]:
    """Get or create a demo user in demo mode"""
    if email not in DEMO_USERS:
        return None
    
    # This is a mock user for demo purposes
    demo_data = DEMO_USERS[email]
    user = User(
        id=hash(email) % 1000000,
        email=email,
        full_name=demo_data["full_name"],
        hashed_password="demo-no-password",
        role=demo_data["role"],
        company=demo_data["company"],
        phone=demo_data["phone"],
        is_active=True
    )
    return user

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> User:
    """
    Get current user with demo mode support.
    In demo mode, accepts X-User-Role header and bypasses JWT validation.
    """
    
    # DEMO MODE: Check for X-User-Role header (frontend sends this in demo mode)
    if settings.is_demo_mode:
        user_role = request.headers.get("X-User-Role")
        user_email = request.headers.get("X-User-Email")
        
        if user_email and user_email in DEMO_USERS:
            demo_user = get_demo_user(user_email)
            if demo_user:
                return demo_user
        
        if user_role:
            # Find demo user by role
            for email, data in DEMO_USERS.items():
                if data["role"] == user_role.lower():
                    return get_demo_user(email)
    
    # JWT VALIDATION: Only when token provided and not in demo mode
    if token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                return user
        except JWTError:
            if not settings.is_demo_mode:
                raise credentials_exception
    
    # DEMO MODE FALLBACK: Return default admin user if no valid auth
    if settings.is_demo_mode:
        return get_demo_user("admin@keruen.local")
    
    # STRICT MODE: No auth provided and not in demo mode
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )

def require_role(*roles: str):
    """Decorator to require specific roles"""
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker
    return role_checker
