# models.py
from pydantic import BaseModel, validator, EmailStr
from datetime import datetime

class BirthData(BaseModel):
    year: int
    month: int
    day: int
    hour: float
    minute: float
    latitude: float
    longitude: float

    # @validator('month')
    # def validate_month(cls, v): return v if 1 <= v <= 12 else raise_(ValueError("Month 1-12"))
    # @validator('day')
    # def validate_day(cls, v): return v if 1 <= v <= 31 else raise_(ValueError("Day 1-31"))
    # @validator('hour')
    # def validate_hour(cls, v): return v if 0 <= v < 24 else raise_(ValueError("Hour 0-23.99"))
    # @validator('minute')
    # def validate_minute(cls, v): return v if 0 <= v < 60 else raise_(ValueError("Minute 0-59.99"))
    # @validator('latitude')
    # def validate_latitude(cls, v): return v if -90 <= v <= 90 else raise_(ValueError("Latitude -90 to 90"))
    # @validator('longitude')
    # def validate_longitude(cls, v): return v if -180 <= v <= 180 else raise_(ValueError("Longitude -180 to 180"))

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
    def sanitize_hour(cls, v):
        if not isinstance(v, (int, float)) or v < 0 or v >= 24:
            raise ValueError("Hour must be a number between 0 and 23.99")
        return round(float(v), 2)  # Round to 2 decimal places

    @validator('minute', pre=True)
    def sanitize_minute(cls, v):
        if not isinstance(v, (int, float)) or v < 0 or v >= 60:
            raise ValueError("Minute must be a number between 0 and 59.99")
        return round(float(v), 2)  # Round to 2 decimal places

    @validator('latitude', pre=True)
    def sanitize_latitude(cls, v):
        if not isinstance(v, (int, float)) or v < -90 or v > 90:
            raise ValueError("Latitude must be a number between -90 and 90")
        return round(float(v), 6)  # Round to 6 decimal places for precision

    @validator('longitude', pre=True)
    def sanitize_longitude(cls, v):
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
    token_type: str = "bearer"