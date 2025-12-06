# Cargo Analytics Page - Complete Function & Logic Explanation

## Overview
The Cargo Analytics page is a React component that displays comprehensive cargo capacity information, predictions, and analytics for flights. It integrates with ML models to predict available cargo space days before a flight.

---

## 1. State Management

### State Variables (Lines 15-20)
```typescript
const [analyticsData, setAnalyticsData] = useState<CargoAnalyticsData | null>(null)
const [availableFlights, setAvailableFlights] = useState<FlightDetails[]>([])
const [loading, setLoading] = useState(true)
const [error, setError] = useState<string | null>(null)
const [daysBeforeFlight, setDaysBeforeFlight] = useState<number>(0)
const [predictionData, setPredictionData] = useState<any>(null)
```

**Purpose:**
- `analyticsData`: Stores the complete analytics data for the selected flight
- `availableFlights`: List of all flights available for selection
- `loading`: Controls loading spinner display
- `error`: Stores error messages
- `daysBeforeFlight`: User-selected prediction horizon (0, 1, 3, 7, 14, 30 days)
- `predictionData`: Extracted ML prediction data for display

---

## 2. Data Fetching Logic (useEffect Hook - Lines 22-68)

### Main Fetch Function (`fetchData`)
This function runs when:
- Component mounts
- `flightId` changes (URL parameter)
- `flightNumber` changes (URL parameter)
- `daysBeforeFlight` changes (user selects different prediction horizon)

### Fetch Logic Flow:

```typescript
1. Set loading state to true
2. Clear any previous errors
3. Fetch available flights list (for dropdown)
4. Determine which flight to fetch analytics for:
   a. If flightId in URL → Use that
   b. Else if flightNumber in URL → Use that
   c. Else use first available flight as default
5. Fetch analytics with prediction (includes ML predictions)
6. Extract prediction data from response
7. Handle errors (show error message, fallback to mock data)
8. Set loading to false
```

### Key Function Call:
```typescript
getCargoAnalyticsWithPrediction(flightId, daysBeforeFlight)
```
- **Backend API**: `GET /api/v1/cargo/analytics/{flightId}?days_before_flight={days}`
- **Returns**: Complete analytics including ML predictions
- **Days Before Flight**: Adjusts prediction uncertainty (more days = less accurate)

---

## 3. Helper Functions

### `getStatusColor(status: string)` (Lines 127-142)
**Purpose**: Maps flight/loading status to color classes

**Logic:**
- `completed` / `arrived` → `success` (green)
- `in_progress` / `departed` → `primary` (blue)
- `delayed` → `warning` (yellow)
- `cancelled` → `danger` (red)
- Default → `primary` (blue)

### `formatDate(dateString: string)` (Lines 144-150)
**Purpose**: Formats ISO date strings for display

**Logic:**
- Parses ISO date string using `date-fns`
- Formats as: "MMM dd, yyyy HH:mm" (e.g., "Dec 06, 2024 10:30")
- Fallback: Returns original string if parsing fails

---

## 4. Safe Data Fallbacks (Lines 96-110)

### `safeLoadingProgress`
**Purpose**: Prevents undefined errors if `loading_progress` is missing

**Default values if missing:**
- `flight_id`: From flight data
- `flight_number`: From flight data
- `total_cargo_tonnes`: From storage_availability
- `loaded_cargo_tonnes`: From storage_availability.current_cargo_tonnes
- `loading_percentage`: From storage_availability.utilization_percentage
- `status`: `'not_started'`

### `safePrediction`
**Purpose**: Fallback for legacy prediction data

**Default values:**
- `predicted_cargo_volume`: 0
- `confidence`: 0

---

## 5. Chart Data Preparation (Lines 112-125)

### `storageData` - Pie Chart Data
```typescript
[
  { name: 'Used', value: current_cargo_tonnes, color: '#3b82f6' },
  { name: 'Available', value: available_capacity_tonnes, color: '#10b981' }
]
```
**Purpose**: Shows used vs available cargo capacity visually

### `utilizationData` - Trend Chart Data
```typescript
[
  { time: '00:00', utilization: 45 },
  { time: '04:00', utilization: 52 },
  { time: '08:00', utilization: 68 },
  { time: '12:00', utilization: current_utilization },
  { time: '16:00', utilization: current_utilization + 5 },
  { time: '20:00', utilization: current_utilization + 10 }
]
```
**Purpose**: Shows storage utilization trend over time (simulated hourly data)
**Note**: First 3 points are hardcoded, last 3 use actual data + progression

---

## 6. UI Sections Breakdown

### A. Header Section (Lines 154-189)
**Components:**
1. **Back Button**: Navigates to cargo analytics list
2. **Flight Selector Dropdown**: 
   - Shows all available flights
   - Format: "FLIGHT_NUMBER - ORIGIN → DESTINATION"
   - Changes flight when selected
3. **Days Before Flight Selector**:
   - Options: 0, 1, 3, 7, 14, 30 days
   - Triggers re-fetch with new prediction horizon
   - Updates `daysBeforeFlight` state → triggers useEffect

### B. Flight Details Card (Lines 192-233)
**Displays:**
- Flight number, airline, aircraft registration & type
- Route (origin → destination)
- Distance in km
- Flight status (with color coding)
- Scheduled departure/arrival times (formatted)

**Logic**: Directly reads from `flight` object in `analyticsData`

### C. Statistics Cards (Lines 236-267)
**Four Key Metrics:**

1. **Storage Utilization** (%)
   - Source: `storage_availability.utilization_percentage`
   - Shows how full the cargo hold is

2. **Available Capacity** (tonnes)
   - Source: `storage_availability.available_capacity_tonnes`
   - Shows remaining space

3. **Loading Progress** (%)
   - Source: `safeLoadingProgress.loading_percentage`
   - Shows how much cargo has been loaded

4. **Predicted Demand** (tonnes)
   - Source: `safePrediction.predicted_cargo_volume`
   - ML prediction of expected cargo demand
   - Shows confidence percentage as trend value

### D. Storage Availability Card (Lines 271-328)
**Components:**

1. **Metrics Display:**
   - Total Capacity (tonnes)
   - Current Cargo (tonnes)
   - Available (tonnes)

2. **Progress Bar:**
   - Shows utilization percentage
   - Color: `warning` if >80%, else `primary`

3. **Pie Chart:**
   - Visual representation of used vs available
   - Uses Recharts library
   - Interactive tooltip showing tonnes

### E. Cargo Loading Progress Card (Lines 331-365)
**Components:**

1. **Status Badge:**
   - Shows loading status (not_started, in_progress, completed)
   - Color-coded via `getStatusColor()`

2. **Progress Bar:**
   - Shows `loading_percentage`
   - Color matches status

3. **Details:**
   - Loaded: X / Y tonnes
   - Remaining: Calculated (total - loaded)
   - Est. Completion: If available

### F. Utilization Trend Chart (Lines 369-399)
**Purpose**: Shows storage utilization over time (24-hour simulation)

**Chart Type**: Area Chart (Recharts)
- X-axis: Time (00:00, 04:00, etc.)
- Y-axis: Utilization percentage (0-100%)
- Gradient fill for visual appeal
- Interactive tooltip

---

## 7. ML Prediction Sections

### A. Capacity Prediction Card (Lines 404-446)
**Only displays if `predictionData` exists** (Lines 402-498)

**Shows 4 Metrics:**

1. **Available Weight** (tonnes)
   - Source: `predictionData.available_weight_kg / 1000`
   - Shows confidence interval range below
   - Format: "X.XX - Y.YY tonnes"

2. **Available Volume** (m³)
   - Source: `predictionData.available_volume_m3`
   - Shows confidence interval range
   - Format: "X.XX - Y.YY m³"

3. **Constraining Factor**
   - Source: `predictionData.constraining_factor`
   - Values: "WEIGHT" or "VOLUME"
   - Color: `warning` if weight, `primary` if volume
   - **Logic**: Shows which limit is reached first

4. **Overbooking Risk**
   - Source: `predictionData.overbooking_risk`
   - Values: "LOW", "MEDIUM", "HIGH"
   - Colors:
     - HIGH → `danger` (red)
     - MEDIUM → `warning` (yellow)
     - LOW → `success` (green)
   - **Business Logic**: Based on predicted demand vs available capacity

**Title**: Dynamically shows selected days (e.g., "Capacity Prediction (7 Days Before Flight)")

### B. Baggage Prediction Card (Lines 448-496)
**Displays ML-predicted baggage information**

**Metrics Shown:**

1. **Predicted Baggage Weight** (tonnes)
   - Source: `predictionData.baggage_prediction.predicted_baggage_weight_kg` or `predictionData.predicted_baggage_weight_kg`
   - Converted from kg to tonnes

2. **Predicted Baggage Volume** (m³)
   - Source: `predictionData.baggage_prediction.predicted_baggage_volume_m3` or `predictionData.predicted_baggage_volume_m3`

3. **Confidence Interval (95%)**
   - Shows weight range (lower - upper)
   - Only displays if available

4. **Aircraft Max Capacity**
   - Shows total aircraft cargo capacity
   - Format: "X.XX tonnes / Y.YY m³"

**Fallback**: Shows "No Baggage Prediction Available" if no data

### C. Legacy Prediction Section (Lines 501-521)
**Only displays if `!predictionData`** (no ML prediction available)

**Shows:**
- Predicted cargo volume
- Confidence score (as progress bar)

---

## 8. Data Flow Architecture

```
User Interaction
    ↓
Select Flight / Days Before Flight
    ↓
useEffect triggers
    ↓
fetchData() executes
    ↓
API Call: GET /api/v1/cargo/analytics/{flightId}?days_before_flight={days}
    ↓
Backend Processing:
  - Loads flight data from database
  - Calls ML service with prediction horizon
  - ML service:
    * Loads trained models (RandomForest)
    * Computes route statistics
    * Predicts baggage weight/volume
    * Calculates available capacity
    * Returns predictions with confidence intervals
  - Combines actual data + predictions
    ↓
Response JSON:
  {
    flight: {...},
    storage_availability: {...},
    loading_progress: {...},
    prediction: {
      // Full ML prediction data
      available_weight_kg,
      available_volume_m3,
      confidence_intervals,
      constraining_factor,
      overbooking_risk,
      baggage_prediction: {...}
    }
  }
    ↓
Frontend receives data
    ↓
Extracts predictionData from response.prediction
    ↓
Updates state → Triggers re-render
    ↓
All sections display with updated data
```

---

## 9. Key Business Logic

### Prediction Horizon Impact
- **0 days (Day of Flight)**: Most accurate (lowest uncertainty)
- **7 days**: Good balance for cargo sales planning
- **30 days**: Higher uncertainty, but enables early planning

**How it works:**
- Backend adjusts confidence intervals based on `days_before_flight`
- More days = wider confidence intervals (more uncertainty)
- Formula: `uncertainty_factor = 1.0 + (days_before_flight / 30.0) * 0.3`

### Constraining Factor Logic
**Determines if weight or volume is the limiting factor:**
```python
weight_utilization = (baggage_weight / max_weight) * 100
volume_utilization = (baggage_volume / max_volume) * 100

if weight_utilization > volume_utilization:
    constraining_factor = "weight"
else:
    constraining_factor = "volume"
```

### Overbooking Risk Assessment
```python
if available_weight < predicted_demand * 0.9:
    risk = "high"  # Very tight capacity
elif available_weight < predicted_demand:
    risk = "medium"  # Tight capacity
else:
    risk = "low"  # Comfortable capacity
```

### Available Capacity Calculation
```
available_weight = max_weight - predicted_baggage_weight
available_weight = available_weight * (1 - safety_margin)  # 5% safety margin

available_volume = max_volume - predicted_baggage_volume
available_volume = available_volume * (1 - safety_margin)
```

---

## 10. Error Handling

### Loading State (Lines 71-80)
- Shows spinner with "Loading cargo analytics..." message
- Displayed while `loading === true`

### Error State (Lines 82-92)
- Shows error message
- Provides "Retry" button (reloads page)
- Triggered when:
  - API call fails
  - No analytics data returned
  - Exception thrown in fetchData

### Graceful Degradation
- If API fails, falls back to mock data (in cargoService.ts)
- Missing fields use safe fallbacks
- Components check for data existence before rendering

---

## 11. API Integration

### Primary API Call
```typescript
GET /api/v1/cargo/analytics/{flightId}?days_before_flight={days}
```

### Supporting API Calls
1. **Get Flights List**: `GET /api/v1/flights/cargo`
   - Returns all flights with cargo data
   - Used for dropdown population

2. **Predict Capacity** (Direct): `POST /api/v1/cargo/predict-capacity`
   - Standalone prediction endpoint
   - Not used in this component (handled by analytics endpoint)

---

## 12. Component Dependencies

### External Libraries:
- **React Router**: `useParams`, `useNavigate` - URL routing
- **date-fns**: `format`, `parseISO` - Date formatting
- **Recharts**: Charts library for visualizations
  - `LineChart`, `AreaChart`, `PieChart`
  - `XAxis`, `YAxis`, `Tooltip`, etc.

### Internal Components:
- `Card` - Reusable card container
- `ProgressBar` - Progress bar component
- `StatCard` - Statistics display card

---

## 13. Performance Considerations

1. **Data Fetching**:
   - Only fetches when dependencies change (useEffect dependencies)
   - Debounced by React's batching (won't trigger multiple times)

2. **Re-rendering**:
   - Only re-renders when state changes
   - Chart components handle their own optimizations

3. **Memory**:
   - State is cleared when component unmounts
   - No memory leaks from event listeners

---

## 14. User Interaction Flow

```
1. User visits page
   ↓
2. Page loads, shows spinner
   ↓
3. Fetches flights list + analytics for default flight
   ↓
4. Displays all sections with data
   ↓
5. User can:
   a. Select different flight → Updates URL → Fetches new data
   b. Change "Days Before Flight" → Re-fetches with new horizon
   c. Click "Back to List" → Navigates away
   ↓
6. All changes trigger re-fetch and re-render
```

---

## Summary

The Cargo Analytics page is a comprehensive dashboard that:
- ✅ Displays current cargo status (actual data)
- ✅ Shows ML predictions for future capacity
- ✅ Adjusts predictions based on time horizon
- ✅ Visualizes data with charts and progress bars
- ✅ Handles errors gracefully
- ✅ Provides interactive controls for flight selection and prediction horizon

The ML integration happens entirely in the backend - the frontend just displays the results in a user-friendly interface.
