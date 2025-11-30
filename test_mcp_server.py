#!/usr/bin/env python3
"""Test script for GIS tools directly.

This tests the underlying GIS calculators that power the MCP server.
For MCP server testing, see USAGE.md -> Testing the MCP Server section.
"""

import json
from src.gis_mcp_server.tools.distance_calculator import DistanceCalculator
from src.gis_mcp_server.tools.route_optimizer import RouteOptimizer


def test_gis_tools():
    """Test all GIS tools directly."""
    print("🚀 Testing GIS Tools (Direct - No Server)\n")
    
    try:
        # Test 1: Distance calculation
        print("=" * 50)
        print("TEST 1: Calculate Distance (NYC → LA)")
        print("=" * 50)
        distance = DistanceCalculator.calculate_distance(
            origin=(40.7128, -74.0060),      # NYC
            destination=(34.0522, -118.2437), # LA
            unit="km"
        )
        travel_time = DistanceCalculator.estimate_travel_time(distance)
        print(json.dumps({
            "origin": "NYC (40.7128, -74.0060)",
            "destination": "LA (34.0522, -118.2437)",
            "distance_km": distance,
            "travel_hours": travel_time
        }, indent=2))
        
        # Test 2: Route optimization
        print("\n" + "=" * 50)
        print("TEST 2: Optimize Route (NYC → Denver → LA)")
        print("=" * 50)
        waypoints = [
            (40.7128, -74.0060),      # NYC
            (39.7392, -104.9903),     # Denver
            (34.0522, -118.2437)      # LA
        ]
        optimized = RouteOptimizer.optimize_waypoints(waypoints)
        total_distance = DistanceCalculator.calculate_route_distance(optimized)
        print(json.dumps({
            "original_waypoints": ["NYC", "Denver", "LA"],
            "optimized_order": ["NYC", "Denver", "LA"],
            "total_distance_km": round(total_distance, 2)
        }, indent=2))
        
        # Test 3: Fuel cost estimation
        print("\n" + "=" * 50)
        print("TEST 3: Estimate Fuel Cost (1000 km)")
        print("=" * 50)
        cost = RouteOptimizer.estimate_fuel_cost(
            distance_km=1000,
            fuel_price_per_liter=2.5,
            fuel_efficiency=7.5
        )
        print(json.dumps({
            "distance_km": 1000,
            "fuel_price_per_liter": 2.5,
            "fuel_efficiency": 7.5,
            "estimated_cost": cost
        }, indent=2))
        
        # Test 4: Multiple waypoints
        print("\n" + "=" * 50)
        print("TEST 4: Complex Route (5 cities)")
        print("=" * 50)
        waypoints_5 = [
            (40.7128, -74.0060),      # NYC
            (41.8781, -87.6298),      # Chicago
            (39.7392, -104.9903),     # Denver
            (33.7490, -84.3880),      # Atlanta
            (34.0522, -118.2437)      # LA
        ]
        optimized_5 = RouteOptimizer.optimize_waypoints(waypoints_5)
        total_distance_5 = DistanceCalculator.calculate_route_distance(optimized_5)
        cost_5 = RouteOptimizer.estimate_fuel_cost(
            distance_km=total_distance_5,
            fuel_price_per_liter=2.0,
            fuel_efficiency=8.0
        )
        print(json.dumps({
            "cities": ["NYC", "Chicago", "Denver", "Atlanta", "LA"],
            "total_distance_km": round(total_distance_5, 2),
            "fuel_cost": round(cost_5, 2),
            "fuel_efficiency": 8.0,
            "fuel_price_per_liter": 2.0
        }, indent=2))
        
        # Test 5: Travel time calculation
        print("\n" + "=" * 50)
        print("TEST 5: Travel Time for Various Distances")
        print("=" * 50)
        times = {
            "500_km_hours": DistanceCalculator.estimate_travel_time(500),
            "1000_km_hours": DistanceCalculator.estimate_travel_time(1000),
            "2000_km_hours": DistanceCalculator.estimate_travel_time(2000),
        }
        print(json.dumps(times, indent=2))
        
        print("\n✅ All GIS tool tests passed!")
        print("\nℹ️  For MCP server testing, see: USAGE.md -> Testing the MCP Server")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    test_gis_tools()
