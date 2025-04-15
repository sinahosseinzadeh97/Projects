"""
Authentication and security module for the Intelligent Multi-Agent Email Automation System.
This file handles user authentication, API security, and access control.
"""

import jwt
import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import configuration
from .config import config

# JWT settings
SECRET_KEY = config.get("security.secret_key", "your-secret-key-here")  # Should be set in production
ALGORITHM = config.get("security.algorithm", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = config.get("security.access_token_expire_minutes", 30)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# User model
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    roles: List[str] = []

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# Token data model
class TokenData(BaseModel):
    username: Optional[str] = None
    roles: List[str] = []

# Mock user database - in production, this would be stored in MongoDB
fake_users_db = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "hashed_password": bcrypt.hashpw("adminpassword".encode(), bcrypt.gensalt()).decode(),
        "disabled": False,
        "roles": ["admin"]
    },
    "user": {
        "username": "user",
        "email": "user@example.com",
        "full_name": "Regular User",
        "hashed_password": bcrypt.hashpw("userpassword".encode(), bcrypt.gensalt()).decode(),
        "disabled": False,
        "roles": ["user"]
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches hash, False otherwise
    """
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def get_user(db, username: str) -> Optional[User]:
    """
    Get a user from the database.
    
    Args:
        db: User database
        username: Username to look up
        
    Returns:
        User object or None if not found
    """
    if username in db:
        user_data = db[username]
        return User(**user_data)
    return None

def authenticate_user(db, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user.
    
    Args:
        db: User database
        username: Username to authenticate
        password: Password to verify
        
    Returns:
        User object if authentication successful, None otherwise
    """
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, db[username]["hashed_password"]):
        return None
    return user

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current user from a JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, roles=payload.get("roles", []))
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: Current user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is disabled
    """
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def has_role(required_roles: List[str]):
    """
    Check if user has required roles.
    
    Args:
        required_roles: List of required roles
        
    Returns:
        Dependency function
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        for role in required_roles:
            if role in current_user.roles:
                return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return role_checker

# Example usage in FastAPI routes:
"""
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "roles": user.roles},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/admin/")
async def admin_only(current_user: User = Depends(has_role(["admin"]))):
    return {"message": "Admin only endpoint", "user": current_user}
"""
