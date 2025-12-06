"""Compare what list and calendar endpoints return"""
import sys
from pathlib import Path
from datetime import datetime, date

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import get_db_context
from app.models.flight import Flight

today = date.today()
current_year = today.year
current_month = today.month

print(f"Current date: {today}")
print(f"Checking month: {current_month}/{current_year}")
print("=" * 80)

with get_db_context() as db:
    # Check what list endpoint would return
    now = datetime.now()
    list_flights = db.query(Flight).filter(
        Flight.flight_type.in_(['passenger', 'mixed', 'cargo']),
        Flight.passenger_count.isnot(None),
        Flight.scheduled_departure >= now
    ).order_by(Flight.scheduled_departure.asc()).limit(10).all()
    
    print(f"\nList endpoint (first 10 future flights):")
    for f in list_flights:
        print(f"  {f.flight_number}: {f.scheduled_departure} ({f.scheduled_departure.date()})")
    
    # Check what calendar endpoint would return for current month
    start_date = date(current_year, current_month, 1)
    if current_month == 12:
        end_date = date(current_year + 1, 1, 1)
    else:
        end_date = date(current_year, current_month + 1, 1)
    
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.min.time())
    
    calendar_flights = db.query(Flight).filter(
        Flight.scheduled_departure >= start_datetime,
        Flight.scheduled_departure < end_datetime,
        Flight.flight_type.in_(['passenger', 'mixed', 'cargo']),
        Flight.passenger_count.isnot(None)
    ).order_by(Flight.scheduled_departure.asc()).all()
    
    print(f"\nCalendar endpoint (current month {current_month}/{current_year}):")
    print(f"  Found {len(calendar_flights)} flights")
    for f in calendar_flights[:10]:
        print(f"  {f.flight_number}: {f.scheduled_departure} ({f.scheduled_departure.date()})")
    
    # Check overlap
    list_ids = {str(f.id) for f in list_flights}
    calendar_ids = {str(f.id) for f in calendar_flights}
    overlap = list_ids & calendar_ids
    
    print(f"\nOverlap:")
    print(f"  List flights in current month: {len(overlap)}/{len(list_flights)}")
    print(f"  Calendar flights: {len(calendar_flights)}")
    
    if len(overlap) > 0:
        print(f"  ✅ Some flights match!")
    else:
        print(f"  ⚠️ No overlap - flights are in different months")
