#!/usr/bin/env python3

import swisseph as swe
from datetime import datetime

# Set ephemeris path
swe.set_ephe_path('./ephe')

# Test basic functions
print("Testing swisseph functionality:")

# Get current Julian Day
now = datetime.now()
jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0 + now.second/3600.0)
print(f"Current Julian Day: {jd}")

# Get Sun position
flags = swe.FLG_SWIEPH | swe.FLG_SPEED
sun_pos = swe.calc_ut(jd, 0, flags)
print(f"Sun position: {sun_pos}")

# Get Moon position
moon_pos = swe.calc_ut(jd, 1, flags)
print(f"Moon position: {moon_pos}")

# Get ayanamsa
swe.set_sid_mode(swe.SIDM_TRUE_CITRA, 0, 0)
ayanamsa = swe.get_ayanamsa_ut(jd)
print(f"Ayanamsa (True Chitrapaksha): {ayanamsa}")

# Calculate house cusps
cusps, ascmc = swe.houses(jd, 13.0827, 80.2707, b'P')  # Chennai, India
print(f"Ascendant: {ascmc[0]}")
print(f"Midheaven: {ascmc[1]}")
print(f"House cusps: {cusps[:3]}...") 