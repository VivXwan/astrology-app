# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_models import Base, Chart, User
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# PostgreSQL connection string (adjust user, host, port if needed)
DATABASE_URL = "postgresql://postgres:123@localhost:5432/astrologyDB"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)  # Create tables if they don’t exist
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_user(name: str, email: str, password: str) -> int:
    """
    Create a new user and return their user_id.
    Raises HTTPException if email already exists.
    """
    session = SessionLocal()
    try:
        hashed_password = pwd_context.hash(password)
        user = User(name=name, email=email, password_hash=hashed_password)
        session.add(user)
        session.commit()
        user_id = user.user_id
    except IntegrityError:  # Email uniqueness violation
        session.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    return user_id

def get_user_by_email(email: str) -> int:
    """
    Retrieve user_id by email. Returns None if not found.
    """
    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == email).first()
        if user:
            return {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "password_hash": user.password_hash
            }
        return None
    except Exception as e:
        raise e
    finally:
        session.close()

def save_chart(birth_data: dict, result: dict, user_id: int = None) -> int:
    """
    Save a chart to the database and return its chart_id.
    """
    session = SessionLocal()
    try:
        chart = Chart(birth_data=birth_data, result=result, user_id=user_id)
        session.add(chart)
        session.commit()
        chart_id = chart.chart_id
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    return chart_id

def get_chart(chart_id: int) -> dict:
    """
    Retrieve a chart by its chart_id.
    """
    session = SessionLocal()
    try:
        chart = session.query(Chart).filter(Chart.chart_id == chart_id).first()
        if chart:
            return {
                "chart_id": chart.chart_id,
                "user_id": chart.user_id,
                "birth_data": chart.birth_data,
                "result": chart.result,
                "created_at": chart.created_at.isoformat()
            }
        return None
    except Exception as e:
        raise e
    finally:
        session.close()