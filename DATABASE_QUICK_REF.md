# Database Quick Reference

## 🚀 Common Commands

### Initialize Database
```bash
cd backend
python scripts/init_db.py
```

### Create Migration
```bash
cd backend
alembic revision --autogenerate -m "Description"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1        # One step back
alembic downgrade base      # All the way back
```

### Check Migration Status
```bash
alembic current            # Current version
alembic history            # All migrations
```

### View Database (SQLite)
```bash
sqlite3 backend/flight_delays.db
.tables                    # List tables
.schema airports           # View table structure
SELECT * FROM airports LIMIT 5;
```

## 📊 Key Tables

| Table | Purpose |
|-------|---------|
| `airports` | Airport information |
| `airlines` | Airline details |
| `aircraft_types` | Aircraft specifications |
| `aircraft` | Individual aircraft |
| `flights` | Flight data with delays |
| `weather_data` | Weather conditions |
| `airport_traffic` | Traffic patterns |
| `flight_delay_predictions` | ML delay predictions |
| `cargo_predictions` | ML cargo forecasts |
| `passenger_traffic_predictions` | ML passenger forecasts |
| `ml_models` | Model metadata |

## 🔗 Key Relationships

```
Airport (1) ←→ (many) Flight
Airline (1) ←→ (many) Aircraft ←→ (many) Flight
Flight (1) ←→ (many) FlightDelayPrediction
Airport (1) ←→ (many) WeatherData
Airport (1) ←→ (many) AirportTraffic
```

## 🔧 Environment Variables

```env
# SQLite (Development)
DATABASE_URL=sqlite:///./flight_delays.db

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/flight_delays
```

## 📝 Common Queries (SQLAlchemy)

### Get all airports
```python
from app.models import Airport
from app.core.database import get_db

db = next(get_db())
airports = db.query(Airport).all()
```

### Get flights with delays
```python
from app.models import Flight
flights_with_delays = db.query(Flight).filter(
    Flight.departure_delay_minutes > 0
).all()
```

### Get predictions for a flight
```python
from app.models import FlightDelayPrediction
predictions = db.query(FlightDelayPrediction).filter(
    FlightDelayPrediction.flight_id == flight_id
).order_by(FlightDelayPrediction.prediction_timestamp.desc()).all()
```

## 📚 Documentation

- **Full Design**: `DATABASE_DESIGN.md`
- **Setup Guide**: `backend/DATABASE_SETUP.md`
- **Summary**: `DATABASE_SUMMARY.md`
