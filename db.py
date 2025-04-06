# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from db_models import Base, Chart, User
from sqlalchemy.exc import IntegrityError, OperationalError
from fastapi import HTTPException, Depends
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

load_dotenv()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# PostgreSQL connection string (adjust user, host, port if needed)
# DATABASE_URL = "postgresql://postgres:123@localhost:5432/astrologyDB"\
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)  # Create tables if they don’t exist
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