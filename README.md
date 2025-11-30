# GIS MCP Server

A Python MCP (Model Context Protocol) Server for GIS distance calculations with LangChain NLP integration for freight optimization.

## Features

- **Distance Calculations**: Accurate geodesic distance calculations between geographic coordinates
- **Route Optimization**: Simple nearest-neighbor optimization for freight delivery routes
- **Travel Time Estimation**: Estimate travel time based on distance and average speed
- **Fuel Cost Estimation**: Calculate estimated fuel costs for routes
- **MCP Integration**: Seamless integration with the Model Context Protocol
- **LangChain Support**: Natural language processing capabilities for freight queries
- **Freight Optimization**: Specialized tools for moving freight efficiently

## Project Structure

```
.
├── src/gis_mcp_server/           # Main server package
│   ├── __init__.py              # Package initialization
│   ├── server.py                # Main MCP server implementation
│   ├── tools/                   # GIS tools
│   │   ├── distance_calculator.py
│   │   └── route_optimizer.py
│   └── agents/                  # LangChain agents
│       └── gis_agent.py
├── tests/                        # Unit tests
├── main.py                       # Entry point
├── requirements.txt              # Python dependencies
└── pyproject.toml               # Project configuration
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd gis-getting-started
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

```bash
python main.py
```

### Basic Distance Calculation

```python
from src.gis_mcp_server.tools.distance_calculator import DistanceCalculator

# Calculate distance between two points
nyc = (40.7128, -74.0060)
la = (34.0522, -118.2437)

distance_km = DistanceCalculator.calculate_distance(nyc, la, unit="km")
print(f"Distance: {distance_km:.2f} km")
```

### Route Optimization

```python
from src.gis_mcp_server.tools.route_optimizer import RouteOptimizer

waypoints = [
    (40.7128, -74.0060),  # NYC
    (39.7392, -104.9903),  # Denver
    (34.0522, -118.2437),  # LA
]

optimized = RouteOptimizer.optimize_waypoints(waypoints)
print(f"Optimized route: {optimized}")
```

### Travel Time Estimation

```python
result = DistanceCalculator.estimate_travel_time(800, avg_speed_kmh=80)
print(f"Travel time: {result['hours']:.1f} hours")
```

## Testing

Run the test suite:

```bash
pytest tests/
```

With coverage:

```bash
pytest tests/ --cov=src/gis_mcp_server
```

## Development

### Code Quality

Format code with Black:
```bash
black src/ tests/
```

Lint with Ruff:
```bash
ruff check src/ tests/
```

Type check with mypy:
```bash
mypy src/
```

## Configuration

Create a `.env` file for configuration:

```
LOG_LEVEL=INFO
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=5000
```

## API Reference

### DistanceCalculator

- `calculate_distance(origin, destination, unit='km')` - Calculate distance between two points
- `calculate_route_distance(waypoints, unit='km')` - Calculate total distance for a route
- `estimate_travel_time(distance_km, avg_speed_kmh=80)` - Estimate travel time

### RouteOptimizer

- `optimize_waypoints(waypoints, start_index=0)` - Optimize waypoint order
- `estimate_fuel_cost(distance_km, fuel_price_per_liter=1.5, fuel_efficiency=8)` - Estimate fuel cost

## Documentation

For more information, visit:
- Project: https://gis-mcp.com/
- AI Agent Guide: https://gis-mcp.com/gis-ai-agent/

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please follow the development guidelines and submit pull requests.
