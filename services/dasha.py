from typing import Dict, List
from datetime import datetime, timedelta
from models import BirthData
from constants import VIMSHOTTARI_PLANETS, VIMSHOTTARI_DURATIONS, NAKSHATRA_SPAN, DAYS_PER_YEAR, NAKSHATRA_TO_PLANET, NAKSHATRA_BOUNDARIES

def calculate_vimshottari_dasha(birth_data: BirthData, moon_data: Dict) -> list:
    try:
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
    except KeyError as e:
        raise ValueError(f"Missing required moon data: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Dasha calculation failed: {str(e)}")
    except TypeError as e:
        raise ValueError(f"Invalid data type in dasha calculation: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error in dasha calculation: {str(e)}")