from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_farmers: int
    total_animals: int
    today_milk_liters: float
    active_alerts: int
    marketplace_revenue: float
    active_sellers: int


class MilkChartData(BaseModel):
    date: str
    liters: float


class GISAlertData(BaseModel):
    lat: float
    lon: float
    severity: str
    disease: str
    animal_name: str
    farmer_name: str
    event_date: str
