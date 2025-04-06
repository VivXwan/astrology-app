# utils.py
from fastapi import HTTPException
import swisseph as swe
from typing import Optional
from constants import AYANAMSA_TYPES
from models import BirthData

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
    
def sanitize_birth_data(data: BirthData, tz_offset: float) -> BirthData:
    """
    Sanitize BirthData inputs, ensuring logical consistency and safe values.
    """
    try:
        # Ensure tz_offset is reasonable (typically -12 to 14)
        if not -12 <= tz_offset <= 14:
            raise ValueError("Timezone offset must be between -12 and 14 hours")
        tz_offset = round(tz_offset, 2)

        # Adjust hour and minute with tz_offset to check feasibility
        adjusted_hour = data.hour + tz_offset
        if adjusted_hour < 0 or adjusted_hour >= 24:
            raise ValueError(f"Hour {data.hour} with timezone offset {tz_offset} results in invalid time")

        # Return sanitized BirthData (Pydantic already rounded fields)
        return data
    except ValueError as e:
        raise ValueError(f"Birth data sanitization failed: {str(e)}")