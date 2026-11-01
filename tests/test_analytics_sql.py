import pytest
from src.services.overview_service import get_executive_kpis, get_hotel_comparison
from src.services.room_service import get_room_reassignment_summary

def test_executive_kpis_accuracy():
    """Verify that calculated KPIs match empirical Phase 1 baseline values."""
    kpis = get_executive_kpis()
    assert kpis["total_bookings"] == 119390
    assert kpis["canceled_bookings"] == 44224
    assert kpis["non_canceled_bookings"] == 75166
    assert float(kpis["cancellation_rate_pct"]) == 37.04
    assert float(kpis["avg_lead_time_days"]) == 104.01
    assert float(kpis["avg_adr"]) == 101.83
    assert float(kpis["repeat_guest_pct"]) == 3.19
    assert float(kpis["room_reassignment_pct"]) == 12.49

def test_hotel_comparison_distribution():
    """Verify hotel distribution between City Hotel and Resort Hotel."""
    comp = get_hotel_comparison()
    hotel_dict = {h["hotel"]: h for h in comp}
    assert "City Hotel" in hotel_dict
    assert "Resort Hotel" in hotel_dict
    assert hotel_dict["City Hotel"]["total_bookings"] == 79330
    assert hotel_dict["Resort Hotel"]["total_bookings"] == 40060

def test_room_reassignment_metrics():
    """Verify room reassignment metrics and operational upgrades."""
    room_sum = get_room_reassignment_summary()
    assert room_sum["total_bookings"] == 119390
    assert room_sum["reassigned_bookings"] == 14917
    assert float(room_sum["reassignment_rate_pct"]) == 12.49
    assert room_sum["operational_reassignments"] == 11028
