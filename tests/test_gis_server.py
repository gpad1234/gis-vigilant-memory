"""Tests for GIS MCP Server."""

import pytest

from src.gis_mcp_server.tools.distance_calculator import DistanceCalculator


class TestDistanceCalculator:
    """Test distance calculation functionality."""

    def test_calculate_distance_km(self) -> None:
        """Test distance calculation in kilometers."""
        # New York to Los Angeles
        nyc = (40.7128, -74.0060)
        lax = (34.0522, -118.2437)

        distance = DistanceCalculator.calculate_distance(nyc, lax, unit="km")
        assert 3900 < distance < 4100  # Approximately 3944 km

    def test_calculate_distance_miles(self) -> None:
        """Test distance calculation in miles."""
        nyc = (40.7128, -74.0060)
        lax = (34.0522, -118.2437)

        distance = DistanceCalculator.calculate_distance(nyc, lax, unit="miles")
        assert 2400 < distance < 2600  # Approximately 2450 miles

    def test_calculate_route_distance(self) -> None:
        """Test route distance calculation."""
        waypoints = [
            (40.7128, -74.0060),  # NYC
            (39.7392, -104.9903),  # Denver
            (34.0522, -118.2437),  # LA
        ]

        distance = DistanceCalculator.calculate_route_distance(waypoints, unit="km")
        assert distance > 0

    def test_estimate_travel_time(self) -> None:
        """Test travel time estimation."""
        # 800 km at 80 km/h = 10 hours
        result = DistanceCalculator.estimate_travel_time(800, avg_speed_kmh=80)

        assert result["hours"] == 10.0
        assert result["minutes"] == 600.0


class TestGISMCPServer:
    """Test GIS MCP Server initialization."""

    def test_server_initialization(self) -> None:
        """Test server can be initialized."""
        from src.gis_mcp_server import GISMCPServer

        server = GISMCPServer()
        assert server is not None
        assert server.server is not None
