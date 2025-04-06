# services.py
import swisseph as swe
from typing import Dict, Optional
from datetime import datetime, timedelta, timezone
from models import BirthData
from constants import ZODIAC_SIGNS, NAKSHATRAS, VIMSHOTTARI_PLANETS, VIMSHOTTARI_DURATIONS, NAKSHATRA_SPAN, NAKSHATRA_PADA_SPAN, DAYS_PER_YEAR, NAKSHATRA_TO_PLANET, NAKSHATRA_BOUNDARIES
from utils import decimal_to_dms, get_ayanamsa_value
from fastapi import HTTPException
import math

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
            "pada": int(lagna_pada)
        }

        for pid, name in planet_list:
            flags = swe.FLG_SWIEPH
            if pid == 10:  # True node for Rahu
                flags |= swe.FLG_TRUEPOS
            trop_longitude = swe.calc_ut(jd, pid, flags)[0][0]
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
                "pada": int(pada)
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
            "pada": int(ketu_pada)
        }

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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Calculation error: {str(e)}")

def calculate_kundali(data: BirthData, tz_offset: float, ayanamsa_type: Optional[str]) -> Dict:

    jd = swe.julday(data.year, data.month, data.day, data.hour + data.minute / 60.0 - tz_offset)
    ayanamsa = get_ayanamsa_value(jd, ayanamsa_type)
    
    # Calculate planetary positions
    kundali = calculate_planet_positions(data, jd, ayanamsa, ayanamsa_type)
    
    kundali["tz_offset"] = tz_offset
    
    return kundali

def calculate_transits(data: BirthData, tz_offset: float, date_time: Optional[datetime] = None, ayanamsa_type: Optional[str] = None) -> Dict:
    if date_time is None:
        date_time = datetime.now(timezone.utc)  # Use UTC for consistency with Swiss Ephemeris

    # Compute Julian Day for the given date/time
    jd = swe.julday(date_time.year, date_time.month, date_time.day, 
                    date_time.hour + date_time.minute / 60.0 + date_time.second / 3600.0 - tz_offset)
    ayanamsa = get_ayanamsa_value(jd, ayanamsa_type)

    # Calculate planetary positions
    transits = calculate_planet_positions(data, jd, ayanamsa, ayanamsa_type)

    transits["tz_offset"] = tz_offset
    transits["transit_date"] = date_time.strftime("%Y-%m-%d %H:%M:%S")

    return transits

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
        hora_planets[planet] = {"hora_sign": hora_sign}
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
        drekkana_planets[planet] = {"drekkana_sign": drekkana_sign}
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
        saptamsa_planets[planet] = {"saptamsa_sign": saptamsa_sign}
    return saptamsa_planets

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

def calculate_dwadasamsa(kundali_data: Dict) -> Dict:
    """Calculate Dwadasamsa (D-12) chart positions for each planet."""
    dwadasamsa_planets = {}
    for planet, data in kundali_data["planets"].items():
        degrees_in_sign = data["degrees_in_sign"]
        rasi_sign_index = ZODIAC_SIGNS.index(data["sign"])
        part = math.ceil(degrees_in_sign / (30 / 12))  # 30/12 = 2.5° per part
        sign_index = (rasi_sign_index + (part - 1)) % 12  # Start from same sign
        dwadasamsa_sign = ZODIAC_SIGNS[sign_index]
        dwadasamsa_planets[planet] = {"dwadasamsa_sign": dwadasamsa_sign}
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
        for start, end, sign_idx in ranges:
            if start <= degrees_in_sign < end:
                trimsamsa_sign = ZODIAC_SIGNS[sign_idx]
                break
        if trimsamsa_sign is None and degrees_in_sign == 30:  # Edge case for 30°
            trimsamsa_sign = ZODIAC_SIGNS[ranges[-1][2]]
        trimsamsa_planets[planet] = {"trimsamsa_sign": trimsamsa_sign}
    return trimsamsa_planets

def calculate_vimshottari_dasha(birth_data: BirthData, moon_data: Dict) -> list:
    moon_longitude = moon_data["longitude"]
    nakshatra_index = None
    for i, (start, end) in enumerate(NAKSHATRA_BOUNDARIES):
        if start <= moon_longitude < end:
            nakshatra_index = i
            break
    if nakshatra_index is None:
        nakshatra_index = 26  # Revati (last Nakshatra) if at 360°
    nakshatra_deg = moon_longitude - NAKSHATRA_BOUNDARIES[nakshatra_index][0]

    # Step 2: Map Nakshatra to starting Dasha planet
    starting_planet = NAKSHATRA_TO_PLANET[(nakshatra_index+1)%9-1]
    starting_planet_index = VIMSHOTTARI_PLANETS.index(starting_planet)

    # Step 3: Calculate balance of the first Dasha
    remaining_deg = NAKSHATRA_SPAN - nakshatra_deg
    proportion = remaining_deg / NAKSHATRA_SPAN
    total_duration = VIMSHOTTARI_DURATIONS[starting_planet]
    balance_years = proportion * total_duration
    balance_days = balance_years * DAYS_PER_YEAR

    # Step 4: Calculate elapsed time and start of first Mahadasha
    elapsed_years = total_duration - balance_years
    elapsed_days = elapsed_years * DAYS_PER_YEAR
    birth_date = datetime(birth_data.year, birth_data.month, birth_data.day)
    first_mahadasha_start = birth_date - timedelta(days=elapsed_days)
    first_mahadasha_end = first_mahadasha_start + timedelta(days=total_duration * DAYS_PER_YEAR)

    # Step 5: Generate Mahadasha timeline
    dasha_timeline = []
    current_date = first_mahadasha_start
    remaining_years = 120
    planet_index = starting_planet_index
    
    while remaining_years > 0:
        planet = VIMSHOTTARI_PLANETS[planet_index]
        duration = VIMSHOTTARI_DURATIONS[planet]
        if duration > remaining_years:
            duration = remaining_years
        end_date = current_date + timedelta(days=duration * 365.25)
        
        # Calculate Antardashas for this Mahadasha
        mahadasha_entry = {
            "planet": planet,
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_years": round(duration, 2),
            "antardashas": []
        }
        
        antardasha_start = current_date
        for i in range(9):
            antardasha_planet = VIMSHOTTARI_PLANETS[(planet_index + i) % 9]
            antardasha_years = (duration * VIMSHOTTARI_DURATIONS[antardasha_planet]) / 120
            antardasha_days = antardasha_years * 365.25
            antardasha_end = antardasha_start + timedelta(days=antardasha_days)

            # Calculate Pratyantar Dashas for this Antardasha
            antardasha_pratyantar = []
            pratyantar_start = antardasha_start
            for j in range(9):
                pratyantar_planet = VIMSHOTTARI_PLANETS[(planet_index + i + j) % 9]
                pratyantar_years = (antardasha_years * VIMSHOTTARI_DURATIONS[pratyantar_planet]) / 120
                pratyantar_days = pratyantar_years * 365.25
                pratyantar_end = pratyantar_start + timedelta(days=pratyantar_days)
                antardasha_pratyantar.append({
                    "planet": pratyantar_planet,
                    "start_date": pratyantar_start.strftime("%Y-%m-%d"),
                    "end_date": pratyantar_end.strftime("%Y-%m-%d"),
                    "duration_days": round(pratyantar_days, 2)
                })
                pratyantar_start = pratyantar_end

            mahadasha_entry["antardashas"].append({
                "planet": antardasha_planet,
                "start_date": antardasha_start.strftime("%Y-%m-%d"),
                "end_date": antardasha_end.strftime("%Y-%m-%d"),
                "duration_years": round(antardasha_years, 2),
                "pratyantar_dashas": antardasha_pratyantar
            })
            antardasha_start = antardasha_end

        dasha_timeline.append(mahadasha_entry)
        current_date = end_date
        remaining_years -= duration
        planet_index = (planet_index + 1) % len(VIMSHOTTARI_PLANETS)

    return dasha_timeline

def calculate_sthana_bala(kundali_data: Dict, hora: Dict, drekkana: Dict, saptamsa: Dict, navamsa: Dict, dwadasamsa: Dict, trimsamsa: Dict) -> Dict:
    """Calculate Sthana Bala for each planet with all subcomponents."""
    sthana_bala = {}
    
    # Exaltation points (sign_index, degree)
    exaltation_points = {
        "Sun": (0, 10), "Moon": (1, 3), "Mars": (9, 28), "Mercury": (5, 15),
        "Jupiter": (3, 5), "Venus": (11, 27), "Saturn": (6, 20),
        "Rahu": (1, 20), "Ketu": (7, 20)
    }
    
    # Dignity points for Saptavargaja Bala
    dignity_points = {
        "exaltation": 30, "moolatrikona": 25, "own": 20, "great_friend": 15,
        "friend": 10, "neutral": 5, "enemy": 4, "great_enemy": 3, "debilitation": 2
    }
    
    # Moolatrikona signs
    moolatrikona_signs = {
        "Sun": "Leo", "Moon": "Taurus", "Mars": "Aries", "Mercury": "Virgo",
        "Jupiter": "Sagittarius", "Venus": "Libra", "Saturn": "Aquarius"
    }
    
    # Friendship and enmity tables (complete for accuracy)
    friends = {
        "Sun": ["Moon", "Mars", "Jupiter"], "Moon": ["Sun", "Mercury"],
        "Mars": ["Sun", "Moon", "Jupiter"], "Mercury": ["Sun", "Venus"],
        "Jupiter": ["Sun", "Moon", "Mars"], "Venus": ["Mercury", "Saturn"],
        "Saturn": ["Mercury", "Venus"]
    }
    enemies = {
        "Sun": ["Venus", "Saturn"], "Moon": ["Mars", "Jupiter", "Saturn", "Venus"],
        "Mars": ["Mercury"], "Mercury": ["Moon"], "Jupiter": ["Mercury", "Venus"],
        "Venus": ["Sun", "Moon"], "Saturn": ["Sun", "Moon", "Mars"]
    }
    great_friends = {
        "Sun": ["Jupiter"], "Moon": ["Mercury"], "Mars": ["Jupiter"],
        "Mercury": ["Venus"], "Jupiter": ["Sun"], "Venus": ["Saturn"],
        "Saturn": ["Venus"]
    }
    great_enemies = {
        "Sun": ["Saturn"], "Moon": [], "Mars": [], "Mercury": [],
        "Jupiter": [], "Venus": [], "Saturn": ["Mars"]
    }
    
    odd_signs = [0, 2, 4, 6, 8, 10]  # Aries, Gemini, Leo, Libra, Sagittarius, Aquarius
    male_planets = ["Sun", "Mars", "Jupiter"]
    female_planets = ["Moon", "Venus"]
    
    for planet, data in kundali_data["planets"].items():
        rasi_sign = data["sign"]
        rasi_sign_idx = ZODIAC_SIGNS.index(rasi_sign)
        degrees_in_sign = data["degrees_in_sign"]
        
        # Uchcha Bala
        if planet in exaltation_points:
            exalt_sign_idx, exalt_deg = exaltation_points[planet]
            exalt_long = exalt_sign_idx * 30 + exalt_deg
            planet_long = rasi_sign_idx * 30 + degrees_in_sign
            angular_distance = min((planet_long - exalt_long) % 360, (exalt_long - planet_long) % 360)
            uchcha_bala_shashtiamsha = 60 * (1 - angular_distance / 180)
            uchcha_bala = uchcha_bala_shashtiamsha / 60  # convert to rupas.
        else:
            uchcha_bala_shashtiamsha = 0
            uchcha_bala = 0
        
        # Saptavargaja Bala
        varga_signs = [
            rasi_sign, hora[planet]["hora_sign"], drekkana[planet]["drekkana_sign"],
            saptamsa[planet]["saptamsa_sign"], navamsa[planet]["navamsa_sign"],
            dwadasamsa[planet]["dwadasamsa_sign"], trimsamsa[planet]["trimsamsa_sign"]
        ]
        total_points = 0
        for varga_sign in varga_signs:
            if planet in exaltation_points and ZODIAC_SIGNS[exaltation_points[planet][0]] == varga_sign:
                total_points += dignity_points["exaltation"]
            elif planet in moolatrikona_signs and moolatrikona_signs[planet] == varga_sign:
                total_points += dignity_points["moolatrikona"]
            elif (planet == "Jupiter" and varga_sign in ["Sagittarius", "Pisces"]) or \
                 (planet == "Sun" and varga_sign == "Leo") or \
                 (planet == "Moon" and varga_sign == "Cancer") or \
                 (planet == "Mars" and varga_sign in ["Aries", "Scorpio"]) or \
                 (planet == "Mercury" and varga_sign in ["Gemini", "Virgo"]) or \
                 (planet == "Venus" and varga_sign in ["Taurus", "Libra"]) or \
                 (planet == "Saturn" and varga_sign in ["Capricorn", "Aquarius"]):
                total_points += dignity_points["own"]
            elif planet in great_friends and varga_sign in great_friends[planet]:
                total_points += dignity_points["great_friend"]
            elif planet in friends and varga_sign in friends[planet]:
                total_points += dignity_points["friend"]
            elif planet in great_enemies and varga_sign in great_enemies[planet]:
                total_points += dignity_points["great_enemy"]
            elif planet in enemies and varga_sign in enemies[planet]:
                total_points += dignity_points["enemy"]
            else:
                total_points += dignity_points["neutral"]
        saptavargaja_bala_shashtiamsha = total_points / 7  # Average over 7 vargas
        saptavargaja_bala = saptavargaja_bala_shashtiamsha / 60  # convert to rupas.
        
        # Oja-Yugma Bala
        rasi_is_odd = rasi_sign_idx in odd_signs
        navamsa_is_odd = ZODIAC_SIGNS.index(navamsa[planet]["navamsa_sign"]) in odd_signs
        oja_yugma_bala_shashtiamsha = 0
        if planet in male_planets:
            if rasi_is_odd:
                oja_yugma_bala_shashtiamsha += 15
            if navamsa_is_odd:
                oja_yugma_bala_shashtiamsha += 15
        elif planet in female_planets:
            if not rasi_is_odd:
                oja_yugma_bala_shashtiamsha += 15
            if not navamsa_is_odd:
                oja_yugma_bala_shashtiamsha += 15
        else:  # Mercury, Saturn
            if rasi_is_odd:
                oja_yugma_bala_shashtiamsha += 15
            if navamsa_is_odd:
                oja_yugma_bala_shashtiamsha += 15
        oja_yugma_bala = oja_yugma_bala_shashtiamsha / 60
        
        # Kendradi Bala
        house_number = (rasi_sign_idx - ZODIAC_SIGNS.index(kundali_data["ascendant"]["sign"]) + 12) % 12 + 1
        kendradi_bala_shashtiamsha = 60 if house_number in [1, 4, 7, 10] else 30 if house_number in [2, 5, 8, 11] else 15
        kendradi_bala = kendradi_bala_shashtiamsha / 60
        
        # Drekkana Bala
        drekkana_part = math.ceil(degrees_in_sign / 10)
        drekkana_bala_shashtiamsha = 0
        if planet in male_planets and drekkana_part == 1:
            drekkana_bala_shashtiamsha = 15
        elif planet in female_planets and drekkana_part == 2:
            drekkana_bala_shashtiamsha = 15
        elif planet not in male_planets and planet not in female_planets and drekkana_part == 3:
            drekkana_bala_shashtiamsha = 15
        drekkana_bala = drekkana_bala_shashtiamsha / 60
        
        # Total Sthana Bala
        total_sthana_bala_shashtiamsha = uchcha_bala_shashtiamsha + saptavargaja_bala_shashtiamsha + oja_yugma_bala_shashtiamsha + kendradi_bala_shashtiamsha + drekkana_bala_shashtiamsha
        total_sthana_bala = uchcha_bala + saptavargaja_bala + oja_yugma_bala + kendradi_bala + drekkana_bala
        
        sthana_bala[planet] = {
            "uchcha_bala": {"rupas": round(uchcha_bala, 3), "shashtiamshas": round(uchcha_bala_shashtiamsha, 3)},
            "saptavargaja_bala": {"rupas": round(saptavargaja_bala, 3), "shashtiamshas": round(saptavargaja_bala_shashtiamsha, 3)},
            "oja_yugma_bala": {"rupas": round(oja_yugma_bala, 3), "shashtiamshas": round(oja_yugma_bala_shashtiamsha, 3)},
            "kendradi_bala": {"rupas": round(kendradi_bala, 3), "shashtiamshas": round(kendradi_bala_shashtiamsha, 3)},
            "drekkana_bala": {"rupas": round(drekkana_bala, 3), "shashtiamshas": round(drekkana_bala_shashtiamsha, 3)},
            "total": {"rupas": round(total_sthana_bala, 3), "shashtiamshas": round(total_sthana_bala_shashtiamsha, 3)}
        }
    
    return sthana_bala

def calculate_dig_bala(kundali_data: Dict) -> Dict:
    """Calculate Dig Bala for each planet based on house position."""
    dig_bala = {}
    
    # Preferred houses (1-based: 1=1st, 4=4th, 7=7th, 10=10th)
    preferred_houses = {
        "Sun": 10, "Moon": 4, "Mars": 10, "Mercury": 1,
        "Jupiter": 1, "Venus": 4, "Saturn": 7
    }
    
    ascendant_sign_idx = ZODIAC_SIGNS.index(kundali_data["ascendant"]["sign"])
    
    for planet, data in kundali_data["planets"].items():

        # Calculate Dig Bala
        if planet in preferred_houses:
            preferred_house = preferred_houses[planet]
            angular_distance = min(abs(kundali_data["planets"][planet]["house"] - preferred_house), 12 - abs(kundali_data["planets"][planet]["house"] - preferred_house)) * 30
            dig_bala_rupas = 1 - (angular_distance / 180)
            dig_bala_shashtiamsha = dig_bala_rupas * 60
            dig_bala[planet] = {"rupas": round(dig_bala_rupas, 3), "shashtiamshas": round(dig_bala_shashtiamsha, 3)}
        else:
            dig_bala[planet] = {"rupas": 0, "shashtiamshas": 0}  # Default for unexpected cases
    
    return dig_bala