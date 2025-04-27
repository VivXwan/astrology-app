# utils.py
from fastapi import HTTPException
import swisseph as swe
from typing import Optional
from constants import AYANAMSA_TYPES
from models import BirthData
from datetime import datetime, timedelta
from timezonefinder import TimezoneFinder
import pytz

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
            minute=int(data.minute),
            second=int(data.second)
        )

        # Convert to UTC by subtracting the timezone offset
        utc_dt = local_dt - timedelta(hours=tz_offset)

        # Create a new BirthData object with UTC values
        utc_data = BirthData(
            year=utc_dt.year,
            month=utc_dt.month,
            day=utc_dt.day,
            hour=utc_dt.hour,
            minute=float(utc_dt.minute),
            second=float(utc_dt.second),
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

def get_timezone_offset(latitude: float, longitude: float) -> float:
    """
    Get timezone offset in hours from coordinates.
    Returns the offset in hours (e.g., 5.5 for IST).
    """
    try:
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
        # print(f"Found timezone string: {timezone_str}")
        
        if timezone_str:
            tz = pytz.timezone(timezone_str)
            # Get offset for current date to handle DST
            offset = tz.utcoffset(datetime.now()).total_seconds() / 3600
            # print(f"Calculated offset: {offset} hours")
            return round(offset, 2)
        # print(f"Warning: No timezone found for coordinates ({latitude}, {longitude})")
        return 0.0  # Default to UTC if timezone not found
    except Exception as e:
        print(f"Error getting timezone: {str(e)}")
        return 0.0  # Default to UTC on error