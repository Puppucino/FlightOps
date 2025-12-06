# Database Design Document
## Flight Delay Prediction & Cargo Forecasting System

## Database Stack Recommendation

### Production Recommendation: **PostgreSQL**
- **Why PostgreSQL?**
  - Excellent support for complex queries and analytics
  - Strong JSON support for flexible data structures
  - Time-series extensions (TimescaleDB) available if needed
  - Mature, reliable, and performant
  - Good integration with SQLAlchemy
  - Full-text search capabilities
  - Excellent for ML data pipelines

### Development/Testing: **SQLite** (Current)
- Lightweight, easy setup
- Perfect for development and testing
- Easy migration to PostgreSQL when needed

### Alternative Consideration: **PostgreSQL with TimescaleDB**
- If you plan to store massive amounts of time-series data (weather, traffic)
- Optimized for time-series queries
- Can handle billions of data points efficiently

---

## Database Schema Design

### Core Entities

#### 1. **Airports** (`airports`)
Primary entity for airport information.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | UUID (PK) | Unique airport identifier | PRIMARY KEY |
| icao_code | VARCHAR(4) | ICAO airport code | UNIQUE, NOT NULL |
| iata_code | VARCHAR(3) | IATA airport code | UNIQUE, NOT NULL |
| name | VARCHAR(255) | Airport name | NOT NULL |
| city | VARCHAR(100) | City name | |
| country | VARCHAR(100) | Country name | |
| latitude | DECIMAL(10,8) | Airport latitude | |
| longitude | DECIMAL(11,8) | Airport longitude | |
| elevation_ft | INTEGER | Elevation in feet | |
| timezone | VARCHAR(50) | Timezone identifier | |
| passenger_capacity | INTEGER | Max passenger capacity | |
| cargo_capacity_tonnes | DECIMAL(10,2) | Max cargo capacity | |
| runways | INTEGER | Number of runways | |
| is_active | BOOLEAN | Active status | DEFAULT true |
| created_at | TIMESTAMP | Record creation time | DEFAULT NOW() |
| updated_at | TIMESTAMP | Last update time | DEFAULT NOW() |

**Indexes:**
- `idx_airports_icao` on `icao_code`
- `idx_airports_iata` on `iata_code`
- `idx_airports_location` on `(latitude, longitude)` (for geographic queries)

---

#### 2. **Airlines** (`airlines`)
Airline information.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | UUID (PK) | Unique airline identifier | PRIMARY KEY |
| icao_code | VARCHAR(3) | ICAO airline code | UNIQUE |
| iata_code | VARCHAR(2) | IATA airline code | UNIQUE |
| name | VARCHAR(255) | Airline name | NOT NULL |
| country | VARCHAR(100) | Country of origin | |
| is_active | BOOLEAN | Active status | DEFAULT true |
| created_at | TIMESTAMP | Record creation time | DEFAULT NOW() |
| updated_at | TIMESTAMP | Last update time | DEFAULT NOW() |

**Indexes:**
- `idx_airlines_icao` on `icao_code`
- `idx_airlines_iata` on `iata_code`

---

#### 3. **Aircraft Types** (`aircraft_types`)
Aircraft type specifications.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | UUID (PK) | Unique aircraft type identifier | PRIMARY KEY |
| icao_code | VARCHAR(4) | ICAO aircraft type code | UNIQUE, NOT NULL |
| manufacturer | VARCHAR(100) | Aircraft manufacturer | |
| model | VARCHAR(100) | Aircraft model | NOT NULL |
| passenger_capacity | INTEGER | Max passenger capacity | |
| cargo_capacity_tonnes | DECIMAL(10,2) | Max cargo capacity | |
| max_range_km | INTEGER | Maximum range | |
| cruising_speed_kmh | INTEGER | Cruising speed | |
| fuel_capacity_liters | DECIMAL(10,2) | Fuel capacity | |
| is_active | BOOLEAN | Active status | DEFAULT true |
| created_at | TIMESTAMP | Record creation time | DEFAULT NOW() |
| updated_at | TIMESTAMP | Last update time | DEFAULT NOW() |

**Indexes:**
- `idx_aircraft_types_icao` on `icao_code`

---

#### 4. **Aircraft** (`aircraft`)
Individual aircraft records.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | UUID (PK) | Unique aircraft identifier | PRIMARY KEY |
| registration | VARCHAR(20) | Aircraft registration | UNIQUE, NOT NULL |
| aircraft_type_id | UUID (FK) | Reference to aircraft_types | FOREIGN KEY |
| airline_id | UUID (FK) | Reference to airlines | FOREIGN KEY |
| year_manufactured | INTEGER | Year of manufacture | |
| maintenance_status | VARCHAR(50) | Maintenance status | |
| is_active | BOOLEAN | Active status | DEFAULT true |
| created_at | TIMESTAMP | Record creation time | DEFAULT NOW() |
| updated_at | TIMESTAMP | Last update time | DEFAULT NOW() |

**Indexes:**
- `idx_aircraft_registration` on `registration`
- `idx_aircraft_type` on `aircraft_type_id`
- `idx_aircraft_airline` on `airline_id`

---

#### 5. **Flights** (`flights`)
Scheduled and actual flight information.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | UUID (PK) | Unique flight identifier | PRIMARY KEY |
| flight_number | VARCHAR(10) | Flight number | NOT NULL |
| airline_id | UUID (FK) | Reference to airlines | FOREIGN KEY |
| aircraft_id | UUID (FK) | Reference to aircraft | FOREIGN KEY |
| origin_airport_id | UUID (FK) | Origin airport | FOREIGN KEY |
| destination_airport_id | UUID (FK) | Destination airport | FOREIGN KEY |
| scheduled_departure | TIMESTAMP | Scheduled departure time | NOT NULL |
| scheduled_arrival | TIMESTAMP | Scheduled arrival time | NOT NULL |
| actual_departure | TIMESTAMP | Actual departure time | |
| actual_arrival | TIMESTAMP | Actual arrival time | |
| departure_delay_minutes | INTEGER | Departure delay in minutes | |
| arrival_delay_minutes | INTEGER | Arrival delay in minutes | |
| cancellation_status | VARCHAR(20) | Cancellation status | |
| flight_type | VARCHAR(20) | 'passenger' or 'cargo' | NOT NULL |
| passenger_count | INTEGER | Number of passengers | |
| cargo_weight_tonnes | DECIMAL(10,2) | Cargo weight | |
| flight_status | VARCHAR(20) | Current status | |
| distance_km | DECIMAL(10,2) | Flight distance | |
| created_at | TIMESTAMP | Record creation time | DEFAULT NOW() |
| updated_at | TIMESTAMP | Last update time | DEFAULT NOW() |

**Indexes:**
- `idx_flights_number_date` on `(flight_number, scheduled_departure)`
- `idx_flights_origin` on `(origin_airport_id, scheduled_departure)`
- `idx_flights_destination` on `(destination_airport_id, scheduled_arrival)`
- `idx_flights_departure` on `scheduled_departure`
- `idx_flights_status` on `flight_status`

---

#### 6. **Weather Data** (`weather_data`)
Historical and current weather conditions.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | UUID (PK) | Unique weather record identifier | PRIMARY KEY |
| airport_id | UUID (FK) | Reference to airports | FOREIGN KEY |
| recorded_at | TIMESTAMP | Weather recording timestamp | NOT NULL |
| temperature_celsius | DECIMAL(5,2) | Temperature in Celsius | |
| humidity_percent | DECIMAL(5,2) | Humidity percentage | |
| wind_speed_kmh | DECIMAL(6,2) | Wind speed | |
| wind_direction_degrees | INTEGER | Wind direction | |
| visibility_km | DECIMAL(6,2) | Visibility | |
| pressure_hpa | DECIMAL(7,2) | Atmospheric pressure | |
| conditions | VARCHAR(100) | Weather conditions (e.g., "clear", "rain", "snow") | |
| precipitation_mm | DECIMAL(6,2) | Precipitation amount | |
| cloud_cover_percent | DECIMAL(5,2) | Cloud cover percentage | |
| created_at | TIMESTAMP | Record creation time | DEFAULT NOW() |

**Indexes:**
- `idx_weather_airport_time` on `(airport_id, recorded_at)`
- `idx_weather_recorded_at` on `recorded_at` (for time-series queries)

---

#### 7. **Airport Traffic** (`airport_traffic`)
Historical airport traffic data (passengers and aircraft movements).

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | UUID (PK) | Unique traffic record identifier | PRIMARY KEY |
| airport_id | UUID (FK) | Reference to airports | FOREIGN KEY |
| recorded_at | TIMESTAMP | Traffic recording timestamp | NOT NULL |
| hour_of_day | INTEGER | Hour of day (0-23) | |
| day_of_week | INTEGER | Day of week (0-6) | |
| passenger_count | INTEGER | Passenger count for the period | |
| aircraft_movements | INTEGER | Number of aircraft movements | |
| cargo_tonnes | DECIMAL(10,2) | Cargo volume | |
| arrival_count | INTEGER | Number of arrivals | |
| departure_count | INTEGER | Number of departures | |
| runway_utilization_percent | DECIMAL(5,2) | Runway utilization | |
| created_at | TIMESTAMP | Record creation time | DEFAULT NOW() |

**Indexes:**
- `idx_traffic_airport_time` on `(airport_id, recorded_at)`
- `idx_traffic_hour` on `hour_of_day`
- `idx_traffic_day` on `day_of_week`

---

#### 8. **Flight Delay Predictions** (`flight_delay_predictions`)
ML model predictions for flight delays.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | UUID (PK) | Unique prediction identifier | PRIMARY KEY |
| flight_id | UUID (FK) | Reference to flights | FOREIGN KEY |
| prediction_timestamp | TIMESTAMP | When prediction was made | NOT NULL |
| delay_probability | DECIMAL(5,4) | Probability of delay (0-1) | NOT NULL |
| predicted_delay_minutes | INTEGER | Predicted delay duration | |
| confidence_score | DECIMAL(5,4) | Model confidence (0-1) | |
| model_version | VARCHAR(50) | ML model version used | |
| predicted_by | VARCHAR(50) | Model identifier | |
| actual_delay_minutes | INTEGER | Actual delay (for validation) | |
| prediction_accuracy | DECIMAL(5,4) | Accuracy after actual data | |
| created_at | TIMESTAMP | Record creation time | DEFAULT NOW() |

**Indexes:**
- `idx_predictions_flight` on `flight_id`
- `idx_predictions_timestamp` on `prediction_timestamp`
- `idx_predictions_model` on `model_version`

---

#### 9. **Cargo Predictions** (`cargo_predictions`)
ML model predictions for cargo demand.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | UUID (PK) | Unique prediction identifier | PRIMARY KEY |
| airport_id | UUID (FK) | Reference to airports | FOREIGN KEY |
| aircraft_id | UUID (FK) | Reference to aircraft | FOREIGN KEY |
| prediction_timestamp | TIMESTAMP | When prediction was made | NOT NULL |
| predicted_cargo_tonnes | DECIMAL(10,2) | Predicted cargo volume | NOT NULL |
| predicted_period_start | TIMESTAMP | Start of prediction period | |
| predicted_period_end | TIMESTAMP | End of prediction period | |
| confidence_score | DECIMAL(5,4) | Model confidence (0-1) | |
| model_version | VARCHAR(50) | ML model version used | |
| actual_cargo_tonnes | DECIMAL(10,2) | Actual cargo (for validation) | |
| prediction_accuracy | DECIMAL(5,4) | Accuracy after actual data | |
| created_at | TIMESTAMP | Record creation time | DEFAULT NOW() |

**Indexes:**
- `idx_cargo_predictions_airport` on `airport_id`
- `idx_cargo_predictions_timestamp` on `prediction_timestamp`
- `idx_cargo_predictions_period` on `(predicted_period_start, predicted_period_end)`

---

#### 10. **Passenger Traffic Predictions** (`passenger_traffic_predictions`)
ML model predictions for passenger traffic.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | UUID (PK) | Unique prediction identifier | PRIMARY KEY |
| airport_id | UUID (FK) | Reference to airports | FOREIGN KEY |
| prediction_timestamp | TIMESTAMP | When prediction was made | NOT NULL |
| predicted_passengers | INTEGER | Predicted passenger count | NOT NULL |
| predicted_period_start | TIMESTAMP | Start of prediction period | |
| predicted_period_end | TIMESTAMP | End of prediction period | |
| confidence_score | DECIMAL(5,4) | Model confidence (0-1) | |
| model_version | VARCHAR(50) | ML model version used | |
| actual_passengers | INTEGER | Actual passengers (for validation) | |
| prediction_accuracy | DECIMAL(5,4) | Accuracy after actual data | |
| created_at | TIMESTAMP | Record creation time | DEFAULT NOW() |

**Indexes:**
- `idx_passenger_predictions_airport` on `airport_id`
- `idx_passenger_predictions_timestamp` on `prediction_timestamp`
- `idx_passenger_predictions_period` on `(predicted_period_start, predicted_period_end)`

---

#### 11. **ML Models** (`ml_models`)
Metadata about trained ML models.

| Column | Type | Description | Constraints |
|--------|------|-------------|-------------|
| id | UUID (PK) | Unique model identifier | PRIMARY KEY |
| model_name | VARCHAR(100) | Model name/identifier | UNIQUE, NOT NULL |
| model_type | VARCHAR(50) | 'delay', 'cargo', 'passenger_traffic' | NOT NULL |
| version | VARCHAR(50) | Model version | NOT NULL |
| file_path | VARCHAR(500) | Path to model file | |
| training_accuracy | DECIMAL(5,4) | Training accuracy | |
| validation_accuracy | DECIMAL(5,4) | Validation accuracy | |
| test_accuracy | DECIMAL(5,4) | Test accuracy | |
| training_data_range_start | TIMESTAMP | Training data start | |
| training_data_range_end | TIMESTAMP | Training data end | |
| feature_list | JSON | List of features used | |
| hyperparameters | JSON | Model hyperparameters | |
| is_active | BOOLEAN | Active model flag | DEFAULT false |
| created_at | TIMESTAMP | Model creation time | DEFAULT NOW() |
| updated_at | TIMESTAMP | Last update time | DEFAULT NOW() |

**Indexes:**
- `idx_models_name_version` on `(model_name, version)`
- `idx_models_type_active` on `(model_type, is_active)`

---

## Entity Relationships

```
Airports (1) ──< (many) Flights [origin_airport_id]
Airports (1) ──< (many) Flights [destination_airport_id]
Airports (1) ──< (many) Weather Data
Airports (1) ──< (many) Airport Traffic
Airports (1) ──< (many) Cargo Predictions
Airports (1) ──< (many) Passenger Traffic Predictions

Airlines (1) ──< (many) Aircraft
Airlines (1) ──< (many) Flights

Aircraft Types (1) ──< (many) Aircraft

Aircraft (1) ──< (many) Flights
Aircraft (1) ──< (many) Cargo Predictions

Flights (1) ──< (many) Flight Delay Predictions
```

---

## Data Flow for ML Predictions

1. **Training Data Collection:**
   - `flights` → Historical flight data with delays
   - `weather_data` → Historical weather at airports
   - `airport_traffic` → Historical traffic patterns
   - `aircraft` + `aircraft_types` → Aircraft characteristics

2. **Prediction Input:**
   - Current/forecasted weather from `weather_data`
   - Current flight info from `flights`
   - Current traffic from `airport_traffic`
   - Aircraft data from `aircraft` and `aircraft_types`

3. **Prediction Output:**
   - `flight_delay_predictions` → Delay predictions
   - `cargo_predictions` → Cargo demand forecasts
   - `passenger_traffic_predictions` → Passenger traffic forecasts

4. **Model Management:**
   - `ml_models` → Tracks model versions and performance

---

## Database Optimization Considerations

### 1. **Partitioning** (PostgreSQL/TimescaleDB)
- Consider partitioning `weather_data` and `airport_traffic` by time (monthly/quarterly)
- Partition `flights` by scheduled_departure date

### 2. **Archival Strategy**
- Move old predictions (>6 months) to archive tables
- Keep recent data hot for fast queries

### 3. **Materialized Views**
- Create materialized views for dashboard aggregations
- Refresh periodically (hourly/daily)

### 4. **Connection Pooling**
- Use SQLAlchemy connection pooling
- Configure pool size based on expected load

---

## Migration Strategy

1. **Phase 1: Core Entities**
   - Airports, Airlines, Aircraft Types, Aircraft

2. **Phase 2: Flight Data**
   - Flights table with relationships

3. **Phase 3: Historical Data**
   - Weather Data, Airport Traffic

4. **Phase 4: ML Integration**
   - Prediction tables, ML Models table

---

## Security Considerations

1. **Row-Level Security (PostgreSQL)**
   - If multi-tenant: implement RLS policies

2. **Sensitive Data**
   - Consider encryption for API keys in `ml_models`

3. **Backup Strategy**
   - Regular backups of production data
   - Point-in-time recovery capability

---

## Next Steps

1. ✅ Review and approve database design
2. ✅ Set up Alembic migrations
3. ✅ Create SQLAlchemy models
4. ✅ Initialize database
5. ✅ Create seed data scripts
6. ✅ Set up database connection pooling
7. ✅ Create database utility functions
