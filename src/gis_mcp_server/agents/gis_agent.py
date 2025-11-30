"""GIS Agent for natural language processing of freight optimization requests."""

import asyncio
import logging
import re
from typing import Any, Optional

from ..tools.distance_calculator import DistanceCalculator
from ..tools.route_optimizer import RouteOptimizer

logger = logging.getLogger(__name__)


# Simple location to coordinates mapping (expandable)
LOCATION_COORDINATES = {
    "new york": (40.7128, -74.0060),
    "nyc": (40.7128, -74.0060),
    "los angeles": (34.0522, -118.2437),
    "la": (34.0522, -118.2437),
    "denver": (39.7392, -104.9903),
    "san francisco": (37.7749, -122.4194),
    "sf": (37.7749, -122.4194),
    "chicago": (41.8781, -87.6298),
    "houston": (29.7604, -95.3698),
    "phoenix": (33.4484, -112.0742),
    "philadelphia": (39.9526, -75.1652),
    "san antonio": (29.4241, -98.4936),
    "san diego": (32.7157, -117.1611),
    "dallas": (32.7767, -96.7970),
    "seattle": (47.6062, -122.3321),
    "atlanta": (33.7490, -84.3880),
    "boston": (42.3601, -71.0589),
    "miami": (25.7617, -80.1918),
}


class GISAgent:
    """Natural language agent for GIS and freight optimization."""

    def __init__(self) -> None:
        """Initialize the GIS Agent."""
        logger.info("GIS Agent initialized")

    def _resolve_location(self, location_name: str) -> Optional[tuple[float, float]]:
        """
        Resolve location name to coordinates.

        Args:
            location_name: Name of the location (e.g., "New York")

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        normalized = location_name.lower().strip()
        return LOCATION_COORDINATES.get(normalized)

    def _parse_distance_query(self, query: str) -> Optional[dict[str, Any]]:
        """
        Parse natural language distance queries.

        Examples:
            - "distance from NYC to LA"
            - "how far is it from New York to Los Angeles"
            - "calculate distance between Denver and Seattle"
        """
        # Pattern: "distance|far|how" ... "from" ... "to"
        patterns = [
            r"(?:distance|how\s+far|calculate\s+(?:the\s+)?distance).*?from\s+(.+?)\s+to\s+(.+?)(?:\?|$)",
            r"(?:distance|far).*?between\s+(.+?)\s+and\s+(.+?)(?:\?|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                origin_name = match.group(1).strip()
                destination_name = match.group(2).strip()

                origin = self._resolve_location(origin_name)
                destination = self._resolve_location(destination_name)

                if origin and destination:
                    return {
                        "type": "distance",
                        "origin_name": origin_name,
                        "destination_name": destination_name,
                        "origin": origin,
                        "destination": destination,
                    }

        return None

    def _parse_route_query(self, query: str) -> Optional[dict[str, Any]]:
        """
        Parse natural language route optimization queries.

        Examples:
            - "optimize a route with stops in NYC, Denver, and LA"
            - "find the best route visiting New York, Chicago, and Los Angeles"
            - "plan a route through San Francisco, Las Vegas, and Los Angeles"
        """
        pattern = r"(?:optimize|best|plan)\s+(?:a\s+)?route.*?(?:stops|visiting|through)\s+(.+?)(?:\?|$)"

        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            stops_str = match.group(1)
            # Split by comma or "and"
            stops_list = re.split(r",\s+and\s+|,\s+|\s+and\s+", stops_str)
            stops_list = [s.strip() for s in stops_list if s.strip()]

            locations = []
            for stop in stops_list:
                coord = self._resolve_location(stop)
                if coord:
                    locations.append((stop, coord))

            if len(locations) >= 2:
                return {
                    "type": "route",
                    "stops": locations,
                    "waypoints": [coord for _, coord in locations],
                }

        return None

    def _parse_cost_query(self, query: str) -> Optional[dict[str, Any]]:
        """
        Parse natural language fuel cost queries.

        Examples:
            - "what's the fuel cost for 500 km"
            - "estimate fuel cost for a 1000 km route"
            - "how much fuel costs for 800 km at $2 per liter"
        """
        # Extract distance in km
        distance_pattern = r"(\d+(?:\.\d+)?)\s*km"
        distance_match = re.search(distance_pattern, query, re.IGNORECASE)

        if distance_match:
            distance_km = float(distance_match.group(1))

            # Extract fuel price if provided
            price_pattern = r"\$?(\d+(?:\.\d+)?)\s*(?:per\s+)?liter"
            price_match = re.search(price_pattern, query, re.IGNORECASE)
            fuel_price = float(price_match.group(1)) if price_match else 1.5

            # Extract fuel efficiency if provided
            efficiency_pattern = r"(\d+(?:\.\d+)?)\s*km/liter|efficiency\s+of\s+(\d+(?:\.\d+)?)"
            efficiency_match = re.search(efficiency_pattern, query, re.IGNORECASE)
            fuel_efficiency = (
                float(efficiency_match.group(1) or efficiency_match.group(2))
                if efficiency_match
                else 8
            )

            return {
                "type": "cost",
                "distance_km": distance_km,
                "fuel_price": fuel_price,
                "fuel_efficiency": fuel_efficiency,
            }

        return None

    async def process_request(self, natural_language_query: str) -> dict[str, Any]:
        """
        Process natural language queries for GIS operations.

        Args:
            natural_language_query: Natural language request for distance/route calculation

        Returns:
            Dictionary with calculated results and explanations
        """
        logger.info(f"Processing query: {natural_language_query}")

        # Try to parse as distance query
        parsed = self._parse_distance_query(natural_language_query)
        if parsed:
            try:
                distance = DistanceCalculator.calculate_distance(
                    parsed["origin"], parsed["destination"], unit="km"
                )
                travel_time = DistanceCalculator.estimate_travel_time(distance)
                return {
                    "status": "success",
                    "type": "distance",
                    "query": natural_language_query,
                    "result": {
                        "from": parsed["origin_name"],
                        "to": parsed["destination_name"],
                        "distance_km": round(distance, 2),
                        "travel_hours": round(travel_time["hours"], 2),
                        "explanation": f"The distance from {parsed['origin_name']} to {parsed['destination_name']} is {distance:.2f} km, which takes approximately {travel_time['hours']:.1f} hours at 80 km/h.",
                    },
                }
            except Exception as e:
                logger.error(f"Error calculating distance: {e}")
                return {"status": "error", "query": natural_language_query, "error": str(e)}

        # Try to parse as route query
        parsed = self._parse_route_query(natural_language_query)
        if parsed:
            try:
                optimized = RouteOptimizer.optimize_waypoints(parsed["waypoints"])
                total_distance = DistanceCalculator.calculate_route_distance(optimized)
                fuel_cost = RouteOptimizer.estimate_fuel_cost(total_distance)
                return {
                    "status": "success",
                    "type": "route",
                    "query": natural_language_query,
                    "result": {
                        "stops": [stop for stop, _ in parsed["stops"]],
                        "total_distance_km": round(total_distance, 2),
                        "estimated_fuel_cost": round(fuel_cost, 2),
                        "explanation": f"Optimized route through {', '.join([s for s, _ in parsed['stops']])} is {total_distance:.2f} km with estimated fuel cost of ${fuel_cost:.2f}.",
                    },
                }
            except Exception as e:
                logger.error(f"Error optimizing route: {e}")
                return {"status": "error", "query": natural_language_query, "error": str(e)}

        # Try to parse as cost query
        parsed = self._parse_cost_query(natural_language_query)
        if parsed:
            try:
                fuel_cost = RouteOptimizer.estimate_fuel_cost(
                    parsed["distance_km"],
                    parsed["fuel_price"],
                    parsed["fuel_efficiency"],
                )
                return {
                    "status": "success",
                    "type": "cost",
                    "query": natural_language_query,
                    "result": {
                        "distance_km": parsed["distance_km"],
                        "fuel_price_per_liter": parsed["fuel_price"],
                        "fuel_efficiency_km_per_liter": parsed["fuel_efficiency"],
                        "estimated_fuel_cost": round(fuel_cost, 2),
                        "explanation": f"For a {parsed['distance_km']} km route at ${parsed['fuel_price']}/L with {parsed['fuel_efficiency']} km/L efficiency, fuel cost is ${fuel_cost:.2f}.",
                    },
                }
            except Exception as e:
                logger.error(f"Error calculating cost: {e}")
                return {"status": "error", "query": natural_language_query, "error": str(e)}

        # Could not parse query
        return {
            "status": "unrecognized",
            "query": natural_language_query,
            "message": "I couldn't understand this query. Try asking about distance, route optimization, or fuel costs.",
            "examples": [
                "How far is it from New York to Los Angeles?",
                "Optimize a route with stops in NYC, Denver, and LA",
                "What's the fuel cost for 500 km at $2 per liter?",
            ],
        }

    async def calculate_freight_route(
        self,
        origin: str,
        destination: str,
        waypoints: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Calculate optimal freight route between locations.

        Args:
            origin: Starting location name (e.g., "New York")
            destination: Ending location name (e.g., "Los Angeles")
            waypoints: Optional intermediate stop names

        Returns:
            Route information with distance and cost estimates
        """
        logger.info(f"Calculating route from {origin} to {destination}")

        # Resolve all locations
        origin_coord = self._resolve_location(origin)
        destination_coord = self._resolve_location(destination)

        if not origin_coord or not destination_coord:
            return {
                "status": "error",
                "message": f"Could not resolve location(s): {origin} or {destination}",
            }

        # Build waypoint list
        all_waypoints = [origin_coord]
        waypoint_names = [origin]

        if waypoints:
            for wp in waypoints:
                coord = self._resolve_location(wp)
                if coord:
                    all_waypoints.append(coord)
                    waypoint_names.append(wp)

        all_waypoints.append(destination_coord)
        waypoint_names.append(destination)

        if len(all_waypoints) < 2:
            return {
                "status": "error",
                "message": "Not enough valid waypoints for route",
            }

        # Optimize route
        try:
            optimized = RouteOptimizer.optimize_waypoints(all_waypoints)
            total_distance = DistanceCalculator.calculate_route_distance(optimized)
            travel_time = DistanceCalculator.estimate_travel_time(total_distance)
            fuel_cost = RouteOptimizer.estimate_fuel_cost(total_distance)

            return {
                "status": "success",
                "origin": origin,
                "destination": destination,
                "waypoints": waypoint_names,
                "total_distance_km": round(total_distance, 2),
                "travel_hours": round(travel_time["hours"], 2),
                "estimated_fuel_cost": round(fuel_cost, 2),
            }
        except Exception as e:
            logger.error(f"Error calculating freight route: {e}")
            return {"status": "error", "message": str(e)}
