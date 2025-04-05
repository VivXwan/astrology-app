import swisseph as swe
swe.set_ephe_path('./ephe')

ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

# Vimshottari Dasha planetary sequence and durations
VIMSHOTTARI_PLANETS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_DURATIONS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}

NAKSHATRA_SPAN = 13 + 20 / 60  # 13.3333 degrees
NAKSHATRA_PADA_SPAN = 3 + 20 / 60  # 3.3333 degrees
DAYS_PER_YEAR = 365.2422  # As specified

NAKSHATRA_TO_PLANET = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

NAKSHATRA_BOUNDARIES = [(i * NAKSHATRA_SPAN, (i + 1) * NAKSHATRA_SPAN) for i in range(27)]

AYANAMSA_TYPES = {
    "true_chitra": swe.SIDM_TRUE_CITRA,
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI
}