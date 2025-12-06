"""
Cargo Mix Optimization Service
Provides intelligent recommendations for optimal cargo mix based on available capacity
"""
from typing import Dict, Any, List, Optional
from app.services.ai_agent_service import AIAgentService
from loguru import logger


class CargoOptimizationService:
    """Service for cargo mix optimization"""
    
    def __init__(self, ai_service: Optional[AIAgentService] = None):
        self.ai_service = ai_service or AIAgentService()
    
    async def optimize_cargo_mix(
        self,
        available_weight_kg: float,
        available_volume_m3: float,
        constraining_factor: str,
        route_info: Optional[Dict[str, Any]] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate optimal cargo mix recommendations
        
        Args:
            available_weight_kg: Available weight capacity
            available_volume_m3: Available volume capacity
            constraining_factor: 'weight' or 'volume'
            route_info: Route information (origin, destination)
            preferences: User preferences (priority cargo types, etc.)
            
        Returns:
            Dict with optimization recommendations
        """
        try:
            # Use AI agent to generate recommendations
            recommendations = await self.ai_service.generate_cargo_recommendations(
                available_weight_kg=available_weight_kg,
                available_volume_m3=available_volume_m3,
                constraining_factor=constraining_factor,
                route_info=route_info or {}
            )
            
            # Validate and enhance recommendations
            validated_mix = self._validate_cargo_mix(
                recommendations.get('recommended_cargo_mix', []),
                available_weight_kg,
                available_volume_m3
            )
            
            recommendations['recommended_cargo_mix'] = validated_mix
            
            # Calculate totals
            total_weight = sum(item.get('weight_kg', 0) for item in validated_mix)
            total_volume = sum(item.get('volume_m3', 0) for item in validated_mix)
            
            recommendations['total_weight_kg'] = total_weight
            recommendations['total_volume_m3'] = total_volume
            recommendations['weight_utilization'] = (total_weight / available_weight_kg * 100) if available_weight_kg > 0 else 0
            recommendations['volume_utilization'] = (total_volume / available_volume_m3 * 100) if available_volume_m3 > 0 else 0
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error optimizing cargo mix: {e}")
            return {
                "recommended_cargo_mix": [],
                "reasoning": f"Unable to generate recommendations: {str(e)}",
                "total_weight_kg": 0,
                "total_volume_m3": 0
            }
    
    def _validate_cargo_mix(
        self,
        cargo_mix: List[Dict[str, Any]],
        max_weight_kg: float,
        max_volume_m3: float
    ) -> List[Dict[str, Any]]:
        """
        Validate and adjust cargo mix to fit within constraints
        
        Args:
            cargo_mix: Recommended cargo mix
            max_weight_kg: Maximum weight capacity
            max_volume_m3: Maximum volume capacity
            
        Returns:
            Validated cargo mix
        """
        validated = []
        current_weight = 0.0
        current_volume = 0.0
        
        # Sort by priority (high priority first)
        sorted_mix = sorted(
            cargo_mix,
            key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x.get('priority', 'low'), 2)
        )
        
        for item in sorted_mix:
            item_weight = item.get('weight_kg', 0)
            item_volume = item.get('volume_m3', 0)
            
            # Check if item fits
            if (current_weight + item_weight <= max_weight_kg and
                current_volume + item_volume <= max_volume_m3):
                validated.append(item)
                current_weight += item_weight
                current_volume += item_volume
            else:
                # Try to fit partial amount if possible
                remaining_weight = max_weight_kg - current_weight
                remaining_volume = max_volume_m3 - current_volume
                
                if remaining_weight > 0 and remaining_volume > 0:
                    # Calculate what percentage we can fit
                    weight_ratio = remaining_weight / item_weight if item_weight > 0 else 0
                    volume_ratio = remaining_volume / item_volume if item_volume > 0 else 0
                    fit_ratio = min(weight_ratio, volume_ratio)
                    
                    if fit_ratio > 0.1:  # At least 10% fits
                        partial_item = item.copy()
                        partial_item['weight_kg'] = item_weight * fit_ratio
                        partial_item['volume_m3'] = item_volume * fit_ratio
                        partial_item['note'] = f"Partial load ({fit_ratio*100:.0f}%)"
                        validated.append(partial_item)
                        current_weight += partial_item['weight_kg']
                        current_volume += partial_item['volume_m3']
        
        return validated
    
    def calculate_revenue_estimate(
        self,
        cargo_mix: List[Dict[str, Any]],
        route_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate revenue from cargo mix
        
        Args:
            cargo_mix: Cargo mix list
            route_info: Route information
            
        Returns:
            Revenue estimate
        """
        # Typical cargo prices per kg by type (can be enhanced with actual pricing data)
        cargo_prices = {
            'electronics': 15.0,  # USD per kg
            'machinery': 8.0,
            'textiles': 3.0,
            'pharmaceuticals': 25.0,
            'food': 2.0,
            'general': 5.0
        }
        
        total_revenue = 0.0
        total_weight = 0.0
        
        for item in cargo_mix:
            cargo_type = item.get('type', 'general').lower()
            weight_kg = item.get('weight_kg', 0)
            
            # Find matching price
            price_per_kg = cargo_prices.get(cargo_type, cargo_prices['general'])
            
            # Check if item has custom price
            if 'price_per_kg' in item:
                price_per_kg = item['price_per_kg']
            
            revenue = weight_kg * price_per_kg
            total_revenue += revenue
            total_weight += weight_kg
        
        # Route-specific adjustments
        if route_info:
            # Some routes have premium pricing
            origin = route_info.get('origin', '')
            destination = route_info.get('destination', '')
            premium_routes = ['KUL', 'SIN', 'HKG', 'PVG', 'NRT', 'DXB']
            if origin in premium_routes or destination in premium_routes:
                total_revenue *= 1.1
        
        return {
            "estimated_revenue_usd": round(total_revenue, 2),
            "total_weight_kg": round(total_weight, 2),
            "average_price_per_kg": round(total_revenue / total_weight, 2) if total_weight > 0 else 0,
            "revenue_category": self._categorize_revenue(total_revenue)
        }
    
    def _categorize_revenue(self, revenue: float) -> str:
        """Categorize revenue level"""
        if revenue > 50000:
            return "very_high"
        elif revenue > 30000:
            return "high"
        elif revenue > 15000:
            return "medium"
        else:
            return "low"
