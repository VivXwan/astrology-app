# app.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
import httpx
from typing import Dict, Optional
from datetime import datetime, timedelta
from models import BirthData, UserData, LoginData, TokenResponse, GeocodeRequest, GeocodeResponse
from services.chart import generate_chart
from db import save_chart, get_chart, create_user, get_user_by_email, get_db
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError, DecodeError, ExpiredSignatureError
from sqlalchemy.orm import Session
import redis.asyncio as redis
from utils import get_timezone_offset

load_dotenv()
app = FastAPI(title="Astrology Chart API", description="Vedic astrology charts with True Chitrapaksha Ayanamsa and timezone support", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all localhost ports
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

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Token creation failed: {str(e)}")

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/charts", response_model=Dict)
async def get_charts(
    data: BirthData,
    tz_offset: Optional[float] = None,
    transit_date: Optional[datetime] = None,
    ayanamsa_type: Optional[str] = None,
    current_user: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # print(f"Received chart request with coordinates: ({data.latitude}, {data.longitude})")
        
        # If tz_offset is not provided, calculate it from coordinates
        if tz_offset is None:
            tz_offset = get_timezone_offset(data.latitude, data.longitude)
            
        result = generate_chart(data, tz_offset, transit_date, ayanamsa_type, current_user, db)
        return result
    except ValueError as e:
        print(f"ValueError in chart generation: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Chart generation failed: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error in chart generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.get("/charts/{chart_id}", response_model=Dict)
async def get_chart_by_id(chart_id: int, current_user: int = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        chart = get_chart(chart_id, db)
        if not chart:
            raise HTTPException(status_code=404, detail="Chart not found")
        
        chart_user_id = chart["user_id"]

        if chart_user_id is not None and chart["user_id"] != current_user:
            raise HTTPException(status_code=403, detail="Chart doesn't exist")
        return chart
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/geocode", response_model=GeocodeResponse)
async def geocode_location(request: GeocodeRequest):
    query = request.query.strip()
    
    try:
        async with httpx.AsyncClient() as client:
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
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=400, detail=f"Geocoding failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Geocoding error: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}