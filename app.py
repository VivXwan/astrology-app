# app.py
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from typing import Dict, Optional
from datetime import datetime, timedelta
from models import BirthData, UserData, LoginData, TokenResponse
from services import calculate_kundali, calculate_navamsa, calculate_vimshottari_dasha, calculate_transits, calculate_hora, calculate_drekkana, calculate_saptamsa, calculate_dwadasamsa, calculate_trimsamsa, calculate_sthana_bala, calculate_dig_bala
from db import save_chart, get_chart, create_user, get_user_by_email
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError

load_dotenv()
app = FastAPI(title="Astrology Chart API", description="Vedic astrology charts with True Chitrapaksha Ayanamsa and timezone support", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")  # Set in .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

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
    except PyJWTError:
        raise credentials_exception

@app.post("/users", response_model=Dict)
async def create_new_user(user: UserData):
    try:
        user_id = create_user(user.name, user.email, user.password)
        return {"user_id": user_id, "name": user.name, "email": user.email}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/login", response_model=TokenResponse)
async def login_for_access_token(form_data: LoginData):
    user = get_user_by_email(form_data.email)
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
    tz_offset: float = 5.5,
    transit_date: Optional[datetime] = None,
    ayanamsa_type: Optional[str] = None,
    current_user: int = Depends(get_current_user)
):
    try:
        # Calculate Kundali, Navamsa, and Dasha
        kundali = calculate_kundali(data, tz_offset, ayanamsa_type)
        D2_hora = calculate_hora(kundali)
        D3_drekkana = calculate_drekkana(kundali)
        D7_saptamsa = calculate_saptamsa(kundali)
        D9_navamsa = calculate_navamsa(kundali)
        D12_dwadasamsa = calculate_dwadasamsa(kundali)
        D30_trimsamsa = calculate_trimsamsa(kundali)
        dasha = calculate_vimshottari_dasha(data, kundali["planets"]["Moon"])
        transits = calculate_transits(data, tz_offset, transit_date, ayanamsa_type)
        sthana_bala = calculate_sthana_bala(kundali, D2_hora, D3_drekkana, D7_saptamsa, D9_navamsa, D12_dwadasamsa, D30_trimsamsa)
        dig_bala = calculate_dig_bala(kundali)

        birth_data = data.dict()
        birth_data["tz_offset"] = tz_offset
        birth_data["ayanamsa_type"] = ayanamsa_type

        result = {
            "kundali": kundali,
            "vimshottari_dasha": dasha,
            "transits": transits,
            "vargas": {
                "D-2": D2_hora,
                "D-3": D3_drekkana,
                "D-7": D7_saptamsa,
                "D-9": D9_navamsa,
                "D-12": D12_dwadasamsa,
                "D-30": D30_trimsamsa
            },
            "sthana_bala": sthana_bala,
            "dig_bala": dig_bala
        }

        chart_id = save_chart(birth_data, result, current_user)
        result["chart_id"] = chart_id
        result["user_id"] = current_user

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/charts/{chart_id}", response_model=Dict)
async def get_chart_by_id(chart_id: int, current_user: int = Depends(get_current_user)):
    try:
        chart = get_chart(chart_id)
        if not chart:
            raise HTTPException(status_code=404, detail="Chart not found")
        
        chart_user_id = chart["user_id"]

        if chart_user_id is not None and chart["user_id"] != current_user:
            raise HTTPException(status_code=403, detail="Chart doesn't exist")
        return chart
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}