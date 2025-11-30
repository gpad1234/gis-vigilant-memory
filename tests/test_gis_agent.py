"""Tests for GIS Agent NLP functionality."""

import asyncio

import pytest

from src.gis_mcp_server.agents.gis_agent import GISAgent


class TestGISAgent:
    """Test GIS Agent NLP capabilities."""

    @pytest.fixture
    def agent(self) -> GISAgent:
        """Create agent instance."""
        return GISAgent()

    def test_agent_initialization(self, agent: GISAgent) -> None:
        """Test agent can be initialized."""
        assert agent is not None

    def test_location_resolution(self, agent: GISAgent) -> None:
        """Test location name to coordinate resolution."""
        nyc = agent._resolve_location("New York")
        assert nyc == (40.7128, -74.0060)

        la = agent._resolve_location("Los Angeles")
        assert la == (34.0522, -118.2437)

        invalid = agent._resolve_location("Invalid Location")
        assert invalid is None

    def test_parse_distance_query(self, agent: GISAgent) -> None:
        """Test parsing distance queries."""
        # Pattern 1: "distance from X to Y"
        query1 = "distance from NYC to LA"
        result1 = agent._parse_distance_query(query1)
        assert result1 is not None
        assert result1["type"] == "distance"
        assert result1["origin_name"] == "NYC"
        assert result1["destination_name"] == "LA"

        # Pattern 2: "how far is it from X to Y"
        query2 = "how far is it from New York to Los Angeles?"
        result2 = agent._parse_distance_query(query2)
        assert result2 is not None
        assert result2["origin_name"] == "New York"

        # Pattern 3: "distance between X and Y"
        query3 = "distance between Denver and Seattle"
        result3 = agent._parse_distance_query(query3)
        assert result3 is not None
        assert result3["destination_name"] == "Seattle"

    def test_parse_route_query(self, agent: GISAgent) -> None:
        """Test parsing route optimization queries."""
        query = "optimize a route with stops in NYC, Denver, and LA"
        result = agent._parse_route_query(query)

        assert result is not None
        assert result["type"] == "route"
        assert len(result["stops"]) >= 2
        stop_names = [s[0].lower() for s in result["stops"]]
        assert "la" in stop_names

    def test_parse_cost_query(self, agent: GISAgent) -> None:
        """Test parsing fuel cost queries."""
        query = "what's the fuel cost for 500 km at $2 per liter"
        result = agent._parse_cost_query(query)

        assert result is not None
        assert result["type"] == "cost"
        assert result["distance_km"] == 500
        assert result["fuel_price"] == 2.0

    def test_process_distance_request(self, agent: GISAgent) -> None:
        """Test processing distance request."""
        query = "distance from New York to Los Angeles"
        result = asyncio.run(agent.process_request(query))

        assert result["status"] == "success"
        assert result["type"] == "distance"
        assert result["result"]["distance_km"] > 3900
        assert result["result"]["distance_km"] < 4100

    def test_process_route_request(self, agent: GISAgent) -> None:
        """Test processing route optimization request."""
        query = "optimize a route with stops in NYC, Denver, and LA"
        result = asyncio.run(agent.process_request(query))

        assert result["status"] == "success"
        assert result["type"] == "route"
        assert result["result"]["total_distance_km"] > 0
        assert result["result"]["estimated_fuel_cost"] > 0

    def test_process_cost_request(self, agent: GISAgent) -> None:
        """Test processing fuel cost request."""
        query = "what's the fuel cost for 800 km at $2 per liter"
        result = asyncio.run(agent.process_request(query))

        assert result["status"] == "success"
        assert result["type"] == "cost"
        assert result["result"]["estimated_fuel_cost"] > 0

    def test_process_unrecognized_query(self, agent: GISAgent) -> None:
        """Test handling of unrecognized queries."""
        query = "what's the weather today?"
        result = asyncio.run(agent.process_request(query))

        assert result["status"] == "unrecognized"
        assert "examples" in result

    def test_calculate_freight_route(self, agent: GISAgent) -> None:
        """Test freight route calculation."""
        result = asyncio.run(
            agent.calculate_freight_route(
                origin="New York",
                destination="Los Angeles",
                waypoints=["Denver"],
            )
        )

        assert result["status"] == "success"
        assert result["total_distance_km"] > 0
        assert result["travel_hours"] > 0
        assert result["estimated_fuel_cost"] > 0
