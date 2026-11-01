from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Executive KPI
class ExecutiveKPIResponse(BaseModel):
    total_bookings: int
    canceled_bookings: int
    non_canceled_bookings: int
    cancellation_rate_pct: float
    avg_lead_time_days: float
    avg_adr: float
    median_adr: float
    total_booked_nights: int
    estimated_gross_booking_value: float
    estimated_realized_booking_value: float
    repeat_guest_pct: float
    room_reassignment_pct: float
    avg_special_requests: float

# Monthly Trend
class MonthlyTrendItem(BaseModel):
    year_month: str
    arrival_year: int
    arrival_month: str
    total_bookings: int
    confirmed_bookings: int
    canceled_bookings: int
    cancellation_rate_pct: float
    avg_adr: float
    realized_booking_value: float

# Hotel Comparison
class HotelComparisonItem(BaseModel):
    hotel: str
    total_bookings: int
    canceled_bookings: int
    cancellation_rate_pct: float
    avg_lead_time_days: float
    avg_adr: float
    median_adr: float
    avg_stay_nights: float
    realized_booking_value: float
    repeat_guest_pct: float
    room_reassignment_pct: float

# Lead Time Band
class LeadTimeBandItem(BaseModel):
    lead_time_band: str
    total_bookings: int
    canceled_bookings: int
    cancellation_rate_pct: float
    avg_adr: float

# Deposit Type
class DepositTypeItem(BaseModel):
    deposit_type: str
    total_bookings: int
    canceled_bookings: int
    cancellation_rate_pct: float
    avg_lead_time_days: float

# Distribution Channel
class ChannelItem(BaseModel):
    distribution_channel_name: str
    total_bookings: int
    booking_share_pct: float
    canceled_bookings: int
    cancellation_rate_pct: float
    avg_lead_time_days: float
    avg_adr: float
    realized_booking_value: float

# Guest Composition
class GuestCompositionItem(BaseModel):
    guest_composition_type: str
    total_bookings: int
    composition_share_pct: float
    canceled_bookings: int
    cancellation_rate_pct: float
    avg_adr: float

# Country Item
class CountryItem(BaseModel):
    country_code: str
    country_name: str
    total_bookings: int
    country_share_pct: float
    canceled_bookings: int
    cancellation_rate_pct: float
    avg_adr: float

# Room Reassignment
class RoomReassignmentResponse(BaseModel):
    total_bookings: int
    reassigned_bookings: int
    reassignment_rate_pct: float
    operational_reassignments: int
    operational_reassignment_pct: float
    reassigned_cancellation_rate_pct: float
    same_room_cancellation_rate_pct: float

# Chat Request & Response
class AnalyzeRequest(BaseModel):
    question: str = Field(..., description="Natural language analytics question")
    thread_id: Optional[str] = Field(None, description="Conversation session thread ID")
    hotel_filter: Optional[str] = Field("All", description="Optional hotel property filter")

class AnalyzeResponse(BaseModel):
    answer: str
    sql_query: Optional[str] = None
    data: Optional[List[Dict[str, Any]]] = None
    chart_type: Optional[str] = None
    thread_id: str
    execution_time_seconds: float
    tokens_used: Optional[int] = None
