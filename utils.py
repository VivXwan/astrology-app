# utils.py
from fastapi import HTTPException
import swisseph as swe
from typing import Optional
from constants import AYANAMSA_TYPES
from models import BirthData
from datetime import datetime, timedelta

swe.set_ephe_path('./ephe')


def decimal_to_dms(decimal: float) -> str:
    degrees = int(decimal)
    minutes_decimal = (decimal - degrees) * 60
    minutes = int(minutes_decimal)
    seconds = int((minutes_decimal - minutes) * 60)
    return f"{degrees}° {minutes}' {seconds}\""

def get_ayanamsa_value(jd: float, ayanamsa_type: Optional[str]) -> float:
    if ayanamsa_type is None:
        swe.set_sid_mode(swe.SIDM_TRUE_CITRA, 0, 0)
        return swe.get_ayanamsa_ut(jd)
    elif ayanamsa_type.lower() in AYANAMSA_TYPES:
        swe.set_sid_mode(AYANAMSA_TYPES[ayanamsa_type.lower()], 0, 0)
        return swe.get_ayanamsa_ut(jd)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid Ayanamsa type: {ayanamsa_type}")
    
def sanitize_birth_data(data: BirthData, tz_offset: float) -> dict:
    """
    Sanitize BirthData inputs, ensuring logical consistency and safe values.
    Handles timezone transitions properly using datetime.
    Returns a dictionary with both original and UTC-converted data.
    """
    try:
        # Ensure tz_offset is reasonable (typically -12 to 14)
        if not -12 <= tz_offset <= 14:
            raise ValueError("Timezone offset must be between -12 and 14 hours")
        tz_offset = round(tz_offset, 2)

        # Create a copy of the original data
        original_data = data.dict()

        # Create datetime object for the local time
        local_dt = datetime(
            year=data.year,
            month=data.month,
            day=data.day,
            hour=int(data.hour),
            minute=int(data.minute)
        )

        # Convert to UTC by subtracting the timezone offset
        utc_dt = local_dt - timedelta(hours=tz_offset)

        # Create a new BirthData object with UTC values
        utc_data = BirthData(
            year=utc_dt.year,
            month=utc_dt.month,
            day=utc_dt.day,
            hour=utc_dt.hour + (utc_dt.minute / 60.0),
            minute=float(utc_dt.minute),
            latitude=data.latitude,
            longitude=data.longitude
        )

        return {
            "original": data,
            "utc": utc_data,
            "tz_offset": tz_offset
        }
    except ValueError as e:
        raise ValueError(f"Birth data sanitization failed: {str(e)}")