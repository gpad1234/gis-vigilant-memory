# GIS MCP Server Usage Documentation

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd gis-getting-started

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Using the System

You have **two main options**:

#### **Option A: Direct NLP Interface (No Server Needed)** ✅ Fastest
```bash
# Try natural language queries directly
python demo_nlp.py
```
Use this for:
- Testing NLP queries
- Running calculations
- Integration in Python scripts
- No server startup required

#### **Option B: MCP Server (For Client Integration)** 
```bash
# Terminal 1: Start the MCP server
python main.py

# Terminal 2: Connect with client (Claude, LangChain, etc.)
# See MCP Server Usage below
```
Use this for:
- Claude Desktop integration
- LangChain agent connections
- Custom MCP clients
- API wrapper services

### 3. Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/gis_mcp_server --cov-report=html
```

---

## Natural Language Interface (NLP)

### Direct NLP Usage (No Server)

Use the `GISAgent` directly in Python for natural language queries:

```python
import asyncio
from src.gis_mcp_server.agents.gis_agent import GISAgent

async def main():
    agent = GISAgent()
    
    # Ask in natural language
    result = await agent.process_request("distance from NYC to LA")
    print(result)

asyncio.run(main())
```

**Supported Query Types:**

1. **Distance Queries**
   ```python
   "distance from New York to Los Angeles"
   "how far is it from NYC to Denver?"
   "calculate distance between Chicago and Seattle"
   ```

2. **Route Optimization**
   ```python
   "optimize a route with stops in NYC, Denver, and LA"
   "find the best route visiting San Francisco, Las Vegas, and Los Angeles"
   "plan a route through Chicago, Kansas City, and Denver"
   ```

3. **Fuel Cost Estimation**
   ```python
   "what's the fuel cost for 500 km?"
   "estimate fuel cost for 1000 km at $2 per liter"
   "fuel cost for 800 km with efficiency of 6 km/liter"
   ```

**Example Output:**
```json
{
  "status": "success",
  "type": "distance",
  "query": "distance from New York to Los Angeles",
  "result": {
    "from": "New York",
    "to": "Los Angeles",
    "distance_km": 3944.42,
    "travel_hours": 49.31,
    "explanation": "The distance from New York to Los Angeles is 3944.42 km, which takes approximately 49.3 hours at 80 km/h."
  }
}
```

**See also:** [NLP_INTERFACE.md](NLP_INTERFACE.md) for comprehensive NLP documentation.

---

## MCP Server Usage

### Starting the Server

```bash
python main.py
```

The server initializes and waits for MCP client connections via stdio.

**Output:**
```
2025-11-30 12:04:23,565 - src.gis_mcp_server.server - INFO - Registering MCP tools...
2025-11-30 12:04:23,565 - src.gis_mcp_server.server - INFO - GIS MCP Server initialized
2025-11-30 12:04:23,565 - src.gis_mcp_server.server - INFO - Starting GIS MCP Server...
```

### MCP Tools Available

Once running, the server exposes 3 tools:

1. **calculate_distance** - Distance between two points
2. **optimize_route** - Route optimization with waypoints
3. **estimate_fuel_cost** - Fuel cost calculation

### Using with Claude Desktop

1. **Configure Claude:**

Edit `~/.claude_config/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "gis": {
      "command": "python",
      "args": ["/path/to/gis-getting-started/main.py"]
    }
  }
}
```

2. **Restart Claude Desktop**

3. **Use in conversations:**
```
User: "What's the distance from New York to Los Angeles?"
Claude: [Calls calculate_distance tool]
"The distance is approximately 3,944 km..."

User: "Optimize a route with stops in NYC, Denver, and LA"
Claude: [Calls optimize_route tool]
"The optimized route would be..."
```

### Using with LangChain

```python
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_community.llms import OpenAI
from src.gis_mcp_server.agents.gis_agent import GISAgent
import asyncio

# Create agent
gis_agent = GISAgent()

# Create LangChain tools
tools = [
    Tool(
        name="calculate_distance",
        func=lambda query: asyncio.run(gis_agent.process_request(query)),
        description="Calculate distance between cities using natural language"
    ),
    Tool(
        name="optimize_route",
        func=lambda waypoints: asyncio.run(
            gis_agent.calculate_freight_route(waypoints[0], waypoints[-1], waypoints[1:-1])
        ),
        description="Optimize freight delivery routes"
    )
]

# Initialize agent
llm = OpenAI(temperature=0)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use it
result = agent.run(
    "I need to ship from NYC to LA with stops in Denver and Phoenix. "
    "What's the distance and fuel cost?"
)
print(result)
```

### Using with Custom MCP Client

```python
import asyncio
import json
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def query_gis_server():
    """Connect to GIS MCP server and call tools."""
    
    # Connect via stdio
    async with stdio_client("python", ["main.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools]}")
            
            # Call calculate_distance
            result = await session.call_tool(
                "calculate_distance",
                {
                    "origin": [40.7128, -74.0060],      # NYC
                    "destination": [34.0522, -118.2437],  # LA
                    "unit": "km"
                }
            )
            print(f"Distance result: {result}")
            
            # Call optimize_route
            result = await session.call_tool(
                "optimize_route",
                {
                    "waypoints": [
                        [40.7128, -74.0060],      # NYC
                        [39.7392, -104.9903],     # Denver
                        [34.0522, -118.2437]      # LA
                    ]
                }
            )
            print(f"Optimized route: {result}")
            
            # Call estimate_fuel_cost
            result = await session.call_tool(
                "estimate_fuel_cost",
                {
                    "distance_km": 1000,
                    "fuel_price_per_liter": 2.0,
                    "fuel_efficiency": 7.5
                }
            )
            print(f"Fuel cost: {result}")

asyncio.run(query_gis_server())
```

### Using with REST API Wrapper

```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.gis_mcp_server.tools.distance_calculator import DistanceCalculator
from src.gis_mcp_server.tools.route_optimizer import RouteOptimizer
import asyncio

app = FastAPI(title="GIS API")

@app.post("/api/distance")
async def api_distance(
    origin: list[float],
    destination: list[float],
    unit: str = "km"
):
    """Calculate distance via REST API."""
    distance = DistanceCalculator.calculate_distance(
        tuple(origin),
        tuple(destination),
        unit
    )
    return {
        "origin": origin,
        "destination": destination,
        "distance": distance,
        "unit": unit
    }

@app.post("/api/route/optimize")
async def api_optimize_route(waypoints: list[list[float]]):
    """Optimize route via REST API."""
    waypoints_tuples = [tuple(wp) for wp in waypoints]
    optimized = RouteOptimizer.optimize_waypoints(waypoints_tuples)
    total_distance = DistanceCalculator.calculate_route_distance(optimized)
    
    return {
        "original_waypoints": waypoints,
        "optimized_waypoints": [list(wp) for wp in optimized],
        "total_distance_km": total_distance
    }

@app.post("/api/fuel-cost")
async def api_fuel_cost(
    distance_km: float,
    fuel_price_per_liter: float = 1.5,
    fuel_efficiency: float = 8
):
    """Estimate fuel cost via REST API."""
    cost = RouteOptimizer.estimate_fuel_cost(
        distance_km,
        fuel_price_per_liter,
        fuel_efficiency
    )
    return {
        "distance_km": distance_km,
        "fuel_price_per_liter": fuel_price_per_liter,
        "fuel_efficiency": fuel_efficiency,
        "estimated_cost": cost
    }

# Run with: uvicorn app:app --reload
```

Then use the API:
```bash
# Calculate distance
curl -X POST http://localhost:8000/api/distance \
  -H "Content-Type: application/json" \
  -d '{"origin": [40.7128, -74.0060], "destination": [34.0522, -118.2437]}'

# Optimize route
curl -X POST http://localhost:8000/api/route/optimize \
  -H "Content-Type: application/json" \
  -d '{"waypoints": [[40.7128, -74.0060], [39.7392, -104.9903], [34.0522, -118.2437]]}'

# Fuel cost
curl -X POST http://localhost:8000/api/fuel-cost \
  -H "Content-Type: application/json" \
  -d '{"distance_km": 500, "fuel_price_per_liter": 2.0, "fuel_efficiency": 8}'
```

---

## Testing the MCP Server

### Method 1: Interactive Testing (Easiest)

**Terminal 1 - Start Server:**
```bash
python main.py
```

**Terminal 2 - Run Test Client:**
```bash
python -c "
import asyncio
import json
from mcp.client.stdio import stdio_client
from mcp import ClientSession

async def test():
    async with stdio_client('python', ['main.py']) as (read, write):
        async with ClientSession(read, write) as session:
            # List tools
            tools = await session.list_tools()
            print('✅ Tools available:')
            for t in tools:
                print(f'   - {t.name}')
            
            # Test distance tool
            print('\n📍 Testing calculate_distance...')
            result = await session.call_tool('calculate_distance', {
                'origin': [40.7128, -74.0060],
                'destination': [34.0522, -118.2437],
                'unit': 'km'
            })
            print(f'   Result: {result}')
            
            # Test optimize route
            print('\n🛣️  Testing optimize_route...')
            result = await session.call_tool('optimize_route', {
                'waypoints': [
                    [40.7128, -74.0060],
                    [39.7392, -104.9903],
                    [34.0522, -118.2437]
                ]
            })
            print(f'   Result: {result}')
            
            # Test fuel cost
            print('\n⛽ Testing estimate_fuel_cost...')
            result = await session.call_tool('estimate_fuel_cost', {
                'distance_km': 1000,
                'fuel_price_per_liter': 2.0,
                'fuel_efficiency': 8
            })
            print(f'   Result: {result}')

asyncio.run(test())
"
```

Expected output:
```
✅ Tools available:
   - calculate_distance
   - optimize_route
   - estimate_fuel_cost

📍 Testing calculate_distance...
   Result: {'distance_km': 3944.42, 'travel_hours': 49.31}

🛣️  Testing optimize_route...
   Result: {'optimized_waypoints': [...], 'total_distance_km': 5616.95}

⛽ Testing estimate_fuel_cost...
   Result: {'estimated_cost': 250.0}
```

### Method 2: Create a Test Script

Create `test_mcp_server.py`:

```python
#!/usr/bin/env python3
"""Test script for MCP GIS Server."""

import asyncio
import json
from mcp.client.stdio import stdio_client
from mcp import ClientSession

async def test_mcp_server():
    """Connect to MCP server and test all tools."""
    print("🚀 Connecting to MCP GIS Server...\n")
    
    try:
        async with stdio_client("python", ["main.py"]) as (read, write):
            async with ClientSession(read, write) as session:
                
                # Test 1: List tools
                print("=" * 50)
                print("TEST 1: List Available Tools")
                print("=" * 50)
                tools = await session.list_tools()
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   • {tool.name}: {tool.description}")
                
                # Test 2: Distance calculation
                print("\n" + "=" * 50)
                print("TEST 2: Calculate Distance (NYC → LA)")
                print("=" * 50)
                result = await session.call_tool(
                    "calculate_distance",
                    {
                        "origin": [40.7128, -74.0060],      # NYC
                        "destination": [34.0522, -118.2437], # LA
                        "unit": "km"
                    }
                )
                print(json.dumps(result, indent=2))
                
                # Test 3: Route optimization
                print("\n" + "=" * 50)
                print("TEST 3: Optimize Route (NYC → Denver → LA)")
                print("=" * 50)
                result = await session.call_tool(
                    "optimize_route",
                    {
                        "waypoints": [
                            [40.7128, -74.0060],      # NYC
                            [39.7392, -104.9903],     # Denver
                            [34.0522, -118.2437]      # LA
                        ]
                    }
                )
                print(json.dumps(result, indent=2))
                
                # Test 4: Fuel cost estimation
                print("\n" + "=" * 50)
                print("TEST 4: Estimate Fuel Cost (1000 km)")
                print("=" * 50)
                result = await session.call_tool(
                    "estimate_fuel_cost",
                    {
                        "distance_km": 1000,
                        "fuel_price_per_liter": 2.5,
                        "fuel_efficiency": 7.5
                    }
                )
                print(json.dumps(result, indent=2))
                
                # Test 5: Multiple waypoints
                print("\n" + "=" * 50)
                print("TEST 5: Complex Route (5 cities)")
                print("=" * 50)
                result = await session.call_tool(
                    "optimize_route",
                    {
                        "waypoints": [
                            [40.7128, -74.0060],      # NYC
                            [41.8781, -87.6298],      # Chicago
                            [39.7392, -104.9903],     # Denver
                            [33.7490, -84.3880],      # Atlanta
                            [34.0522, -118.2437]      # LA
                        ]
                    }
                )
                print(json.dumps(result, indent=2))
                
                print("\n✅ All tests completed successfully!")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
```

Run it:
```bash
# Terminal 1
python main.py

# Terminal 2
python test_mcp_server.py
```

### Method 3: Using pytest with MCP

Create `tests/test_mcp_server.py`:

```python
"""Tests for MCP server functionality."""

import pytest
import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession

@pytest.fixture
async def mcp_session():
    """Connect to MCP server for tests."""
    async with stdio_client("python", ["main.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            yield session

def test_list_tools():
    """Test listing available MCP tools."""
    async def run():
        async with stdio_client("python", ["main.py"]) as (read, write):
            async with ClientSession(read, write) as session:
                tools = await session.list_tools()
                assert len(tools) == 3
                tool_names = {t.name for t in tools}
                assert tool_names == {
                    "calculate_distance",
                    "optimize_route", 
                    "estimate_fuel_cost"
                }
    
    asyncio.run(run())

def test_calculate_distance():
    """Test distance calculation via MCP."""
    async def run():
        async with stdio_client("python", ["main.py"]) as (read, write):
            async with ClientSession(read, write) as session:
                result = await session.call_tool(
                    "calculate_distance",
                    {
                        "origin": [40.7128, -74.0060],
                        "destination": [34.0522, -118.2437],
                        "unit": "km"
                    }
                )
                assert "distance_km" in result
                assert result["distance_km"] > 3900
                assert result["distance_km"] < 4000
    
    asyncio.run(run())

def test_optimize_route():
    """Test route optimization via MCP."""
    async def run():
        async with stdio_client("python", ["main.py"]) as (read, write):
            async with ClientSession(read, write) as session:
                result = await session.call_tool(
                    "optimize_route",
                    {
                        "waypoints": [
                            [40.7128, -74.0060],
                            [39.7392, -104.9903],
                            [34.0522, -118.2437]
                        ]
                    }
                )
                assert "total_distance_km" in result
                assert "optimized_waypoints" in result
    
    asyncio.run(run())

def test_fuel_cost():
    """Test fuel cost estimation via MCP."""
    async def run():
        async with stdio_client("python", ["main.py"]) as (read, write):
            async with ClientSession(read, write) as session:
                result = await session.call_tool(
                    "estimate_fuel_cost",
                    {
                        "distance_km": 1000,
                        "fuel_price_per_liter": 2.0,
                        "fuel_efficiency": 8
                    }
                )
                assert "estimated_cost" in result
                assert result["estimated_cost"] == 250.0
    
    asyncio.run(run())
```

Run tests:
```bash
pytest tests/test_mcp_server.py -v
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection refused" | Make sure `python main.py` is running in another terminal |
| "Tool not found" | Verify tool name is correct (case-sensitive) |
| "Invalid parameters" | Check parameter names and types match the schema |
| Server crashes | Check logs in server terminal for error messages |

---

## API Reference

### Tool: `calculate_distance`

Calculate the geodesic distance between two geographic coordinates.

**Input Schema:**
```json
{
  "origin": [latitude, longitude],
  "destination": [latitude, longitude],
  "unit": "km" | "miles" (optional, default: "km")
}
```

**Example Request:**
```python
from src.gis_mcp_server.tools.distance_calculator import DistanceCalculator

# New York to Los Angeles
nyc = (40.7128, -74.0060)
la = (34.0522, -118.2437)

distance = DistanceCalculator.calculate_distance(nyc, la, unit="km")
print(f"Distance: {distance:.2f} km")
# Output: Distance: 3944.23 km
```

**Via MCP Protocol:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "calculate_distance",
    "arguments": {
      "origin": [40.7128, -74.0060],
      "destination": [34.0522, -118.2437],
      "unit": "km"
    }
  }
}
```

**Output:**
```json
{
  "type": "text",
  "text": "Distance: 3944.23 km"
}
```

**Use Cases:**
- Freight distance estimation
- Route planning validation
- Cost per kilometer calculations
- Geographic proximity checks

---

### Tool: `optimize_route`

Optimize waypoint order using a nearest-neighbor algorithm to minimize travel distance.

**Input Schema:**
```json
{
  "waypoints": [
    [latitude, longitude],
    [latitude, longitude],
    ...
  ]
}
```

**Example Request:**
```python
from src.gis_mcp_server.tools.route_optimizer import RouteOptimizer

waypoints = [
    (40.7128, -74.0060),   # New York
    (39.7392, -104.9903),  # Denver
    (34.0522, -118.2437),  # Los Angeles
    (47.6062, -122.3321),  # Seattle
]

optimized = RouteOptimizer.optimize_waypoints(waypoints, start_index=0)
print(f"Optimized route: {optimized}")
```

**Via MCP Protocol:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "optimize_route",
    "arguments": {
      "waypoints": [
        [40.7128, -74.0060],
        [39.7392, -104.9903],
        [34.0522, -118.2437],
        [47.6062, -122.3321]
      ]
    }
  }
}
```

**Output:**
```json
{
  "type": "text",
  "text": "Optimized route: [(40.7128, -74.0060), (39.7392, -104.9903), (34.0522, -118.2437), (47.6062, -122.3321)]"
}
```

**Algorithm Notes:**
- Uses nearest-neighbor heuristic
- Time complexity: O(n²) where n = waypoints
- Not guaranteed to be globally optimal
- Good for small-to-medium sized problems (< 1000 waypoints)
- Greedy approach: locally optimal choices don't guarantee global optimum

**Use Cases:**
- Delivery route optimization
- Multi-stop freight routes
- Traveling salesman approximation
- Tour planning

---

### Tool: `estimate_fuel_cost`

Estimate fuel consumption and cost for a route based on distance and vehicle efficiency.

**Input Schema:**
```json
{
  "distance_km": number,
  "fuel_price_per_liter": number (optional, default: 1.5),
  "fuel_efficiency": number (optional, default: 8, in km/liter)
}
```

**Example Request:**
```python
from src.gis_mcp_server.tools.route_optimizer import RouteOptimizer

# 800 km route with truck efficiency
cost = RouteOptimizer.estimate_fuel_cost(
    distance_km=800,
    fuel_price_per_liter=1.75,
    fuel_efficiency=6.5  # Heavy truck
)
print(f"Estimated fuel cost: ${cost:.2f}")
# Output: Estimated fuel cost: $192.31
```

**Via MCP Protocol:**
```json
{
  "method": "tools/call",
  "params": {
    "name": "estimate_fuel_cost",
    "arguments": {
      "distance_km": 800,
      "fuel_price_per_liter": 1.75,
      "fuel_efficiency": 6.5
    }
  }
}
```

**Output:**
```json
{
  "type": "text",
  "text": "Estimated fuel cost: $192.31"
}
```

**Fuel Efficiency Reference:**
```
Vehicle Type          Efficiency (km/liter)
─────────────────────────────────────────
Passenger Car         10-15 km/L
Van                   8-12 km/L
Light Truck           6-8 km/L
Heavy Truck           4-6 km/L
Semi-Truck            5-7 km/L
Electric Truck        3-5 km/kWh equivalent
```

**Use Cases:**
- Route cost estimation
- Budget planning for freight
- Fuel surcharge calculations
- Vehicle economics analysis

---

## Python Direct Integration

### Basic Usage

```python
from src.gis_mcp_server.tools.distance_calculator import DistanceCalculator
from src.gis_mcp_server.tools.route_optimizer import RouteOptimizer

# Calculate distance
distance = DistanceCalculator.calculate_distance(
    origin=(40.7128, -74.0060),
    destination=(34.0522, -118.2437),
    unit="km"
)

# Calculate route distance
waypoints = [
    (40.7128, -74.0060),   # NYC
    (39.7392, -104.9903),  # Denver
    (34.0522, -118.2437),  # LA
]
route_distance = DistanceCalculator.calculate_route_distance(waypoints)

# Estimate travel time
travel_time = DistanceCalculator.estimate_travel_time(
    distance_km=1000,
    avg_speed_kmh=100
)

# Optimize waypoints
optimized = RouteOptimizer.optimize_waypoints(waypoints)

# Estimate fuel cost
fuel_cost = RouteOptimizer.estimate_fuel_cost(
    distance_km=route_distance,
    fuel_price_per_liter=2.0,
    fuel_efficiency=7.5
)
```

### Server Integration

```python
from src.gis_mcp_server import GISMCPServer
import asyncio

async def main():
    server = GISMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## MCP Client Integration

### Using Claude with MCP

Configure Claude desktop to use the GIS MCP server:

**~/.claude_config/claude_desktop_config.json:**
```json
{
  "mcpServers": {
    "gis": {
      "command": "python",
      "args": ["/path/to/gis-getting-started/main.py"]
    }
  }
}
```

Then Claude can use GIS tools in conversations:
```
User: "What's the distance from NYC to LA?"
Claude: [Uses calculate_distance tool]
"The distance from New York to Los Angeles is approximately 3,944 km."

User: "Optimize a route with stops in NYC, Denver, and LA"
Claude: [Uses optimize_route tool]
"The optimized route sequence is..."
```

### Using with LangChain

```python
from langchain.agents import Tool, AgentExecutor, initialize_agent, AgentType
from langchain_community.llms import OpenAI
from src.gis_mcp_server.tools.distance_calculator import DistanceCalculator
from src.gis_mcp_server.tools.route_optimizer import RouteOptimizer

# Define tools
distance_tool = Tool(
    name="calculate_distance",
    func=lambda origin, destination, unit="km": 
        DistanceCalculator.calculate_distance(origin, destination, unit),
    description="Calculate distance between two geographic points"
)

optimize_tool = Tool(
    name="optimize_route",
    func=lambda waypoints: 
        RouteOptimizer.optimize_waypoints(waypoints),
    description="Optimize waypoint order for efficient route"
)

# Create agent
tools = [distance_tool, optimize_tool]
llm = OpenAI(temperature=0)
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use agent
result = agent.run("Find the distance from NYC to LA and optimize a route with 3 stops")
print(result)
```

### Custom MCP Client

```python
import asyncio
import json
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def main():
    # Connect to server
    async with stdio_client("python", ["main.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools])
            
            # Call calculate_distance
            result = await session.call_tool(
                "calculate_distance",
                {
                    "origin": [40.7128, -74.0060],
                    "destination": [34.0522, -118.2437],
                    "unit": "km"
                }
            )
            print("Distance result:", result)

asyncio.run(main())
```

---

## Advanced Usage Examples

### Multi-Stop Freight Route Planning

```python
from src.gis_mcp_server.tools.distance_calculator import DistanceCalculator
from src.gis_mcp_server.tools.route_optimizer import RouteOptimizer

# Define pickup/delivery locations
locations = {
    "warehouse": (40.7128, -74.0060),      # NYC warehouse
    "customer_a": (39.7392, -104.9903),    # Denver customer
    "customer_b": (34.0522, -118.2437),    # LA customer
    "customer_c": (37.7749, -122.4194),    # SF customer
}

waypoints = list(locations.values())

# Optimize route
optimized = RouteOptimizer.optimize_waypoints(waypoints)

# Calculate total distance
total_distance = DistanceCalculator.calculate_route_distance(optimized)

# Estimate travel time (assume 70 km/h average due to traffic)
travel_time = DistanceCalculator.estimate_travel_time(total_distance, avg_speed_kmh=70)

# Calculate fuel cost
fuel_cost = RouteOptimizer.estimate_fuel_cost(
    distance_km=total_distance,
    fuel_price_per_liter=2.50,
    fuel_efficiency=6.0
)

print(f"Total distance: {total_distance:.2f} km")
print(f"Travel time: {travel_time['hours']:.1f} hours")
print(f"Fuel cost: ${fuel_cost:.2f}")
```

### Comparing Route Alternatives

```python
# Route 1: Direct path
route1 = [
    (40.7128, -74.0060),   # NYC
    (34.0522, -118.2437),  # LA
]
distance1 = DistanceCalculator.calculate_route_distance(route1)

# Route 2: Via Denver
route2 = [
    (40.7128, -74.0060),   # NYC
    (39.7392, -104.9903),  # Denver
    (34.0522, -118.2437),  # LA
]
distance2 = DistanceCalculator.calculate_route_distance(route2)

# Route 3: Optimized multi-stop
waypoints = [
    (40.7128, -74.0060),   # NYC
    (39.7392, -104.9903),  # Denver
    (34.0522, -118.2437),  # LA
    (37.7749, -122.4194),  # SF
]
optimized = RouteOptimizer.optimize_waypoints(waypoints)
distance3 = DistanceCalculator.calculate_route_distance(optimized)

print(f"Direct NYC→LA: {distance1:.0f} km")
print(f"Via Denver: {distance2:.0f} km")
print(f"Optimized 4-stop: {distance3:.0f} km")
```

### Dynamic Pricing Based on Distance

```python
def calculate_freight_price(distance_km, base_rate=50, per_km_rate=0.75):
    """Calculate shipping price based on distance"""
    return base_rate + (distance_km * per_km_rate)

# Example freight pricing
origin = (40.7128, -74.0060)  # NYC
destination = (34.0522, -118.2437)  # LA

distance = DistanceCalculator.calculate_distance(origin, destination)
price = calculate_freight_price(distance)

print(f"Distance: {distance:.2f} km")
print(f"Freight price: ${price:.2f}")
```

---

## Configuration & Customization

### Environment Variables

Create `.env` file:
```bash
LOG_LEVEL=INFO
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=5000
```

### Custom Defaults

Modify in code:
```python
# Distance calculator defaults
DEFAULT_SPEED_KMH = 80

# Route optimizer defaults
DEFAULT_FUEL_PRICE = 1.50  # USD per liter
DEFAULT_FUEL_EFFICIENCY = 8  # km/liter
```

### Adding Custom Tools

```python
# In server.py, add to _register_tools()

@self.server.list_tools()
async def list_tools() -> list[dict[str, Any]]:
    tools = [...]  # existing tools
    
    # Add custom tool
    tools.append({
        "name": "calculate_toll",
        "description": "Calculate toll charges based on distance",
        "inputSchema": {
            "type": "object",
            "properties": {
                "distance_km": {"type": "number"},
                "vehicle_class": {"type": "string"}
            },
            "required": ["distance_km"]
        }
    })
    return tools

@self.server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Any:
    # ... existing handlers ...
    
    elif name == "calculate_toll":
        distance = arguments["distance_km"]
        vehicle_class = arguments.get("vehicle_class", "standard")
        toll = calculate_toll(distance, vehicle_class)
        return [{"type": "text", "text": f"Toll: ${toll:.2f}"}]
```

---

## Troubleshooting

### Server Won't Start
```
Error: "No module named 'mcp'"
Solution: pip install mcp
```

### Distance Results Seem Off
```
Check: Are coordinates in (latitude, longitude) format?
Remember: latitude ranges -90 to 90, longitude ranges -180 to 180
NYC is (40.7128, -74.0060), not (-74.0060, 40.7128)
```

### Route Optimization Too Slow
```
For >1000 waypoints:
- Use approximate algorithm or smaller batches
- Consider pre-filtering nearby waypoints
- Implement spatial indexing (KD-tree)
```

### MCP Client Connection Issues
```
Verify: Server is running (python main.py)
Check: Server uses stdio transport (not network)
Test: python -m pytest tests/
```

---

## Performance Tips

1. **Batch Operations**: Process multiple routes together
2. **Caching**: Cache frequently used distance calculations
3. **Limiting Waypoints**: Keep optimized routes under 100 waypoints for speed
4. **Lazy Evaluation**: Calculate only needed metrics

---

## Contributing

To add new features:

1. Add tool logic to `tools/` directory
2. Register tool in `server.py` _register_tools()
3. Add tests in `tests/`
4. Update documentation

---

## License

MIT License - see LICENSE file
