"""Seed data for reference tables (species, breeds, districts).

Pure functions returning plain dicts -- no ORM or DB dependency.
Used by bootstrap scripts and tests.
"""


def get_seed_species() -> list[dict]:
    """All livestock species tracked by PashuRaksha."""
    return [
        {
            "code": "cattle",
            "name_en": "Cattle",
            "name_kn": "ಹಸು",
            "name_hi": "ग௨ય",
            "emoji": "\U0001f404",
        },
        {
            "code": "buffalo",
            "name_en": "Buffalo",
            "name_kn": "ಎಮ್ಮೆ",
            "name_hi": "भैंस",
            "emoji": "\U0001f403",
        },
        {
            "code": "goat",
            "name_en": "Goat",
            "name_kn": "ಮೇಕೆ",
            "name_hi": "बकरी",
            "emoji": "\U0001f410",
        },
        {
            "code": "sheep",
            "name_en": "Sheep",
            "name_kn": "ಕುರಿ",
            "name_hi": "भेड़",
            "emoji": "\U0001f411",
        },
        {
            "code": "poultry",
            "name_en": "Poultry",
            "name_kn": "ಕೋಳಿ",
            "name_hi": "मुर्गी",
            "emoji": "\U0001f414",
        },
    ]


def _breed(
    name: str,
    species: str,
    origin: str,
    *,
    indigenous: bool = True,
    nbagr: str | None = None,
) -> dict:
    return {
        "name": name,
        "species_code": species,
        "origin": origin,
        "is_indigenous": indigenous,
        "nbagr_code": nbagr,
    }


def get_seed_breeds() -> list[dict]:
    """Breeds relevant to Karnataka and wider India."""
    return [
        # Cattle -- Karnataka-local + national + exotic
        _breed("Hallikar", "cattle", "Karnataka",
               nbagr="INDIA_CATTLE_0600"),
        _breed("Amrit Mahal", "cattle", "Karnataka",
               nbagr="INDIA_CATTLE_0100"),
        _breed("Khillari", "cattle", "Maharashtra",
               nbagr="INDIA_CATTLE_0800"),
        _breed("Deoni", "cattle", "Maharashtra",
               nbagr="INDIA_CATTLE_0400"),
        _breed("Krishna Valley", "cattle", "Karnataka",
               nbagr="INDIA_CATTLE_0900"),
        _breed("Gir", "cattle", "Gujarat",
               nbagr="INDIA_CATTLE_0500"),
        _breed("Sahiwal", "cattle", "Punjab",
               nbagr="INDIA_CATTLE_1400"),
        _breed("Red Sindhi", "cattle", "Sindh",
               nbagr="INDIA_CATTLE_1300"),
        _breed("Tharparkar", "cattle", "Rajasthan",
               nbagr="INDIA_CATTLE_1700"),
        _breed("Kangayam", "cattle", "Tamil Nadu",
               nbagr="INDIA_CATTLE_0700"),
        _breed("Holstein Friesian", "cattle", "Netherlands",
               indigenous=False),
        _breed("Jersey", "cattle", "Jersey, UK",
               indigenous=False),
        _breed("HF Cross", "cattle", "India",
               indigenous=False),
        # Buffalo
        _breed("Murrah", "buffalo", "Haryana",
               nbagr="INDIA_BUFFALO_0500"),
        _breed("Jaffarabadi", "buffalo", "Gujarat",
               nbagr="INDIA_BUFFALO_0200"),
        _breed("Surti", "buffalo", "Gujarat",
               nbagr="INDIA_BUFFALO_0700"),
        # Goat
        _breed("Osmanabadi", "goat", "Maharashtra",
               nbagr="INDIA_GOAT_1900"),
        _breed("Beetal", "goat", "Punjab",
               nbagr="INDIA_GOAT_0400"),
        _breed("Jamunapari", "goat", "Uttar Pradesh",
               nbagr="INDIA_GOAT_1200"),
        _breed("Sirohi", "goat", "Rajasthan",
               nbagr="INDIA_GOAT_2500"),
        _breed("Black Bengal", "goat", "West Bengal",
               nbagr="INDIA_GOAT_0500"),
        # Sheep
        _breed("Bannur", "sheep", "Karnataka",
               nbagr="INDIA_SHEEP_0300"),
        _breed("Deccani", "sheep", "Maharashtra",
               nbagr="INDIA_SHEEP_0800"),
        _breed("Nellore", "sheep", "Andhra Pradesh",
               nbagr="INDIA_SHEEP_2200"),
        _breed("Hassan", "sheep", "Karnataka"),
        _breed("Bellary", "sheep", "Karnataka"),
        # Poultry
        _breed("Giriraja", "poultry", "Karnataka"),
        _breed("Swarnadhara", "poultry", "Karnataka"),
        _breed("Vanaraja", "poultry", "Hyderabad"),
        _breed("Desi", "poultry", "India"),
        _breed("BV 380", "poultry", "India",
               indigenous=False),
    ]


def _district(
    name: str,
    lgd: int,
    lat: float,
    lon: float,
    elev: int,
) -> dict:
    return {
        "name": name,
        "lgd_code": lgd,
        "state_lgd_code": 29,
        "latitude": lat,
        "longitude": lon,
        "elevation_m": elev,
    }


def get_seed_karnataka_districts() -> list[dict]:
    """All 31 districts of Karnataka with LGD codes."""
    return [
        _district("Bagalkote", 2901, 16.18, 75.70, 542),
        _district("Ballari", 2902, 15.14, 76.92, 460),
        _district("Belagavi", 2903, 15.85, 74.50, 751),
        _district("Bengaluru Rural", 2904, 13.23, 77.71, 898),
        _district("Bengaluru Urban", 2905, 12.97, 77.59, 920),
        _district("Bidar", 2906, 17.91, 77.52, 670),
        _district("Chamarajanagara", 2907, 11.92, 76.94, 766),
        _district("Chikballapura", 2908, 13.44, 77.73, 915),
        _district("Chikkamagaluru", 2909, 13.32, 75.77, 1090),
        _district("Chitradurga", 2910, 14.23, 76.40, 732),
        _district("Dakshina Kannada", 2911, 12.87, 74.88, 22),
        _district("Davanagere", 2912, 14.47, 75.92, 589),
        _district("Dharwad", 2913, 15.46, 75.01, 727),
        _district("Gadag", 2914, 15.43, 75.63, 650),
        _district("Hassan", 2915, 13.01, 76.10, 827),
        _district("Haveri", 2916, 14.79, 75.40, 557),
        _district("Kalaburagi", 2917, 17.33, 76.83, 454),
        _district("Kodagu", 2918, 12.42, 75.74, 1150),
        _district("Kolar", 2919, 13.14, 78.13, 882),
        _district("Koppal", 2920, 15.35, 76.15, 509),
        _district("Mandya", 2921, 12.52, 76.90, 695),
        _district("Mysuru", 2922, 12.30, 76.66, 770),
        _district("Raichur", 2923, 16.21, 77.37, 407),
        _district("Ramanagara", 2924, 12.72, 77.28, 804),
        _district("Shivamogga", 2925, 13.93, 75.57, 569),
        _district("Tumakuru", 2926, 13.34, 77.10, 822),
        _district("Udupi", 2927, 13.34, 74.74, 5),
        _district("Uttara Kannada", 2928, 14.80, 74.13, 550),
        _district("Vijayapura", 2929, 16.83, 75.71, 593),
        _district("Vijayanagara", 2930, 15.34, 76.47, 468),
        _district("Yadgir", 2931, 16.77, 77.14, 420),
    ]


def get_seed_karnataka_state() -> dict:
    """Karnataka state metadata."""
    return {
        "lgd_code": 29,
        "name": "Karnataka",
        "name_local": "ಕರ್ನಾಟಕ",
    }
