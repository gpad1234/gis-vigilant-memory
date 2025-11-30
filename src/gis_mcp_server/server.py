"""Main MCP Server implementation for GIS distance calculations."""

import asyncio
import logging
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from pydantic import BaseModel

from .tools.distance_calculator import DistanceCalculator
from .tools.route_optimizer import RouteOptimizer

logger = logging.getLogger(__name__)


class DistanceRequest(BaseModel):
    """Request model for distance calculation."""

    origin: tuple[float, float]  # (latitude, longitude)
    destination: tuple[float, float]  # (latitude, longitude)


class DistanceResponse(BaseModel):
    """Response model for distance calculation."""

    distance_km: float
    origin: tuple[float, float]
    destination: tuple[float, float]


class GISMCPServer:
    """MCP Server for GIS operations and distance calculations."""

    def __init__(self) -> None:
        """Initialize the GIS MCP Server."""
        self.server = Server("gis-mcp-server")
        self._register_tools()
        logger.info("GIS MCP Server initialized")

    def _register_tools(self) -> None:
        """Register MCP tools for distance calculations."""
        logger.info("Registering MCP tools...")

        @self.server.list_tools()
        async def list_tools() -> list[dict[str, Any]]:
            """List available GIS tools."""
            return [
                {
                    "name": "calculate_distance",
                    "description": "Calculate geodesic distance between two geographic points",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "origin": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Origin as [latitude, longitude]",
                            },
                            "destination": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Destination as [latitude, longitude]",
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["km", "miles"],
                                "description": "Distance unit",
                            },
                        },
                        "required": ["origin", "destination"],
                    },
                },
                {
                    "name": "optimize_route",
                    "description": "Optimize waypoints using nearest-neighbor algorithm",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "waypoints": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                },
                                "description": "List of [latitude, longitude] waypoints",
                            },
                        },
                        "required": ["waypoints"],
                    },
                },
                {
                    "name": "estimate_fuel_cost",
                    "description": "Estimate fuel cost for a route",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "distance_km": {
                                "type": "number",
                                "description": "Distance in kilometers",
                            },
                            "fuel_price_per_liter": {
                                "type": "number",
                                "description": "Fuel price per liter",
                            },
                            "fuel_efficiency": {
                                "type": "number",
                                "description": "Vehicle fuel efficiency in km/liter",
                            },
                        },
                        "required": ["distance_km"],
                    },
                },
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any]) -> Any:
            """Call a GIS tool."""
            if name == "calculate_distance":
                origin = tuple(arguments["origin"])
                destination = tuple(arguments["destination"])
                unit = arguments.get("unit", "km")
                distance = DistanceCalculator.calculate_distance(origin, destination, unit)
                return [{"type": "text", "text": f"Distance: {distance:.2f} {unit}"}]

            elif name == "optimize_route":
                waypoints = [tuple(wp) for wp in arguments["waypoints"]]
                optimized = RouteOptimizer.optimize_waypoints(waypoints)
                return [
                    {
                        "type": "text",
                        "text": f"Optimized route: {optimized}",
                    }
                ]

            elif name == "estimate_fuel_cost":
                distance_km = arguments["distance_km"]
                fuel_price = arguments.get("fuel_price_per_liter", 1.5)
                fuel_eff = arguments.get("fuel_efficiency", 8)
                cost = RouteOptimizer.estimate_fuel_cost(
                    distance_km, fuel_price, fuel_eff
                )
                return [
                    {
                        "type": "text",
                        "text": f"Estimated fuel cost: ${cost:.2f}",
                    }
                ]

            else:
                return [{"type": "text", "text": f"Unknown tool: {name}"}]

    def calculate_distance(
        self, origin: tuple[float, float], destination: tuple[float, float]
    ) -> DistanceResponse:
        """
        Calculate distance between two geographic coordinates.

        Args:
            origin: Tuple of (latitude, longitude) for start point
            destination: Tuple of (latitude, longitude) for end point

        Returns:
            DistanceResponse with calculated distance in kilometers
        """
        from geopy.distance import geodesic

        dist = geodesic(origin, destination).kilometers
        return DistanceResponse(distance_km=dist, origin=origin, destination=destination)

    async def run(self) -> None:
        """Run the MCP server using stdio transport."""
        logger.info("Starting GIS MCP Server...")
        async with stdio_server() as (read_stream, write_stream):
            init_options = self.server.create_initialization_options()
            await self.server.run(read_stream, write_stream, init_options)
