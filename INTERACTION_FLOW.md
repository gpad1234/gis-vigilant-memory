# GIS MCP Server Interaction Flow

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER LAYER                                   │
│  (Claude Desktop, IDE, Custom Application, etc.)                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ User Query
                             │ "Distance from NYC to LA?"
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    HOST AGENT CLIENT                                │
│            (Claude / Language Model Integration)                     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────┐         │
│  │ MCP Client                                             │         │
│  │ - Manages protocol communication                       │         │
│  │ - Sends tool calls to server                           │         │
│  │ - Receives results from server                         │         │
│  │ - Maintains context across requests                    │         │
│  └────────────────────────────────────────────────────────┘         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ MCP Protocol (JSON-RPC over stdio)
                             │
                             │ Request:
                             │ {
                             │   "method": "tools/call",
                             │   "params": {
                             │     "name": "calculate_distance",
                             │     "arguments": {
                             │       "origin": [40.7128, -74.0060],
                             │       "destination": [34.0522, -118.2437],
                             │       "unit": "km"
                             │     }
                             │   }
                             │ }
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      GIS MCP SERVER                                  │
│         (Stdio-based MCP Server, Python asyncio)                    │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │ main.py                                                   │       │
│  │ └─ Async event loop                                      │       │
│  │    └─ server_main()                                      │       │
│  └──────────────────────────────────────────────────────────┘       │
│                             │                                       │
│                             ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │ src/gis_mcp_server/server.py                             │       │
│  │ @server.list_tools() decorator                           │       │
│  │ └─ Returns Tool[] with schema                            │       │
│  │                                                           │       │
│  │ @server.call_tool() decorator                            │       │
│  │ ├─ calculate_distance()                                  │       │
│  │ ├─ optimize_route()                                      │       │
│  │ └─ estimate_fuel_cost()                                  │       │
│  └──────────────────────────────────────────────────────────┘       │
│                             │                                       │
│                             ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │ src/gis_mcp_server/agents/gis_agent.py                  │       │
│  │ GISAgent class                                           │       │
│  │ ├─ process_request(query)                                │       │
│  │ │  ├─ _parse_distance_query()                            │       │
│  │ │  ├─ _parse_route_query()                               │       │
│  │ │  └─ _parse_cost_query()                                │       │
│  │ └─ calculate_freight_route()                             │       │
│  │    └─ _resolve_location()                                │       │
│  └──────────────────────────────────────────────────────────┘       │
│                             │                                       │
│                             ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │ src/gis_mcp_server/tools/                                │       │
│  │                                                           │       │
│  │ distance_calculator.py                                   │       │
│  │ ├─ calculate_distance()       [Geopy geodesic]           │       │
│  │ ├─ calculate_route_distance()                            │       │
│  │ └─ estimate_travel_time()     [80 km/h]                  │       │
│  │                                                           │       │
│  │ route_optimizer.py                                       │       │
│  │ ├─ optimize_waypoints()       [Nearest-neighbor]         │       │
│  │ └─ estimate_fuel_cost()       [8 km/L default]           │       │
│  └──────────────────────────────────────────────────────────┘       │
│                             │                                       │
│                             ↓                                       │
│  ┌──────────────────────────────────────────────────────────┐       │
│  │ Results Dictionary                                       │       │
│  │ {                                                         │       │
│  │   "status": "success",                                   │       │
│  │   "type": "distance",                                    │       │
│  │   "result": {                                            │       │
│  │     "distance_km": 3944.05,                              │       │
│  │     "travel_hours": 49.3                                 │       │
│  │   }                                                       │       │
│  │ }                                                         │       │
│  └──────────────────────────────────────────────────────────┘       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ MCP Protocol (JSON-RPC Response over stdio)
                             │
                             │ Response:
                             │ {
                             │   "result": {
                             │     "content": [
                             │       {
                             │         "type": "text",
                             │         "text": "Distance: 3944.05 km"
                             │       }
                             │     ]
                             │   }
                             │ }
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    HOST AGENT CLIENT                                │
│  - Receives result from server                                      │
│  - Integrates result into agent context                             │
│  - Generates natural language response                              │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Natural Language Response
                             │ "The distance from NYC to LA is 3944.05 km,
                             │  which takes approximately 49.3 hours at
                             │  80 km/h."
                             ↓
┌─────────────────────────────────────────────────────────────────────┐
│                         USER LAYER                                   │
│  (Claude Desktop, IDE, Custom Application, etc.)                    │
│  Displays result to user                                            │
└─────────────────────────────────────────────────────────────────────┘
```

## Detailed Interaction Flow

### Scenario 1: Distance Query

```
USER                 CLIENT                   SERVER                 TOOLS
  │                    │                         │                     │
  ├─ "NYC to LA?"      │                         │                     │
  │─────────────────>  │                         │                     │
  │                    ├─ MCP call               │                     │
  │                    │────────────────────>    │                     │
  │                    │                         ├─ Parse query        │
  │                    │                         ├─ GISAgent.process() │
  │                    │                         ├────────────────────>│
  │                    │                         │                     │
  │                    │                         │  _resolve_location()│
  │                    │                         │  _parse_distance()  │
  │                    │                         │                     │
  │                    │                         │  calculate_distance()
  │                    │                         │<────────────────────│
  │                    │                         │                     │
  │                    │                         │  estimate_travel_time
  │                    │                         │<────────────────────│
  │                    │                         │                     │
  │                    │  MCP result            │                     │
  │                    │<────────────────────    │                     │
  │  "3944 km,         │                         │                     │
  │   49 hours"        │                         │                     │
  │<─────────────────  │                         │                     │
```

### Scenario 2: Route Optimization Query

```
USER                 CLIENT                   SERVER                 TOOLS
  │                    │                         │                     │
  ├─ "Route: NYC,      │                         │                     │
  │   Denver, LA"      │                         │                     │
  │─────────────────>  │                         │                     │
  │                    ├─ MCP call               │                     │
  │                    │────────────────────>    │                     │
  │                    │                         ├─ Parse query        │
  │                    │                         ├─ GISAgent.process() │
  │                    │                         ├────────────────────>│
  │                    │                         │                     │
  │                    │                         │ _parse_route_query()│
  │                    │                         │ _resolve_location() │
  │                    │ (3 times)               │ (3 times)           │
  │                    │                         │                     │
  │                    │                         │ optimize_waypoints()│
  │                    │                         │<────────────────────│
  │                    │                         │                     │
  │                    │                         │ calculate_route_distance
  │                    │                         │<────────────────────│
  │                    │                         │                     │
  │                    │                         │ estimate_fuel_cost()│
  │                    │                         │<────────────────────│
  │                    │                         │                     │
  │                    │  MCP result            │                     │
  │                    │<────────────────────    │                     │
  │  "5235 km,         │                         │                     │
  │   $419 fuel"       │                         │                     │
  │<─────────────────  │                         │                     │
```

### Scenario 3: Fuel Cost Query

```
USER                 CLIENT                   SERVER                 TOOLS
  │                    │                         │                     │
  ├─ "Fuel for 500km   │                         │                     │
  │   at $2/L?"        │                         │                     │
  │─────────────────>  │                         │                     │
  │                    ├─ MCP call               │                     │
  │                    │────────────────────>    │                     │
  │                    │                         ├─ Parse query        │
  │                    │                         ├─ GISAgent.process() │
  │                    │                         ├────────────────────>│
  │                    │                         │                     │
  │                    │                         │ _parse_cost_query() │
  │                    │                         │ (extract params)    │
  │                    │                         │                     │
  │                    │                         │ estimate_fuel_cost()│
  │                    │                         │<────────────────────│
  │                    │                         │                     │
  │                    │  MCP result            │                     │
  │                    │<────────────────────    │                     │
  │  "$125 fuel"       │                         │                     │
  │<─────────────────  │                         │                     │
```

## MCP Protocol Details

### Tool Discovery Phase

**Request from Client**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

**Response from Server**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "calculate_distance",
        "description": "Calculate distance between two locations",
        "inputSchema": {
          "type": "object",
          "properties": {
            "origin": { "type": "array", "items": {"type": "number"} },
            "destination": { "type": "array", "items": {"type": "number"} },
            "unit": { "type": "string", "enum": ["km", "miles"] }
          },
          "required": ["origin", "destination"]
        }
      },
      // ... optimize_route, estimate_fuel_cost
    ]
  }
}
```

### Tool Execution Phase

**Request from Client**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
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

**Response from Server**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"distance_km\": 3944.05, \"travel_hours\": 49.3}"
      }
    ]
  }
}
```

## Error Flow

```
USER                 CLIENT                   SERVER
  │                    │                         │
  ├─ "Distance to     │                         │
  │   InvalidCity?"   │                         │
  │─────────────────> │                         │
  │                    ├─ MCP call               │
  │                    │────────────────────>    │
  │                    │                         ├─ Parse fails
  │                    │                         │  (location not found)
  │                    │                         │
  │                    │  Error response        │
  │                    │<────────────────────    │
  │  "Couldn't find    │                         │
  │   InvalidCity"     │                         │
  │<─────────────────  │                         │
```

## Transport Mechanism

```
┌─────────────────────────────────────┐
│  HOST AGENT CLIENT (Claude)         │
│  Manages MCP Protocol Communication │
└────────────┬────────────────────────┘
             │
             │ STDIN/STDOUT (Stdio Transport)
             │ JSON-RPC over Text Stream
             │
┌────────────▼────────────────────────┐
│  GIS MCP SERVER (Python)            │
│  src/gis_mcp_server/server.py       │
│  - Reads JSON from STDIN            │
│  - Writes JSON to STDOUT            │
│  - Processes tool calls             │
│  - Returns results                  │
└─────────────────────────────────────┘
```

## Key Components Summary

| Component | Role | Technology |
|-----------|------|-----------|
| **User Interface** | Submits queries | Claude Desktop, IDE, CLI |
| **MCP Client** | Protocol management, tool discovery | MCP stdlib |
| **Stdio Transport** | Communication channel | JSON-RPC over STDIN/STDOUT |
| **Server Main** | Event loop, transport setup | asyncio, MCP Server |
| **Tool Handlers** | Routing and validation | @server decorators |
| **GIS Agent** | NLP parsing, query interpretation | Regex, Python |
| **Distance Calculator** | Geodesic calculations | Geopy library |
| **Route Optimizer** | Waypoint optimization | Nearest-neighbor algorithm |

## Startup Sequence

```
1. User launches Claude Desktop with GIS MCP Server configured
2. Claude initializes MCP client connection to server via stdio
3. Client sends tools/list request
4. Server returns 3 available tools with full schemas
5. Client caches tool definitions for AI model
6. User submits query to Claude
7. Claude selects appropriate tool based on query semantics
8. Client sends tools/call request with tool arguments
9. Server processes and returns result
10. Claude formats response and shows to user
```

## Performance Characteristics

- **Tool Discovery**: ~50ms (one-time on startup)
- **Distance Query**: ~100ms (geopy calculation + travel time)
- **Route Query**: ~200-500ms (depends on waypoint count)
- **Cost Query**: ~50ms (arithmetic calculation)
- **MCP Protocol Overhead**: ~30-50ms per call (JSON serialization)

**Total Latency**: 100-600ms typical (imperceptible to user)
