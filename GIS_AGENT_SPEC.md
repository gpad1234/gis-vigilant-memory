# GIS Agent Specification

## Overview

The GIS Agent is a natural language processing interface for freight optimization queries. It parses unstructured NLP requests and translates them into structured GIS operations (distance calculations, route optimization, fuel cost estimation).

## Architecture

```
Natural Language Query
        ↓
[GISAgent.process_request()]
        ↓
    ┌─────┬──────┬─────────┐
    ↓     ↓      ↓         ↓
Distance Route  Cost   Unrecognized
    ↓     ↓      ↓         ↓
Result  Result  Result  Suggestion
```

## Query Types

### 1. Distance Queries

**Purpose**: Calculate distance and travel time between two locations

**Pattern Recognition**:
- "distance from {origin} to {destination}"
- "how far is it from {origin} to {destination}"
- "calculate distance between {origin} and {destination}"

**Examples**:
```
"What's the distance from New York to Los Angeles?"
"How far is it from NYC to LA?"
"Calculate distance between Denver and Seattle"
```

**Response**:
```json
{
  "status": "success",
  "type": "distance",
  "query": "What's the distance from New York to Los Angeles?",
  "result": {
    "from": "New York",
    "to": "Los Angeles",
    "distance_km": 3944.05,
    "travel_hours": 49.3,
    "explanation": "The distance from New York to Los Angeles is 3944.05 km, which takes approximately 49.3 hours at 80 km/h."
  }
}
```

### 2. Route Optimization Queries

**Purpose**: Optimize route visiting multiple stops using nearest-neighbor algorithm

**Pattern Recognition**:
- "optimize a route with stops in {stop1}, {stop2}, {stop3}"
- "find the best route visiting {stop1}, {stop2}, {stop3}"
- "plan a route through {stop1}, {stop2}, {stop3}"

**Examples**:
```
"Optimize a route with stops in NYC, Denver, and LA"
"Find the best route visiting New York, Chicago, and Los Angeles"
"Plan a route through San Francisco, Las Vegas, and Los Angeles"
```

**Response**:
```json
{
  "status": "success",
  "type": "route",
  "query": "Optimize a route with stops in NYC, Denver, and LA",
  "result": {
    "stops": ["NYC", "Denver", "LA"],
    "total_distance_km": 5234.87,
    "estimated_fuel_cost": 418.79,
    "explanation": "Optimized route through NYC, Denver, LA is 5234.87 km with estimated fuel cost of $418.79."
  }
}
```

### 3. Fuel Cost Queries

**Purpose**: Estimate fuel costs for a given distance with custom parameters

**Pattern Recognition**:
- "what's the fuel cost for {distance} km"
- "estimate fuel cost for a {distance} km route"
- "fuel cost for {distance} km at ${price} per liter"
- "fuel cost for {distance} km with {efficiency} km/liter efficiency"

**Examples**:
```
"What's the fuel cost for 500 km?"
"Estimate fuel cost for a 1000 km route"
"How much fuel costs for 800 km at $2 per liter?"
"Fuel cost for 2000 km at $1.50/L with 8 km/L efficiency"
```

**Response**:
```json
{
  "status": "success",
  "type": "cost",
  "query": "What's the fuel cost for 500 km?",
  "result": {
    "distance_km": 500,
    "fuel_price_per_liter": 1.5,
    "fuel_efficiency_km_per_liter": 8,
    "estimated_fuel_cost": 93.75,
    "explanation": "For a 500 km route at $1.5/L with 8 km/L efficiency, fuel cost is $93.75."
  }
}
```

### 4. Unrecognized Queries

**Response**:
```json
{
  "status": "unrecognized",
  "query": "what time is it",
  "message": "I couldn't understand this query. Try asking about distance, route optimization, or fuel costs.",
  "examples": [
    "How far is it from New York to Los Angeles?",
    "Optimize a route with stops in NYC, Denver, and LA",
    "What's the fuel cost for 500 km at $2 per liter?"
  ]
}
```

## Supported Locations

**18 Major US Cities**:

| Location | Aliases | Coordinates |
|----------|---------|------------|
| New York | NYC | (40.7128, -74.0060) |
| Los Angeles | LA | (34.0522, -118.2437) |
| Denver | - | (39.7392, -104.9903) |
| San Francisco | SF | (37.7749, -122.4194) |
| Chicago | - | (41.8781, -87.6298) |
| Houston | - | (29.7604, -95.3698) |
| Phoenix | - | (33.4484, -112.0742) |
| Philadelphia | - | (39.9526, -75.1652) |
| San Antonio | - | (29.4241, -98.4936) |
| San Diego | - | (32.7157, -117.1611) |
| Dallas | - | (32.7767, -96.7970) |
| Seattle | - | (47.6062, -122.3321) |
| Atlanta | - | (33.7490, -84.3880) |
| Boston | - | (42.3601, -71.0589) |
| Miami | - | (25.7617, -80.1918) |

## API Reference

### `process_request(natural_language_query: str) → dict[str, Any]`

**Purpose**: Main entry point for NLP query processing

**Args**:
- `natural_language_query`: Unstructured natural language request

**Returns**: Result dictionary with status, type, and explanation

**Example**:
```python
agent = GISAgent()
result = await agent.process_request("What's the distance from NYC to LA?")
# Returns distance calculation with travel time
```

### `calculate_freight_route(origin: str, destination: str, waypoints: Optional[list[str]] = None) → dict[str, Any]`

**Purpose**: Structured API for freight route calculation

**Args**:
- `origin`: Starting location name (e.g., "New York")
- `destination`: Ending location name (e.g., "Los Angeles")
- `waypoints`: Optional list of intermediate stops

**Returns**: Route information with distance, travel time, and fuel cost

**Example**:
```python
agent = GISAgent()
result = await agent.calculate_freight_route(
    origin="New York",
    destination="Los Angeles",
    waypoints=["Denver", "Las Vegas"]
)
# Returns optimized route with totals
```

## Internal Methods

### `_resolve_location(location_name: str) → Optional[tuple[float, float]]`

Normalizes location name to (lat, lon) coordinates. Returns None if location not found.

### `_parse_distance_query(query: str) → Optional[dict[str, Any]]`

Regex-based parser for distance queries. Returns parsed dict or None if no match.

### `_parse_route_query(query: str) → Optional[dict[str, Any]]`

Regex-based parser for route queries. Splits by comma or "and", resolves locations.

### `_parse_cost_query(query: str) → Optional[dict[str, Any]]`

Regex-based parser for fuel cost queries. Extracts distance, price, efficiency parameters with defaults:
- Default fuel price: $1.50/liter
- Default fuel efficiency: 8 km/liter

## Assumptions & Defaults

| Parameter | Default | Notes |
|-----------|---------|-------|
| Travel speed | 80 km/h | Used for travel time estimation |
| Fuel price | $1.50/liter | Used if not specified in query |
| Fuel efficiency | 8 km/liter | Used if not specified in query |
| Route algorithm | Nearest-neighbor | Greedy optimization for waypoints |

## Error Handling

All methods return structured responses with `status` field:
- `"success"`: Query processed and result calculated
- `"error"`: Calculation failed (invalid locations, API issues)
- `"unrecognized"`: Query pattern not matched, suggestions provided

## Integration with MCP Server

The GIS Agent is used by the MCP server to provide tool implementations:

1. **MCP Tool**: `calculate_distance`
   - Calls: `GISAgent.process_request()` for distance queries

2. **MCP Tool**: `optimize_route`
   - Calls: `GISAgent.calculate_freight_route()` for multi-stop routes

3. **MCP Tool**: `estimate_fuel_cost`
   - Calls: `GISAgent.process_request()` for fuel cost queries

## Testing

15 comprehensive tests covering:
- Location resolution
- Query parsing (all 3 types)
- Request processing
- Freight route calculation
- Error cases

Run tests: `pytest tests/test_gis_agent.py -v`

## Future Enhancements

1. **Location Database**: Expand from 18 to 1000+ locations
2. **Fuzzy Matching**: Handle misspellings (e.g., "Newyork" → "New York")
3. **Real-time Traffic**: Integrate live traffic API for accurate ETA
4. **Multiple Routing Algorithms**: Allow choice between nearest-neighbor, genetic algorithm, etc.
5. **Multi-language Support**: Parse queries in Spanish, Mandarin, etc.
6. **Custom Waypoint Constraints**: "Avoid highways", "Visit in order", etc.
