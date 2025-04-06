from typing import Dict
import math
from constants import ZODIAC_SIGNS

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
    try:
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
    except KeyError as e:
        raise ValueError(f"Missing required data for sthana bala: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Sthana bala calculation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error in sthana bala calculation: {str(e)}")

def calculate_dig_bala(kundali_data: Dict) -> Dict:
    """Calculate Dig Bala for each planet based on house position."""
    dig_bala = {}
    
    # Preferred houses (1-based: 1=1st, 4=4th, 7=7th, 10=10th)
    preferred_houses = {
        "Sun": 10, "Moon": 4, "Mars": 10, "Mercury": 1,
        "Jupiter": 1, "Venus": 4, "Saturn": 7
    }
    try:
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
    except KeyError as e:
        raise ValueError(f"Missing required data for dig bala: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Dig bala calculation failed: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error in dig bala calculation: {str(e)}")