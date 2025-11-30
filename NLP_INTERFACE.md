# NLP Interface Guide

## Overview

The GIS MCP Server now includes a **Natural Language Processing (NLP) interface** via the `GISAgent` class. This allows users to interact with GIS tools using natural language queries instead of structured API calls.

## Quick Start

### Basic Usage

```python
import asyncio
from src.gis_mcp_server.agents.gis_agent import GISAgent

async def main():
    agent = GISAgent()
    
    # Ask natural language questions
    result = await agent.process_request(
        "distance from New York to Los Angeles"
    )
    print(result)

asyncio.run(main())
```

### Output Example

```json
{
  "status": "success",
  "type": "distance",
  "query": "distance from New York to Los Angeles",
  "result": {
    "from": "New York",
    "to": "Los Angeles",
    "distance_km": 3944.23,
    "travel_hours": 49.3,
    "explanation": "The distance from New York to Los Angeles is 3944.23 km, which takes approximately 49.3 hours at 80 km/h."
  }
}
```

---

## Supported Query Types

### 1. Distance Queries

Ask about distances between two locations.

**Query Patterns:**
- "distance from X to Y"
- "how far is it from X to Y"
- "calculate distance between X and Y"
- "what's the distance from X to Y?"

**Examples:**
```python
await agent.process_request("distance from NYC to LA?")
await agent.process_request("how far is it from New York to Denver?")
await agent.process_request("calculate distance between Chicago and Seattle")
```

**Response Includes:**
- Distance in kilometers
- Estimated travel time (at 80 km/h default)
- Natural language explanation

---

### 2. Route Optimization Queries

Ask to optimize routes with multiple stops.

**Query Patterns:**
- "optimize a route with stops in X, Y, and Z"
- "find the best route visiting X, Y, Z"
- "plan a route through X, Y, Z"

**Examples:**
```python
await agent.process_request("optimize a route with stops in NYC, Denver, and LA")
await agent.process_request("find the best route visiting San Francisco, Las Vegas, and Los Angeles")
await agent.process_request("plan a route through Chicago, Kansas City, and Denver")
```

**Response Includes:**
- List of stops in optimized order
- Total distance
- Estimated fuel cost
- Natural language explanation

---

### 3. Fuel Cost Queries

Ask about fuel cost estimation for routes.

**Query Patterns:**
- "fuel cost for X km"
- "what's the fuel cost for X km at $Y per liter"
- "estimate fuel cost for X km"

**Examples:**
```python
await agent.process_request("what's the fuel cost for 500 km?")
await agent.process_request("estimate fuel cost for 1000 km at $2 per liter")
await agent.process_request("fuel cost for 800 km with efficiency of 6 km/liter")
```

**Response Includes:**
- Distance
- Fuel price per liter
- Vehicle efficiency
- Calculated fuel cost
- Natural language explanation

---

## Supported Locations

The NLP agent recognizes the following location names (case-insensitive):

**Major US Cities:**
- New York / NYC
- Los Angeles / LA
- San Francisco / SF
- Denver
- Chicago
- Houston
- Phoenix
- Philadelphia
- San Antonio
- San Diego
- Dallas
- Seattle
- Atlanta
- Boston
- Miami

**Adding More Locations:**

Edit `src/gis_mcp_server/agents/gis_agent.py`:

```python
LOCATION_COORDINATES = {
    "your city": (latitude, longitude),
    "another city": (lat, lon),
    # ... more locations
}
```

---

## Integration Examples

### With LangChain Agents

```python
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_community.llms import OpenAI
from src.gis_mcp_server.agents.gis_agent import GISAgent

agent = GISAgent()
llm = OpenAI(temperature=0)

# Create LangChain tool
gis_tool = Tool(
    name="gis_query",
    func=lambda query: asyncio.run(agent.process_request(query)),
    description="Process natural language GIS queries for distance, route, and fuel calculations"
)

# Create agent
tools = [gis_tool]
react_agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use it
result = react_agent.run(
    "I need to ship from NYC to LA with stops in Denver. What's the distance and cost?"
)
```

### With MCP Client

```python
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def query_nlp():
    async with stdio_client("python", ["main.py"]) as (read, write):
        async with ClientSession(read, write) as session:
            # Call calculate_distance tool
            result = await session.call_tool(
                "calculate_distance",
                {
                    "origin": [40.7128, -74.0060],
                    "destination": [34.0522, -118.2437]
                }
            )
            print(result)

asyncio.run(query_nlp())
```

### REST API Wrapper

```python
from fastapi import FastAPI
from src.gis_mcp_server.agents.gis_agent import GISAgent

app = FastAPI()
agent = GISAgent()

@app.post("/nlp/query")
async def nlp_query(query: str):
    """Process NLP GIS queries via REST API."""
    return await agent.process_request(query)

# Run with: uvicorn app:app --reload
# Then POST to: http://localhost:8000/nlp/query?query=distance%20from%20NYC%20to%20LA
```

---

## Query Parsing Details

### How Distance Queries Work

The agent uses regex patterns to extract location names from natural language:

```python
pattern = r"(?:distance|how\s+far|calculate\s+(?:the\s+)?distance).*?from\s+(.+?)\s+to\s+(.+?)(?:\?|$)"
```

This matches variations like:
- ✅ "distance from X to Y"
- ✅ "how far is it from X to Y"
- ✅ "calculate distance from X to Y?"
- ❌ "the distance" (without explicit keywords)

### How Route Queries Work

Routes are detected by keywords like "optimize", "best", "plan" and parsing stop lists:

```python
pattern = r"(?:optimize|best|plan)\s+(?:a\s+)?route.*?(?:stops|visiting|through)\s+(.+?)(?:\?|$)"
```

This matches:
- ✅ "optimize a route with stops in A, B, and C"
- ✅ "find the best route visiting A, B, C"
- ✅ "plan a route through A, B, C"

Stops are parsed from comma-separated or "and"-separated lists.

### How Cost Queries Work

Cost queries extract numeric values:

```python
distance_pattern = r"(\d+(?:\.\d+)?)\s*km"
price_pattern = r"\$?(\d+(?:\.\d+)?)\s*(?:per\s+)?liter"
efficiency_pattern = r"(\d+(?:\.\d+)?)\s*km/liter"
```

---

## Error Handling

### Unrecognized Queries

If the agent doesn't recognize a query, it returns suggestions:

```python
result = await agent.process_request("what's the weather?")

# Returns:
{
    "status": "unrecognized",
    "query": "what's the weather?",
    "message": "I couldn't understand this query. Try asking about distance, route optimization, or fuel costs.",
    "examples": [
        "How far is it from New York to Los Angeles?",
        "Optimize a route with stops in NYC, Denver, and LA",
        "What's the fuel cost for 500 km at $2 per liter?"
    ]
}
```

### Missing Locations

If a location isn't recognized:

```python
result = await agent.process_request("distance from UnknownCity to LA")

# The query won't match if both locations aren't found
# Returns unrecognized status
```

### Calculation Errors

Any calculation errors are caught and reported:

```python
{
    "status": "error",
    "query": "...",
    "error": "Error message details"
}
```

---

## Advanced Usage

### Custom Route Calculation

```python
result = await agent.calculate_freight_route(
    origin="New York",
    destination="Los Angeles",
    waypoints=["Denver", "Las Vegas", "Phoenix"]
)

print(f"Route distance: {result['total_distance_km']} km")
print(f"Travel time: {result['travel_hours']} hours")
print(f"Fuel cost: ${result['estimated_fuel_cost']}")
```

### Batch Processing

```python
queries = [
    "distance from NYC to LA",
    "optimize a route with stops in NYC, Denver, and LA",
    "fuel cost for 1500 km at $2.50 per liter"
]

results = []
for query in queries:
    result = await agent.process_request(query)
    results.append(result)
```

### Integration with Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

result = await agent.process_request("distance from NYC to LA")

if result["status"] == "success":
    logger.info(f"Success: {result['result']['explanation']}")
else:
    logger.warning(f"Failed to process: {result.get('message')}")
```

---

## Testing the NLP Agent

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run NLP agent tests
pytest tests/test_gis_agent.py -v

# Run with output
pytest tests/test_gis_agent.py -v -s
```

### Manual Testing

```python
import asyncio
from src.gis_mcp_server.agents.gis_agent import GISAgent

async def test_queries():
    agent = GISAgent()
    
    queries = [
        "distance from New York to Los Angeles",
        "optimize a route with stops in NYC, Denver, and LA",
        "what's the fuel cost for 500 km at $2 per liter?",
        "how far is it from Chicago to Seattle?",
    ]
    
    for query in queries:
        print(f"\n📍 Query: {query}")
        result = await agent.process_request(query)
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Result: {result['result']}")

asyncio.run(test_queries())
```

---

## Future Enhancements

### Phase 2: LangChain Full Integration
- Use OpenAI/Claude to parse more natural language variations
- Support complex multi-turn conversations
- Context awareness for follow-up questions

### Phase 3: Real-time Data
- Traffic data integration
- Weather-based routing adjustments
- Dynamic fuel pricing

### Phase 4: Advanced Features
- Location alias support ("The Big Apple" → NYC)
- Unit conversion (miles → km)
- Historical route data
- Driver preferences and constraints

---

## Troubleshooting

### Query Not Recognized
**Problem**: Query returns `"status": "unrecognized"`

**Solution**: 
- Check location names are in `LOCATION_COORDINATES`
- Use explicit keywords like "distance from", "optimize route", "fuel cost"
- Avoid complex phrasing

### Location Not Found
**Problem**: Location name doesn't resolve

**Solution**:
- Add the location to `LOCATION_COORDINATES` in `gis_agent.py`
- Try alternate names (e.g., "NYC" instead of "New York")

### Async Issues
**Problem**: `RuntimeError: no running event loop`

**Solution**:
```python
# Use asyncio.run() for standalone scripts
result = asyncio.run(agent.process_request(query))

# Or use await in async context
async def my_function():
    result = await agent.process_request(query)
```

---

## API Reference

### `GISAgent.process_request()`

```python
async def process_request(self, natural_language_query: str) -> dict[str, Any]
```

**Args:**
- `natural_language_query` (str): Natural language GIS query

**Returns:**
- Dictionary with keys:
  - `status`: "success", "error", or "unrecognized"
  - `type`: "distance", "route", "cost" (if successful)
  - `query`: Original query
  - `result`: Calculated results (if successful)
  - `message` or `error`: Status message/error (if error)

### `GISAgent.calculate_freight_route()`

```python
async def calculate_freight_route(
    self,
    origin: str,
    destination: str,
    waypoints: Optional[list[str]] = None
) -> dict[str, Any]
```

**Args:**
- `origin` (str): Starting location name
- `destination` (str): Ending location name
- `waypoints` (list[str]): Optional intermediate stop names

**Returns:**
- Dictionary with route information including distance, time, and cost

---

## Example Response Structures

### Distance Query Response

```json
{
  "status": "success",
  "type": "distance",
  "query": "distance from New York to Los Angeles",
  "result": {
    "from": "New York",
    "to": "Los Angeles",
    "distance_km": 3944.23,
    "travel_hours": 49.3,
    "explanation": "The distance from New York to Los Angeles is 3944.23 km, which takes approximately 49.3 hours at 80 km/h."
  }
}
```

### Route Optimization Response

```json
{
  "status": "success",
  "type": "route",
  "query": "optimize a route with stops in NYC, Denver, and LA",
  "result": {
    "stops": ["NYC", "Denver", "LA"],
    "total_distance_km": 3156.45,
    "estimated_fuel_cost": 394.56,
    "explanation": "Optimized route through NYC, Denver, LA is 3156.45 km with estimated fuel cost of $394.56."
  }
}
```

### Fuel Cost Response

```json
{
  "status": "success",
  "type": "cost",
  "query": "what's the fuel cost for 500 km at $2 per liter",
  "result": {
    "distance_km": 500,
    "fuel_price_per_liter": 2.0,
    "fuel_efficiency_km_per_liter": 8,
    "estimated_fuel_cost": 125.0,
    "explanation": "For a 500 km route at $2/L with 8 km/L efficiency, fuel cost is $125.00."
  }
}
```
