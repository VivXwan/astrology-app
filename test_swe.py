#!/usr/bin/env python3

import sys
print("Python Version:", sys.version)
print("Python Path:", sys.path)

try:
    import pyswisseph as swe
    print("Successfully imported pyswisseph")
    print("Dir:", dir(swe))
except Exception as e:
    print("Error importing pyswisseph:", str(e))
    import site
    print("Site packages:", site.getsitepackages())

try:
    import swisseph as swe
    print("Successfully imported swisseph")
    print("Dir:", dir(swe))
except Exception as e:
    print("Error importing swisseph:", str(e)) 