"""
PashuRaksha ERP — Comprehensive demo seed data.

Idempotent: safe to run multiple times. Checks for existing records
before inserting using phone (users), pashu_aadhaar_id (animals),
code (centers), scheme_code (schemes), etc.

Usage:
    python -m app.seed.demo_data
"""

import asyncio
import random
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models import (
    AdvisoryTip,
    Animal,
    CommunityAlert,
    FeedIngredient,
    GovtScheme,
    HealthEvent,
    InsuranceClaim,
    InsurancePolicy,
    Medicine,
    MedicineAdministration,
    MilkCollectionCenter,
    MilkCollectionRecord,
    SellRecord,
    SHGGroup,
    TraditionalRemedy,
    Transaction,
    User,
    Vaccination,
    WeatherAlert,
    YieldLog,
)
from app.models.advisory import AdvisoryCategory, AdvisorySource
from app.models.alerts import AlertSeverity as CommunityAlertSeverity
from app.models.animal import AnimalSex, BreedType, Species
from app.models.ethno_vet import EvidenceRating
from app.models.feed import FeedCategory
from app.models.finance import TransactionStatus, TransactionType
from app.models.health import HealthEventType
from app.models.insurance import ClaimStatus, PolicyStatus
from app.models.marketplace import ProductType
from app.models.milk import MilkSession
from app.models.shg import SHGGrading
from app.models.vet import (
    ConsultationChannel,
    ConsultationPriority,
    ConsultationStatus,
    VetConsultation,
)
from app.models.weather import AlertSeverity as WeatherAlertSeverity

# Fixed seed for reproducibility across runs
random.seed(42)

TODAY = date.today()
UTC = timezone.utc


# ---------------------------------------------------------------------------
# 1. Users
# ---------------------------------------------------------------------------
async def seed_users(session: AsyncSession) -> dict:
    """Create 5 users: 1 admin + 3 farmers + 1 vet. Returns {key: User}."""
    user_specs = [
        {
            "key": "admin",
            "name": "Deepak Kumar",
            "phone": "+919900000001",
            "role": "admin",
            "district": "Mysore",
            "village_code": None,
            "gender": "male",
        },
        {
            "key": "lakshmi",
            "name": "Lakshmi Devi",
            "phone": "+919900000002",
            "role": "farmer",
            "district": "Mysore",
            "village_code": "KA-MYS-001",
            "gender": "female",
        },
        {
            "key": "annapurna",
            "name": "Annapurna Gowda",
            "phone": "+919900000003",
            "role": "farmer",
            "district": "Mandya",
            "village_code": "KA-MAN-001",
            "gender": "female",
        },
        {
            "key": "savitri",
            "name": "Savitri Bai",
            "phone": "+919900000004",
            "role": "farmer",
            "district": "Mysore",
            "village_code": "KA-MYS-002",
            "gender": "female",
        },
        {
            "key": "vet_ramesh",
            "name": "Dr. Ramesh",
            "phone": "+919900000005",
            "role": "vet",
            "district": "Mysore",
            "village_code": "KA-MYS-001",
            "gender": "male",
        },
    ]

    users: dict[str, User] = {}
    for spec in user_specs:
        existing = (
            await session.execute(select(User).where(User.phone == spec["phone"]))
        ).scalar_one_or_none()
        if existing:
            users[spec["key"]] = existing
            print(f"  User '{spec['name']}' already exists, skipping.")
            continue

        user = User(
            name=spec["name"],
            phone=spec["phone"],
            role=spec["role"],
            location_district=spec["district"],
            village_code=spec["village_code"],
            gender=spec.get("gender"),
            lang_pref="kn",
            location_state="Karnataka",
        )
        session.add(user)
        users[spec["key"]] = user

    await session.flush()
    print(f"  Users seeded: {len(users)}")
    return users


# ---------------------------------------------------------------------------
# 2. Animals
# ---------------------------------------------------------------------------
async def seed_animals(session: AsyncSession, users: dict) -> dict:
    """Create 8 animals across 3 farmers. Returns {key: Animal}."""
    animal_specs = [
        # Farmer 1: Lakshmi
        {
            "key": "lakshmi_cow",
            "user_key": "lakshmi",
            "pashu_id": "KA2200000001",
            "name": "Lakshmi",
            "species": Species.cattle,
            "breed": "HF Cross",
            "breed_type": BreedType.crossbreed,
            "sex": AnimalSex.female,
            "dob": TODAY - timedelta(days=4 * 365),
            "lactation": 3,
            "bcs": 3.5,
            "insured": True,
        },
        {
            "key": "gowri",
            "user_key": "lakshmi",
            "pashu_id": "KA2200000002",
            "name": "Gowri",
            "species": Species.cattle,
            "breed": "Hallikar",
            "breed_type": BreedType.indigenous,
            "sex": AnimalSex.female,
            "dob": TODAY - timedelta(days=5 * 365),
            "lactation": 4,
            "bcs": 3.0,
            "insured": False,
        },
        {
            "key": "gauri_goat",
            "user_key": "lakshmi",
            "pashu_id": "KA2200000003",
            "name": "Gauri",
            "species": Species.goat,
            "breed": "Osmanabadi",
            "breed_type": BreedType.indigenous,
            "sex": AnimalSex.female,
            "dob": TODAY - timedelta(days=2 * 365),
            "lactation": 2,
            "bcs": 2.5,
            "insured": False,
        },
        # Farmer 2: Annapurna
        {
            "key": "nandini",
            "user_key": "annapurna",
            "pashu_id": "KA2200000004",
            "name": "Nandini",
            "species": Species.cattle,
            "breed": "Jersey Cross",
            "breed_type": BreedType.crossbreed,
            "sex": AnimalSex.female,
            "dob": TODAY - timedelta(days=3 * 365),
            "lactation": 2,
            "bcs": 3.5,
            "insured": True,
        },
        {
            "key": "kaveri",
            "user_key": "annapurna",
            "pashu_id": "KA2200000005",
            "name": "Kaveri",
            "species": Species.cattle,
            "breed": "Amrit Mahal",
            "breed_type": BreedType.indigenous,
            "sex": AnimalSex.female,
            "dob": TODAY - timedelta(days=6 * 365),
            "lactation": 5,
            "bcs": 3.0,
            "insured": False,
        },
        {
            "key": "malli",
            "user_key": "annapurna",
            "pashu_id": "KA2200000006",
            "name": "Malli",
            "species": Species.sheep,
            "breed": "Bannur",
            "breed_type": BreedType.indigenous,
            "sex": AnimalSex.female,
            "dob": TODAY - timedelta(days=int(1.5 * 365)),
            "lactation": 1,
            "bcs": 2.5,
            "insured": False,
        },
        # Farmer 3: Savitri
        {
            "key": "kolugalu",
            "user_key": "savitri",
            "pashu_id": "KA2200000007",
            "name": "Kolugalu batch",
            "species": Species.poultry,
            "breed": "Giriraja",
            "breed_type": BreedType.crossbreed,
            "sex": AnimalSex.female,
            "dob": TODAY - timedelta(days=180),
            "lactation": None,
            "bcs": None,
            "insured": False,
            "metadata": {"flock_size": 5},
        },
        {
            "key": "natikoli",
            "user_key": "savitri",
            "pashu_id": "KA2200000008",
            "name": "Nati Koli batch",
            "species": Species.poultry,
            "breed": "Country Chicken",
            "breed_type": BreedType.indigenous,
            "sex": AnimalSex.female,
            "dob": TODAY - timedelta(days=240),
            "lactation": None,
            "bcs": None,
            "insured": False,
            "metadata": {"flock_size": 3},
        },
    ]

    animals: dict[str, Animal] = {}
    for spec in animal_specs:
        existing = (
            await session.execute(
                select(Animal).where(Animal.pashu_aadhaar_id == spec["pashu_id"])
            )
        ).scalar_one_or_none()
        if existing:
            animals[spec["key"]] = existing
            print(f"  Animal '{spec['name']}' already exists, skipping.")
            continue

        animal = Animal(
            user_id=users[spec["user_key"]].id,
            pashu_aadhaar_id=spec["pashu_id"],
            name=spec["name"],
            species=spec["species"],
            breed=spec["breed"],
            breed_type=spec["breed_type"],
            sex=spec["sex"],
            date_of_birth=spec["dob"],
            lactation_number=spec["lactation"],
            body_condition_score=spec["bcs"],
            is_insured=spec["insured"],
            metadata_=spec.get("metadata"),
        )
        session.add(animal)
        animals[spec["key"]] = animal

    await session.flush()
    print(f"  Animals seeded: {len(animals)}")
    return animals


# ---------------------------------------------------------------------------
# 3. Milk Collection Center
# ---------------------------------------------------------------------------
async def seed_milk_center(session: AsyncSession, users: dict) -> dict:
    """Create 1 milk collection center."""
    code = "KMF-MYS-001"
    existing = (
        await session.execute(
            select(MilkCollectionCenter).where(MilkCollectionCenter.code == code)
        )
    ).scalar_one_or_none()
    if existing:
        print("  Milk center already exists, skipping.")
        return {"mysore": existing}

    center = MilkCollectionCenter(
        name="Nandini Milk Center - Mysore",
        code=code,
        district="Mysore",
        village_code="KA-MYS-001",
        manager_user_id=users["admin"].id,
        is_active=True,
    )
    session.add(center)
    await session.flush()
    print("  Milk collection center seeded.")
    return {"mysore": center}


# ---------------------------------------------------------------------------
# 4. Milk Yield Logs (30 days)
# ---------------------------------------------------------------------------
BREED_YIELD = {
    # breed: (mean_liters, std_dev) per session
    "HF Cross": (7.0, 0.8),
    "Hallikar": (3.0, 0.5),
    "Jersey Cross": (6.0, 0.7),
    "Amrit Mahal": (2.5, 0.4),
    "Osmanabadi": (1.5, 0.3),  # goat
}


async def seed_yield_logs(session: AsyncSession, users: dict, animals: dict) -> int:
    """Create 30 days of morning + evening yield logs for milking animals."""
    # Check if we already have yield data
    count_result = await session.execute(select(YieldLog))
    if count_result.first() is not None:
        print("  Yield logs already exist, skipping.")
        return 0

    milking_animals = {
        "lakshmi_cow": ("lakshmi", "HF Cross"),
        "gowri": ("lakshmi", "Hallikar"),
        "gauri_goat": ("lakshmi", "Osmanabadi"),
        "nandini": ("annapurna", "Jersey Cross"),
        "kaveri": ("annapurna", "Amrit Mahal"),
    }

    count = 0
    for day_offset in range(30, 0, -1):
        log_date = TODAY - timedelta(days=day_offset)
        for animal_key, (user_key, breed) in milking_animals.items():
            mean, std = BREED_YIELD[breed]
            for sess in [MilkSession.morning, MilkSession.evening]:
                qty = max(0.5, round(random.gauss(mean, std), 1))
                # Evening yields are typically ~80% of morning
                if sess == MilkSession.evening:
                    qty = round(qty * 0.8, 1)
                hour = 6 if sess == MilkSession.morning else 17
                recorded_at = datetime(
                    log_date.year, log_date.month, log_date.day, hour, 0, tzinfo=UTC
                )
                log = YieldLog(
                    animal_id=animals[animal_key].id,
                    user_id=users[user_key].id,
                    quantity_liters=qty,
                    session=sess,
                    recorded_at=recorded_at,
                )
                session.add(log)
                count += 1

    await session.flush()
    print(f"  Yield logs seeded: {count}")
    return count


# ---------------------------------------------------------------------------
# 5. Milk Collection Records (30 days)
# ---------------------------------------------------------------------------
async def seed_milk_collections(
    session: AsyncSession, users: dict, centers: dict
) -> int:
    """Create 30 days of milk collection records at the center."""
    count_result = await session.execute(select(MilkCollectionRecord))
    if count_result.first() is not None:
        print("  Milk collection records already exist, skipping.")
        return 0

    center = centers["mysore"]
    milk_farmers = ["lakshmi", "annapurna"]
    # Approximate daily totals per farmer for center delivery
    farmer_daily = {"lakshmi": (12.0, 1.5), "annapurna": (10.0, 1.2)}

    count = 0
    for day_offset in range(30, 0, -1):
        log_date = TODAY - timedelta(days=day_offset)
        for farmer_key in milk_farmers:
            mean, std = farmer_daily[farmer_key]
            for shift in [MilkSession.morning, MilkSession.evening]:
                qty = max(1.0, round(random.gauss(mean * 0.55, std), 1))
                if shift == MilkSession.evening:
                    qty = round(qty * 0.8, 1)
                fat = round(random.uniform(3.5, 4.8), 1)
                snf = round(random.uniform(8.0, 8.8), 1)
                rate = round(30.0 + fat * 2.0, 2)
                total = round(qty * rate, 2)
                hour = 7 if shift == MilkSession.morning else 18
                collected_at = datetime(
                    log_date.year, log_date.month, log_date.day, hour, 0, tzinfo=UTC
                )
                rec = MilkCollectionRecord(
                    center_id=center.id,
                    farmer_user_id=users[farmer_key].id,
                    quantity_liters=qty,
                    fat_pct=fat,
                    snf_pct=snf,
                    rate_per_liter=rate,
                    total_amount=total,
                    shift=shift,
                    collected_at=collected_at,
                )
                session.add(rec)
                count += 1

    await session.flush()
    print(f"  Milk collection records seeded: {count}")
    return count


# ---------------------------------------------------------------------------
# 6. Health Events
# ---------------------------------------------------------------------------
async def seed_health_events(
    session: AsyncSession, users: dict, animals: dict
) -> int:
    """Create 6 health events: 1 high-risk, 2 medium, 3 routine."""
    count_result = await session.execute(select(HealthEvent))
    if count_result.first() is not None:
        print("  Health events already exist, skipping.")
        return 0

    admin_id = users["admin"].id
    events = [
        # HIGH RISK: Gowri — mastitis symptoms
        {
            "animal_key": "gowri",
            "event_type": HealthEventType.symptom,
            "description": "Gowri showing fever, reduced milk output, and swollen udder. Suspected mastitis.",
            "symptoms": {
                "fever": True,
                "reduced_milk": True,
                "swollen_udder": True,
                "loss_of_appetite": False,
            },
            "ai_risk_score": 0.89,
            "recommended_action": "Immediate veterinary examination. Start antibiotic course. Isolate from herd.",
            "probable_diseases": [
                {"name": "Mastitis", "probability": 0.85},
                {"name": "Udder Edema", "probability": 0.10},
            ],
            "days_ago": 2,
        },
        # MEDIUM RISK: Nandini — mild lameness
        {
            "animal_key": "nandini",
            "event_type": HealthEventType.symptom,
            "description": "Nandini limping on right hind leg. Mild swelling observed.",
            "symptoms": {
                "lameness": True,
                "swelling": True,
                "fever": False,
            },
            "ai_risk_score": 0.52,
            "recommended_action": "Monitor for 48 hours. Apply anti-inflammatory if persists.",
            "probable_diseases": [
                {"name": "Foot Rot", "probability": 0.45},
                {"name": "Sprain", "probability": 0.40},
            ],
            "days_ago": 5,
        },
        # MEDIUM RISK: Gauri goat — diarrhea
        {
            "animal_key": "gauri_goat",
            "event_type": HealthEventType.symptom,
            "description": "Gauri has loose stools for 2 days. Eating normally.",
            "symptoms": {
                "diarrhea": True,
                "loss_of_appetite": False,
                "fever": False,
            },
            "ai_risk_score": 0.41,
            "recommended_action": "Deworm if not done recently. Ensure clean water supply.",
            "probable_diseases": [
                {"name": "Parasitic Infection", "probability": 0.55},
                {"name": "Dietary Upset", "probability": 0.35},
            ],
            "days_ago": 7,
        },
        # ROUTINE: Lakshmi cow — checkup
        {
            "animal_key": "lakshmi_cow",
            "event_type": HealthEventType.checkup,
            "description": "Routine monthly health checkup. All vitals normal.",
            "symptoms": None,
            "ai_risk_score": 0.05,
            "recommended_action": "Continue current feeding regimen.",
            "probable_diseases": None,
            "days_ago": 10,
        },
        # ROUTINE: Kaveri — checkup
        {
            "animal_key": "kaveri",
            "event_type": HealthEventType.checkup,
            "description": "Routine checkup. Body condition improving after calving.",
            "symptoms": None,
            "ai_risk_score": 0.08,
            "recommended_action": "Increase concentrate feed by 0.5 kg/day.",
            "probable_diseases": None,
            "days_ago": 14,
        },
        # ROUTINE: Malli sheep — checkup
        {
            "animal_key": "malli",
            "event_type": HealthEventType.checkup,
            "description": "Routine pre-shearing health check. Coat healthy, no skin lesions.",
            "symptoms": None,
            "ai_risk_score": 0.03,
            "recommended_action": "Proceed with shearing. Deworm post-shearing.",
            "probable_diseases": None,
            "days_ago": 20,
        },
    ]

    count = 0
    for ev in events:
        event_dt = datetime(
            (TODAY - timedelta(days=ev["days_ago"])).year,
            (TODAY - timedelta(days=ev["days_ago"])).month,
            (TODAY - timedelta(days=ev["days_ago"])).day,
            10, 0, tzinfo=UTC,
        )
        health_event = HealthEvent(
            animal_id=animals[ev["animal_key"]].id,
            event_type=ev["event_type"],
            description=ev["description"],
            symptoms=ev["symptoms"],
            ai_risk_score=ev["ai_risk_score"],
            recommended_action=ev["recommended_action"],
            probable_diseases=ev["probable_diseases"],
            recorded_by=admin_id,
            event_date=event_dt,
        )
        session.add(health_event)
        count += 1

    await session.flush()
    print(f"  Health events seeded: {count}")
    return count


# ---------------------------------------------------------------------------
# 7. Vaccinations
# ---------------------------------------------------------------------------
async def seed_vaccinations(
    session: AsyncSession, users: dict, animals: dict
) -> int:
    """Create vaccination records: FMD, PPR, Newcastle, Brucella."""
    count_result = await session.execute(select(Vaccination))
    if count_result.first() is not None:
        print("  Vaccinations already exist, skipping.")
        return 0

    admin_id = users["admin"].id
    administered_date = TODAY - timedelta(days=60)
    fmd_next = administered_date + timedelta(days=180)
    brucella_next = administered_date + timedelta(days=365)

    vacc_specs = [
        # FMD for all cattle
        ("lakshmi_cow", "FMD Vaccine (Foot and Mouth Disease)", administered_date, fmd_next, "FMD-B-2026-001"),
        ("gowri", "FMD Vaccine (Foot and Mouth Disease)", administered_date, fmd_next, "FMD-B-2026-001"),
        ("nandini", "FMD Vaccine (Foot and Mouth Disease)", administered_date, fmd_next, "FMD-B-2026-002"),
        ("kaveri", "FMD Vaccine (Foot and Mouth Disease)", administered_date, fmd_next, "FMD-B-2026-002"),
        # Brucella for cattle
        ("lakshmi_cow", "Brucella abortus S19", administered_date - timedelta(days=30), brucella_next, "BRU-B-2025-044"),
        ("gowri", "Brucella abortus S19", administered_date - timedelta(days=30), brucella_next, "BRU-B-2025-044"),
        ("nandini", "Brucella abortus S19", administered_date - timedelta(days=30), brucella_next, "BRU-B-2025-045"),
        ("kaveri", "Brucella abortus S19", administered_date - timedelta(days=30), brucella_next, "BRU-B-2025-045"),
        # PPR for goats
        ("gauri_goat", "PPR Vaccine (Peste des Petits Ruminants)", administered_date - timedelta(days=10), administered_date + timedelta(days=355), "PPR-B-2026-011"),
        # Newcastle for poultry
        ("kolugalu", "Newcastle Disease Vaccine (Lasota)", administered_date - timedelta(days=20), administered_date + timedelta(days=70), "NDV-B-2026-033"),
        ("natikoli", "Newcastle Disease Vaccine (Lasota)", administered_date - timedelta(days=20), administered_date + timedelta(days=70), "NDV-B-2026-033"),
    ]

    count = 0
    for animal_key, vaccine, admin_on, next_due, batch in vacc_specs:
        vacc = Vaccination(
            animal_id=animals[animal_key].id,
            vaccine_name=vaccine,
            administered_on=admin_on,
            next_due=next_due,
            batch_number=batch,
            recorded_by=admin_id,
        )
        session.add(vacc)
        count += 1

    await session.flush()
    print(f"  Vaccinations seeded: {count}")
    return count


# ---------------------------------------------------------------------------
# 8. Sell Records (15 days)
# ---------------------------------------------------------------------------
async def seed_sell_records(session: AsyncSession, users: dict) -> list:
    """Create 15 days of sell records for each farmer."""
    count_result = await session.execute(select(SellRecord))
    if count_result.first() is not None:
        print("  Sell records already exist, skipping.")
        return []

    records_created: list[SellRecord] = []

    for day_offset in range(15, 0, -1):
        sell_date = TODAY - timedelta(days=day_offset)
        sell_dt = datetime(sell_date.year, sell_date.month, sell_date.day, 8, 0, tzinfo=UTC)

        # Lakshmi: daily milk, weekly eggs
        milk_qty = round(random.gauss(14.0, 1.5), 1)
        milk_price = Decimal("38.00")
        milk_total = Decimal(str(round(float(milk_price) * milk_qty, 2)))
        rec = SellRecord(
            user_id=users["lakshmi"].id,
            product_type=ProductType.milk,
            quantity=milk_qty,
            unit="liters",
            price_per_unit=milk_price,
            total_amount=milk_total,
            buyer_name="Nandini Milk Center",
            sold_at=sell_dt,
        )
        session.add(rec)
        records_created.append(rec)

        if day_offset % 7 == 0:  # weekly eggs
            egg_qty = random.randint(20, 30)
            egg_price = Decimal("6.00")
            egg_total = egg_price * egg_qty
            rec = SellRecord(
                user_id=users["lakshmi"].id,
                product_type=ProductType.eggs,
                quantity=float(egg_qty),
                unit="pieces",
                price_per_unit=egg_price,
                total_amount=egg_total,
                buyer_name="Local Market",
                sold_at=sell_dt,
            )
            session.add(rec)
            records_created.append(rec)

        # Annapurna: daily milk, monthly wool
        milk_qty_a = round(random.gauss(11.0, 1.2), 1)
        milk_total_a = Decimal(str(round(float(milk_price) * milk_qty_a, 2)))
        rec = SellRecord(
            user_id=users["annapurna"].id,
            product_type=ProductType.milk,
            quantity=milk_qty_a,
            unit="liters",
            price_per_unit=milk_price,
            total_amount=milk_total_a,
            buyer_name="Nandini Milk Center",
            sold_at=sell_dt,
        )
        session.add(rec)
        records_created.append(rec)

        if day_offset == 15:  # monthly wool (once in the period)
            wool_qty = round(random.gauss(2.0, 0.3), 1)
            wool_price = Decimal("150.00")
            wool_total = Decimal(str(round(float(wool_price) * wool_qty, 2)))
            rec = SellRecord(
                user_id=users["annapurna"].id,
                product_type=ProductType.wool,
                quantity=wool_qty,
                unit="kg",
                price_per_unit=wool_price,
                total_amount=wool_total,
                buyer_name="Wool Cooperative",
                sold_at=sell_dt,
            )
            session.add(rec)
            records_created.append(rec)

        # Savitri: daily eggs, weekly manure
        egg_qty_s = random.randint(5, 8)
        egg_price_s = Decimal("6.50")
        egg_total_s = egg_price_s * egg_qty_s
        rec = SellRecord(
            user_id=users["savitri"].id,
            product_type=ProductType.eggs,
            quantity=float(egg_qty_s),
            unit="pieces",
            price_per_unit=egg_price_s,
            total_amount=egg_total_s,
            buyer_name="Village Shop",
            sold_at=sell_dt,
        )
        session.add(rec)
        records_created.append(rec)

        if day_offset % 7 == 0:  # weekly manure
            manure_qty = round(random.gauss(25.0, 3.0), 1)
            manure_price = Decimal("5.00")
            manure_total = Decimal(str(round(float(manure_price) * manure_qty, 2)))
            rec = SellRecord(
                user_id=users["savitri"].id,
                product_type=ProductType.manure,
                quantity=manure_qty,
                unit="kg",
                price_per_unit=manure_price,
                total_amount=manure_total,
                buyer_name="Farmer Raju",
                sold_at=sell_dt,
            )
            session.add(rec)
            records_created.append(rec)

    await session.flush()
    print(f"  Sell records seeded: {len(records_created)}")
    return records_created


# ---------------------------------------------------------------------------
# 9. Financial Transactions (from sell records)
# ---------------------------------------------------------------------------
async def seed_transactions(
    session: AsyncSession, sell_records: list[SellRecord]
) -> int:
    """Create income transactions corresponding to sell records."""
    count_result = await session.execute(select(Transaction))
    if count_result.first() is not None:
        print("  Transactions already exist, skipping.")
        return 0

    count = 0
    for rec in sell_records:
        txn = Transaction(
            user_id=rec.user_id,
            type=TransactionType.income,
            amount=rec.total_amount,
            category=rec.product_type if isinstance(rec.product_type, str) else rec.product_type.value,
            reference_id=str(rec.id),
            description=f"Sale of {rec.product_type if isinstance(rec.product_type, str) else rec.product_type.value}: {rec.quantity} {rec.unit} to {rec.buyer_name or 'buyer'}",
            status=TransactionStatus.completed,
        )
        session.add(txn)
        count += 1

    await session.flush()
    print(f"  Transactions seeded: {count}")
    return count


# ---------------------------------------------------------------------------
# 10. SHG Groups
# ---------------------------------------------------------------------------
async def seed_shg_groups(session: AsyncSession, users: dict) -> int:
    """Create 2 Self-Help Groups."""
    count_result = await session.execute(select(SHGGroup))
    if count_result.first() is not None:
        print("  SHG groups already exist, skipping.")
        return 0

    groups = [
        {
            "name": "Lakshmi Mahila Sangha",
            "registration_number": "SHG-KA-MYS-2024-001",
            "district": "Mysore",
            "village_code": "KA-MYS-001",
            "admin_user_id": users["lakshmi"].id,
            "member_count": 12,
            "women_only": True,
            "formation_date": date(2024, 3, 15),
            "total_savings": Decimal("45000.00"),
            "grading": SHGGrading.A,
            "panchsutra_compliance": {
                "regular_meetings": True,
                "regular_savings": True,
                "regular_inter_loaning": True,
                "timely_repayment": True,
                "updated_books": True,
            },
        },
        {
            "name": "Kaveri Swasahaya",
            "registration_number": "SHG-KA-MAN-2025-001",
            "district": "Mandya",
            "village_code": "KA-MAN-001",
            "admin_user_id": users["annapurna"].id,
            "member_count": 8,
            "women_only": True,
            "formation_date": date(2025, 1, 10),
            "total_savings": Decimal("22000.00"),
            "grading": SHGGrading.B,
            "panchsutra_compliance": {
                "regular_meetings": True,
                "regular_savings": True,
                "regular_inter_loaning": False,
                "timely_repayment": True,
                "updated_books": False,
            },
        },
    ]

    for g in groups:
        session.add(SHGGroup(**g))

    await session.flush()
    print(f"  SHG groups seeded: {len(groups)}")
    return len(groups)


# ---------------------------------------------------------------------------
# 11. Government Schemes
# ---------------------------------------------------------------------------
async def seed_govt_schemes(session: AsyncSession) -> int:
    """Create 5 government schemes."""
    count_result = await session.execute(select(GovtScheme))
    if count_result.first() is not None:
        print("  Government schemes already exist, skipping.")
        return 0

    schemes = [
        {
            "scheme_code": "RGM-2024",
            "name": "Rashtriya Gokul Mission",
            "ministry": "Ministry of Fisheries, Animal Husbandry and Dairying",
            "description": "Development and conservation of indigenous bovine breeds. Focuses on breed improvement through genomic selection and artificial insemination.",
            "eligibility_criteria": "Farmers owning indigenous cattle breeds. Must have valid Pashu Aadhaar for each animal.",
            "required_documents": ["Pashu Aadhaar card", "Land ownership proof", "Aadhaar card", "Bank passbook"],
            "max_subsidy_amount": Decimal("50000.00"),
            "subsidy_percentage": 50.0,
            "is_active": True,
            "valid_from": date(2024, 4, 1),
            "valid_to": date(2027, 3, 31),
        },
        {
            "scheme_code": "NLM-2024",
            "name": "National Livestock Mission",
            "ministry": "Ministry of Fisheries, Animal Husbandry and Dairying",
            "description": "Sustainable development of the livestock sector. Covers entrepreneurship development, breed improvement, and feed/fodder development for all species.",
            "eligibility_criteria": "All livestock farmers. Priority to women farmers and SC/ST beneficiaries.",
            "required_documents": ["Aadhaar card", "Bank passbook", "Caste certificate (if applicable)", "BPL card (if applicable)"],
            "max_subsidy_amount": Decimal("100000.00"),
            "subsidy_percentage": 50.0,
            "is_active": True,
            "valid_from": date(2024, 4, 1),
            "valid_to": date(2027, 3, 31),
        },
        {
            "scheme_code": "KMF-DD-2025",
            "name": "KMF Dairy Development Scheme",
            "ministry": "Karnataka Milk Federation",
            "description": "Karnataka state scheme for dairy infrastructure development. Provides subsidies for milking machines, bulk coolers, and dairy sheds.",
            "eligibility_criteria": "Karnataka resident dairy farmers with minimum 2 milch animals. Must be KMF member.",
            "required_documents": ["KMF membership card", "Pashu Aadhaar card", "Aadhaar card", "Land record (RTC)"],
            "max_subsidy_amount": Decimal("200000.00"),
            "subsidy_percentage": 33.33,
            "is_active": True,
            "valid_from": date(2025, 1, 1),
            "valid_to": date(2026, 12, 31),
        },
        {
            "scheme_code": "NABARD-DE-2024",
            "name": "NABARD Dairy Entrepreneurship Development Scheme",
            "ministry": "NABARD",
            "description": "Back-ended capital subsidy for setting up modern dairy farms, heifer rearing units, and milk processing facilities.",
            "eligibility_criteria": "Individuals, SHGs, NGOs, cooperatives. No prior default on institutional loans.",
            "required_documents": ["Project report", "Bank loan sanction letter", "Aadhaar card", "IT returns (if applicable)"],
            "max_subsidy_amount": Decimal("700000.00"),
            "subsidy_percentage": 25.0,
            "is_active": True,
            "valid_from": date(2024, 4, 1),
            "valid_to": date(2027, 3, 31),
        },
        {
            "scheme_code": "PMFBY-2025",
            "name": "Pradhan Mantri Fasal Bima Yojana",
            "ministry": "Ministry of Agriculture and Farmers Welfare",
            "description": "Comprehensive crop and livestock insurance scheme. Covers natural calamities, pests, and diseases at subsidized premiums.",
            "eligibility_criteria": "All farmers including sharecroppers and tenant farmers. Both loanee and non-loanee farmers eligible.",
            "required_documents": ["Aadhaar card", "Bank passbook", "Land records / lease agreement", "Sowing certificate"],
            "max_subsidy_amount": Decimal("200000.00"),
            "subsidy_percentage": 50.0,
            "is_active": True,
            "valid_from": date(2025, 4, 1),
            "valid_to": date(2026, 3, 31),
        },
    ]

    for s in schemes:
        session.add(GovtScheme(**s))

    await session.flush()
    print(f"  Government schemes seeded: {len(schemes)}")
    return len(schemes)


# ---------------------------------------------------------------------------
# 12. Weather Alerts
# ---------------------------------------------------------------------------
async def seed_weather_alerts(session: AsyncSession) -> int:
    """Create 3 weather alerts for Mysore/Mandya districts."""
    count_result = await session.execute(select(WeatherAlert))
    if count_result.first() is not None:
        print("  Weather alerts already exist, skipping.")
        return 0

    now = datetime.now(UTC)
    alerts = [
        {
            "district": "Mysore",
            "alert_type": "Heat Wave",
            "severity": WeatherAlertSeverity.severe,
            "description": (
                "Severe heat wave warning for Mysore district. Maximum temperatures "
                "expected to reach 42°C. Keep livestock in shade, ensure adequate "
                "water supply. Avoid grazing between 11 AM and 4 PM."
            ),
            "valid_from": now,
            "valid_to": now + timedelta(days=3),
            "source": "IMD",
        },
        {
            "district": "Mandya",
            "alert_type": "Thunderstorm",
            "severity": WeatherAlertSeverity.moderate,
            "description": (
                "Pre-monsoon thunderstorm expected in Mandya district with gusty winds "
                "up to 50 km/h and heavy rainfall. Secure livestock shelters, avoid "
                "open grazing. Lightning risk high near water bodies."
            ),
            "valid_from": now + timedelta(days=1),
            "valid_to": now + timedelta(days=2),
            "source": "IMD",
        },
        {
            "district": "Mysore",
            "alert_type": "High Humidity",
            "severity": WeatherAlertSeverity.low,
            "description": (
                "High humidity advisory for Mysore district. Relative humidity expected "
                "above 85%. Increased risk of fungal infections in livestock. Ensure "
                "proper ventilation in sheds. Monitor for respiratory distress."
            ),
            "valid_from": now,
            "valid_to": now + timedelta(days=5),
            "source": "IMD",
        },
    ]

    for a in alerts:
        session.add(WeatherAlert(**a))

    await session.flush()
    print(f"  Weather alerts seeded: {len(alerts)}")
    return len(alerts)


# ---------------------------------------------------------------------------
# 13. Feed Ingredients (30 common Karnataka ingredients)
# ---------------------------------------------------------------------------
async def seed_feed_ingredients(session: AsyncSession) -> dict:
    """Create 30 feed ingredients with NDDB nutritional data. Returns {name_en: FeedIngredient}."""
    count_result = await session.execute(select(FeedIngredient))
    if count_result.first() is not None:
        print("  Feed ingredients already exist, skipping.")
        # Return existing for downstream use
        result = await session.execute(select(FeedIngredient))
        return {fi.name_en: fi for fi in result.scalars().all()}

    # (name_en, name_kn, category, protein_pct, energy_kcal, cost_per_kg, availability_season, locally_available)
    ingredient_specs = [
        # --- Roughages ---
        ("Paddy Straw", "ಭತ್ತದ ಹುಲ್ಲು", FeedCategory.roughage, 3.5, 1600, 3.00, "Oct-Mar", True),
        ("Ragi Straw", "ರಾಗಿ ಹುಲ್ಲು", FeedCategory.roughage, 4.2, 1700, 2.50, "Sep-Feb", True),
        ("Jowar Stover", "ಜೋಳದ ಕಡ್ಡಿ", FeedCategory.roughage, 4.0, 1650, 2.80, "Oct-Feb", True),
        ("Sugarcane Tops", "ಕಬ್ಬಿನ ಸೊಪ್ಪು", FeedCategory.roughage, 3.8, 1550, 2.00, "Dec-Apr", True),
        ("Napier Grass", "ನೇಪಿಯರ್ ಹುಲ್ಲು", FeedCategory.roughage, 7.5, 1800, 4.00, "Year-round", True),
        ("Guinea Grass", "ಗಿನಿ ಹುಲ್ಲು", FeedCategory.roughage, 8.0, 1850, 4.50, "Jun-Nov", True),
        ("Lucerne (Alfalfa)", "ಲೂಸರ್ನ್", FeedCategory.roughage, 18.0, 2200, 8.00, "Oct-Mar", True),
        ("Berseem", "ಬರ್ಸೀಮ್", FeedCategory.roughage, 17.5, 2100, 7.50, "Nov-Mar", True),
        ("Maize Fodder", "ಮೆಕ್ಕೆಜೋಳ ಮೇವು", FeedCategory.roughage, 8.5, 2000, 5.00, "Jun-Sep", True),
        ("Sorghum Fodder", "ಜೋಳದ ಮೇವು", FeedCategory.roughage, 7.0, 1900, 4.50, "Jun-Oct", True),
        # --- Concentrates ---
        ("Groundnut Cake", "ಕಡಲೆಕಾಯಿ ಹಿಂಡಿ", FeedCategory.concentrate, 42.0, 2750, 35.00, "Year-round", True),
        ("Coconut Cake", "ತೆಂಗಿನ ಹಿಂಡಿ", FeedCategory.concentrate, 22.0, 2600, 28.00, "Year-round", True),
        ("Cottonseed Cake", "ಹತ್ತಿ ಬೀಜ ಹಿಂಡಿ", FeedCategory.concentrate, 24.0, 2500, 25.00, "Oct-Mar", True),
        ("Rice Bran", "ಅಕ್ಕಿ ತೌಡು", FeedCategory.concentrate, 12.0, 2300, 15.00, "Year-round", True),
        ("Wheat Bran", "ಗೋಧಿ ತೌಡು", FeedCategory.concentrate, 15.0, 2400, 18.00, "Year-round", True),
        ("Maize Grain", "ಮೆಕ್ಕೆಜೋಳ ಕಾಳು", FeedCategory.concentrate, 9.0, 3300, 20.00, "Year-round", True),
        ("Rice Polish", "ಅಕ್ಕಿ ಪಾಲಿಶ್", FeedCategory.concentrate, 11.5, 2800, 16.00, "Year-round", True),
        ("Soybean Meal", "ಸೋಯಾಬೀನ್ ಹಿಟ್ಟು", FeedCategory.concentrate, 45.0, 2900, 40.00, "Year-round", True),
        ("Sunflower Cake", "ಸೂರ್ಯಕಾಂತಿ ಹಿಂಡಿ", FeedCategory.concentrate, 30.0, 2550, 22.00, "Oct-Mar", True),
        ("Til Cake (Sesame)", "ಎಳ್ಳಿನ ಹಿಂಡಿ", FeedCategory.concentrate, 35.0, 2700, 30.00, "Nov-Feb", True),
        # --- Supplements ---
        ("Mineral Mixture", "ಖನಿಜ ಮಿಶ್ರಣ", FeedCategory.supplement, 0.0, 0, 80.00, "Year-round", True),
        ("Common Salt", "ಉಪ್ಪು", FeedCategory.supplement, 0.0, 0, 12.00, "Year-round", True),
        ("Calcite Powder", "ಕ್ಯಾಲ್ಸೈಟ್ ಪುಡಿ", FeedCategory.supplement, 0.0, 0, 8.00, "Year-round", True),
        ("Urea", "ಯೂರಿಯಾ", FeedCategory.supplement, 287.0, 0, 10.00, "Year-round", True),
        ("Molasses", "ಬೆಲ್ಲದ ಪಾಕ", FeedCategory.supplement, 3.0, 2700, 12.00, "Dec-May", True),
        # --- Additional regional ingredients ---
        ("Horse Gram Husk", "ಹುರುಳಿ ಸಿಪ್ಪೆ", FeedCategory.roughage, 6.5, 1750, 5.00, "Oct-Jan", True),
        ("Tamarind Seed Powder", "ಹುಣಸೆ ಬೀಜದ ಪುಡಿ", FeedCategory.concentrate, 15.0, 2600, 18.00, "Year-round", True),
        ("Neem Seed Cake", "ಬೇವಿನ ಬೀಜ ಹಿಂಡಿ", FeedCategory.concentrate, 18.0, 2200, 12.00, "Apr-Jul", True),
        ("Banana Pseudo-stem", "ಬಾಳೆ ದಿಂಡು", FeedCategory.roughage, 2.5, 1400, 1.50, "Year-round", True),
        ("Dried Brewers Grain", "ಒಣ ಬ್ರೂವರ್ಸ್ ಧಾನ್ಯ", FeedCategory.concentrate, 25.0, 2400, 14.00, "Year-round", True),
    ]

    ingredients: dict[str, FeedIngredient] = {}
    for name_en, name_kn, category, protein, energy, cost, season, local in ingredient_specs:
        fi = FeedIngredient(
            name_en=name_en,
            name_kn=name_kn,
            category=category,
            protein_pct=protein,
            energy_kcal=energy,
            cost_per_kg=cost,
            availability_season=season,
            locally_available=local,
        )
        session.add(fi)
        ingredients[name_en] = fi

    await session.flush()
    print(f"  Feed ingredients seeded: {len(ingredients)}")
    return ingredients


# ---------------------------------------------------------------------------
# 14. Ethno-Veterinary Remedies (25 traditional remedies)
# ---------------------------------------------------------------------------
async def seed_ethno_vet_remedies(session: AsyncSession) -> int:
    """Create 25 traditional remedies from ICAR ethno-vet documentation."""
    count_result = await session.execute(select(TraditionalRemedy))
    if count_result.first() is not None:
        print("  Traditional remedies already exist, skipping.")
        return 0

    remedies = [
        {
            "name_en": "Turmeric Paste for Wounds",
            "name_kn": "ಅರಿಶಿನ ಲೇಪನ",
            "plant_ingredient": "Turmeric (Curcuma longa)",
            "preparation_method": "Mix 50g turmeric powder with coconut oil to form thick paste. Clean wound thoroughly with warm water before applying. Cover with clean cloth.",
            "dosage_by_species": {"cattle": "50g paste", "goat": "20g paste", "sheep": "20g paste", "poultry": "5g paste"},
            "conditions_treated": ["wounds", "skin infections", "cuts", "abrasions"],
            "evidence_rating": EvidenceRating.icar_validated,
            "safety_warnings": "Avoid applying on deep puncture wounds. Seek veterinary care if wound shows signs of infection after 48 hours.",
            "source_reference": "ICAR Ethno-Veterinary Practices, Publication No. 2019/034",
        },
        {
            "name_en": "Neem Leaves Decoction for Parasites",
            "name_kn": "ಬೇವಿನ ಎಲೆ ಕಷಾಯ",
            "plant_ingredient": "Neem (Azadirachta indica)",
            "preparation_method": "Boil 200g fresh neem leaves in 2 liters water for 20 minutes. Strain and cool. Administer orally once daily for 3 days.",
            "dosage_by_species": {"cattle": "500ml", "goat": "150ml", "sheep": "150ml"},
            "conditions_treated": ["internal parasites", "worm infestation", "ectoparasites"],
            "evidence_rating": EvidenceRating.studied,
            "safety_warnings": "Do not administer to pregnant animals in first trimester. Reduce dose for young stock.",
            "source_reference": "Journal of Ethno-pharmacology, Vol 142, 2012",
        },
        {
            "name_en": "Ajwain and Jaggery for Bloat",
            "name_kn": "ಓಮ ಮತ್ತು ಬೆಲ್ಲ",
            "plant_ingredient": "Carom seeds (Trachyspermum ammi) + Jaggery",
            "preparation_method": "Crush 50g ajwain seeds. Mix with 100g jaggery and 500ml warm water. Administer orally as drench. Massage abdomen gently.",
            "dosage_by_species": {"cattle": "50g ajwain + 100g jaggery", "buffalo": "60g ajwain + 120g jaggery"},
            "conditions_treated": ["bloat", "indigestion", "gas", "tympany"],
            "evidence_rating": EvidenceRating.icar_validated,
            "safety_warnings": "For mild to moderate bloat only. Severe bloat with respiratory distress requires immediate veterinary intervention with trocar.",
            "source_reference": "ICAR Ethno-Veterinary Practices, Publication No. 2019/034",
        },
        {
            "name_en": "Aloe Vera Gel for Burns",
            "name_kn": "ಲೋಳೆಸರ ಲೇಪ",
            "plant_ingredient": "Aloe vera (Aloe barbadensis)",
            "preparation_method": "Split fresh aloe vera leaf. Scoop out gel and apply directly to burn area. Reapply every 6 hours.",
            "dosage_by_species": {"cattle": "Apply liberally", "goat": "Apply liberally", "sheep": "Apply liberally", "poultry": "Thin layer"},
            "conditions_treated": ["burns", "scalds", "sunburn", "skin irritation"],
            "evidence_rating": EvidenceRating.traditional,
            "safety_warnings": "For superficial burns only. Deep or extensive burns require veterinary treatment.",
            "source_reference": "Traditional knowledge, Karnataka Veterinary Association documentation",
        },
        {
            "name_en": "Garlic Paste for Mastitis",
            "name_kn": "ಬೆಳ್ಳುಳ್ಳಿ ಲೇಪ",
            "plant_ingredient": "Garlic (Allium sativum)",
            "preparation_method": "Crush 100g garlic cloves into paste. Mix with 50ml mustard oil. Apply on affected udder quarter. Also give 50g garlic orally with feed.",
            "dosage_by_species": {"cattle": "100g paste external + 50g oral", "goat": "30g paste external + 15g oral"},
            "conditions_treated": ["mastitis", "udder inflammation", "subclinical mastitis"],
            "evidence_rating": EvidenceRating.studied,
            "safety_warnings": "May cause temporary increase in garlic odor in milk. Not a substitute for antibiotic therapy in severe clinical mastitis.",
            "source_reference": "Indian Journal of Traditional Knowledge, Vol 11(3), 2012",
        },
        {
            "name_en": "Papaya Leaf Extract for Fever",
            "name_kn": "ಪಪ್ಪಾಯಿ ಎಲೆ ರಸ",
            "plant_ingredient": "Papaya (Carica papaya)",
            "preparation_method": "Crush 300g fresh papaya leaves. Extract juice by squeezing through cloth. Mix with 200ml water. Administer orally twice daily.",
            "dosage_by_species": {"cattle": "200ml extract", "goat": "50ml extract"},
            "conditions_treated": ["fever", "low platelet count", "general weakness"],
            "evidence_rating": EvidenceRating.traditional,
            "safety_warnings": "Monitor temperature. If fever exceeds 104°F or persists beyond 48 hours, seek veterinary help immediately.",
            "source_reference": "Traditional knowledge, BAIF documentation",
        },
        {
            "name_en": "Castor Oil for Constipation",
            "name_kn": "ಹರಳೆಣ್ಣೆ",
            "plant_ingredient": "Castor (Ricinus communis)",
            "preparation_method": "Administer castor oil orally as drench. Mix with equal volume of warm water. Give on empty stomach.",
            "dosage_by_species": {"cattle": "200-300ml", "goat": "30-50ml", "sheep": "30-50ml", "poultry": "5ml"},
            "conditions_treated": ["constipation", "impaction", "digestive sluggishness"],
            "evidence_rating": EvidenceRating.icar_validated,
            "safety_warnings": "Do not administer to pregnant animals. Ensure animal is hydrated before and after administration.",
            "source_reference": "ICAR Ethno-Veterinary Practices, Publication No. 2019/034",
        },
        {
            "name_en": "Betel Leaf with Pepper for Cold",
            "name_kn": "ವೀಳ್ಯದೆಲೆ ಮತ್ತು ಮೆಣಸು",
            "plant_ingredient": "Betel leaf (Piper betle) + Black pepper (Piper nigrum)",
            "preparation_method": "Crush 10 betel leaves with 10g black pepper and 20g jaggery. Make into bolus. Administer orally twice daily for 3 days.",
            "dosage_by_species": {"cattle": "10 leaves + 10g pepper", "buffalo": "12 leaves + 12g pepper"},
            "conditions_treated": ["cold", "nasal discharge", "mild respiratory infection"],
            "evidence_rating": EvidenceRating.traditional,
            "safety_warnings": "For mild respiratory symptoms only. Persistent cough or labored breathing needs veterinary attention.",
            "source_reference": "Traditional knowledge, South Indian veterinary practitioners",
        },
        {
            "name_en": "Ginger and Honey for Cough",
            "name_kn": "ಶುಂಠಿ ಮತ್ತು ಜೇನುತುಪ್ಪ",
            "plant_ingredient": "Ginger (Zingiber officinale) + Honey",
            "preparation_method": "Grate 50g fresh ginger. Mix with 100g honey and 200ml warm water. Administer orally twice daily.",
            "dosage_by_species": {"goat": "25g ginger + 50g honey", "sheep": "25g ginger + 50g honey"},
            "conditions_treated": ["cough", "sore throat", "mild bronchitis"],
            "evidence_rating": EvidenceRating.studied,
            "safety_warnings": "If cough persists beyond 5 days or is accompanied by fever, seek veterinary care.",
            "source_reference": "Journal of Veterinary Science & Technology, 2015",
        },
        {
            "name_en": "Drumstick Leaves for Nutrition",
            "name_kn": "ನುಗ್ಗೆ ಸೊಪ್ಪು",
            "plant_ingredient": "Moringa (Moringa oleifera)",
            "preparation_method": "Dry moringa leaves in shade. Crush to powder. Mix with regular feed at 2-5% inclusion rate.",
            "dosage_by_species": {"poultry": "5g per bird per day", "cattle": "100g per day", "goat": "30g per day"},
            "conditions_treated": ["nutritional deficiency", "low immunity", "poor growth", "low egg production"],
            "evidence_rating": EvidenceRating.traditional,
            "safety_warnings": "No known adverse effects at recommended dosage. Rich in vitamins A, C, and iron.",
            "source_reference": "ICAR Research Complex for NEH Region, Technical Bulletin",
        },
        # --- 15 additional remedies ---
        {
            "name_en": "Tulsi (Holy Basil) for Respiratory Infections",
            "name_kn": "ತುಳಸಿ ಕಷಾಯ",
            "plant_ingredient": "Holy Basil (Ocimum sanctum)",
            "preparation_method": "Boil 100g fresh tulsi leaves in 1 liter water for 15 minutes. Strain and cool. Administer orally.",
            "dosage_by_species": {"cattle": "300ml twice daily", "goat": "100ml twice daily"},
            "conditions_treated": ["respiratory infection", "cough", "fever", "stress"],
            "evidence_rating": EvidenceRating.studied,
            "safety_warnings": "Safe for all ages. Can be given alongside conventional treatment.",
            "source_reference": "Indian Veterinary Journal, Vol 89, 2012",
        },
        {
            "name_en": "Tobacco Leaf Wash for Ectoparasites",
            "name_kn": "ತಂಬಾಕು ಎಲೆ ತೊಳೆಯುವಿಕೆ",
            "plant_ingredient": "Tobacco (Nicotiana tabacum)",
            "preparation_method": "Soak 200g tobacco leaves in 5 liters water overnight. Strain. Use as body wash, avoiding eyes and mouth.",
            "dosage_by_species": {"cattle": "Full body wash", "goat": "Full body wash"},
            "conditions_treated": ["ticks", "lice", "mites", "ectoparasites"],
            "evidence_rating": EvidenceRating.icar_validated,
            "safety_warnings": "EXTERNAL USE ONLY. Highly toxic if ingested. Keep away from feed and water troughs. Wear gloves during application.",
            "source_reference": "ICAR Ethno-Veterinary Practices, Publication No. 2019/034",
        },
        {
            "name_en": "Fenugreek Seeds for Milk Enhancement",
            "name_kn": "ಮೆಂತ್ಯ ಕಾಳು",
            "plant_ingredient": "Fenugreek (Trigonella foenum-graecum)",
            "preparation_method": "Soak 100g fenugreek seeds overnight. Grind to paste. Mix with feed. Give daily for 15 days.",
            "dosage_by_species": {"cattle": "100g daily", "goat": "30g daily", "buffalo": "120g daily"},
            "conditions_treated": ["low milk yield", "poor lactation", "post-partum weakness"],
            "evidence_rating": EvidenceRating.studied,
            "safety_warnings": "May cause slight change in milk flavor. Start with half dose and increase gradually.",
            "source_reference": "Asian Journal of Dairy and Food Research, Vol 34(2), 2015",
        },
        {
            "name_en": "Haldi-Nimbu (Turmeric-Lime) for Foot Rot",
            "name_kn": "ಅರಿಶಿನ-ನಿಂಬೆ ಲೇಪ",
            "plant_ingredient": "Turmeric + Lime (Citrus aurantiifolia)",
            "preparation_method": "Mix 50g turmeric powder with juice of 3 limes. Apply thick paste between hooves. Bandage loosely. Replace daily.",
            "dosage_by_species": {"cattle": "50g turmeric + 3 limes", "goat": "20g turmeric + 1 lime"},
            "conditions_treated": ["foot rot", "hoof infection", "interdigital dermatitis"],
            "evidence_rating": EvidenceRating.icar_validated,
            "safety_warnings": "Keep animal on dry surface after application. If condition worsens, switch to veterinary treatment.",
            "source_reference": "ICAR Ethno-Veterinary Practices, Publication No. 2019/034",
        },
        {
            "name_en": "Pumpkin Seeds for Deworming",
            "name_kn": "ಕುಂಬಳಕಾಯಿ ಬೀಜ",
            "plant_ingredient": "Pumpkin (Cucurbita maxima)",
            "preparation_method": "Dry and grind pumpkin seeds to powder. Mix with jaggery water. Administer orally on empty stomach.",
            "dosage_by_species": {"cattle": "200g powder", "goat": "50g powder", "sheep": "50g powder", "poultry": "10g powder"},
            "conditions_treated": ["tapeworm", "roundworm", "intestinal parasites"],
            "evidence_rating": EvidenceRating.studied,
            "safety_warnings": "Less effective than conventional dewormers for heavy infestations. Best used as preventive measure.",
            "source_reference": "Veterinary Parasitology, Vol 199, 2014",
        },
        {
            "name_en": "Coconut Oil for Skin Conditions",
            "name_kn": "ತೆಂಗಿನ ಎಣ್ಣೆ ಲೇಪ",
            "plant_ingredient": "Coconut (Cocos nucifera)",
            "preparation_method": "Warm virgin coconut oil slightly. Apply generously on affected skin areas. Massage gently. Repeat twice daily.",
            "dosage_by_species": {"cattle": "Apply liberally", "goat": "Apply liberally", "poultry": "Thin layer on comb/wattle"},
            "conditions_treated": ["dry skin", "mange", "minor dermatitis", "cracked teats"],
            "evidence_rating": EvidenceRating.traditional,
            "safety_warnings": "For mild skin conditions only. Mange requires additional treatment with acaricides.",
            "source_reference": "Traditional knowledge, Kerala Veterinary University documentation",
        },
        {
            "name_en": "Amla (Indian Gooseberry) for Immunity",
            "name_kn": "ನೆಲ್ಲಿಕಾಯಿ",
            "plant_ingredient": "Amla (Emblica officinalis)",
            "preparation_method": "Dry and powder amla fruits. Mix 50g powder with feed daily. Can also give fresh fruits directly.",
            "dosage_by_species": {"cattle": "50g powder daily", "goat": "15g powder daily", "poultry": "5g powder per bird"},
            "conditions_treated": ["low immunity", "vitamin C deficiency", "convalescence", "heat stress"],
            "evidence_rating": EvidenceRating.studied,
            "safety_warnings": "Safe for long-term use. No known interactions with conventional medicines.",
            "source_reference": "Indian Journal of Animal Sciences, Vol 85(4), 2015",
        },
        {
            "name_en": "Linseed Gruel for Retained Placenta",
            "name_kn": "ಅಗಸೆ ಬೀಜ ಗಂಜಿ",
            "plant_ingredient": "Linseed (Linum usitatissimum)",
            "preparation_method": "Boil 500g crushed linseed in 5 liters water until mucilaginous. Cool to lukewarm. Give as drench.",
            "dosage_by_species": {"cattle": "3-5 liters gruel", "buffalo": "4-6 liters gruel"},
            "conditions_treated": ["retained placenta", "post-partum recovery", "constipation after calving"],
            "evidence_rating": EvidenceRating.icar_validated,
            "safety_warnings": "Administer within 12 hours of calving for best effect. If placenta not expelled within 24 hours, call veterinarian.",
            "source_reference": "ICAR Ethno-Veterinary Practices, Publication No. 2019/034",
        },
        {
            "name_en": "Custard Apple Seed Paste for Lice",
            "name_kn": "ಸೀತಾಫಲ ಬೀಜ ಲೇಪ",
            "plant_ingredient": "Custard Apple (Annona squamosa)",
            "preparation_method": "Dry and powder custard apple seeds. Mix with coconut oil to form paste. Apply on affected areas.",
            "dosage_by_species": {"cattle": "Apply on infested areas", "goat": "Apply on infested areas"},
            "conditions_treated": ["lice", "fleas", "ectoparasites"],
            "evidence_rating": EvidenceRating.traditional,
            "safety_warnings": "EXTERNAL USE ONLY. Seeds are toxic if ingested. Avoid application near eyes and mouth.",
            "source_reference": "Traditional knowledge, ICAR-IVRI documentation",
        },
        {
            "name_en": "Jaggery-Salt Solution for Dehydration",
            "name_kn": "ಬೆಲ್ಲ-ಉಪ್ಪು ದ್ರಾವಣ",
            "plant_ingredient": "Jaggery + Common salt",
            "preparation_method": "Dissolve 200g jaggery and 10g salt in 2 liters clean water. Administer orally in small quantities repeatedly.",
            "dosage_by_species": {"cattle": "2-3 liters", "goat": "500ml-1 liter", "sheep": "500ml-1 liter", "poultry": "50ml per bird"},
            "conditions_treated": ["dehydration", "diarrhea recovery", "heat exhaustion", "post-transport stress"],
            "evidence_rating": EvidenceRating.icar_validated,
            "safety_warnings": "Not a substitute for IV fluids in severe dehydration. Monitor urine output.",
            "source_reference": "ICAR Ethno-Veterinary Practices, Publication No. 2019/034",
        },
        {
            "name_en": "Vitex (Nochi) Leaves for Joint Pain",
            "name_kn": "ಲಕ್ಕಿ ಸೊಪ್ಪು",
            "plant_ingredient": "Vitex negundo (Nochi/Lakki)",
            "preparation_method": "Heat fresh leaves, apply as warm poultice on affected joints. Bandage in place. Replace every 12 hours.",
            "dosage_by_species": {"cattle": "Large poultice", "goat": "Small poultice"},
            "conditions_treated": ["joint pain", "arthritis", "swelling", "sprains"],
            "evidence_rating": EvidenceRating.studied,
            "safety_warnings": "Ensure poultice is warm, not hot. Remove if skin shows irritation.",
            "source_reference": "Journal of Ayurveda and Integrative Medicine, Vol 3(2), 2012",
        },
        {
            "name_en": "Banana Stem Juice for Kidney Stones",
            "name_kn": "ಬಾಳೆ ದಿಂಡಿನ ರಸ",
            "plant_ingredient": "Banana (Musa paradisiaca)",
            "preparation_method": "Extract juice from banana pseudo-stem. Mix with 100ml lime juice. Give orally once daily for 7 days.",
            "dosage_by_species": {"cattle": "500ml juice", "goat": "150ml juice"},
            "conditions_treated": ["urinary calculi", "kidney stones", "urinary tract issues"],
            "evidence_rating": EvidenceRating.traditional,
            "safety_warnings": "Monitor urination. If animal shows signs of urinary obstruction (straining, no urine), seek immediate veterinary care.",
            "source_reference": "Traditional knowledge, Karnataka State Veterinary documentation",
        },
        {
            "name_en": "Curry Leaves for Digestive Health",
            "name_kn": "ಕರಿಬೇವಿನ ಸೊಪ್ಪು",
            "plant_ingredient": "Curry leaves (Murraya koenigii)",
            "preparation_method": "Mix 100g fresh curry leaves with feed daily. Alternatively, make decoction by boiling in 1 liter water.",
            "dosage_by_species": {"cattle": "100g leaves or 300ml decoction", "goat": "30g leaves or 100ml decoction", "poultry": "5g per bird"},
            "conditions_treated": ["indigestion", "poor appetite", "diarrhea", "nutritional supplement"],
            "evidence_rating": EvidenceRating.traditional,
            "safety_warnings": "Safe for regular use. Rich in iron and calcium.",
            "source_reference": "Traditional knowledge, South Indian veterinary practice",
        },
        {
            "name_en": "Calotropis Leaf Bandage for Swelling",
            "name_kn": "ಎಕ್ಕದ ಎಲೆ ಕಟ್ಟು",
            "plant_ingredient": "Calotropis (Calotropis gigantea)",
            "preparation_method": "Warm fresh calotropis leaves over flame. Apply on swollen area and bandage. Replace twice daily.",
            "dosage_by_species": {"cattle": "3-4 large leaves", "goat": "2 leaves"},
            "conditions_treated": ["swelling", "edema", "inflammation", "sprains"],
            "evidence_rating": EvidenceRating.studied,
            "safety_warnings": "EXTERNAL USE ONLY. Latex is toxic if ingested. Wash hands after handling. Avoid contact with eyes.",
            "source_reference": "Indian Journal of Traditional Knowledge, Vol 14(2), 2015",
        },
        {
            "name_en": "Tamarind Pulp for Heat Stroke",
            "name_kn": "ಹುಣಸೆ ಹಣ್ಣಿನ ರಸ",
            "plant_ingredient": "Tamarind (Tamarindus indica)",
            "preparation_method": "Soak 200g tamarind pulp in 2 liters water. Strain. Add 50g jaggery and 5g salt. Give as oral drench. Also apply cold water on body.",
            "dosage_by_species": {"cattle": "2 liters", "goat": "500ml", "sheep": "500ml"},
            "conditions_treated": ["heat stroke", "heat stress", "hyperthermia", "summer exhaustion"],
            "evidence_rating": EvidenceRating.traditional,
            "safety_warnings": "Move animal to shade immediately. If body temperature exceeds 106°F, pour cold water on body and call veterinarian.",
            "source_reference": "Traditional knowledge, Mysore Veterinary College documentation",
        },
    ]

    for r in remedies:
        session.add(TraditionalRemedy(**r))

    await session.flush()
    print(f"  Traditional remedies seeded: {len(remedies)}")
    return len(remedies)


# ---------------------------------------------------------------------------
# 15. Insurance Policies & Claims
# ---------------------------------------------------------------------------
async def seed_insurance_policies(
    session: AsyncSession, users: dict, animals: dict
) -> dict:
    """Create 3 insurance policies and 1 claim. Returns {key: InsurancePolicy}."""
    count_result = await session.execute(select(InsurancePolicy))
    if count_result.first() is not None:
        print("  Insurance policies already exist, skipping.")
        return {}

    now = datetime.now(UTC)
    policies_data = [
        {
            "key": "lakshmi_cow_policy",
            "animal_key": "lakshmi_cow",
            "provider": "United India Insurance Company",
            "policy_number": "UIIC-KA-MYS-2025-00142",
            "premium_amount": Decimal("500.00"),
            "coverage_amount": Decimal("40000.00"),
            "valid_from": now - timedelta(days=180),
            "valid_to": now + timedelta(days=185),
            "status": PolicyStatus.active,
        },
        {
            "key": "nandini_policy",
            "animal_key": "nandini",
            "provider": "National Insurance Company",
            "policy_number": "NIC-KA-MAN-2025-00087",
            "premium_amount": Decimal("450.00"),
            "coverage_amount": Decimal("35000.00"),
            "valid_from": now - timedelta(days=120),
            "valid_to": now + timedelta(days=245),
            "status": PolicyStatus.active,
        },
        {
            "key": "gauri_goat_policy",
            "animal_key": "gauri_goat",
            "provider": "United India Insurance Company",
            "policy_number": "UIIC-KA-MYS-2024-00533",
            "premium_amount": Decimal("200.00"),
            "coverage_amount": Decimal("8000.00"),
            "valid_from": now - timedelta(days=400),
            "valid_to": now - timedelta(days=35),
            "status": PolicyStatus.expired,
        },
    ]

    policies: dict[str, InsurancePolicy] = {}
    for spec in policies_data:
        policy = InsurancePolicy(
            animal_id=animals[spec["animal_key"]].id,
            provider=spec["provider"],
            policy_number=spec["policy_number"],
            premium_amount=spec["premium_amount"],
            coverage_amount=spec["coverage_amount"],
            valid_from=spec["valid_from"],
            valid_to=spec["valid_to"],
            status=spec["status"],
        )
        session.add(policy)
        policies[spec["key"]] = policy

    await session.flush()

    # Create 1 insurance claim for Gauri's expired policy
    claim = InsuranceClaim(
        policy_id=policies["gauri_goat_policy"].id,
        claim_type="Injury",
        description=(
            "Gauri (Osmanabadi goat) sustained injuries from a dog attack on the grazing field. "
            "Wounds on right hind leg and abdomen. Veterinary treatment administered. "
            "Claiming treatment costs and loss of milk production for recovery period."
        ),
        photo_urls=["uploads/claims/gauri_injury_01.jpg", "uploads/claims/gauri_injury_02.jpg"],
        status=ClaimStatus.under_review,
    )
    session.add(claim)
    await session.flush()

    print(f"  Insurance policies seeded: {len(policies)}, claims: 1")
    return policies


# ---------------------------------------------------------------------------
# 16. Community Alerts
# ---------------------------------------------------------------------------
async def seed_community_alerts(session: AsyncSession, users: dict) -> int:
    """Create 2 community disease alerts near demo farm locations."""
    count_result = await session.execute(select(CommunityAlert))
    if count_result.first() is not None:
        print("  Community alerts already exist, skipping.")
        return 0

    now = datetime.now(UTC)
    alerts = [
        {
            "reported_by": users["lakshmi"].id,
            "disease_name": "Foot and Mouth Disease (FMD)",
            "lat": 12.3252,  # ~3km from Mysore center
            "lon": 76.6538,
            "radius_km": 3.0,
            "severity": CommunityAlertSeverity.severe,
            "verified": True,
            "created_at": now - timedelta(days=2),
            "expires_at": now + timedelta(days=12),
        },
        {
            "reported_by": users["annapurna"].id,
            "disease_name": "Lumpy Skin Disease (LSD)",
            "lat": 12.5463,  # ~8km from Mandya center
            "lon": 76.8956,
            "radius_km": 8.0,
            "severity": CommunityAlertSeverity.moderate,
            "verified": False,
            "created_at": now - timedelta(days=5),
            "expires_at": now + timedelta(days=9),
        },
    ]

    for a in alerts:
        session.add(CommunityAlert(**a))

    await session.flush()
    print(f"  Community alerts seeded: {len(alerts)}")
    return len(alerts)


# ---------------------------------------------------------------------------
# 17. Medicines (15 common veterinary medicines)
# ---------------------------------------------------------------------------
async def seed_medicines(session: AsyncSession) -> dict:
    """Create 15 veterinary medicines with ICAR withdrawal periods. Returns {name_en: Medicine}."""
    count_result = await session.execute(select(Medicine))
    if count_result.first() is not None:
        print("  Medicines already exist, skipping.")
        result = await session.execute(select(Medicine))
        return {m.name_en: m for m in result.scalars().all()}

    # (name_en, name_kn, type, withdrawal_milk_days, withdrawal_meat_days, species_applicable)
    medicine_specs = [
        ("Oxytetracycline", "ಆಕ್ಸಿಟೆಟ್ರಾಸೈಕ್ಲಿನ್", "Antibiotic", 7, 28,
         ["cattle", "buffalo", "goat", "sheep"]),
        ("Penicillin", "ಪೆನಿಸಿಲಿನ್", "Antibiotic", 3, 14,
         ["cattle", "buffalo", "goat", "sheep"]),
        ("Enrofloxacin", "ಎನ್ರೋಫ್ಲಾಕ್ಸಾಸಿನ್", "Antibiotic", 5, 14,
         ["cattle", "buffalo", "goat", "sheep", "poultry"]),
        ("Ivermectin", "ಐವರ್ಮೆಕ್ಟಿನ್", "Antiparasitic", 28, 35,
         ["cattle", "buffalo", "goat", "sheep"]),
        ("Albendazole", "ಆಲ್ಬೆಂಡಜೋಲ್", "Anthelmintic", 5, 14,
         ["cattle", "buffalo", "goat", "sheep"]),
        ("Fenbendazole", "ಫೆನ್ಬೆಂಡಜೋಲ್", "Anthelmintic", 4, 14,
         ["cattle", "buffalo", "goat", "sheep"]),
        ("Ceftiofur", "ಸೆಫ್ಟಿಯೋಫರ್", "Antibiotic", 0, 3,
         ["cattle", "buffalo"]),
        ("Gentamicin", "ಜೆಂಟಾಮೈಸಿನ್", "Antibiotic", 4, 40,
         ["cattle", "buffalo", "goat"]),
        ("Amoxicillin", "ಅಮಾಕ್ಸಿಸಿಲಿನ್", "Antibiotic", 2, 25,
         ["cattle", "buffalo", "goat", "sheep", "poultry"]),
        ("Sulfonamides", "ಸಲ್ಫೋನಮೈಡ್ಸ್", "Antibiotic", 4, 10,
         ["cattle", "buffalo", "goat", "sheep", "poultry"]),
        ("Dexamethasone", "ಡೆಕ್ಸಾಮೆಥಾಸೋನ್", "Anti-inflammatory", 0, 0,
         ["cattle", "buffalo", "goat", "sheep"]),
        ("Flunixin", "ಫ್ಲುನಿಕ್ಸಿನ್", "NSAID", 4, 4,
         ["cattle", "buffalo"]),
        ("Meloxicam", "ಮೆಲಾಕ್ಸಿಕ್ಯಾಮ್", "NSAID", 5, 15,
         ["cattle", "buffalo", "goat"]),
        ("Trimethoprim", "ಟ್ರೈಮೆಥೋಪ್ರಿಮ್", "Antibiotic", 4, 10,
         ["cattle", "buffalo", "goat", "sheep", "poultry"]),
        ("Tylosin", "ಟೈಲೋಸಿನ್", "Antibiotic", 4, 21,
         ["cattle", "buffalo", "goat", "sheep", "poultry"]),
    ]

    medicines: dict[str, Medicine] = {}
    for name_en, name_kn, med_type, milk_wd, meat_wd, species in medicine_specs:
        med = Medicine(
            name_en=name_en,
            name_kn=name_kn,
            type=med_type,
            withdrawal_milk_days=milk_wd,
            withdrawal_meat_days=meat_wd,
            species_applicable=species,
        )
        session.add(med)
        medicines[name_en] = med

    await session.flush()
    print(f"  Medicines seeded: {len(medicines)}")
    return medicines


# ---------------------------------------------------------------------------
# 18. Advisory Tips (15 bilingual tips)
# ---------------------------------------------------------------------------
async def seed_advisory_tips(session: AsyncSession) -> int:
    """Create 15 advisory tips across health, feeding, breeding, and government categories."""
    count_result = await session.execute(select(AdvisoryTip))
    if count_result.first() is not None:
        print("  Advisory tips already exist, skipping.")
        return 0

    tips = [
        # --- Health Tips (5) ---
        {
            "title_en": "Deworming Schedule for Livestock",
            "title_kn": "ಜಾನುವಾರು ಜಂತುಹುಳ ನಿವಾರಣೆ ವೇಳಾಪಟ್ಟಿ",
            "body_en": "Deworm all cattle and goats every 3 months using broad-spectrum anthelmintics. Rotate between Albendazole and Fenbendazole to prevent resistance. Deworm before monsoon and after monsoon season for best results. Young stock should be dewormed from 3 months of age.",
            "body_kn": "ಪ್ರತಿ 3 ತಿಂಗಳಿಗೊಮ್ಮೆ ಎಲ್ಲಾ ಜಾನುವಾರು ಮತ್ತು ಮೇಕೆಗಳಿಗೆ ಜಂತುಹುಳ ಔಷಧಿ ಕೊಡಿ. ಆಲ್ಬೆಂಡಜೋಲ್ ಮತ್ತು ಫೆನ್ಬೆಂಡಜೋಲ್ ನಡುವೆ ಬದಲಾಯಿಸಿ. ಮಳೆಗಾಲದ ಮೊದಲು ಮತ್ತು ನಂತರ ಔಷಧಿ ನೀಡಿ.",
            "category": AdvisoryCategory.health,
            "species_applicable": ["cattle", "buffalo", "goat", "sheep"],
            "source": AdvisorySource.ICAR,
            "priority": 8,
            "is_active": True,
        },
        {
            "title_en": "Heat Stress Prevention in Summer",
            "title_kn": "ಬೇಸಿಗೆಯಲ್ಲಿ ಉಷ್ಣ ಒತ್ತಡ ತಡೆಗಟ್ಟುವಿಕೆ",
            "body_en": "During summer months (March-June), provide shade structures and ensure 24/7 water access. Install fans or misters in sheds. Avoid grazing between 11 AM and 3 PM. Add electrolytes to drinking water. Milk yield can drop 20-30% without heat management.",
            "body_kn": "ಬೇಸಿಗೆ ತಿಂಗಳುಗಳಲ್ಲಿ ನೆರಳು ಮತ್ತು 24 ಗಂಟೆ ನೀರಿನ ವ್ಯವಸ್ಥೆ ಮಾಡಿ. ಬೆಳಿಗ್ಗೆ 11 ರಿಂದ ಮಧ್ಯಾಹ್ನ 3 ರ ನಡುವೆ ಮೇಯಿಸಬೇಡಿ. ಕುಡಿಯುವ ನೀರಿಗೆ ಎಲೆಕ್ಟ್ರೋಲೈಟ್ ಸೇರಿಸಿ.",
            "category": AdvisoryCategory.health,
            "species_applicable": ["cattle", "buffalo", "goat", "sheep"],
            "source": AdvisorySource.ICAR,
            "priority": 9,
            "is_active": True,
        },
        {
            "title_en": "FMD Vaccination Reminder — April 2026",
            "title_kn": "ಎಫ್‌ಎಂಡಿ ಲಸಿಕೆ ನೆನಪೋಲೆ — ಏಪ್ರಿಲ್ 2026",
            "body_en": "FMD vaccination round scheduled for April 15-30, 2026 under the National FMD Control Programme. All cattle, buffalo, goat, sheep, and pigs must be vaccinated. Contact your nearest veterinary dispensary or call 1962 helpline. Vaccination is FREE of cost.",
            "body_kn": "ರಾಷ್ಟ್ರೀಯ ಎಫ್‌ಎಂಡಿ ನಿಯಂತ್ರಣ ಕಾರ್ಯಕ್ರಮದ ಅಡಿಯಲ್ಲಿ ಏಪ್ರಿಲ್ 15-30 ರಂದು ಲಸಿಕೆ ಅಭಿಯಾನ. ಎಲ್ಲಾ ಜಾನುವಾರುಗಳಿಗೆ ಉಚಿತ ಲಸಿಕೆ. 1962 ಸಹಾಯವಾಣಿಗೆ ಕರೆ ಮಾಡಿ.",
            "category": AdvisoryCategory.health,
            "species_applicable": ["cattle", "buffalo", "goat", "sheep"],
            "source": AdvisorySource.ICAR,
            "priority": 10,
            "is_active": True,
        },
        {
            "title_en": "Mastitis Prevention — Clean Milking Practices",
            "title_kn": "ಕೆಚ್ಚಲು ಊತ ತಡೆಗಟ್ಟುವಿಕೆ — ಶುಚಿ ಹಾಲು ಕರೆಯುವಿಕೆ",
            "body_en": "Wash hands and udder with warm water before milking. Use teat dip after milking. Strip first 2-3 streams into a strip cup to check for clots. Keep milking area clean and dry. Treat clinical mastitis immediately — each day delay increases recovery time by 3 days.",
            "body_kn": "ಹಾಲು ಕರೆಯುವ ಮೊದಲು ಕೈ ಮತ್ತು ಕೆಚ್ಚಲನ್ನು ಬೆಚ್ಚಗಿನ ನೀರಿನಿಂದ ತೊಳೆಯಿರಿ. ಹಾಲು ಕರೆದ ನಂತರ ಟೀಟ್ ಡಿಪ್ ಬಳಸಿ. ಕೆಚ್ಚಲು ಊತಕ್ಕೆ ತಕ್ಷಣ ಚಿಕಿತ್ಸೆ ನೀಡಿ.",
            "category": AdvisoryCategory.health,
            "species_applicable": ["cattle", "buffalo", "goat"],
            "source": AdvisorySource.KMF,
            "priority": 8,
            "is_active": True,
        },
        {
            "title_en": "Tick Control in Monsoon Season",
            "title_kn": "ಮಳೆಗಾಲದಲ್ಲಿ ಉಣ್ಣಿ ನಿಯಂತ್ರಣ",
            "body_en": "Tick population peaks during monsoon. Inspect animals daily, especially ears, dewlap, and udder region. Use approved acaricides (Amitraz, Deltamethrin) as pour-on or spray. Traditional neem oil spray also helps. Remove vegetation around sheds to reduce tick habitat.",
            "body_kn": "ಮಳೆಗಾಲದಲ್ಲಿ ಉಣ್ಣಿ ಹೆಚ್ಚಾಗುತ್ತವೆ. ಪ್ರತಿದಿನ ಪ್ರಾಣಿಗಳನ್ನು ಪರೀಕ್ಷಿಸಿ. ಅನುಮೋದಿತ ಔಷಧಿ ಅಥವಾ ಬೇವಿನ ಎಣ್ಣೆ ಸಿಂಪಡಿಸಿ. ಕೊಟ್ಟಿಗೆ ಸುತ್ತ ಕಳೆ ತೆಗೆಯಿರಿ.",
            "category": AdvisoryCategory.health,
            "species_applicable": ["cattle", "buffalo", "goat", "sheep"],
            "source": AdvisorySource.ICAR,
            "priority": 7,
            "is_active": True,
        },
        # --- Feeding Tips (4) ---
        {
            "title_en": "Monsoon Fodder Storage — Silage Making",
            "title_kn": "ಮಳೆಗಾಲದ ಮೇವು ಸಂಗ್ರಹ — ಸೈಲೇಜ್ ತಯಾರಿಕೆ",
            "body_en": "Prepare silage before monsoon using maize or sorghum fodder. Chop to 2-3 cm pieces, fill in pit/bag, compress tightly, and seal. Good silage has sweet smell and olive-green color. One cow needs ~10 tons of silage for 4 months of monsoon.",
            "body_kn": "ಮಳೆಗಾಲಕ್ಕೆ ಮೊದಲು ಮೆಕ್ಕೆಜೋಳ ಅಥವಾ ಜೋಳದಿಂದ ಸೈಲೇಜ್ ತಯಾರಿಸಿ. 2-3 ಸೆಂ.ಮೀ. ತುಂಡು ಮಾಡಿ, ಗುಂಡಿಯಲ್ಲಿ ಭದ್ರವಾಗಿ ತುಂಬಿ ಮುಚ್ಚಿ.",
            "category": AdvisoryCategory.feeding,
            "species_applicable": ["cattle", "buffalo"],
            "source": AdvisorySource.ICAR,
            "priority": 7,
            "is_active": True,
        },
        {
            "title_en": "Mineral Supplementation for Dairy Animals",
            "title_kn": "ಹೈನು ಪ್ರಾಣಿಗಳಿಗೆ ಖನಿಜ ಪೂರಕ",
            "body_en": "Mix 30-50g mineral mixture per day in concentrate feed for dairy animals. Provide salt lick blocks in the shed. Calcium deficiency leads to milk fever; phosphorus deficiency causes poor conception. NDDB-approved mineral mixtures are available at milk cooperatives.",
            "body_kn": "ಹೈನು ಪ್ರಾಣಿಗಳಿಗೆ ದಿನಕ್ಕೆ 30-50 ಗ್ರಾಂ ಖನಿಜ ಮಿಶ್ರಣ ಕೊಡಿ. ಕೊಟ್ಟಿಗೆಯಲ್ಲಿ ಉಪ್ಪಿನ ಕಲ್ಲು ಇಡಿ. ಕ್ಯಾಲ್ಸಿಯಂ ಕೊರತೆಯಿಂದ ಹಾಲು ಜ್ವರ ಬರುತ್ತದೆ.",
            "category": AdvisoryCategory.feeding,
            "species_applicable": ["cattle", "buffalo", "goat"],
            "source": AdvisorySource.KMF,
            "priority": 6,
            "is_active": True,
        },
        {
            "title_en": "Lactation Feeding — Balanced Ration",
            "title_kn": "ಹಾಲು ಕೊಡುವ ಅವಧಿಯ ಆಹಾರ",
            "body_en": "For every liter of milk produced, provide 400g concentrate feed above maintenance. A cow producing 10 liters needs: 5kg dry roughage + 10kg green fodder + 4kg concentrate + 50g mineral mix. Ensure clean water ad libitum (60-80 liters/day for high yielders).",
            "body_kn": "ಪ್ರತಿ ಲೀಟರ್ ಹಾಲಿಗೆ 400 ಗ್ರಾಂ ಹಿಂಡಿ ಕೊಡಿ. 10 ಲೀಟರ್ ಹಾಲಿನ ಹಸುವಿಗೆ: 5 ಕೆ.ಜಿ. ಒಣ ಹುಲ್ಲು + 10 ಕೆ.ಜಿ. ಹಸಿರು ಮೇವು + 4 ಕೆ.ಜಿ. ಹಿಂಡಿ + 50 ಗ್ರಾಂ ಖನಿಜ ಮಿಶ್ರಣ.",
            "category": AdvisoryCategory.feeding,
            "species_applicable": ["cattle", "buffalo"],
            "source": AdvisorySource.ICAR,
            "priority": 7,
            "is_active": True,
        },
        {
            "title_en": "Colostrum Management for Newborn Calves",
            "title_kn": "ಹೊಸ ಕರುಗಳಿಗೆ ಜುಂಜು ಹಾಲು ನಿರ್ವಹಣೆ",
            "body_en": "Feed colostrum within 1 hour of birth — this is critical for calf survival. Give 2 liters in first feeding, then 2 liters every 6 hours for first 3 days. Colostrum provides antibodies that protect against diseases. Never discard colostrum.",
            "body_kn": "ಕರು ಹುಟ್ಟಿದ 1 ಗಂಟೆಯೊಳಗೆ ಜುಂಜು ಹಾಲು ಕೊಡಿ. ಮೊದಲ ಬಾರಿ 2 ಲೀಟರ್, ನಂತರ ಪ್ರತಿ 6 ಗಂಟೆಗೆ 2 ಲೀಟರ್ 3 ದಿನ ಕೊಡಿ. ಜುಂಜು ಹಾಲು ರೋಗ ನಿರೋಧಕ ಶಕ್ತಿ ಕೊಡುತ್ತದೆ.",
            "category": AdvisoryCategory.feeding,
            "species_applicable": ["cattle", "buffalo", "goat"],
            "source": AdvisorySource.ICAR,
            "priority": 9,
            "is_active": True,
        },
        # --- Breeding Tips (3) ---
        {
            "title_en": "AI Timing — When to Inseminate",
            "title_kn": "ಕೃತಕ ಗರ್ಭಧಾರಣೆ ಸಮಯ",
            "body_en": "Inseminate 12-18 hours after first signs of heat (standing heat). AM-PM rule: if heat detected in morning, inseminate in evening; if detected in evening, inseminate next morning. Use only ICAR-approved semen straws. Contact your nearest AI center or call 1962.",
            "body_kn": "ಬೆದೆಯ ಮೊದಲ ಲಕ್ಷಣ ಕಂಡ 12-18 ಗಂಟೆ ನಂತರ ಕೃತಕ ಗರ್ಭಧಾರಣೆ ಮಾಡಿಸಿ. ಬೆಳಿಗ್ಗೆ ಬೆದೆ ಕಂಡರೆ ಸಂಜೆ, ಸಂಜೆ ಕಂಡರೆ ಮರುದಿನ ಬೆಳಿಗ್ಗೆ. 1962 ಸಹಾಯವಾಣಿಗೆ ಕರೆ ಮಾಡಿ.",
            "category": AdvisoryCategory.breeding,
            "species_applicable": ["cattle", "buffalo"],
            "source": AdvisorySource.ICAR,
            "priority": 7,
            "is_active": True,
        },
        {
            "title_en": "Pregnancy Detection at 60 Days",
            "title_kn": "60 ದಿನಗಳಲ್ಲಿ ಗರ್ಭ ಪರೀಕ್ಷೆ",
            "body_en": "Get pregnancy confirmed by veterinarian at 60 days post-AI through rectal examination. Early detection helps plan dry period, nutrition, and calving preparation. Non-return to heat after 21 days is a positive sign but not confirmatory.",
            "body_kn": "ಕೃತಕ ಗರ್ಭಧಾರಣೆಯ 60 ದಿನಗಳ ನಂತರ ಪಶುವೈದ್ಯರಿಂದ ಗರ್ಭ ಪರೀಕ್ಷೆ ಮಾಡಿಸಿ. 21 ದಿನಗಳ ನಂತರ ಬೆದೆ ಬಾರದಿರುವುದು ಒಳ್ಳೆಯ ಸಂಕೇತ.",
            "category": AdvisoryCategory.breeding,
            "species_applicable": ["cattle", "buffalo", "goat"],
            "source": AdvisorySource.ICAR,
            "priority": 6,
            "is_active": True,
        },
        {
            "title_en": "Calving Preparation — Last 2 Weeks",
            "title_kn": "ಕರು ಹಾಕುವ ತಯಾರಿ — ಕೊನೆಯ 2 ವಾರ",
            "body_en": "2 weeks before expected calving: move cow to clean, dry calving pen. Increase concentrate by 1 kg/day. Deworm and vaccinate if pending. Keep emergency vet number ready. Signs of imminent calving: udder filling, relaxation of pelvic ligaments, mucus discharge.",
            "body_kn": "ಕರು ಹಾಕುವ 2 ವಾರ ಮೊದಲು: ಶುಚಿ ಕೊಟ್ಟಿಗೆಗೆ ಸ್ಥಳಾಂತರಿಸಿ. ಹಿಂಡಿ 1 ಕೆ.ಜಿ. ಹೆಚ್ಚಿಸಿ. ಜಂತುಹುಳ ಮತ್ತು ಲಸಿಕೆ ಬಾಕಿ ಇದ್ದರೆ ಕೊಡಿ. ಪಶುವೈದ್ಯರ ಸಂಖ್ಯೆ ಸಿದ್ಧವಾಗಿರಲಿ.",
            "category": AdvisoryCategory.breeding,
            "species_applicable": ["cattle", "buffalo"],
            "source": AdvisorySource.ICAR,
            "priority": 8,
            "is_active": True,
        },
        # --- Government Announcements (3) ---
        {
            "title_en": "NABARD Dairy Subsidy — Apply Before June 30",
            "title_kn": "ನಬಾರ್ಡ್ ಹೈನು ಸಬ್ಸಿಡಿ — ಜೂನ್ 30 ಒಳಗೆ ಅರ್ಜಿ ಹಾಕಿ",
            "body_en": "NABARD Dairy Entrepreneurship Development Scheme open for applications. Get up to 25% subsidy (max ₹7 lakh) for dairy units, milking machines, and cold storage. Apply through your nearest bank branch with project report. SHG members get priority processing.",
            "body_kn": "ನಬಾರ್ಡ್ ಹೈನು ಉದ್ಯಮ ಯೋಜನೆಗೆ ಅರ್ಜಿ ಆಹ್ವಾನ. 25% ಸಬ್ಸಿಡಿ (ಗರಿಷ್ಠ ₹7 ಲಕ್ಷ). ಹತ್ತಿರದ ಬ್ಯಾಂಕ್ ಶಾಖೆಯಲ್ಲಿ ಅರ್ಜಿ ಹಾಕಿ. ಸ್ವಸಹಾಯ ಗುಂಪು ಸದಸ್ಯರಿಗೆ ಆದ್ಯತೆ.",
            "category": AdvisoryCategory.government,
            "species_applicable": ["cattle", "buffalo", "goat"],
            "source": AdvisorySource.NABARD,
            "priority": 9,
            "is_active": True,
        },
        {
            "title_en": "KMF Announces ₹2/liter Bonus for April",
            "title_kn": "ಕೆಎಂಎಫ್ ಏಪ್ರಿಲ್ ತಿಂಗಳಿಗೆ ₹2/ಲೀಟರ್ ಬೋನಸ್ ಘೋಷಣೆ",
            "body_en": "KMF has announced a bonus of ₹2 per liter for milk supplied during April 2026 to all its cooperative member farmers. The bonus will be credited to your bank account along with the regular May payment. Ensure your bank details are updated with your cooperative.",
            "body_kn": "ಕೆಎಂಎಫ್ ಏಪ್ರಿಲ್ 2026 ರ ಹಾಲು ಪೂರೈಕೆಗೆ ₹2/ಲೀಟರ್ ಬೋನಸ್ ಘೋಷಿಸಿದೆ. ಮೇ ತಿಂಗಳ ಪಾವತಿಯೊಂದಿಗೆ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ ಜಮಾ ಆಗುತ್ತದೆ. ನಿಮ್ಮ ಬ್ಯಾಂಕ್ ವಿವರ ಸಹಕಾರ ಸಂಘದಲ್ಲಿ ನವೀಕರಿಸಿ.",
            "category": AdvisoryCategory.government,
            "species_applicable": ["cattle", "buffalo"],
            "source": AdvisorySource.KMF,
            "priority": 10,
            "is_active": True,
        },
        {
            "title_en": "Livestock Insurance Enrollment — Last Date May 15",
            "title_kn": "ಜಾನುವಾರು ವಿಮೆ ನೋಂದಣಿ — ಕೊನೆಯ ದಿನಾಂಕ ಮೇ 15",
            "body_en": "Government-subsidized livestock insurance enrollment is open. Farmers pay only 50% premium (remaining by state/central government). Cover available for cattle, buffalo, goat, sheep, and poultry. Requires Pashu Aadhaar, health certificate from vet, and 2 photos of animal with ear tag visible.",
            "body_kn": "ಸರ್ಕಾರಿ ಸಬ್ಸಿಡಿ ಜಾನುವಾರು ವಿಮೆ ನೋಂದಣಿ ಪ್ರಾರಂಭ. ರೈತರು ಅರ್ಧ ಪ್ರೀಮಿಯಂ ಮಾತ್ರ ಕಟ್ಟಬೇಕು. ಪಶು ಆಧಾರ್, ಆರೋಗ್ಯ ಪ್ರಮಾಣಪತ್ರ, ಮತ್ತು 2 ಫೋಟೋ ಬೇಕು.",
            "category": AdvisoryCategory.government,
            "species_applicable": ["cattle", "buffalo", "goat", "sheep", "poultry"],
            "source": AdvisorySource.Community,
            "priority": 9,
            "is_active": True,
        },
    ]

    for t in tips:
        session.add(AdvisoryTip(**t))

    await session.flush()
    print(f"  Advisory tips seeded: {len(tips)}")
    return len(tips)


# ---------------------------------------------------------------------------
# 19. Medicine Administrations
# ---------------------------------------------------------------------------
async def seed_medicine_administrations(
    session: AsyncSession, animals: dict, medicines: dict
) -> int:
    """Create 2 medicine administration records with withdrawal tracking."""
    count_result = await session.execute(select(MedicineAdministration))
    if count_result.first() is not None:
        print("  Medicine administrations already exist, skipping.")
        return 0

    now = datetime.now(UTC)
    administrations = [
        {
            "animal_key": "gowri",
            "medicine_name": "Oxytetracycline",
            "days_ago": 3,
        },
        {
            "animal_key": "gauri_goat",
            "medicine_name": "Ivermectin",
            "days_ago": 10,
        },
    ]

    count = 0
    for spec in administrations:
        med = medicines.get(spec["medicine_name"])
        animal = animals.get(spec["animal_key"])
        if not med or not animal:
            print(f"  Skipping admin for {spec['animal_key']}/{spec['medicine_name']}: not found.")
            continue

        administered_at = now - timedelta(days=spec["days_ago"])
        admin_date = (now - timedelta(days=spec["days_ago"])).date()
        milk_until = admin_date + timedelta(days=med.withdrawal_milk_days)
        meat_until = admin_date + timedelta(days=med.withdrawal_meat_days)

        admin_rec = MedicineAdministration(
            animal_id=animal.id,
            medicine_id=med.id,
            administered_at=administered_at,
            withdrawal_milk_until=milk_until,
            withdrawal_meat_until=meat_until,
        )
        session.add(admin_rec)
        count += 1

    await session.flush()
    print(f"  Medicine administrations seeded: {count}")
    return count


# ---------------------------------------------------------------------------
# 20. Vet Consultations
# ---------------------------------------------------------------------------
async def seed_vet_consultations(
    session: AsyncSession, users: dict, animals: dict
) -> int:
    """Create 3 sample VetConsultation records: pending, diagnosed, and one with video_call_url."""
    count_result = await session.execute(select(VetConsultation))
    if count_result.first() is not None:
        print("  Vet consultations already exist, skipping.")
        return 0

    now = datetime.now(UTC)
    vet_id = str(users["vet_ramesh"].id)

    consultation_specs = [
        # Pending — Gowri suspected mastitis, photo submission
        {
            "animal_key": "gowri",
            "farmer_key": "lakshmi",
            "status": ConsultationStatus.pending,
            "priority": ConsultationPriority.emergency,
            "channel": ConsultationChannel.photo,
            "farmer_notes": "Gowri showing fever, reduced milk output, and swollen udder. Suspected mastitis.",
            "photo_urls": [
                "/uploads/gowri_udder_01.jpg",
                "/uploads/gowri_udder_02.jpg",
            ],
            "diagnosis": None,
            "prescription": None,
            "follow_up_date": None,
            "video_call_url": None,
            "vet_id": None,
            "district": "Mysore",
            "days_ago": 2,
        },
        # Diagnosed — Nandini foot rot, vet assigned
        {
            "animal_key": "nandini",
            "farmer_key": "annapurna",
            "status": ConsultationStatus.diagnosed,
            "priority": ConsultationPriority.urgent,
            "channel": ConsultationChannel.referral,
            "farmer_notes": "Nandini limping on right hind leg. Mild swelling observed.",
            "photo_urls": None,
            "diagnosis": "Foot Rot — interdigital necrobacillosis. Moderate infection, no systemic involvement.",
            "prescription": "Clean wound with potassium permanganate. Apply oxytetracycline spray. Oral meloxicam 0.5mg/kg for 3 days.",
            "follow_up_date": (TODAY + timedelta(days=5)),
            "video_call_url": None,
            "vet_id": vet_id,
            "district": "Mandya",
            "days_ago": 5,
        },
        # In-review — Gauri goat diarrhea, video call scheduled
        {
            "animal_key": "gauri_goat",
            "farmer_key": "lakshmi",
            "status": ConsultationStatus.in_review,
            "priority": ConsultationPriority.routine,
            "channel": ConsultationChannel.photo,
            "farmer_notes": "Gauri has loose stools for 2 days. Eating normally.",
            "photo_urls": ["/uploads/gauri_stool_sample.jpg"],
            "diagnosis": None,
            "prescription": None,
            "follow_up_date": None,
            "video_call_url": "https://meet.pashuraksha.in/consult/gauri-20260412",
            "vet_id": vet_id,
            "district": "Mysore",
            "days_ago": 3,
        },
    ]

    count = 0
    for spec in consultation_specs:
        created_at = now - timedelta(days=spec["days_ago"])
        consultation = VetConsultation(
            animal_id=str(animals[spec["animal_key"]].id),
            farmer_id=str(users[spec["farmer_key"]].id),
            vet_id=spec["vet_id"],
            status=spec["status"],
            priority=spec["priority"],
            channel=spec["channel"],
            farmer_notes=spec["farmer_notes"],
            photo_urls=spec["photo_urls"],
            diagnosis=spec["diagnosis"],
            prescription=spec["prescription"],
            follow_up_date=spec["follow_up_date"],
            video_call_url=spec["video_call_url"],
            district=spec["district"],
        )
        session.add(consultation)
        count += 1

    await session.flush()
    print(f"  Vet consultations seeded: {count}")
    return count


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
async def main():
    print("PashuRaksha ERP — Seeding demo data...")
    print("=" * 50)

    engine = create_async_engine(settings.database_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            print("\n[1/20] Users")
            users = await seed_users(session)

            print("[2/20] Animals")
            animals = await seed_animals(session, users)

            print("[3/20] Milk Collection Center")
            centers = await seed_milk_center(session, users)

            print("[4/20] Milk Yield Logs (30 days)")
            await seed_yield_logs(session, users, animals)

            print("[5/20] Milk Collection Records (30 days)")
            await seed_milk_collections(session, users, centers)

            print("[6/20] Health Events")
            await seed_health_events(session, users, animals)

            print("[7/20] Vaccinations")
            await seed_vaccinations(session, users, animals)

            print("[8/20] Sell Records (15 days)")
            sell_records = await seed_sell_records(session, users)

            print("[9/20] Financial Transactions")
            await seed_transactions(session, sell_records)

            print("[10/20] SHG Groups")
            await seed_shg_groups(session, users)

            print("[11/20] Government Schemes")
            await seed_govt_schemes(session)

            print("[12/20] Weather Alerts")
            await seed_weather_alerts(session)

            print("[13/20] Feed Ingredients")
            await seed_feed_ingredients(session)

            print("[14/20] Ethno-Veterinary Remedies")
            await seed_ethno_vet_remedies(session)

            print("[15/20] Insurance Policies & Claims")
            await seed_insurance_policies(session, users, animals)

            print("[16/20] Community Alerts")
            await seed_community_alerts(session, users)

            print("[17/20] Medicines")
            medicines = await seed_medicines(session)

            print("[18/20] Advisory Tips")
            await seed_advisory_tips(session)

            print("[19/20] Medicine Administrations")
            await seed_medicine_administrations(session, animals, medicines)

            print("[20/20] Vet Consultations")
            await seed_vet_consultations(session, users, animals)

        print("\n" + "=" * 50)
        print("Seed data loaded successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
