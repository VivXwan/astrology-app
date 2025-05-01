from typing import Dict
import math
from constants import ZODIAC_SIGNS

def calculate_hora(kundali_data: Dict) -> Dict:
    """Calculate Hora (D-2) chart positions for each planet."""
    hora_planets = {}
    odd_signs = [0, 2, 4, 6, 8, 10]  # Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
    
    for planet, data in kundali_data["planets"].items():
        degrees_in_sign = data["degrees_in_sign"]
        rasi_sign_index = ZODIAC_SIGNS.index(data["sign"])
        is_odd = rasi_sign_index in odd_signs
        part = math.ceil(degrees_in_sign / 15)  # 15° per part
        if is_odd:
            hora_sign = "Leo" if part == 1 else "Cancer"  # 0°-15°: Leo, 15°-30°: Cancer
        else:
            hora_sign = "Cancer" if part == 1 else "Leo"  # 0°-15°: Cancer, 15°-30°: Leo
        
        hora_sign_idx = ZODIAC_SIGNS.index(hora_sign)
        if planet == "Lagna":
            ascendant_sign_idx = hora_sign_idx
        house_number = (hora_sign_idx - ascendant_sign_idx + 12) % 12 + 1
        
        hora_planets[planet] = {
            "sign": hora_sign,
            "sign_index": hora_sign_idx,
            "house": house_number
        }
    return hora_planets

def calculate_drekkana(kundali_data: Dict) -> Dict:
    """Calculate Drekkana (D-3) chart positions for each planet."""
    drekkana_planets = {}
    
    for planet, data in kundali_data["planets"].items():
        degrees_in_sign = data["degrees_in_sign"]
        rasi_sign_index = ZODIAC_SIGNS.index(data["sign"])
        part = math.ceil(degrees_in_sign / 10)  # 10° per part
        sign_index = (rasi_sign_index + (part - 1) * 4) % 12  # Formula: (Rasi + (Part-1)*4) mod 12
        drekkana_sign = ZODIAC_SIGNS[sign_index]
        if planet == "Lagna":
            ascendant_sign_idx = sign_index
        house_number = (sign_index - ascendant_sign_idx + 12) % 12 + 1
        
        drekkana_planets[planet] = {
            "sign": drekkana_sign,
            "sign_index": sign_index,
            "house": house_number
        }
    return drekkana_planets

def calculate_saptamsa(kundali_data: Dict) -> Dict:
    """Calculate Saptamsa (D-7) chart positions for each planet."""
    saptamsa_planets = {}
    odd_signs = [0, 2, 4, 6, 8, 10]  # Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
    
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
        if planet == "Lagna":
            ascendant_sign_idx = sign_index
        house_number = (sign_index - ascendant_sign_idx + 12) % 12 + 1
        
        saptamsa_planets[planet] = {
            "sign": saptamsa_sign,
            "sign_index": sign_index,
            "house": house_number
        }
    return saptamsa_planets

def calculate_navamsa(kundali_data: Dict) -> Dict:
    """Calculate Navamsa (D-9) chart positions for each planet."""
    navamsa_planets = {}
    # Define starting signs by element
    element_starts = {
        "fire": 0,   # Aries for Fire signs (Aries, Leo, Sagittarius)
        "earth": 9,  # Capricorn for Earth signs (Taurus, Virgo, Capricorn)
        "air": 6,    # Libra for Air signs (Gemini, Libra, Aquarius)
        "water": 3   # Cancer for Water signs (Cancer, Scorpio, Pisces)
    }
    sign_elements = ["fire", "earth", "air", "water"]
    
    for planet, data in kundali_data["planets"].items():
        sid_longitude = data["longitude"]
        degrees_in_sign = sid_longitude % 30
        segment = int(degrees_in_sign / (30.0 / 9))  # 0-8
        orig_sign = int(sid_longitude / 30)
        element = sign_elements[(orig_sign+1)%4-1]
        start_sign = element_starts[element]
        new_sign_idx = (start_sign + segment) % 12
        navamsa_sign = ZODIAC_SIGNS[new_sign_idx]
        if planet == "Lagna":
            ascendant_sign_idx = new_sign_idx
        house_number = (new_sign_idx - ascendant_sign_idx + 12) % 12 + 1
        
        navamsa_planets[planet] = {
            "sign": navamsa_sign,
            "sign_index": new_sign_idx,
            "house": house_number
        }
    return navamsa_planets

def calculate_dwadasamsa(kundali_data: Dict) -> Dict:
    """Calculate Dwadasamsa (D-12) chart positions for each planet."""
    dwadasamsa_planets = {}
    
    for planet, data in kundali_data["planets"].items():
        degrees_in_sign = data["degrees_in_sign"]
        rasi_sign_index = ZODIAC_SIGNS.index(data["sign"])
        part = math.ceil(degrees_in_sign / (30 / 12))  # 30/12 = 2.5° per part
        sign_index = (rasi_sign_index + (part - 1)) % 12  # Start from same sign
        dwadasamsa_sign = ZODIAC_SIGNS[sign_index]
        if planet == "Lagna":
            ascendant_sign_idx = sign_index
        house_number = (sign_index - ascendant_sign_idx + 12) % 12 + 1
        
        dwadasamsa_planets[planet] = {
            "sign": dwadasamsa_sign,
            "sign_index": sign_index,
            "house": house_number
        }
    return dwadasamsa_planets

def calculate_trimsamsa(kundali_data: Dict) -> Dict:
    """Calculate Trimsamsa (D-30) chart positions for each planet."""
    trimsamsa_planets = {}
    odd_signs = [0, 2, 4, 6, 8, 10]  # Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
    odd_ranges = [(0, 5, 0), (5, 10, 1), (10, 18, 2), (18, 25, 5), (25, 30, 6)]  # (start, end, sign_index)
    even_ranges = [(0, 5, 7), (5, 12, 8), (12, 20, 11), (20, 25, 9), (25, 30, 10)]  # Scorpio, Sagittarius, Pisces, Capricorn, Aquarius
    
    for planet, data in kundali_data["planets"].items():
        degrees_in_sign = data["degrees_in_sign"]
        rasi_sign_index = ZODIAC_SIGNS.index(data["sign"])
        is_odd = rasi_sign_index in odd_signs
        ranges = odd_ranges if is_odd else even_ranges
        trimsamsa_sign = None
        sign_index = None
        
        for start, end, idx in ranges:
            if start <= degrees_in_sign < end:
                trimsamsa_sign = ZODIAC_SIGNS[idx]
                sign_index = idx
                break
                
        if trimsamsa_sign is None and degrees_in_sign == 30:  # Edge case for 30°
            trimsamsa_sign = ZODIAC_SIGNS[ranges[-1][2]]
            sign_index = ranges[-1][2]
            
        if planet == "Lagna":
            ascendant_sign_idx = sign_index
        house_number = (sign_index - ascendant_sign_idx + 12) % 12 + 1
        
        trimsamsa_planets[planet] = {
            "sign": trimsamsa_sign,
            "sign_index": sign_index,
            "house": house_number
        }
    return trimsamsa_planets