# How Current Services Solve the Problem Statement

## Problem Statement Overview

Based on the images provided, the core problems are:

1. **"how much cargo space will I have to sell?"**
   - Passenger baggage isn't confirmed until day of flight
   - Airlines predict using historical trends (Christmas busier, routes out of Africa more bag-dense)

2. **"help me figure out how much capacity I have x days before the flight"**
   - Current software sucks
   - Airlines default to spreadsheets
   - Must optimize for both volume & weight

---

## How Current Services Address These Problems

### ✅ Problem 1: Predicting Available Cargo Space After Ticket Sales

**Current Solution:**

1. **Baggage Prediction (ML-based)**
   - Your `BaggagePredictor` uses RandomForest models trained on historical data
   - Takes `passenger_count` (from ticket sales) as input
   - Predicts baggage weight/volume BEFORE the flight
   - Addresses the "baggage isn't confirmed until day of flight" problem

2. **Available Capacity Calculation**
   - `CargoCapacityPredictor` calculates: `available = max_capacity - predicted_baggage`
   - Provides both weight (kg) and volume (m³) predictions
   - Shows which is the constraining factor (weight vs volume)
   - **This directly answers "how much cargo space will I have to sell?"**

3. **Historical Route Trends**
   - Route-specific statistics (avg/std baggage per passenger)
   - Captures route patterns (e.g., "routes out of Africa are more bag-dense")
   - Computed from historical flight data in database

### ✅ Problem 2: Capacity Prediction X Days Before Flight

**Current Solution:**

1. **Time Horizon Selection**
   - Frontend allows selecting: 0, 1, 3, 7, 14, 30 days before flight
   - Backend adjusts prediction uncertainty based on days
   - More days = wider confidence intervals (accounts for uncertainty)

2. **Confidence Intervals**
   - Provides upper/lower bounds for predictions
   - Helps airlines make decisions with appropriate risk levels
   - Formula: `uncertainty_factor = 1.0 + (days_before_flight / 30.0) * 0.3`

3. **Interactive Dashboard (Replaces Spreadsheets)**
   - Visual charts instead of complex spreadsheets
   - Real-time predictions vs manual calculations
   - Clear indicators for constraining factor and overbooking risk

### ✅ Problem 3: Optimize for Both Weight & Volume

**Current Solution:**

1. **Dual Predictions**
   - Predicts both available weight (kg) and volume (m³)
   - Shows which is the limiting factor (`constraining_factor`)
   - Helps prioritize which cargo to accept

2. **Utilization Tracking**
   - Weight utilization percentage
   - Volume utilization percentage
   - Visual indicators for capacity limits

---

## What's Working Well

✅ **ML-based baggage prediction** - Uses historical data to predict baggage  
✅ **Route-specific patterns** - Captures route differences (Africa routes, etc.)  
✅ **Temporal features** - Month, day of week, holiday seasons (December, January, July)  
✅ **Time horizon flexibility** - Predictions for different days before flight  
✅ **Confidence intervals** - Provides uncertainty bounds  
✅ **Interactive UI** - Replaces spreadsheet-based workflows  

---

## What Needs Enhancement (Based on Your Dataset)

Your dataset contains **crucial columns** that aren't fully utilized:

### Current Gap: Cargo Demand Prediction

**Current Implementation (Placeholder):**
```python
# Line 143 in cargo_capacity_predictor.py
predicted_cargo_demand_kg = max(0, available_weight_kg * 0.8)  # Assume 80% utilization
```

**Problem:** This is a simple heuristic, not a real prediction based on:
- Historical cargo demand (`gross_weight_cargo_kg`, `gross_volume_cargo_m3`)
- Peak seasons (your data spans 2023-2024, enough to detect patterns)
- Route-specific cargo trends
- Aircraft type preferences

---

## Recommended Enhancements

### 1. Create Cargo Demand Predictor Model

**New Service:** `CargoDemandPredictor`

**Purpose:** Predict actual cargo demand (not just available capacity)

**Features to Train On:**
```python
# From your dataset:
- flight_date → Extract: month, day_of_week, is_holiday_season
- origin, destination → Route patterns
- aircraft_type → Aircraft-specific cargo demand
- passenger_count → Passenger load correlation
- days_before_flight → Temporal uncertainty

# Target variables:
- gross_weight_cargo_kg (historical actual cargo weight)
- gross_volume_cargo_m3 (historical actual cargo volume)
```

**Benefits:**
- More accurate overbooking risk assessment
- Better pricing decisions (high demand = higher prices)
- Identifies peak seasons automatically
- Route-specific cargo demand patterns

### 2. Enhance Peak Season Detection

**Current:** Simple month-based holidays (Dec, Jan, Jul)

**Enhancement:** Use your historical data to detect:
- Actual peak periods (analyze cargo utilization spikes)
- Route-specific peaks (e.g., KUL→SIN vs KUL→PVG)
- Multi-month patterns (not just single months)
- Year-over-year trends

**Implementation:**
```python
# Analyze historical data for patterns
monthly_cargo_stats = df.groupby(['origin', 'destination', 'month']).agg({
    'gross_weight_cargo_kg': ['mean', 'std', 'max'],
    'gross_volume_cargo_m3': ['mean', 'std', 'max'],
    'passenger_count': 'mean'
})
```

### 3. Trend Analysis Service

**New Service:** `CargoTrendAnalyzer`

**Purpose:** Identify cargo utilization trends over time

**Features:**
- Weekly/monthly trends per route
- Seasonal patterns
- Growth/decline indicators
- Comparative analysis (this month vs same month last year)

**Use Cases:**
- "Is cargo demand increasing on KUL→SIN route?"
- "What's the trend for December cargo utilization?"
- "Compare Q1 2023 vs Q1 2024"

### 4. Load Optimization Engine

**Enhancement:** Use `gross_weight_cargo_kg` and `gross_volume_cargo_m3` to:

1. **Optimal Cargo Mix Calculator**
   - Given available weight and volume
   - Recommend cargo mix (heavy dense items vs light bulky items)
   - Maximize revenue per unit capacity

2. **Overbooking Optimization**
   - Based on historical no-show rates
   - Calculate optimal overbooking percentage per route
   - Account for cargo vs passenger baggage competition

3. **Route Profitability Analysis**
   - Combine `cargo_price_per_kg` with predicted demand
   - Identify high-value routes
   - Recommend cargo pricing strategies

---

## Implementation Plan

### Phase 1: Cargo Demand Prediction Model

1. **Create training script:**
   ```bash
   backend/scripts/train_cargo_demand_model.py
   ```

2. **Features to engineer:**
   - Temporal: month, day_of_week, quarter, is_holiday_season
   - Route: origin, destination, route_encoded
   - Aircraft: aircraft_type_encoded
   - Passenger: passenger_count, passenger_load_factor
   - Historical: route_avg_cargo_weight, route_std_cargo_weight
   - Seasonal: month_cargo_avg (route-specific)

3. **Target variables:**
   - `gross_weight_cargo_kg`
   - `gross_volume_cargo_m3`

4. **Model type:**
   - RandomForestRegressor (similar to baggage predictor)
   - Or XGBoost for better performance

### Phase 2: Peak Season Detection

1. **Create analysis service:**
   ```python
   backend/app/services/peak_season_analyzer.py
   ```

2. **Analysis methods:**
   - Statistical: Identify months with cargo > 1.5x average
   - Route-specific: Different peaks for different routes
   - Time-series: Detect patterns across years

3. **Output:**
   - Peak season calendar per route
   - Multiplier factors (peak = 1.3x normal demand)

### Phase 3: Trend Analysis Dashboard

1. **New API endpoint:**
   ```
   GET /api/v1/cargo/trends?route=KUL-SIN&period=monthly
   ```

2. **Frontend enhancement:**
   - Add "Trends" section to CargoAnalytics page
   - Show historical utilization charts
   - Compare periods

### Phase 4: Enhanced Overbooking Risk

**Current (simplified):**
```python
if available_weight < predicted_demand * 0.9:
    risk = "high"
```

**Enhanced:**
```python
# Use actual cargo demand model prediction
predicted_demand = cargo_demand_predictor.predict(...)

# Account for historical overbooking patterns
overbooking_factor = route_stats.get('avg_overbooking_rate', 1.0)

# Calculate risk with confidence intervals
if predicted_demand_upper_ci * overbooking_factor > available_weight * 0.95:
    risk = "high"
```

---

## Data Flow with Enhancements

```
User selects flight + days before flight
    ↓
Backend fetches:
  1. Flight data (passenger_count from ticket sales)
  2. Historical route data (cargo trends, peak seasons)
    ↓
ML Models Run:
  1. BaggagePredictor → Predicts passenger baggage
  2. CargoDemandPredictor → Predicts cargo demand (NEW)
  3. PeakSeasonAnalyzer → Adjusts for seasonality (NEW)
    ↓
Calculate:
  - Available capacity = Max - Predicted baggage
  - Predicted demand = Cargo demand + seasonal adjustment
  - Overbooking risk = Compare demand vs available
  - Load optimization = Recommend cargo mix
    ↓
Frontend displays:
  - Available weight & volume
  - Predicted cargo demand
  - Peak season indicators
  - Trend charts
  - Optimization recommendations
```

---

## How This Solves Your Problem Statement

### ✅ "how much cargo space will I have to sell?"

**Answer:** 
- Available Weight: X.XX tonnes (with confidence range)
- Available Volume: Y.YY m³ (with confidence range)
- Updated as passenger bookings change
- Adjusted for prediction horizon (X days before flight)

### ✅ "help me figure out how much capacity I have x days before the flight"

**Answer:**
- Interactive dashboard (not spreadsheets!)
- Select any number of days (0-30)
- Real-time ML predictions
- Confidence intervals show uncertainty
- Historical trends show patterns

### ✅ "optimize for both volume & weight"

**Answer:**
- Shows both weight and volume predictions
- Identifies constraining factor (weight vs volume)
- Provides optimal cargo mix recommendations
- Helps prioritize high-value cargo

### ✅ Load Optimization & Trend Prediction

**Answer (with enhancements):**
- Peak season detection from historical data
- Route-specific cargo trends
- Utilization trend charts
- Demand forecasting
- Revenue optimization suggestions

---

## Next Steps to Implement

1. **Immediate (Use existing data):**
   - Create `CargoDemandPredictor` service
   - Train model on `gross_weight_cargo_kg` and `gross_volume_cargo_m3`
   - Replace placeholder cargo demand prediction

2. **Short-term (1-2 weeks):**
   - Implement peak season detection
   - Add trend analysis endpoints
   - Enhance overbooking risk calculation

3. **Medium-term (1 month):**
   - Load optimization engine
   - Route profitability analysis
   - Pricing recommendations

4. **Long-term (Ongoing):**
   - Continuous model retraining
   - A/B testing of predictions
   - Integration with pricing systems

---

## Summary

**Current services already solve the core problem:**
- ✅ Predict available cargo space after ticket sales
- ✅ Provide predictions X days before flight
- ✅ Optimize for both weight and volume
- ✅ Replace spreadsheet workflows

**Enhancements needed for full optimization:**
- 🔄 Cargo demand prediction (currently placeholder)
- 🔄 Peak season detection from historical data
- 🔄 Trend analysis and forecasting
- 🔄 Load optimization recommendations

The foundation is solid - the enhancements will make it production-ready for real-world cargo optimization!
