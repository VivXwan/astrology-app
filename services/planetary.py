import swisseph as swe
from typing import Dict, Optional
from datetime import datetime, timezone, timedelta
from models import BirthData
from constants import ZODIAC_SIGNS, NAKSHATRAS, NAKSHATRA_SPAN, NAKSHATRA_PADA_SPAN
from utils import decimal_to_dms, get_ayanamsa_value

swe.set_ephe_path('./ephe')

def calculate_planet_positions(data: BirthData, jd: float, ayanamsa: float, ayanamsa_type: Optional[str]) -> Dict:
    """
    Calculate sidereal positions for planets and lagna given a Julian Day and ayanamsa.
    Returns a dictionary with planetary data (longitude, sign, nakshatra, pada).
    """
    try:
        cusps, ascmc = swe.houses(jd, data.latitude, data.longitude, b'P')
        sidereal_cusps = [(c - ayanamsa) % 360 for c in cusps]
        sidereal_asc = (cusps[0] - ayanamsa) % 360
        sidereal_mc = (ascmc[1] - ayanamsa) % 360
        
        planets = {}
        planet_list = [(0, "Sun"), (1, "Moon"), (2, "Mercury"), (3, "Venus"), (4, "Mars"),
                    (5, "Jupiter"), (6, "Saturn"), (10, "Rahu")]  # Ketu computed from Rahu

        # Lagna(Ascendant)
        lagna_sign_index = int(sidereal_asc / 30)
        lagna_nakshatra_index = int(sidereal_asc / NAKSHATRA_SPAN)
        lagna_pada = int((sidereal_asc % NAKSHATRA_SPAN) / NAKSHATRA_PADA_SPAN) + 1
        planets["Lagna"] = {
            "longitude": float(sidereal_asc),
            "longitude_dms": decimal_to_dms(sidereal_asc),
            "sign": ZODIAC_SIGNS[lagna_sign_index],
            "house": 1,
            "degrees_in_sign": float(sidereal_asc % 30),
            "degrees_in_sign_dms": decimal_to_dms(sidereal_asc % 30),
            "nakshatra": NAKSHATRAS[lagna_nakshatra_index],
            "pada": int(lagna_pada),
            "retrograde": "no"
        }

        for pid, name in planet_list:
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            if pid == 10:  # True node for Rahu
                flags |= swe.FLG_TRUEPOS
            
            calc_result = swe.calc_ut(jd, pid, flags)
            trop_longitude = calc_result[0][0]
            longitude_speed = calc_result[0][3]

            is_retrograde = "yes" if longitude_speed < 0 else "no"

            sid_longitude = (trop_longitude - ayanamsa) % 360
            sign_index = int(sid_longitude / 30)
            house_number = (sign_index - lagna_sign_index + 12) % 12 + 1
            nakshatra_deg = sid_longitude % 360
            nakshatra_index = int(nakshatra_deg / NAKSHATRA_SPAN)
            nakshatra_name = NAKSHATRAS[nakshatra_index]
            pada = int((nakshatra_deg % NAKSHATRA_SPAN) / NAKSHATRA_PADA_SPAN) + 1

            planets[name] = {
                "longitude": float(sid_longitude),
                "longitude_dms": decimal_to_dms(sid_longitude),
                "sign": ZODIAC_SIGNS[sign_index],
                "house": house_number,
                "degrees_in_sign": float(sid_longitude % 30),
                "degrees_in_sign_dms": decimal_to_dms(sid_longitude % 30),
                "nakshatra": nakshatra_name,
                "pada": int(pada),
                "retrograde": is_retrograde
            }

        # Compute Ketu (180° opposite Rahu)
        ketu_long = (planets["Rahu"]["longitude"] + 180) % 360
        ketu_sign_index = int(ketu_long / 30)
        ketu_house_number = (ketu_sign_index - lagna_sign_index + 12) % 12 + 1
        ketu_nakshatra_index = int(ketu_long / NAKSHATRA_SPAN)
        ketu_pada = int((ketu_long % NAKSHATRA_SPAN) / NAKSHATRA_PADA_SPAN) + 1
        planets["Ketu"] = {
            "longitude": float(ketu_long),
            "longitude_dms": decimal_to_dms(ketu_long),
            "sign": ZODIAC_SIGNS[ketu_sign_index],
            "house": ketu_house_number,
            "degrees_in_sign": float(ketu_long % 30),
            "degrees_in_sign_dms": decimal_to_dms(ketu_long % 30),
            "nakshatra": NAKSHATRAS[ketu_nakshatra_index],
            "pada": int(ketu_pada),
            "retrograde": "yes"
        }

        # Update Lagna with retrograde field (always "no")
        planets["Lagna"]["retrograde"] = "no"

        return {
                "ayanamsa": float(ayanamsa),
                "ayanamsa_type": ayanamsa_type if ayanamsa_type else "true_chitra",
                "ascendant": {
                    "longitude": float(sidereal_asc),
                    "longitude_dms": decimal_to_dms(sidereal_asc),
                    "sign": ZODIAC_SIGNS[int(sidereal_asc / 30)]
                },
                "midheaven": float(sidereal_mc),
                "midheaven_dms": decimal_to_dms(sidereal_mc),
                "planets": planets
            }
    except swe.Error as e:
        raise ValueError(f"Swiss Ephemeris calculation failed: {str(e)}")
    except IndexError as e:
        raise ValueError(f"Invalid planetary data index: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error in position calculation: {str(e)}")

def calculate_kundali(data: BirthData, tz_offset: float, ayanamsa_type: Optional[str]) -> Dict:
    """Calculate the birth chart (Kundali) with planetary positions."""
    try:
        # Convert birth time to Julian Day
        jd = swe.julday(data.year, data.month, data.day, 
                       data.hour + data.minute / 60.0 + data.second / 3600.0)
        
        # Get ayanamsa value
        ayanamsa = get_ayanamsa_value(jd, ayanamsa_type)
        
        # Calculate planetary positions
        kundali = calculate_planet_positions(data, jd, ayanamsa, ayanamsa_type)
        
        # Add timezone offset to result
        kundali["tz_offset"] = tz_offset
        
        return kundali
    except Exception as e:
        raise ValueError(f"Kundali calculation failed: {str(e)}")

def calculate_transits(data: BirthData, tz_offset: float, date_time: Optional[datetime] = None, ayanamsa_type: Optional[str] = None) -> Dict:
    """Calculate transit positions for a given date/time."""
    try:
        if date_time is None:
            date_time = datetime.now(timezone.utc)
        else:
            # Convert transit_date to UTC if it's not
            date_time = date_time - timedelta(hours=tz_offset)
        # Convert transit time to Julian Day
        jd = swe.julday(date_time.year, date_time.month, date_time.day,
                       date_time.hour + date_time.minute / 60.0 + date_time.second / 3600.0)
        
        # Get ayanamsa value
        ayanamsa = get_ayanamsa_value(jd, ayanamsa_type)
        
        # Calculate planetary positions
        transits = calculate_planet_positions(data, jd, ayanamsa, ayanamsa_type)
        
        # Add timezone offset and transit date to result
        transits["tz_offset"] = tz_offset
        transits["transit_date"] = date_time.strftime("%Y-%m-%d %H:%M:%S")
        
        return transits
    except Exception as e:
        raise ValueError(f"Transit calculation failed: {str(e)}")