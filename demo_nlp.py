#!/usr/bin/env python
"""Demo script for GIS NLP Agent - try natural language queries."""

import asyncio

from src.gis_mcp_server.agents.gis_agent import GISAgent


async def main() -> None:
    """Run interactive NLP demo."""
    agent = GISAgent()

    # Example queries
    example_queries = [
        "distance from New York to Los Angeles",
        "how far is it from NYC to Denver?",
        "optimize a route with stops in NYC, Denver, and LA",
        "what's the fuel cost for 500 km at $2 per liter",
        "estimate fuel cost for 800 km",
        "plan a route through San Francisco, Las Vegas, and Los Angeles",
    ]

    print("=" * 70)
    print("🚛 GIS MCP Server - Natural Language Interface Demo")
    print("=" * 70)

    for query in example_queries:
        print(f"\n📍 Query: {query}")
        print("-" * 70)

        result = await agent.process_request(query)

        if result["status"] == "success":
            print(f"✅ Status: {result['status']}")
            print(f"📊 Type: {result['type']}")
            if "result" in result:
                print("\n📋 Results:")
                for key, value in result["result"].items():
                    if key != "explanation":
                        print(f"   • {key.replace('_', ' ').title()}: {value}")
                print(f"\n💡 {result['result'].get('explanation', '')}")
        else:
            print(f"⚠️  Status: {result['status']}")
            if "message" in result:
                print(f"   Message: {result['message']}")
            if "examples" in result:
                print("\n   Example queries:")
                for ex in result["examples"]:
                    print(f"   - {ex}")

    print("\n" + "=" * 70)
    print("✨ Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
