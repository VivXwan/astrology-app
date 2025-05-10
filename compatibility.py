"""
Compatibility layer for Swiss Ephemeris.
This module attempts to use pyswisseph (the proper package) first,
then falls back to swisseph (placeholder) if needed.
"""

try:
    import pyswisseph as swe
    # print("Successfully loaded pyswisseph library")
    USING_PYSWISSEPH = True
except ImportError:
    import swisseph as swe
    # print("Falling back to swisseph placeholder library")
    USING_PYSWISSEPH = False

# Export the swe module for use by other modules
__all__ = ['swe', 'USING_PYSWISSEPH'] 