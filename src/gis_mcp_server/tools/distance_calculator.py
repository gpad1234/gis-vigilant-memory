"""Distance calculation tool for freight optimization."""

import logging
from typing import Optional

from geopy.distance import geodesic

logger = logging.getLogger(__name__)


class DistanceCalculator:
    """Calculate distances between geographic coordinates for freight routes."""

    @staticmethod
    def calculate_distance(
        origin: tuple[float, float],
        destination: tuple[float, float],
        unit: str = "km",
    ) -> float:
        """
        Calculate geodesic distance between two points.

        Args:
            origin: Tuple of (latitude, longitude) for start point
            destination: Tuple of (latitude, longitude) for end point
            unit: Distance unit ('km' or 'miles')

        Returns:
            Distance in specified unit
        """
        dist = geodesic(origin, destination)
        return dist.kilometers if unit == "km" else dist.miles

    @staticmethod
    def calculate_route_distance(waypoints: list[tuple[float, float]], unit: str = "km") -> float:
        """
        Calculate total distance for a route with multiple waypoints.

        Args:
            waypoints: List of (latitude, longitude) tuples
            unit: Distance unit ('km' or 'miles')

        Returns:
            Total distance in specified unit
        """
        if len(waypoints) < 2:
            return 0.0

        total_distance = 0.0
        for i in range(len(waypoints) - 1):
            total_distance += DistanceCalculator.calculate_distance(
                waypoints[i], waypoints[i + 1], unit
            )

        return total_distance

    @staticmethod
    def estimate_travel_time(distance_km: float, avg_speed_kmh: float = 80) -> dict[str, float]:
        """
        Estimate travel time based on distance and average speed.

        Args:
            distance_km: Distance in kilometers
            avg_speed_kmh: Average speed in km/h (default: 80)

        Returns:
            Dictionary with hours and total minutes
        """
        total_minutes = (distance_km / avg_speed_kmh) * 60
        return {
            "hours": total_minutes / 60,
            "minutes": total_minutes,
        }
