"""Pydantic schema registry — re-exports for convenience.

Each sub-module defines its own public names; the package-level ``__all__``
is the union of all of them so that ``from app.schemas import X`` works and
star-imports are bounded.
"""

from app.schemas.admin import *  # noqa: F401, F403
from app.schemas.advisory import *  # noqa: F401, F403
from app.schemas.alerts import *  # noqa: F401, F403
from app.schemas.animals import *  # noqa: F401, F403
from app.schemas.auth import *  # noqa: F401, F403
from app.schemas.bharat_pashudhan import *  # noqa: F401, F403
from app.schemas.ethno_vet import *  # noqa: F401, F403
from app.schemas.feed import *  # noqa: F401, F403
from app.schemas.files import *  # noqa: F401, F403
from app.schemas.finance import *  # noqa: F401, F403
from app.schemas.health import *  # noqa: F401, F403
from app.schemas.income import *  # noqa: F401, F403
from app.schemas.insurance import *  # noqa: F401, F403
from app.schemas.iot import *  # noqa: F401, F403
from app.schemas.map_points import *  # noqa: F401, F403
from app.schemas.marketplace import *  # noqa: F401, F403
from app.schemas.medicine import *  # noqa: F401, F403
from app.schemas.medicine_log import *  # noqa: F401, F403
from app.schemas.milk import *  # noqa: F401, F403
from app.schemas.milk_center import *  # noqa: F401, F403
from app.schemas.onboarding import *  # noqa: F401, F403
from app.schemas.reference import *  # noqa: F401, F403
from app.schemas.schemes import *  # noqa: F401, F403
from app.schemas.shg import *  # noqa: F401, F403
from app.schemas.users import *  # noqa: F401, F403
from app.schemas.vaccination import *  # noqa: F401, F403
from app.schemas.vet import *  # noqa: F401, F403
from app.schemas.weather import *  # noqa: F401, F403

__all__ = [  # noqa: F405
    # admin
    "DashboardStats",
    "MilkChartData",
    "GISAlertData",
    # advisory
    "AdvisoryCategory",
    "AdvisorySource",
    "AdvisoryTipRead",
    "AdvisoryTipListResponse",
    # alerts
    "CommunityAlertSeverity",
    "CommunityAlertCreate",
    "CommunityAlertRead",
    # animals
    "Species",
    "BreedType",
    "AnimalSex",
    "AnimalCreate",
    "AnimalUpdate",
    "AnimalRead",
    "AnimalListResponse",
    # auth
    "OTPRequest",
    "OTPVerify",
    "AuthUserResponse",
    "TokenResponse",
    "RefreshTokenRequest",
    "AuthErrorCode",
    "AuthErrorResponse",
    # bharat_pashudhan
    "RegistryOwner",
    "RegistryGPS",
    "RegistryVaccination",
    "RegistryInsurance",
    "RegistryAnimalLookup",
    "RegistrySyncResponse",
    # ethno_vet
    "EvidenceRating",
    "TraditionalRemedyRead",
    "TraditionalRemedyListResponse",
    # feed
    "FeedCategory",
    "LactationStage",
    "FeedIngredientRead",
    "FeedIngredientListResponse",
    "RationIngredient",
    "RationRequest",
    "RationResult",
    # files
    "FileUploadResponse",
    "FileMetadata",
    "FileListResponse",
    # finance
    "TransactionType",
    "TransactionStatus",
    "TransactionCreate",
    "TransactionRead",
    "FinanceSummary",
    # health
    "HealthEventType",
    "HealthEventCreate",
    "HealthEventRead",
    "HealthEventListResponse",
    "VaccinationCreate",
    "VaccinationRead",
    "TriageResult",
    # income
    "IncomeSummary",
    "IncomeBreakdown",
    # insurance
    "PolicyStatus",
    "ClaimStatus",
    "InsurancePolicyRead",
    "InsurancePolicyListResponse",
    "InsuranceClaimCreate",
    "InsuranceClaimRead",
    "PremiumEstimate",
    # iot
    "IoTDeviceRead",
    "IoTDeviceListResponse",
    "DeviceTypeCount",
    "TelemetryMetric",
    "TelemetryReading",
    "TelemetryListResponse",
    # map_points
    "HealthAlertPoint",
    "MilkCenterPoint",
    "CommunityAlertPoint",
    "FarmerClusterPoint",
    "MapPoint",
    "MapPointsResponse",
    # marketplace
    "ProductType",
    "SellRecordCreate",
    "SellRecordRead",
    "SellRecordListResponse",
    "MarketplaceSummary",
    "ProductPriceRate",
    # medicine
    "MedicineRead",
    "MedicineAdministerRequest",
    "WithdrawalStatus",
    # medicine_log
    "WithdrawalItem",
    "WithdrawalListResponse",
    # milk
    "MilkSession",
    "YieldLogCreate",
    "YieldLogRead",
    "YieldLogListResponse",
    "MilkHistoryResponse",
    "CollectionRecordCreate",
    "CollectionRecordRead",
    # milk_center
    "MilkReceiveRequest",
    "QuickEnrollRequest",
    "MyCenterResponse",
    "MilkReceiveResponse",
    "ShiftSummary",
    "DailyReportSummary",
    "DailyReportResponse",
    "FarmerSettlementItem",
    "FarmerSettlementsResponse",
    "FarmerSearchResult",
    "QuickEnrollResponse",
    # onboarding
    "OnboardingCompleteRequest",
    "OnboardingPreferences",
    "OnboardingCompleteResponse",
    # reference
    "MarketRateUpdate",
    "MarketRateRead",
    "MarketRateListResponse",
    "InsurancePremiumUpdate",
    "InsurancePremiumRead",
    "InsurancePremiumListResponse",
    "MedicineCatalogRead",
    "MedicineCatalogListResponse",
    # schemes
    "GovtSchemeCreate",
    "GovtSchemeRead",
    "GovtSchemeListResponse",
    # shg
    "SHGGrading",
    "SHGGroupCreate",
    "SHGGroupUpdate",
    "SHGGroupRead",
    "SHGGroupListResponse",
    "PanchsutraScore",
    # users
    "UserRoleUpdate",
    "FarmerListItem",
    "FarmerListResponse",
    "UserProfile",
    # vaccination
    "SpeciesBreakdownItem",
    "SpeciesBreakdownResponse",
    "VillageCoverageItem",
    "VillageCoverageResponse",
    "ScheduleEntry",
    "ScheduleListResponse",
    "SpeciesScheduleResponse",
    "DueVaccinationItem",
    "DueVaccinationsResponse",
    "SingleVillageCoverage",
    # vet
    "ConsultationStatus",
    "ConsultationPriority",
    "ConsultationChannel",
    "DiagnoseBody",
    "VideoLinkBody",
    "OwnerBrief",
    "AnimalBrief",
    "FarmerBrief",
    "VetCaseRead",
    "VetCaseListResponse",
    "VetMyCasesResponse",
    "VetDashboardStats",
    "VetDashboardAlertsResponse",
    "CommunityAlertRead",
    "HealthEventRead",
    # validators (shared utilities)
    "strip_html",
    # weather
    "WeatherAlertSeverity",
    "WeatherAlertCreate",
    "WeatherAlertRead",
    "WeatherForecast",
]
