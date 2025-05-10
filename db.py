# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db_models import Base, Chart, User, RefreshToken
from sqlalchemy.exc import IntegrityError, OperationalError
from fastapi import HTTPException, Depends
from passlib.context import CryptContext
from dotenv import load_dotenv
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from models import ChartResponse

load_dotenv()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Get database URL from environment with fallback
DATABASE_URL = os.getenv("DATABASE_URL")

# Fix for SQLAlchemy - convert postgres:// to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)  # Create tables if they don't exist
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to provide a session
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_user(name: str, email: str, password: str, db: Session = Depends(get_db)) -> int:
    """
    Create a new user and return their user_id.
    Raises HTTPException if email already exists.
    """
    try:
        hashed_password = pwd_context.hash(password)
        user = User(name=name, email=email, password_hash=hashed_password)
        db.add(user)
        db.commit()
        return user.user_id
    except IntegrityError:  # Email uniqueness violation
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    except OperationalError as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")

def get_user_by_email(email: str, db: Session = Depends(get_db)) -> int:
    """
    Retrieve user_id by email. Returns None if not found.
    """
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            return {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "password_hash": user.password_hash
            }
        return None
    except OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")

def save_chart(birth_data: dict, result: dict, user_id: int = None, db: Session = Depends(get_db)) -> int:
    """
    Save a chart to the database and return its chart_id.
    """
    try:
        chart = Chart(birth_data=birth_data, result=result, user_id=user_id)
        db.add(chart)
        db.commit()
        chart_id = chart.chart_id
        return chart_id
    except OperationalError as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid chart data: {str(e)}")

def get_chart(chart_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Retrieve a chart by its chart_id.
    """
    try:
        chart = db.query(Chart).filter(Chart.chart_id == chart_id).first()
        if chart:
            return {
                "chart_id": chart.chart_id,
                "user_id": chart.user_id,
                "birth_data": chart.birth_data,
                "result": chart.result,
                "created_at": chart.created_at.isoformat()
            }
        return None
    except OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")

def get_charts_by_user_id(user_id: int, db: Session) -> List[ChartResponse]:
    """
    Retrieve all charts for a given user_id, ordered by creation date.
    """
    try:
        charts_db = db.query(Chart).filter(Chart.user_id == user_id).order_by(Chart.created_at.desc()).all()
        return [
            ChartResponse(
                chart_id=chart.chart_id,
                user_id=chart.user_id,
                birth_data=chart.birth_data,
                created_at=chart.created_at
            ) for chart in charts_db
        ]
    except OperationalError as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error retrieving charts")

def create_refresh_token(user_id: int, db: Session, expires_delta: timedelta = timedelta(days=30)) -> str:
    """
    Create a new refresh token for a user and store it in the database.
    """
    try:
        # Generate a secure random token
        token = secrets.token_hex(32)
        expires_at = datetime.now(timezone.utc) + expires_delta
        
        # Create new refresh token entry
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        # Save to database
        db.add(refresh_token)
        db.commit()
        
        return token
    except Exception as e:
        db.rollback()
        # Use generic error message to avoid exposing implementation details
        raise HTTPException(status_code=500, detail="Error creating refresh token")

def validate_refresh_token(token: str, db: Session) -> int:
    """
    Validate a refresh token and return the associated user_id if valid.
    """
    try:
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc)
        ).first()
        
        if not refresh_token:
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
        
        return refresh_token.user_id
    except HTTPException:
        raise
    except Exception:
        # Use generic error message to avoid exposing implementation details
        raise HTTPException(status_code=500, detail="Error validating refresh token")

def revoke_refresh_token(token: str, db: Session) -> bool:
    """
    Revoke a refresh token (mark it as invalid).
    """
    try:
        refresh_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if refresh_token:
            refresh_token.is_revoked = True
            db.commit()
            return True
        return False
    except Exception:
        db.rollback()
        # Use generic error message to avoid exposing implementation details
        raise HTTPException(status_code=500, detail="Error revoking refresh token")