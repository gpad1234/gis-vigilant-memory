"""Route optimization tool for efficient freight delivery."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class RouteOptimizer:
    """Optimize freight delivery routes."""

    @staticmethod
    def optimize_waypoints(
        waypoints: list[tuple[float, float]], start_index: int = 0
    ) -> list[tuple[float, float]]:
        """
        Simple nearest-neighbor optimization for waypoints.

        Args:
            waypoints: List of (latitude, longitude) tuples
            start_index: Starting waypoint index

        Returns:
            Optimized list of waypoints
        """
        from geopy.distance import geodesic

        if len(waypoints) <= 2:
            return waypoints

        unvisited = set(range(len(waypoints)))
        current = start_index
        optimized = [waypoints[current]]
        unvisited.remove(current)

        while unvisited:
            nearest = min(
                unvisited,
                key=lambda i: geodesic(waypoints[current], waypoints[i]).kilometers,
            )
            optimized.append(waypoints[nearest])
            current = nearest
            unvisited.remove(current)

        return optimized

    @staticmethod
    def estimate_fuel_cost(
        distance_km: float, fuel_price_per_liter: float = 1.5, fuel_efficiency: float = 8
    ) -> float:
        """
        Estimate fuel cost for a route.

        Args:
            distance_km: Distance in kilometers
            fuel_price_per_liter: Price per liter of fuel
            fuel_efficiency: Vehicle fuel efficiency in km/liter

        Returns:
            Estimated fuel cost
        """
        liters_needed = distance_km / fuel_efficiency
        return liters_needed * fuel_price_per_liter
