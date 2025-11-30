# External Components & Integrations

## Overview

Your GIS MCP Server integrates with several external components and libraries. This document explains each integration, what it's used for, and how to extend or replace them.

---

## Core Dependencies

### 1. **MCP (Model Context Protocol)** `mcp==1.0.0`

**Purpose**: Enable communication with MCP-compliant clients

**Usage in Project**:
- `from mcp.server import Server` - Create MCP server instance
- `from mcp.server.stdio import stdio_server` - Handle stdio transport

**Key Components Used**:
```python
# Server initialization
server = Server("gis-mcp-server")

# Tool registration decorators
@server.list_tools()
@server.call_tool()

# Transport handling
async with stdio_server() as (read_stream, write_stream):
    await server.run(read_stream, write_stream, options)
```

**What It Enables**:
- ✅ Claude integration (Claude Desktop, Claude API with MCP)
- ✅ LangChain agent integration
- ✅ Custom MCP client applications
- ✅ Standardized protocol for tool access

**Documentation**: https://modelcontextprotocol.io

**Alternative**: Could use OpenAI Plugin format or custom REST API (less standardized)

---

### 2. **Geopy** `geopy==2.4.0`

**Purpose**: Calculate geodesic distances between geographic coordinates

**Used For**:
- `DistanceCalculator.calculate_distance()` - Core distance calculations
- `RouteOptimizer.optimize_waypoints()` - Finding nearest waypoints

**Key Function Used**:
```python
from geopy.distance import geodesic

# Calculate distance between two points
distance_km = geodesic((40.7128, -74.0060), (34.0522, -118.2437)).kilometers
```

**Accuracy**:
- Uses Vincenty formula (ellipsoidal model)
- Precision: ~50 meters at Earth's surface
- Handles Earth's curvature and oblateness

**Why Geopy?**:
- ✅ Battle-tested library (15+ years)
- ✅ Handles ellipsoidal calculations correctly
- ✅ Lightweight, no external dependencies
- ✅ Well-documented

**Alternatives**:
- `haversine` - Simpler spherical formula, faster but less accurate
- `OSMnx` - Integrates OpenStreetMap data (more complex)
- Custom implementation - Lower accuracy, no network data

---

### 3. **Pydantic** `pydantic==2.5.0`

**Purpose**: Data validation and serialization

**Usage in Project**:
```python
class DistanceRequest(BaseModel):
    origin: tuple[float, float]
    destination: tuple[float, float]

class DistanceResponse(BaseModel):
    distance_km: float
    origin: tuple[float, float]
    destination: tuple[float, float]
```

**What It Provides**:
- ✅ Type validation (ensures lat/lon are floats)
- ✅ JSON serialization/deserialization
- ✅ Schema generation for MCP tools
- ✅ Error messages for invalid data

**Current Usage**:
- Defined but not actively enforced in tool handlers
- Could be enhanced for stricter input validation

**Future Enhancement**:
```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Any:
    if name == "calculate_distance":
        # Validate with Pydantic
        request = DistanceRequest(**arguments)
        distance = DistanceCalculator.calculate_distance(
            request.origin,
            request.destination
        )
        response = DistanceResponse(
            distance_km=distance,
            origin=request.origin,
            destination=request.destination
        )
        return [{"type": "text", "text": str(response.distance_km)}]
```

---

### 4. **LangChain** `langchain==0.1.0` + `langchain-community==0.0.10`

**Purpose**: NLP capabilities and agent framework

**Current Status**: 
- ✅ Installed and available
- ⚠️ Not actively integrated yet (foundation for GISAgent)

**Potential Integration Points**:
```python
from langchain.agents import Tool, initialize_agent, AgentType
from langchain_community.llms import OpenAI

# Create LangChain tools from GIS functions
tools = [
    Tool(
        name="calculate_distance",
        func=calculate_distance_func,
        description="Calculate distance between two locations"
    ),
    Tool(
        name="optimize_route",
        func=optimize_route_func,
        description="Optimize delivery route"
    )
]

# Initialize agent with LLM
agent = initialize_agent(
    tools,
    OpenAI(),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use natural language
result = agent.run("Find optimal route for NYC to LA with stops in Denver")
```

**Planned Enhancements**:
- Location name resolution (NYC → coordinates)
- Multi-step route planning with conversational interface
- Travel time and cost considerations in natural language

**Documentation**: https://langchain.com

---

### 5. **Python-dotenv** `python-dotenv==1.0.0`

**Purpose**: Load environment variables from `.env` files

**Current Setup**:
- Available but not actively used in current code
- Ready for configuration management

**Potential Usage**:
```python
from dotenv import load_dotenv
import os

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "localhost")
MCP_SERVER_PORT = os.getenv("MCP_SERVER_PORT", "5000")
```

**Why Useful**:
- ✅ Separate configuration from code
- ✅ Support different environments (dev, staging, prod)
- ✅ Secure credential management
- ✅ Easy local development setup

---

### 6. **HTTPX** `httpx==0.25.0`

**Purpose**: Async HTTP client

**Current Status**: 
- ✅ Installed as dependency
- ⚠️ Not currently used

**Potential Usage Scenarios**:
```python
import httpx

async def get_traffic_data(route):
    """Fetch real-time traffic data for route optimization."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.traffic-service.com/route",
            params={"waypoints": route}
        )
        return response.json()

async def get_weather_conditions(coordinates):
    """Fetch weather to adjust route recommendations."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.weather-service.com/forecast",
            params={"lat": coordinates[0], "lon": coordinates[1]}
        )
        return response.json()
```

**Why HTTPX Over Requests?**:
- ✅ Async/await support (better for MCP server)
- ✅ Built on httpcore (more modern)
- ✅ Streaming support
- ✅ Compatible with requests API

---

## Development Dependencies

### Testing & Coverage
- **pytest** `>=7.4.0` - Test framework
- **pytest-cov** `>=4.1.0` - Coverage reporting

### Code Quality
- **black** `>=23.0.0` - Code formatting
- **ruff** `>=0.1.0` - Linting
- **mypy** `>=1.5.0` - Type checking

---

## External GIS Services (Future Integration)

### Option 1: OpenStreetMap + Nominatim

```python
from geopy.geocoders import Nominatim

geocoder = Nominatim(user_agent="gis-mcp-server")

# Convert location name to coordinates
location = geocoder.geocode("New York, USA")
print(f"Coordinates: {location.latitude}, {location.longitude}")

# Reverse geocoding
address = geocoder.reverse((40.7128, -74.0060))
print(f"Address: {address}")
```

**Use Cases**:
- ✅ Convert "New York" → (40.7128, -74.0060)
- ✅ Convert coordinates → Address
- ✅ Free and open source
- ⚠️ Rate-limited (1 request/second)

---

### Option 2: Google Maps API

```python
import googlemaps

gmaps = googlemaps.Client(key='YOUR_API_KEY')

# Distance Matrix for multiple routes
result = gmaps.distance_matrix(
    origins=[(40.7128, -74.0060)],
    destinations=[(34.0522, -118.2437)],
    mode='driving'
)

# Real traffic data
directions = gmaps.directions(
    origin=(40.7128, -74.0060),
    destination=(34.0522, -118.2437),
    alternatives=True
)
```

**Advantages**:
- ✅ Real-time traffic data
- ✅ Multiple route alternatives
- ✅ Turn-by-turn directions
- ⚠️ Costs money
- ⚠️ Rate limits apply

---

### Option 3: OSRM (Open Source Routing Machine)

```python
import requests

def calculate_osrm_distance(waypoints):
    """Use OSRM for accurate routing."""
    coords = ";".join([f"{lon},{lat}" for lat, lon in waypoints])
    url = f"http://router.project-osrm.org/route/v1/driving/{coords}"
    
    response = requests.get(url, params={"overview": "full"})
    data = response.json()
    
    return {
        "distance_meters": data["routes"][0]["distance"],
        "duration_seconds": data["routes"][0]["duration"],
        "geometry": data["routes"][0]["geometry"]
    }
```

**Advantages**:
- ✅ Self-hostable (no API key needed)
- ✅ Accurate routing with real road networks
- ✅ Multiple profiles (driving, walking, cycling)
- ⚠️ Requires running OSRM server

---

## Current Architecture Summary

```
Your GIS MCP Server
├── MCP Protocol Layer
│   └── Uses: mcp library (stdio transport)
│       └── Enables: Claude, LangChain, custom clients
│
├── Distance & Routing Layer
│   └── Uses: geopy.distance.geodesic
│       └── Provides: Accurate Earth distance calculations
│
├── Data Validation Layer
│   └── Uses: pydantic
│       └── Provides: Type checking, serialization
│
├── NLP/Agent Layer (Foundation)
│   └── Uses: langchain (not yet integrated)
│       └── Planned: Natural language query processing
│
├── Configuration
│   └── Uses: python-dotenv (ready to use)
│       └── Planned: Environment-based configuration
│
└── External API Layer (Future)
    ├── HTTP Client: httpx (installed, ready)
    ├── Geolocation: Nominatim/Google/Proprietary
    ├── Traffic: Real-time data providers
    └── Routing: OSRM/Google/Proprietary
```

---

## Integration Recommendations

### Immediate (Current)
- ✅ MCP + Geopy + Pydantic working well
- ✅ Suitable for distance/route calculations
- ✅ Ready for Claude and LangChain agents

### Short-term (1-2 weeks)
- Implement location name → coordinates (Nominatim)
- Integrate LangChain agent for NLP
- Add Pydantic validation to tool handlers
- Environment configuration with python-dotenv

### Medium-term (1-2 months)
- Real-time traffic integration (Google/OSRM)
- Weather-based route recommendations
- Fuel price API integration
- Caching layer (Redis)

### Long-term (3+ months)
- Custom ML model for route optimization
- Advanced algorithms (Genetic Algorithm, ACO)
- Multi-modal transport planning
- Integration with logistics platforms

---

## Component Dependency Graph

```
external_clients (Claude, LangChain, etc.)
        ↓
    MCP Server
        ↓
GISMCPServer (server.py)
    ↓         ↓
Distance    Route
Calculator  Optimizer
    ↓         ↓
  Geopy ← Shared dependency
    ↓
Vincenty Algorithm
    ↓
Earth Model
```

---

## How to Replace Components

### Replace Geopy with Haversine

```python
# Old
from geopy.distance import geodesic
distance = geodesic(origin, destination).kilometers

# New
from haversine import haversine
distance = haversine(origin, destination, unit='km')
```

**Trade-offs**: 
- Faster but less accurate
- No ellipsoidal model
- Good for approximate calculations

### Replace MCP with REST API

```python
# Instead of MCP stdio server
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/tools/calculate_distance")
async def api_calculate_distance(origin: list, destination: list):
    distance = DistanceCalculator.calculate_distance(
        tuple(origin),
        tuple(destination)
    )
    return {"distance_km": distance}

# Run with: uvicorn server:app --reload
```

**Trade-offs**:
- Easier for web integration
- Less standardized
- Requires API management

### Replace LangChain with Simpler NLP

```python
# Simple pattern matching instead of LangChain
def parse_distance_query(query: str):
    """Parse 'distance from A to B' queries."""
    import re
    match = re.search(r'distance from (.+) to (.+)', query, re.IGNORECASE)
    if match:
        return {
            "action": "calculate_distance",
            "origin": match.group(1),
            "destination": match.group(2)
        }
```

**Trade-offs**:
- Simpler, fewer dependencies
- Limited to predefined patterns
- Not truly NLP-based

---

## Monitoring External Dependencies

### Check for Updates

```bash
# Check outdated packages
pip list --outdated

# Update specific package
pip install --upgrade geopy

# Update all
pip install --upgrade -r requirements.txt
```

### Dependency Health

```bash
# Check for security vulnerabilities
pip install safety
safety check

# Generate requirements from code
pip install pipreqs
pipreqs --force src/
```

---

## Conclusion

Your GIS MCP Server has a clean, modular architecture with:
- **Core**: MCP + Geopy (working well)
- **Extensible**: LangChain ready, HTTPX for APIs
- **Maintainable**: Pydantic for validation, python-dotenv for config

The design allows easy replacement or addition of external components as your requirements grow.
