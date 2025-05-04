from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import functools
from models import BirthData
from constants import VIMSHOTTARI_PLANETS, VIMSHOTTARI_DURATIONS, NAKSHATRA_SPAN, DAYS_PER_YEAR, NAKSHATRA_TO_PLANET, NAKSHATRA_BOUNDARIES

# LRU Cache for dasha calculations - will store up to 128 results
@functools.lru_cache(maxsize=128)
def cached_dasha_periods(birth_year: int, birth_month: int, birth_day: int, 
                         moon_longitude: float, max_level: int) -> List:
    """
    Cached version of the dasha calculation that uses hashable parameters.
    
    Args:
        birth_year, birth_month, birth_day: Birth date components
        moon_longitude: Moon's longitude at birth
        max_level: Maximum level of sub-dashas to calculate
        
    Returns:
        List of dasha periods
    """
    # Create a datetime object from the components
    birth_date = datetime(birth_year, birth_month, birth_day)
    
    # Find nakshatra information
    nakshatra_index = None
    for i, (start, end) in enumerate(NAKSHATRA_BOUNDARIES):
        if start <= moon_longitude < end:
            nakshatra_index = i
            break
    if nakshatra_index is None:
        nakshatra_index = 26  # Revati (last Nakshatra) if at 360°
    
    nakshatra_deg = moon_longitude - NAKSHATRA_BOUNDARIES[nakshatra_index][0]
    
    # Map Nakshatra to starting Dasha planet
    starting_planet = NAKSHATRA_TO_PLANET[(nakshatra_index+1)%9-1]
    starting_planet_index = VIMSHOTTARI_PLANETS.index(starting_planet)
    
    # Calculate balance of the first Dasha
    remaining_deg = NAKSHATRA_SPAN - nakshatra_deg
    proportion = remaining_deg / NAKSHATRA_SPAN
    total_duration = VIMSHOTTARI_DURATIONS[starting_planet]
    balance_years = proportion * total_duration
    
    # Calculate elapsed time and start of first Mahadasha
    elapsed_years = total_duration - balance_years
    elapsed_days = elapsed_years * DAYS_PER_YEAR
    first_mahadasha_start = birth_date - timedelta(days=elapsed_days)
    
    # Generate the dasha timeline using optimized methods
    return generate_dasha_timeline(
        first_mahadasha_start, 
        starting_planet_index,
        max_level
    )

def generate_dasha_timeline(start_date: datetime, planet_index: int, max_level: int) -> List:
    """
    Generates the complete dasha timeline starting from the given date and planet.
    
    Args:
        start_date: The start date for the first mahadasha
        planet_index: The index of the first mahadasha lord
        max_level: Maximum dasha level to calculate
        
    Returns:
        List of dasha periods
    """
    dasha_timeline = []
    current_date = start_date
    remaining_years = 120  # Total Vimshottari cycle
    current_planet_index = planet_index
    
    # Pre-calculate actual end dates for better performance
    while remaining_years > 0:
        planet = VIMSHOTTARI_PLANETS[current_planet_index]
        duration = VIMSHOTTARI_DURATIONS[planet]
        if duration > remaining_years:
            duration = remaining_years
        
        # Calculate this Mahadasha and its sub-periods
        mahadasha_end = current_date + timedelta(days=duration * 365.25)
        
        # Use optimized recursive calculation
        mahadasha = calculate_dasha_period(
            planet, 
            current_date,
            mahadasha_end,
            current_planet_index,
            0,
            max_level
        )
        
        dasha_timeline.append(mahadasha)
        
        # Update for next iteration
        current_date = mahadasha_end
        remaining_years -= duration
        current_planet_index = (current_planet_index + 1) % len(VIMSHOTTARI_PLANETS)
    
    return dasha_timeline

def calculate_dasha_period(planet: str, start_date: datetime, end_date: datetime, 
                          planet_index: int, level: int, max_level: int) -> Dict:
    """
    Optimized function to calculate a dasha period and its sub-periods.
    
    Args:
        planet: The dasha lord planet
        start_date: Period start date
        end_date: Period end date
        planet_index: Index of the planet in the Vimshottari sequence
        level: Current dasha level (0=Mahadasha, etc.)
        max_level: Maximum level to calculate
        
    Returns:
        Dict with dasha period information
    """
    # Base result with essential data only
    result = {
        "planet": planet,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    # No sub-periods if at max level or only calculating Mahadashas
    if level >= max_level or max_level == 0:
        return result
    
    # Determine the key for this level's sub-periods
    sub_keys = [
        "antardashas", 
        "pratyantar_dashas", 
        "sookshma_dashas", 
        "prana_dashas", 
        "deha_dashas"
    ]
    
    sub_key = sub_keys[level]
    result[sub_key] = []
    
    # Calculate duration in days and years
    duration_days = (end_date - start_date).total_seconds() / 86400
    duration_years = duration_days / 365.25
    
    # Iterate through the sub-periods
    sub_start = start_date
    for i in range(9):
        sub_planet_index = (planet_index + i) % 9
        sub_planet = VIMSHOTTARI_PLANETS[sub_planet_index]
        
        # Calculate sub-period duration
        sub_duration_years = (duration_years * VIMSHOTTARI_DURATIONS[sub_planet]) / 120
        sub_duration_days = sub_duration_years * 365.25
        sub_end = sub_start + timedelta(days=sub_duration_days)
        
        # Create the sub-period recursively
        sub_period = calculate_dasha_period(
            sub_planet,
            sub_start,
            sub_end,
            sub_planet_index,
            level + 1,
            max_level
        )
        
        result[sub_key].append(sub_period)
        sub_start = sub_end
    
    return result

def calculate_vimshottari_dasha(birth_data: BirthData, moon_data: Dict, max_level: int = 2) -> list:
    """
    Calculate the Vimshottari Dasha periods based on the Moon's position at birth.
    
    Args:
        birth_data (BirthData): Birth details including date, time, and location.
        moon_data (Dict): Moon's position data including longitude.
        max_level (int, optional): Maximum level of sub-dashas to calculate.
                                  0 = Only Mahadasha
                                  1 = Mahadasha + Antardasha
                                  2 = Mahadasha + Antardasha + Pratyantar
                                  3 = Adding Sookshma
                                  4 = Adding Prana
                                  5 = Adding Deha (full calculation)
                                  Defaults to 2 (up to Pratyantar).
    
    Returns:
        list: A hierarchical list of dasha periods.
    """
    try:
        # Ensure max_level is valid
        if max_level < 0 or max_level > 5:
            max_level = 2  # Default to Pratyantar level if invalid
        
        # Extract the key values for caching
        moon_longitude = moon_data["longitude"]
        
        # Use the cached function
        return cached_dasha_periods(
            birth_data.year,
            birth_data.month,
            birth_data.day,
            moon_longitude,
            max_level
        )
    except KeyError as e:
        raise ValueError(f"Missing required moon data: {str(e)}")
    except ValueError as e:
        raise ValueError(f"Dasha calculation failed: {str(e)}")
    except TypeError as e:
        raise ValueError(f"Invalid data type in dasha calculation: {str(e)}")
    except Exception as e:
        raise ValueError(f"Unexpected error in dasha calculation: {str(e)}")

# For backward compatibility
def calculate_sub_dasha_periods(start_date, duration_years, planet_index, level=0, max_level=2):
    """
    Helper function to recursively calculate sub-dasha periods based on the level.
    Maintained for backward compatibility.
    
    Args:
        start_date (datetime): Start date of the parent dasha
        duration_years (float): Duration of the parent dasha in years
        planet_index (int): Index of the starting planet for this dasha
        level (int): Current dasha level (0=Mahadasha, 1=Antardasha, etc.)
        max_level (int): Maximum dasha level to calculate (5 would include Deha Dasha)
        
    Returns:
        dict: Nested dictionary of dasha periods
    """
    if level > max_level:
        return None
    
    duration_days = duration_years * 365.25
    end_date = start_date + timedelta(days=duration_days)
    planet = VIMSHOTTARI_PLANETS[planet_index % 9]
    
    return calculate_dasha_period(
        planet,
        start_date,
        end_date,
        planet_index,
        level,
        max_level
    )