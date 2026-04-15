"""Tests for the ICAR vaccination scheduling service (app.services.vaccination_scheduler)."""

from datetime import date, timedelta

from app.services.vaccination_scheduler import (
    VACCINATION_CALENDAR,
    get_due_vaccinations,
    get_vaccination_schedule,
)


# ---------------------------------------------------------------------------
# get_vaccination_schedule — species lookup
# ---------------------------------------------------------------------------

class TestGetVaccinationSchedule:

    def test_cattle_schedule(self):
        schedule = get_vaccination_schedule("cattle")
        assert len(schedule) == len(VACCINATION_CALENDAR["cattle"])
        names = [v["vaccine"] for v in schedule]
        assert "FMD Vaccine" in names
        assert "HS Vaccine" in names
        assert "BQ Vaccine" in names

    def test_goat_schedule(self):
        schedule = get_vaccination_schedule("goat")
        names = [v["vaccine"] for v in schedule]
        assert "PPR Vaccine" in names
        assert "Enterotoxemia Vaccine" in names

    def test_sheep_schedule(self):
        schedule = get_vaccination_schedule("sheep")
        names = [v["vaccine"] for v in schedule]
        assert "Blue Tongue Vaccine" in names
        assert "Sheep Pox Vaccine" in names

    def test_poultry_schedule(self):
        schedule = get_vaccination_schedule("poultry")
        names = [v["vaccine"] for v in schedule]
        assert "Marek's Disease Vaccine" in names
        assert "Newcastle Disease (F1) Vaccine" in names

    def test_unknown_species_empty(self):
        assert get_vaccination_schedule("fish") == []

    def test_case_insensitive(self):
        assert get_vaccination_schedule("Cattle") == get_vaccination_schedule("cattle")

    def test_whitespace_stripped(self):
        assert get_vaccination_schedule("  goat  ") == get_vaccination_schedule("goat")

    def test_schedule_fields_present(self):
        for entry in get_vaccination_schedule("cattle"):
            assert "vaccine" in entry
            assert "first_dose" in entry
            assert "repeat_interval" in entry
            assert "mandatory" in entry
            assert "notes" in entry

    def test_first_dose_format_months(self):
        schedule = get_vaccination_schedule("cattle")
        fmd = next(v for v in schedule if v["vaccine"] == "FMD Vaccine")
        assert "months" in fmd["first_dose"]

    def test_first_dose_format_days_poultry(self):
        schedule = get_vaccination_schedule("poultry")
        mareks = next(v for v in schedule if v["vaccine"] == "Marek's Disease Vaccine")
        assert "days" in mareks["first_dose"]

    def test_single_dose_display(self):
        schedule = get_vaccination_schedule("cattle")
        bruc = next(v for v in schedule if "Brucellosis" in v["vaccine"])
        assert bruc["repeat_interval"] == "Single dose"

    def test_repeat_interval_display(self):
        schedule = get_vaccination_schedule("cattle")
        fmd = next(v for v in schedule if v["vaccine"] == "FMD Vaccine")
        assert "Every" in fmd["repeat_interval"]


# ---------------------------------------------------------------------------
# get_due_vaccinations — age-based scheduling
# ---------------------------------------------------------------------------

class TestGetDueVaccinations:

    def test_newborn_calf_nothing_due(self):
        """A calf born today should not have any vaccines due yet."""
        dob = date.today()
        due = get_due_vaccinations("cattle", dob)
        assert due == []

    def test_four_month_calf_fmd_due(self):
        """A 4-month-old calf should have FMD and Brucellosis due."""
        dob = date.today() - timedelta(days=4 * 31)
        due = get_due_vaccinations("cattle", dob)
        names = [v["vaccine"] for v in due]
        assert "FMD Vaccine" in names

    def test_six_month_calf_hs_bq_due(self):
        """A 6-month-old calf should have HS and BQ due."""
        dob = date.today() - timedelta(days=6 * 31)
        due = get_due_vaccinations("cattle", dob)
        names = [v["vaccine"] for v in due]
        assert "HS Vaccine" in names
        assert "BQ Vaccine" in names

    def test_overdue_status(self):
        """A vaccine past its due window should be marked overdue."""
        dob = date.today() - timedelta(days=8 * 31)  # 8 months old
        due = get_due_vaccinations("cattle", dob)
        fmd = next((v for v in due if v["vaccine"] == "FMD Vaccine"), None)
        assert fmd is not None
        assert fmd["status"] == "overdue"

    def test_due_now_status(self):
        """A vaccine at exactly the right age should be due_now."""
        # FMD first dose at 4 months — create animal exactly 4 months old
        dob = date.today() - timedelta(days=int(4 * 30.44))
        due = get_due_vaccinations("cattle", dob)
        fmd = next((v for v in due if v["vaccine"] == "FMD Vaccine"), None)
        assert fmd is not None
        assert fmd["status"] == "due_now"

    def test_with_last_vaccination_repeat_due(self):
        """When repeat interval elapsed, vaccine should be due again."""
        dob = date.today() - timedelta(days=365)
        # FMD was given 7 months ago, repeat is every 6 months
        last_fmd = date.today() - timedelta(days=7 * 31)
        due = get_due_vaccinations("cattle", dob, {"FMD Vaccine": last_fmd})
        fmd = next((v for v in due if v["vaccine"] == "FMD Vaccine"), None)
        assert fmd is not None
        assert fmd["status"] == "overdue"

    def test_with_last_vaccination_not_yet_due(self):
        """Recently vaccinated animal should not have repeat due."""
        dob = date.today() - timedelta(days=365)
        last_fmd = date.today() - timedelta(days=30)  # Vaccinated 1 month ago
        due = get_due_vaccinations("cattle", dob, {"FMD Vaccine": last_fmd})
        fmd = next((v for v in due if v["vaccine"] == "FMD Vaccine"), None)
        assert fmd is None  # Not due yet (6 month interval)

    def test_due_soon_status(self):
        """Vaccine due within 30 days should be 'due_soon'."""
        dob = date.today() - timedelta(days=365)
        # FMD given ~5.5 months ago — due in ~2 weeks
        last_fmd = date.today() - timedelta(days=int(5.5 * 30.44))
        due = get_due_vaccinations("cattle", dob, {"FMD Vaccine": last_fmd})
        fmd = next((v for v in due if v["vaccine"] == "FMD Vaccine"), None)
        assert fmd is not None
        assert fmd["status"] == "due_soon"

    def test_none_dob_returns_empty(self):
        """If DOB is not known, no schedule can be computed."""
        assert get_due_vaccinations("cattle", None) == []

    def test_poultry_day_based_schedule(self):
        """Poultry vaccines use days, not months."""
        dob = date.today() - timedelta(days=10)
        due = get_due_vaccinations("poultry", dob)
        names = [v["vaccine"] for v in due]
        assert "Marek's Disease Vaccine" in names
        assert "Newcastle Disease (F1) Vaccine" in names

    def test_poultry_newborn_day1(self):
        """Day-old chick — Marek's is due at day 1."""
        dob = date.today() - timedelta(days=1)
        due = get_due_vaccinations("poultry", dob)
        mareks = next((v for v in due if "Marek" in v["vaccine"]), None)
        assert mareks is not None
        assert mareks["status"] == "due_now"

    def test_mandatory_flag_preserved(self):
        dob = date.today() - timedelta(days=365)
        due = get_due_vaccinations("cattle", dob)
        for v in due:
            assert isinstance(v["mandatory"], bool)

    def test_unknown_species_empty(self):
        dob = date.today() - timedelta(days=365)
        assert get_due_vaccinations("fish", dob) == []

    def test_old_animal_all_overdue(self):
        """A very old animal with no vaccination history — everything overdue."""
        dob = date.today() - timedelta(days=5 * 365)  # 5 years old
        due = get_due_vaccinations("cattle", dob)
        assert len(due) >= 5
        for v in due:
            assert v["status"] == "overdue"

    def test_goat_three_month_ppr_due(self):
        """PPR is due at 3 months for goats."""
        dob = date.today() - timedelta(days=int(3 * 30.44))
        due = get_due_vaccinations("goat", dob)
        ppr = next((v for v in due if "PPR" in v["vaccine"]), None)
        assert ppr is not None
