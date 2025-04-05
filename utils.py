# utils.py
from fastapi import HTTPException
import swisseph as swe
from typing import Optional
from constants import AYANAMSA_TYPES

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
    
def raise_(e): raise e