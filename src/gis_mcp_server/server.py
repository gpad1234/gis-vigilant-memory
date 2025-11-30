"""Main MCP Server implementation for GIS distance calculations.

Simplified pattern based on osquery MCP server best practices.
"""

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult

from .tools.distance_calculator import DistanceCalculator
from .tools.route_optimizer import RouteOptimizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
server = Server("gis-mcp-server")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available GIS tools."""
    return [
        Tool(
            name="calculate_distance",
            description="Calculate geodesic distance between two geographic points",
            inputSchema={
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Origin coordinates [latitude, longitude]",
                    },
                    "destination": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Destination coordinates [latitude, longitude]",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["km", "miles"],
                        "description": "Distance unit",
                        "default": "km",
                    },
                },
                "required": ["origin", "destination"],
            },
        ),
        Tool(
            name="optimize_route",
            description="Optimize route through multiple waypoints using nearest-neighbor algorithm",
            inputSchema={
                "type": "object",
                "properties": {
                    "waypoints": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                        },
                        "description": "List of waypoint coordinates [[lat, lon], ...]",
                    },
                },
                "required": ["waypoints"],
            },
        ),
        Tool(
            name="estimate_fuel_cost",
            description="Estimate fuel cost for a journey",
            inputSchema={
                "type": "object",
                "properties": {
                    "distance_km": {
                        "type": "number",
                        "description": "Distance in kilometers",
                    },
                    "fuel_price_per_liter": {
                        "type": "number",
                        "description": "Fuel price per liter",
                        "default": 1.5,
                    },
                    "fuel_efficiency": {
                        "type": "number",
                        "description": "Fuel efficiency in km/liter",
                        "default": 8.0,
                    },
                },
                "required": ["distance_km"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
    """Call a GIS tool."""
    try:
        if name == "calculate_distance":
            origin = tuple(arguments["origin"])
            destination = tuple(arguments["destination"])
            unit = arguments.get("unit", "km")
            distance = DistanceCalculator.calculate_distance(
                origin, destination, unit
            )
            travel_time = DistanceCalculator.estimate_travel_time(distance)
            result_text = f"Distance: {distance:.2f} {unit}, Travel time: {travel_time.get('hours', 0):.2f} hours"
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)],
                isError=False
            )

        elif name == "optimize_route":
            waypoints = [tuple(wp) for wp in arguments["waypoints"]]
            optimized = RouteOptimizer.optimize_waypoints(waypoints)
            total_distance = DistanceCalculator.calculate_route_distance(optimized)
            result_text = f"Optimized route distance: {total_distance:.2f} km"
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)],
                isError=False
            )

        elif name == "estimate_fuel_cost":
            distance_km = arguments["distance_km"]
            fuel_price = arguments.get("fuel_price_per_liter", 1.5)
            efficiency = arguments.get("fuel_efficiency", 8.0)
            cost = RouteOptimizer.estimate_fuel_cost(
                distance_km, fuel_price, efficiency
            )
            result_text = f"Estimated fuel cost: ${cost:.2f}"
            return CallToolResult(
                content=[TextContent(type="text", text=result_text)],
                isError=False
            )

        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {name}")],
                isError=True
            )

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}", exc_info=True)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            isError=True
        )


async def main() -> None:
    """Run the MCP server."""
    logger.info("Starting GIS MCP Server...")
    async with server:
        logger.info("GIS MCP Server running on stdio")


def get_server():
    """Get the MCP server instance for testing."""
    return server


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted")
