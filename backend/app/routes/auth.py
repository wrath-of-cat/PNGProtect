"""
Authentication routes for PNGProtect API
Handles user registration, login, and authentication verification
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import sqlite3
from typing import Optional
from app.services.hashing import hash_password, verify_password

router = APIRouter()
security = HTTPBearer()

# Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Database path (use absolute or relative path that works from any directory)
import os
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "storage", "users.db")

# =============================
# Pydantic Models
# =============================

class UserRegister(BaseModel):
    """User registration request"""
    email: str
    username: str
    password: str


class UserLogin(BaseModel):
    """User login request"""
    email: str
    password: str


class UserResponse(BaseModel):
    """User response"""
    id: int
    email: str
    username: str
    created_at: str
    watermarks_count: int = 0


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str
    user: UserResponse


class AuthError(BaseModel):
    """Auth error response"""
    detail: str


# =============================
# Database Functions
# =============================

def init_db():
    """Initialize users database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()


def get_user_by_email(email: str) -> Optional[dict]:
    """Get user by email"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, username, password_hash, created_at FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "email": row[1],
                "username": row[2],
                "password_hash": row[3],
                "created_at": row[4]
            }
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def get_user_by_username(username: str) -> Optional[dict]:
    """Get user by username"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, username, password_hash, created_at FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "email": row[1],
                "username": row[2],
                "password_hash": row[3],
                "created_at": row[4]
            }
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Get user by ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, username, password_hash, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "email": row[1],
                "username": row[2],
                "password_hash": row[3],
                "created_at": row[4]
            }
        return None
    except Exception as e:
        print(f"Error getting user: {e}")
        return None


def create_user(email: str, username: str, password: str) -> Optional[dict]:
    """Create a new user"""
    try:
        password_hash = hash_password(password)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO users (email, username, password_hash)
            VALUES (?, ?, ?)
        """, (email, username, password_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return get_user_by_id(user_id)
    except sqlite3.IntegrityError as e:
        if "email" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        elif "username" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    except Exception as e:
        print(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


def get_watermarks_count(user_id: int) -> int:
    """Get number of watermarks created by user"""
    try:
        watermarks_db = os.path.join(os.path.dirname(__file__), "..", "storage", "watermarks.db")
        conn = sqlite3.connect(watermarks_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM watermarks WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


# =============================
# Token Functions
# =============================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        return {"user_id": user_id}
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(credentials = Depends(security)) -> dict:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    user = get_user_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# Alias for backwards compatibility
require_auth = get_current_user


# =============================
# Endpoints
# =============================

@router.post("/register", response_model=TokenResponse, tags=["Authentication"])
async def register(user_data: UserRegister):
    """
    Register a new user
    
    **Request body:**
    - `email`: User's email address
    - `username`: Unique username
    - `password`: User's password
    
    **Response:**
    - `access_token`: JWT token for authentication
    - `token_type`: Token type (Bearer)
    - `user`: User information
    """
    # Validate input
    if not user_data.email or not user_data.username or not user_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email, username, and password are required"
        )
    
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters"
        )
    
    # Check if user exists
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user = create_user(user_data.email, user_data.username, user_data.password)
    
    # Create token
    access_token = create_access_token(data={"sub": user["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            created_at=user["created_at"],
            watermarks_count=get_watermarks_count(user["id"])
        )
    }


@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
async def login(credentials: UserLogin):
    """
    Login user
    
    **Request body:**
    - `email`: User's email address
    - `password`: User's password
    
    **Response:**
    - `access_token`: JWT token for authentication
    - `token_type`: Token type (Bearer)
    - `user`: User information
    """
    # Get user
    user = get_user_by_email(credentials.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create token
    access_token = create_access_token(data={"sub": user["id"]})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            created_at=user["created_at"],
            watermarks_count=get_watermarks_count(user["id"])
        )
    }


@router.get("/me", response_model=UserResponse, tags=["Authentication"])
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    
    **Headers:**
    - `Authorization`: Bearer {token}
    
    **Response:**
    - User information including email, username, and watermark count
    """
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        username=current_user["username"],
        created_at=current_user["created_at"],
        watermarks_count=get_watermarks_count(current_user["id"])
    )


@router.post("/logout", tags=["Authentication"])
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout user (client-side token removal)
    
    **Headers:**
    - `Authorization`: Bearer {token}
    
    **Response:**
    - Success message
    """
    return {"message": "Logged out successfully", "status": "ok"}


@router.get("/verify-token", tags=["Authentication"])
async def verify_token_endpoint(current_user: dict = Depends(get_current_user)):
    """
    Verify if current token is valid
    
    **Headers:**
    - `Authorization`: Bearer {token}
    
    **Response:**
    - Valid token status
    """
    return {"valid": True, "user_id": current_user["id"]}


# Initialize database on startup
init_db()
