from typing import Dict
import math
from constants import ZODIAC_SIGNS

def calculate_hora(kundali_data: Dict) -> Dict:
    """Calculate Hora (D-2) chart positions for each planet."""
    hora_planets = {}
    odd_signs = [0, 2, 4, 6, 8, 10]  # Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
    try:
        for planet, data in kundali_data["planets"].items():
            degrees_in_sign = data["degrees_in_sign"]
            rasi_sign_index = ZODIAC_SIGNS.index(data["sign"])
            is_odd = rasi_sign_index in odd_signs
            part = math.ceil(degrees_in_sign / 15)  # 15° per part
            if is_odd:
                hora_sign = "Leo" if part == 1 else "Cancer"  # 0°-15°: Leo, 15°-30°: Cancer
            else:
                hora_sign = "Cancer" if part == 1 else "Leo"  # 0°-15°: Cancer, 15°-30°: Leo
            hora_planets[planet] = {"hora_sign": hora_sign}
        return hora_planets
    except KeyError as e:
        raise ValueError(f"Missing required kundali data: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Hora calculation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error in hora calculation: {str(e)}")

def calculate_drekkana(kundali_data: Dict) -> Dict:
    """Calculate Drekkana (D-3) chart positions for each planet."""
    drekkana_planets = {}
    try:
        for planet, data in kundali_data["planets"].items():
            degrees_in_sign = data["degrees_in_sign"]
            rasi_sign_index = ZODIAC_SIGNS.index(data["sign"])
            part = math.ceil(degrees_in_sign / 10)  # 10° per part
            sign_index = (rasi_sign_index + (part - 1) * 4) % 12  # Formula: (Rasi + (Part-1)*4) mod 12
            drekkana_sign = ZODIAC_SIGNS[sign_index]
            drekkana_planets[planet] = {"drekkana_sign": drekkana_sign}
        return drekkana_planets
    except KeyError as e:
        raise ValueError(f"Missing required kundali data: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Drekkana calculation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error in drekkana calculation: {str(e)}")

def calculate_saptamsa(kundali_data: Dict) -> Dict:
    """Calculate Saptamsa (D-7) chart positions for each planet."""
    saptamsa_planets = {}
    odd_signs = [0, 2, 4, 6, 8, 10]  # Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
    try:
        for planet, data in kundali_data["planets"].items():
            degrees_in_sign = data["degrees_in_sign"]
            rasi_sign_index = ZODIAC_SIGNS.index(data["sign"])
            part = math.ceil(degrees_in_sign / (30 / 7))  # 30/7 ≈ 4.2857° per part
            is_odd = rasi_sign_index in odd_signs
            if is_odd:
                sign_index = (rasi_sign_index + (part - 1)) % 12  # Start from same sign
            else:
                sign_index = (rasi_sign_index + 6 + (part - 1)) % 12  # Start from 7th sign
            saptamsa_sign = ZODIAC_SIGNS[sign_index]
            saptamsa_planets[planet] = {"saptamsa_sign": saptamsa_sign}
        return saptamsa_planets
    except KeyError as e:
        raise ValueError(f"Missing required kundali data: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Saptamsa calculation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error in drekkana calculation: {str(e)}")

def calculate_navamsa(kundali_data: Dict) -> Dict:
    navamsa_planets = {}
    # Define starting signs by element
    element_starts = {
        "fire": 0,   # Aries for Fire signs (Aries, Leo, Sagittarius)
        "earth": 9,  # Capricorn for Earth signs (Taurus, Virgo, Capricorn)
        "air": 6,    # Libra for Air signs (Gemini, Libra, Aquarius)
        "water": 3   # Cancer for Water signs (Cancer, Scorpio, Pisces)
    }
    sign_elements = [
    "fire", "earth", "air", "water"
]
    try:
        for planet, data in kundali_data["planets"].items():
            sid_longitude = data["longitude"]
            degrees_in_sign = sid_longitude % 30
            segment = int(degrees_in_sign / (30.0 / 9))  # 0-8
            orig_sign = int(sid_longitude / 30)
            element = sign_elements[(orig_sign+1)%4-1]
            start_sign = element_starts[element]
            new_sign_idx = (start_sign + segment) % 12
            navamsa_planets[planet] = {
                "navamsa_sign": ZODIAC_SIGNS[new_sign_idx],
                "navamsa_sign_index": new_sign_idx
            }
        return navamsa_planets
    except KeyError as e:
        raise ValueError(f"Missing required kundali data: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Drekkana calculation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error in drekkana calculation: {str(e)}")

def calculate_dwadasamsa(kundali_data: Dict) -> Dict:
    """Calculate Dwadasamsa (D-12) chart positions for each planet."""
    dwadasamsa_planets = {}
    try:
        for planet, data in kundali_data["planets"].items():
            degrees_in_sign = data["degrees_in_sign"]
            rasi_sign_index = ZODIAC_SIGNS.index(data["sign"])
            part = math.ceil(degrees_in_sign / (30 / 12))  # 30/12 = 2.5° per part
            sign_index = (rasi_sign_index + (part - 1)) % 12  # Start from same sign
            dwadasamsa_sign = ZODIAC_SIGNS[sign_index]
            dwadasamsa_planets[planet] = {"dwadasamsa_sign": dwadasamsa_sign}
        return dwadasamsa_planets
    except KeyError as e:
        raise ValueError(f"Missing required kundali data: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Drekkana calculation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error in drekkana calculation: {str(e)}")

def calculate_trimsamsa(kundali_data: Dict) -> Dict:
    """Calculate Trimsamsa (D-30) chart positions for each planet."""
    trimsamsa_planets = {}
    odd_signs = [0, 2, 4, 6, 8, 10]  # Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
    odd_ranges = [(0, 5, 0), (5, 10, 1), (10, 18, 2), (18, 25, 5), (25, 30, 6)]  # (start, end, sign_index)
    even_ranges = [(0, 5, 7), (5, 12, 8), (12, 20, 11), (20, 25, 9), (25, 30, 10)]  # Scorpio, Sagittarius, Pisces, Capricorn, Aquarius
    try:
        for planet, data in kundali_data["planets"].items():
            degrees_in_sign = data["degrees_in_sign"]
            rasi_sign_index = ZODIAC_SIGNS.index(data["sign"])
            is_odd = rasi_sign_index in odd_signs
            ranges = odd_ranges if is_odd else even_ranges
            trimsamsa_sign = None
            for start, end, sign_idx in ranges:
                if start <= degrees_in_sign < end:
                    trimsamsa_sign = ZODIAC_SIGNS[sign_idx]
                    break
            if trimsamsa_sign is None and degrees_in_sign == 30:  # Edge case for 30°
                trimsamsa_sign = ZODIAC_SIGNS[ranges[-1][2]]
            trimsamsa_planets[planet] = {"trimsamsa_sign": trimsamsa_sign}
        return trimsamsa_planets
    except KeyError as e:
        raise ValueError(f"Missing required kundali data: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Drekkana calculation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error in drekkana calculation: {str(e)}")