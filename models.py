# models.py
from pydantic import BaseModel, validator, EmailStr
from datetime import datetime

class BirthData(BaseModel):
    year: int
    month: int
    day: int
    hour: float
    minute: float
    second: float = 0.0  # Default to 0 if not provided
    latitude: float
    longitude: float

    @validator('month', pre=True)
    def validate_month(cls, v):
        if not isinstance(v, int) or not 1 <= v <= 12:
            raise ValueError("Month must be an integer between 1 and 12")
        return v

    @validator('day', pre=True)
    def validate_day(cls, v, values):
        if "year" not in values or "month" not in values:
            raise ValueError("Year and month must be provided before day validation")
        year, month = values["year"], values["month"]
        try:
            # Check if the day is valid for the given year and month
            datetime(year, month, v)
            return v
        except ValueError:
            raise ValueError(f"Day {v} is invalid for month {month} and year {year}")

    @validator('hour', pre=True)
    def validate_hour(cls, v):
        if not isinstance(v, (int, float)) or v < 0 or v >= 24:
            raise ValueError("Hour must be a number between 0 and 23.99")
        return round(float(v), 2)  # Round to 2 decimal places

    @validator('minute', pre=True)
    def validate_minute(cls, v):
        if not isinstance(v, (int, float)) or v < 0 or v >= 60:
            raise ValueError("Minute must be a number between 0 and 59.99")
        return round(float(v), 2)  # Round to 2 decimal places

    @validator('second', pre=True)
    def validate_second(cls, v):
        if not isinstance(v, (int, float)) or v < 0 or v >= 60:
            raise ValueError("Second must be a number between 0 and 59.99")
        return round(float(v), 2)  # Round to 2 decimal places

    @validator('latitude', pre=True)
    def validate_latitude(cls, v):
        if not isinstance(v, (int, float)) or v < -90 or v > 90:
            raise ValueError("Latitude must be a number between -90 and 90")
        return round(float(v), 6)  # Round to 6 decimal places for precision

    @validator('longitude', pre=True)
    def validate_longitude(cls, v):
        if not isinstance(v, (int, float)) or v < -180 or v > 180:
            raise ValueError("Longitude must be a number between -180 and 180")
        return round(float(v), 6)  # Round to 6 decimal places for precision

class CustomAyanamsaData(BaseModel):
    name: str
    value: float

    @validator('value')
    def validate_value(cls, v):
        if not isinstance(v, (int, float)) or v < 0 or v >= 360:
            raise ValueError("Ayanamsa value must be a number between 0 and 359.99")
        return round(float(v), 6)

class UserData(BaseModel):
    name: str
    email: EmailStr  # Ensures valid email format
    password: str  # Added for registration

class LoginData(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600  # 1 hour in seconds

class LocationData(BaseModel):
    latitude: float
    longitude: float
    display_name: str
    place_id: int
    osm_type: str
    osm_id: int
    type: str
    class_type: str
    importance: float
    address: dict

class GeocodeRequest(BaseModel):
    query: str

class GeocodeResponse(BaseModel):
    locations: list[LocationData]
    total_results: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str