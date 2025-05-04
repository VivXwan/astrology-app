#!/usr/bin/env python3

print("Testing Swiss Ephemeris compatibility layer:")

# Import the compatibility layer
from compatibility import swe, USING_PYSWISSEPH

# Print which package we're actually using
print(f"Using pyswisseph: {USING_PYSWISSEPH}")

# Set ephemeris path
swe.set_ephe_path('./ephe')

# Test basic Swiss Ephemeris functionality
jd = swe.julday(2023, 1, 1, 12.0)
print(f"Julian Day for 2023-01-01 12:00: {jd}")

# Test planet position calculation
flags = swe.FLG_SWIEPH | swe.FLG_SPEED
sun_pos = swe.calc_ut(jd, 0, flags)
print(f"Sun position: {sun_pos}")

# Test ayanamsa calculation
swe.set_sid_mode(swe.SIDM_TRUE_CITRA, 0, 0)
ayanamsa = swe.get_ayanamsa_ut(jd)
print(f"Ayanamsa (True Chitrapaksha): {ayanamsa}")

print("All tests completed successfully!") 