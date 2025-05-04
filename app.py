# app.py
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
import httpx
from typing import Dict, Optional, List
from datetime import datetime, timedelta, timezone
from models import BirthData, UserData, LoginData, TokenResponse, GeocodeRequest, GeocodeResponse, RefreshTokenRequest
from services.chart import generate_chart
from db import save_chart, get_chart, create_user, get_user_by_email, get_db, create_refresh_token, validate_refresh_token, revoke_refresh_token
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError, DecodeError, ExpiredSignatureError
from sqlalchemy.orm import Session
import redis.asyncio as redis
from utils import get_timezone_offset
import time

load_dotenv()
app = FastAPI(title="Astrology Chart API", description="Vedic astrology charts with True Chitrapaksha Ayanamsa and timezone support", version="0.1.0")

# Get CORS allowed origins from environment or use a default for development
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Specific origins instead of wildcard
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)

# Get Redis configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_SSL = os.getenv("REDIS_SSL", "false").lower() == "true"

# Configure Redis client with proper security
redis_client = redis.Redis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    db=REDIS_DB,
    password=REDIS_PASSWORD,
    ssl=REDIS_SSL,
    decode_responses=True
)

# Rate limiting configuration
RATE_LIMIT_DURATION = int(os.getenv("RATE_LIMIT_DURATION", "60"))  # seconds
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))  # requests per duration

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Skip rate limiting for certain paths if needed
    if request.url.path in ["/health"]:
        return await call_next(request)
    
    # Get client IP or another identifier
    client_id = request.client.host
    
    # Create a Redis key for this client
    redis_key = f"rate_limit:{client_id}"
    
    # Get current count for this client
    try:
        count = await redis_client.get(redis_key)
        count = int(count) if count else 0
        
        # Check if rate limit exceeded
        if count >= RATE_LIMIT_REQUESTS:
            return HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            ).responses[429]
        
        # Increment request count
        pipeline = redis_client.pipeline()
        await pipeline.incr(redis_key)
        if count == 0:
            await pipeline.expire(redis_key, RATE_LIMIT_DURATION)
        await pipeline.execute()
    except Exception:
        # If Redis fails, continue without rate limiting
        pass
    
    # Process the request
    return await call_next(request)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception:
        # Generic error to avoid exposing implementation details
        raise HTTPException(status_code=500, detail="Token creation failed")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        return None  # No token provided, allow anonymous access
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return int(user_id)
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired", headers={"WWW-Authenticate": "Bearer"})
    except DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
    except PyJWTError:
        raise credentials_exception

@app.post("/users", response_model=Dict)
async def create_new_user(user: UserData, db: Session = Depends(get_db)):
    try:
        user_id = create_user(user.name, user.email, user.password, db)
        return {"user_id": user_id, "name": user.name, "email": user.email}
    except HTTPException as e:
        raise e
    except Exception:
        # Generic error to avoid exposing implementation details
        raise HTTPException(status_code=500, detail="Error creating user")

@app.post("/login", response_model=TokenResponse)
async def login_for_access_token(form_data: LoginData, db: Session = Depends(get_db)):
    user = get_user_by_email(form_data.email, db)
    if not user or not pwd_context.verify(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["user_id"])}, expires_delta=access_token_expires
    )
    # Create refresh token
    refresh_token = create_refresh_token(user["user_id"], db)
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        # Validate the refresh token
        user_id = validate_refresh_token(data.refresh_token, db)
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user_id)}, expires_delta=access_token_expires
        )
        
        # Create new refresh token and revoke the old one
        new_refresh_token = create_refresh_token(user_id, db)
        revoke_refresh_token(data.refresh_token, db)
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    except HTTPException as e:
        raise e
    except Exception:
        # Generic error to avoid exposing implementation details
        raise HTTPException(status_code=500, detail="Error refreshing token")

@app.post("/logout")
async def logout(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        success = revoke_refresh_token(data.refresh_token, db)
        if success:
            return {"detail": "Successfully logged out"}
        return {"detail": "Logout failed"}
    except Exception:
        # Generic error to avoid exposing implementation details
        raise HTTPException(status_code=500, detail="Error during logout")

@app.post("/charts", response_model=Dict)
async def get_charts(
    data: BirthData,
    tz_offset: Optional[float] = None,
    transit_date: Optional[datetime] = None,
    ayanamsa_type: Optional[str] = None,
    dasha_level: Optional[int] = 3,
    current_user: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # If tz_offset is not provided, calculate it from coordinates
        if tz_offset is None:
            tz_offset = get_timezone_offset(data.latitude, data.longitude)
            
        result = generate_chart(data, tz_offset, transit_date, ayanamsa_type, current_user, dasha_level, db)
        return result
    except ValueError as e:
        # Limited error details to avoid information leakage
        raise HTTPException(status_code=400, detail="Chart generation failed: invalid input")
    except HTTPException as e:
        raise e
    except Exception:
        # Generic error to avoid exposing implementation details
        raise HTTPException(status_code=500, detail="Unexpected error generating chart")

@app.get("/charts/{chart_id}", response_model=Dict)
async def get_chart_by_id(chart_id: int, current_user: int = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        chart = get_chart(chart_id, db)
        if not chart:
            raise HTTPException(status_code=404, detail="Chart not found")
        
        chart_user_id = chart["user_id"]

        if chart_user_id is None or chart["user_id"] != current_user:
            raise HTTPException(status_code=403, detail="Chart doesn't exist")
        return chart
    except HTTPException as e:
        raise e
    except Exception:
        # Generic error to avoid exposing implementation details
        raise HTTPException(status_code=400, detail="Error retrieving chart")
    
@app.post("/geocode", response_model=GeocodeResponse)
async def geocode_location(request: GeocodeRequest):
    query = request.query.strip()
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:  # Set timeout
            # Nominatim API request with detailed address data, limit 5 results
            url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=5&addressdetails=1"
            headers = {"User-Agent": "VedicAstrologyApp/1.0"}
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                raise HTTPException(status_code=404, detail="Location not found")
            
            # Sort locations by importance score (highest first)
            locations = sorted(data, key=lambda x: float(x.get("importance", 0)), reverse=True)
            
            # Convert locations to LocationData format
            location_results = []
            for location in locations:
                location_results.append({
                    "latitude": float(location["lat"]),
                    "longitude": float(location["lon"]),
                    "display_name": location["display_name"],
                    "place_id": location["place_id"],
                    "osm_type": location["osm_type"],
                    "osm_id": location["osm_id"],
                    "type": location["type"],
                    "class_type": location["class"],
                    "importance": float(location.get("importance", 0.0)),
                    "address": location.get("address", {})
                })
            
            return {
                "locations": location_results,
                "total_results": len(location_results)
            }
            
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=400, detail="Geocoding failed")
    except httpx.TimeoutException:
        raise HTTPException(status_code=408, detail="Geocoding request timed out")
    except Exception:
        # Generic error to avoid exposing implementation details
        raise HTTPException(status_code=500, detail="Geocoding error")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}