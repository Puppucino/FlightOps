"""
Traffic Estimation Service
Estimates passenger traffic and cargo demand based on date, holidays, and school holidays
"""
from datetime import datetime, date
from typing import Dict, Any, List, Optional
import calendar


class TrafficEstimator:
    """Estimates traffic and demand based on date patterns"""
    
    # Major holidays (month, day) - can be expanded
    MAJOR_HOLIDAYS = [
        (1, 1),   # New Year's Day
        (12, 25), # Christmas
        (12, 31), # New Year's Eve
        (7, 4),   # Independence Day (US)
        (11, 1),  # All Saints' Day
        (10, 31), # Halloween
    ]
    
    # School holiday periods (approximate, region-specific)
    # Format: (start_month, start_day, end_month, end_day)
    SCHOOL_HOLIDAYS = [
        (12, 15, 1, 5),   # Winter break (Dec 15 - Jan 5)
        (6, 1, 8, 31),    # Summer break (Jun 1 - Aug 31)
        (3, 15, 3, 31),   # Spring break (Mar 15 - Mar 31)
        (10, 1, 10, 15),  # Fall break (Oct 1 - Oct 15)
    ]
    
    def __init__(self):
        """Initialize traffic estimator"""
        pass
    
    def is_holiday(self, check_date: date) -> bool:
        """Check if date is a major holiday"""
        month = check_date.month
        day = check_date.day
        return (month, day) in self.MAJOR_HOLIDAYS
    
    def is_school_holiday(self, check_date: date) -> bool:
        """Check if date falls within school holiday period"""
        month = check_date.month
        day = check_date.day
        
        for start_month, start_day, end_month, end_day in self.SCHOOL_HOLIDAYS:
            # Handle year wrap-around (e.g., Dec 15 - Jan 5)
            if start_month > end_month:
                # Crosses year boundary
                if (month == start_month and day >= start_day) or \
                   (month == end_month and day <= end_day) or \
                   (month > start_month) or \
                   (month < end_month):
                    return True
            else:
                # Within same year
                if month == start_month and day >= start_day:
                    return True
                if month == end_month and day <= end_day:
                    return True
                if start_month < month < end_month:
                    return True
        
        return False
    
    def is_weekend(self, check_date: date) -> bool:
        """Check if date is a weekend"""
        return check_date.weekday() >= 5
    
    def get_traffic_multiplier(self, check_date: date) -> float:
        """
        Get traffic multiplier based on date patterns
        
        Returns:
            Multiplier for expected traffic (1.0 = normal, >1.0 = higher traffic)
        """
        multiplier = 1.0
        
        # Weekend effect (slightly higher traffic)
        if self.is_weekend(check_date):
            multiplier *= 1.15
        
        # Holiday effect (much higher traffic)
        if self.is_holiday(check_date):
            multiplier *= 1.5
        
        # School holiday effect (higher traffic)
        if self.is_school_holiday(check_date):
            multiplier *= 1.3
        
        # Month-based patterns (summer and winter peaks)
        month = check_date.month
        if month in [6, 7, 8]:  # Summer months
            multiplier *= 1.2
        elif month in [12, 1]:  # Winter holiday season
            multiplier *= 1.25
        
        return multiplier
    
    def estimate_passenger_traffic(
        self,
        base_passenger_count: int,
        flight_date: date,
        route: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimate passenger traffic for a given date
        
        Args:
            base_passenger_count: Base passenger count (from bookings or historical average)
            flight_date: Flight departure date
            route: Optional route identifier (e.g., "KUL-SIN")
            
        Returns:
            Dictionary with traffic estimation
        """
        multiplier = self.get_traffic_multiplier(flight_date)
        estimated_passengers = int(base_passenger_count * multiplier)
        
        # Determine peak season type
        peak_season_type = None
        if self.is_holiday(flight_date):
            peak_season_type = "holiday"
        elif self.is_school_holiday(flight_date):
            peak_season_type = "school_holiday"
        elif multiplier >= 1.3:
            peak_season_type = "peak_season"
        
        return {
            "base_passenger_count": base_passenger_count,
            "estimated_passenger_count": estimated_passengers,
            "traffic_multiplier": multiplier,
            "is_holiday": self.is_holiday(flight_date),
            "is_school_holiday": self.is_school_holiday(flight_date),
            "is_weekend": self.is_weekend(flight_date),
            "peak_season_type": peak_season_type,
            "month": flight_date.month,
            "day_of_week": calendar.day_name[flight_date.weekday()],
        }
    
    def estimate_cargo_demand(
        self,
        base_cargo_demand_kg: float,
        flight_date: date,
        route: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Estimate cargo demand for a given date
        
        Args:
            base_cargo_demand_kg: Base cargo demand in kg
            flight_date: Flight departure date
            route: Optional route identifier
            
        Returns:
            Dictionary with cargo demand estimation
        """
        # Cargo demand typically increases with passenger traffic
        # but may have different patterns (e.g., holiday shopping)
        multiplier = self.get_traffic_multiplier(flight_date)
        
        # Cargo demand might increase more during holidays (shopping, gifts)
        if self.is_holiday(flight_date) or (flight_date.month == 12):
            multiplier *= 1.1  # Extra boost for cargo during holidays
        
        estimated_demand = base_cargo_demand_kg * multiplier
        
        return {
            "base_cargo_demand_kg": base_cargo_demand_kg,
            "estimated_cargo_demand_kg": estimated_demand,
            "demand_multiplier": multiplier,
            "is_holiday": self.is_holiday(flight_date),
            "is_school_holiday": self.is_school_holiday(flight_date),
            "is_weekend": self.is_weekend(flight_date),
            "month": flight_date.month,
        }
    
    def get_peak_seasons_for_month(self, year: int, month: int) -> List[Dict[str, Any]]:
        """
        Get all peak season periods for a given month
        
        Returns:
            List of peak season periods with details
        """
        peak_periods = []
        
        # Check each day in the month
        num_days = calendar.monthrange(year, month)[1]
        for day in range(1, num_days + 1):
            check_date = date(year, month, day)
            multiplier = self.get_traffic_multiplier(check_date)
            
            if multiplier >= 1.2:  # Significant peak
                peak_type = None
                if self.is_holiday(check_date):
                    peak_type = "holiday"
                elif self.is_school_holiday(check_date):
                    peak_type = "school_holiday"
                else:
                    peak_type = "peak_season"
                
                peak_periods.append({
                    "date": check_date,
                    "day": day,
                    "multiplier": multiplier,
                    "type": peak_type,
                    "is_holiday": self.is_holiday(check_date),
                    "is_school_holiday": self.is_school_holiday(check_date),
                    "is_weekend": self.is_weekend(check_date),
                })
        
        return peak_periods
