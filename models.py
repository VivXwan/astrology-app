# models.py
from pydantic import BaseModel, validator, EmailStr
from utils import raise_

class BirthData(BaseModel):
    year: int
    month: int
    day: int
    hour: float
    minute: float
    latitude: float
    longitude: float

    @validator('month')
    def validate_month(cls, v): return v if 1 <= v <= 12 else raise_(ValueError("Month 1-12"))
    @validator('day')
    def validate_day(cls, v): return v if 1 <= v <= 31 else raise_(ValueError("Day 1-31"))
    @validator('hour')
    def validate_hour(cls, v): return v if 0 <= v < 24 else raise_(ValueError("Hour 0-23.99"))
    @validator('minute')
    def validate_minute(cls, v): return v if 0 <= v < 60 else raise_(ValueError("Minute 0-59.99"))
    @validator('latitude')
    def validate_latitude(cls, v): return v if -90 <= v <= 90 else raise_(ValueError("Latitude -90 to 90"))
    @validator('longitude')
    def validate_longitude(cls, v): return v if -180 <= v <= 180 else raise_(ValueError("Longitude -180 to 180"))

class CustomAyanamsaData(BaseModel):
    name: str
    value: float

    @validator('value')
    def validate_value(cls, v): return v if 0 <= v < 360 else raise_(ValueError("Ayanamsa value must be 0-359.99"))

class UserData(BaseModel):
    name: str
    email: EmailStr  # Ensures valid email format
    password: str  # Added for registration

class LoginData(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"