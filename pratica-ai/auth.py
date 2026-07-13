"""JWT authentication module for the Italian FNOL voice agent.

Provides password hashing (bcrypt), JWT creation/verification,
FastAPI OAuth2 dependency, and auth-related API endpoints.
"""

from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel, Field

from database import get_db, create_operator, get_operator_by_email

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480")
)  # 8-hour operator shift

# ---------------------------------------------------------------------------
# Password hashing (direct bcrypt — passlib is unmaintained)
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed.encode("utf-8"),
    )


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class OperatorCreate(BaseModel):
    """Schema for creating a new operator account."""
    email: str = Field(..., description="E-mail dell'operatore")
    password: str = Field(..., min_length=8, description="Password (min 8 chars)")
    nome: str = Field(..., description="Nome dell'operatore")
    cognome: str = Field(..., description="Cognome dell'operatore")
    ruolo: str = Field(
        default="operatore",
        description="Ruolo: operatore | liquidatore | supervisore | admin",
    )


class OperatorOut(BaseModel):
    """Public-safe operator representation."""
    id: str
    email: str
    nome: str
    cognome: str
    ruolo: str
    attivo: bool

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """OAuth2-compatible token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Payload extracted from JWT."""
    email: Optional[str] = None


# ---------------------------------------------------------------------------
# FastAPI OAuth2 dependency
# ---------------------------------------------------------------------------

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_operator(
    token: str = Depends(oauth2_scheme),
) -> OperatorOut:
    """FastAPI dependency: validate JWT and return the current operator."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenziali non valide o token scaduto.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    email: Optional[str] = payload.get("sub")
    if email is None:
        raise credentials_exception

    async with get_db() as db:
        operator = await get_operator_by_email(db, email)

    if operator is None or not operator.attivo:
        raise credentials_exception

    return OperatorOut.model_validate(operator)


# ---------------------------------------------------------------------------
# Auth router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Authenticate an operator and return a JWT access token."""
    async with get_db() as db:
        operator = await get_operator_by_email(db, form_data.username)

    if operator is None or not verify_password(
        form_data.password, operator.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail o password non corretti.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not operator.attivo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabilitato. Contattare il supervisore.",
        )

    # Update last_login
    async with get_db() as db:
        op = await get_operator_by_email(db, operator.email)
        if op:
            op.last_login = datetime.now(timezone.utc)

    access_token = create_access_token(data={"sub": operator.email})
    return Token(access_token=access_token)


@router.post("/register", response_model=OperatorOut, status_code=201)
async def register(payload: OperatorCreate) -> OperatorOut:
    """Register a new operator account.

    In production, restrict this endpoint to admin-only.
    For bootstrap, the first registered user becomes admin.
    """
    async with get_db() as db:
        existing = await get_operator_by_email(db, payload.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Un operatore con questa e-mail esiste già.",
            )

        hashed = hash_password(payload.password)
        operator = await create_operator(
            db,
            email=payload.email,
            hashed_password=hashed,
            nome=payload.nome,
            cognome=payload.cognome,
            ruolo=payload.ruolo,
        )
        return OperatorOut.model_validate(operator)


@router.get("/me", response_model=OperatorOut)
async def me(
    current_operator: OperatorOut = Depends(get_current_operator),
) -> OperatorOut:
    """Return the currently authenticated operator."""
    return current_operator
