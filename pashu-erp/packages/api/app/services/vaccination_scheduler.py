"""ICAR vaccination calendar and scheduling service."""

from datetime import date, timedelta

# ICAR-recommended vaccination schedule per species
VACCINATION_CALENDAR = {
    "cattle": [
        {
            "vaccine": "FMD Vaccine",
            "first_dose_months": 4,
            "booster_months": 6,
            "repeat_interval_months": 6,
            "mandatory": True,
            "notes": "Foot and Mouth Disease — mandatory under national FMD-CP",
        },
        {
            "vaccine": "HS Vaccine",
            "first_dose_months": 6,
            "booster_months": None,
            "repeat_interval_months": 12,
            "mandatory": True,
            "notes": "Hemorrhagic Septicemia — before monsoon season",
        },
        {
            "vaccine": "BQ Vaccine",
            "first_dose_months": 6,
            "booster_months": None,
            "repeat_interval_months": 12,
            "mandatory": True,
            "notes": "Black Quarter — before monsoon season",
        },
        {
            "vaccine": "Brucellosis Vaccine (S19)",
            "first_dose_months": 4,
            "booster_months": None,
            "repeat_interval_months": None,
            "mandatory": True,
            "notes": "Single dose for female calves 4-8 months only",
        },
        {
            "vaccine": "Theileriosis Vaccine",
            "first_dose_months": 2,
            "booster_months": None,
            "repeat_interval_months": None,
            "mandatory": False,
            "notes": "Recommended in endemic areas for crossbred cattle",
        },
        {
            "vaccine": "LSD Vaccine",
            "first_dose_months": 4,
            "booster_months": None,
            "repeat_interval_months": 12,
            "mandatory": True,
            "notes": "Lumpy Skin Disease — annual vaccination",
        },
        {
            "vaccine": "Anthrax Vaccine",
            "first_dose_months": 6,
            "booster_months": None,
            "repeat_interval_months": 12,
            "mandatory": False,
            "notes": "Recommended in anthrax-endemic districts",
        },
    ],
    "goat": [
        {
            "vaccine": "PPR Vaccine",
            "first_dose_months": 3,
            "booster_months": None,
            "repeat_interval_months": 36,
            "mandatory": True,
            "notes": "Peste des Petits Ruminants — under national PPR-CP",
        },
        {
            "vaccine": "Enterotoxemia Vaccine",
            "first_dose_months": 4,
            "booster_months": 5,
            "repeat_interval_months": 6,
            "mandatory": True,
            "notes": "Pre-monsoon and pre-winter boosters",
        },
        {
            "vaccine": "Goat Pox Vaccine",
            "first_dose_months": 3,
            "booster_months": None,
            "repeat_interval_months": 12,
            "mandatory": True,
            "notes": "Annual vaccination",
        },
        {
            "vaccine": "FMD Vaccine",
            "first_dose_months": 4,
            "booster_months": 6,
            "repeat_interval_months": 6,
            "mandatory": True,
            "notes": "Foot and Mouth Disease",
        },
        {
            "vaccine": "CCPP Vaccine",
            "first_dose_months": 3,
            "booster_months": None,
            "repeat_interval_months": 12,
            "mandatory": False,
            "notes": "Contagious Caprine Pleuropneumonia — endemic areas",
        },
    ],
    "sheep": [
        {
            "vaccine": "PPR Vaccine",
            "first_dose_months": 3,
            "booster_months": None,
            "repeat_interval_months": 36,
            "mandatory": True,
            "notes": "Peste des Petits Ruminants",
        },
        {
            "vaccine": "Enterotoxemia Vaccine",
            "first_dose_months": 4,
            "booster_months": 5,
            "repeat_interval_months": 6,
            "mandatory": True,
            "notes": "Pre-monsoon and pre-winter",
        },
        {
            "vaccine": "Sheep Pox Vaccine",
            "first_dose_months": 3,
            "booster_months": None,
            "repeat_interval_months": 12,
            "mandatory": True,
            "notes": "Annual vaccination",
        },
        {
            "vaccine": "Blue Tongue Vaccine",
            "first_dose_months": 6,
            "booster_months": None,
            "repeat_interval_months": 12,
            "mandatory": False,
            "notes": "Recommended in endemic areas before monsoon",
        },
        {
            "vaccine": "FMD Vaccine",
            "first_dose_months": 4,
            "booster_months": 6,
            "repeat_interval_months": 6,
            "mandatory": True,
            "notes": "Foot and Mouth Disease",
        },
    ],
    "poultry": [
        {
            "vaccine": "Marek's Disease Vaccine",
            "first_dose_days": 1,
            "booster_months": None,
            "repeat_interval_months": None,
            "mandatory": True,
            "notes": "Day-old chick vaccination",
        },
        {
            "vaccine": "Newcastle Disease (F1) Vaccine",
            "first_dose_days": 7,
            "booster_months": None,
            "repeat_interval_months": None,
            "mandatory": True,
            "notes": "First week — eye drop",
        },
        {
            "vaccine": "IBD Vaccine (Gumboro)",
            "first_dose_days": 14,
            "booster_months": None,
            "repeat_interval_months": None,
            "mandatory": True,
            "notes": "Second week — drinking water",
        },
        {
            "vaccine": "Newcastle Disease (R2B) Vaccine",
            "first_dose_days": 28,
            "booster_months": None,
            "repeat_interval_months": 3,
            "mandatory": True,
            "notes": "Fourth week — IM injection, repeat quarterly",
        },
        {
            "vaccine": "Fowl Pox Vaccine",
            "first_dose_days": 42,
            "booster_months": None,
            "repeat_interval_months": None,
            "mandatory": False,
            "notes": "Wing web method at 6 weeks",
        },
    ],
}


def get_vaccination_schedule(species: str) -> list[dict]:
    """Return ICAR vaccination schedule for a species."""
    species_key = species.lower().strip()
    schedule = VACCINATION_CALENDAR.get(species_key, [])
    return [
        {
            "vaccine": v["vaccine"],
            "first_dose": f"{v.get('first_dose_months', v.get('first_dose_days', '?'))} {'months' if 'first_dose_months' in v else 'days'}",
            "repeat_interval": f"Every {v['repeat_interval_months']} months" if v.get("repeat_interval_months") else "Single dose",
            "mandatory": v["mandatory"],
            "notes": v["notes"],
        }
        for v in schedule
    ]


def get_due_vaccinations(
    species: str,
    date_of_birth: date | None,
    last_vaccinations: dict[str, date] | None = None,
) -> list[dict]:
    """Determine which vaccinations are coming due based on age and history.

    Args:
        species: Animal species
        date_of_birth: Animal DOB (for age-based calculations)
        last_vaccinations: Dict of vaccine_name -> last_administered_date
    """
    species_key = species.lower().strip()
    schedule = VACCINATION_CALENDAR.get(species_key, [])
    last_vaccinations = last_vaccinations or {}
    today = date.today()

    if date_of_birth is None:
        return []

    age_days = (today - date_of_birth).days
    age_months = age_days / 30.44  # approximate

    due = []
    for vaccine in schedule:
        vaccine_name = vaccine["vaccine"]
        last_date = last_vaccinations.get(vaccine_name)

        # Determine when the next dose is due
        first_dose_months = vaccine.get("first_dose_months")
        first_dose_days = vaccine.get("first_dose_days")
        repeat_months = vaccine.get("repeat_interval_months")

        if last_date is None:
            # Never administered — check if old enough for first dose
            if first_dose_months and age_months >= first_dose_months:
                due.append({
                    "vaccine": vaccine_name,
                    "status": "overdue" if age_months > first_dose_months + 1 else "due_now",
                    "due_date": (date_of_birth + timedelta(days=int(first_dose_months * 30.44))).isoformat(),
                    "notes": vaccine["notes"],
                    "mandatory": vaccine["mandatory"],
                })
            elif first_dose_days and age_days >= first_dose_days:
                due.append({
                    "vaccine": vaccine_name,
                    "status": "overdue" if age_days > first_dose_days + 7 else "due_now",
                    "due_date": (date_of_birth + timedelta(days=first_dose_days)).isoformat(),
                    "notes": vaccine["notes"],
                    "mandatory": vaccine["mandatory"],
                })
        elif repeat_months:
            # Has been administered — check if repeat is due
            next_due = last_date + timedelta(days=int(repeat_months * 30.44))
            days_until = (next_due - today).days
            if days_until <= 30:  # Due within 30 days
                due.append({
                    "vaccine": vaccine_name,
                    "status": "overdue" if days_until < 0 else "due_soon",
                    "due_date": next_due.isoformat(),
                    "last_administered": last_date.isoformat(),
                    "notes": vaccine["notes"],
                    "mandatory": vaccine["mandatory"],
                })

    return due
