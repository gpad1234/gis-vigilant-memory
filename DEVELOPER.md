# GIS MCP Server Developer Guide

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd gis-getting-started

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate

# Install with development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black ruff mypy

# Verify setup
python -m pytest tests/ -v
```

### Code Quality Standards

#### Formatting with Black
```bash
black src/ tests/ main.py
```

**Configuration** (`pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ["py310", "py311", "py312"]
```

#### Linting with Ruff
```bash
ruff check src/ tests/
ruff check --fix src/ tests/  # Auto-fix issues
```

#### Type Checking with mypy
```bash
mypy src/
```

#### Combined Check
```bash
black --check src/ tests/
ruff check src/ tests/
mypy src/
pytest tests/ -v --cov=src/gis_mcp_server
```

---

## Architecture Patterns

### Tool Implementation Pattern

All GIS tools follow this pattern:

```python
class MyTool:
    """One-line description."""

    @staticmethod
    def tool_operation(param1: Type1, param2: Type2) -> ReturnType:
        """
        Full documentation with examples.
        
        Args:
            param1: Description
            param2: Description
            
        Returns:
            Description of return value
            
        Raises:
            ValueError: When input is invalid
        """
        # Implementation
        return result
```

**Key Principles:**
- Use `@staticmethod` for pure functions
- Type hints on all parameters and returns
- Comprehensive docstrings
- No side effects
- Testable in isolation

### MCP Tool Registration Pattern

```python
@self.server.list_tools()
async def list_tools() -> list[dict[str, Any]]:
    """Define tool schemas for MCP protocol."""
    return [
        {
            "name": "tool_name",
            "description": "User-friendly description",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string|number|array",
                        "description": "Parameter description"
                    }
                },
                "required": ["param1"]
            }
        }
    ]

@self.server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Route tool invocations to handlers."""
    if name == "tool_name":
        result = MyTool.operation(arguments["param1"])
        return [{"type": "text", "text": str(result)}]
```

---

## Adding New Tools

### Step 1: Create Tool Module

Create `src/gis_mcp_server/tools/my_new_tool.py`:

```python
"""My new GIS tool for specific functionality."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MyNewTool:
    """Calculate or process geographic data."""

    @staticmethod
    def my_operation(param1: float, param2: str) -> dict[str, float]:
        """
        Perform operation on geographic data.
        
        Args:
            param1: Input parameter
            param2: Configuration parameter
            
        Returns:
            Dictionary with results
        """
        logger.info(f"Processing with {param1}, {param2}")
        
        # Implementation
        result = {"value": param1 * 2}
        
        return result
```

### Step 2: Register Tool

Update `src/gis_mcp_server/tools/__init__.py`:

```python
"""GIS tools for distance calculations and route optimization."""

from .distance_calculator import DistanceCalculator
from .route_optimizer import RouteOptimizer
from .my_new_tool import MyNewTool  # Add this

__all__ = ["DistanceCalculator", "RouteOptimizer", "MyNewTool"]
```

### Step 3: Register with MCP Server

Update `src/gis_mcp_server/server.py`:

```python
from .tools.my_new_tool import MyNewTool  # Add import

# In _register_tools(), add to @server.list_tools():
{
    "name": "my_operation",
    "description": "Perform my operation on geographic data",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "number",
                "description": "First parameter"
            },
            "param2": {
                "type": "string",
                "description": "Configuration"
            }
        },
        "required": ["param1", "param2"]
    }
}

# In @server.call_tool(), add handler:
elif name == "my_operation":
    result = MyNewTool.my_operation(
        arguments["param1"],
        arguments["param2"]
    )
    return [{"type": "text", "text": str(result)}]
```

### Step 4: Write Tests

Create or update `tests/test_my_new_tool.py`:

```python
"""Tests for my new GIS tool."""

import pytest
from src.gis_mcp_server.tools.my_new_tool import MyNewTool


class TestMyNewTool:
    """Test my new tool."""

    def test_my_operation_basic(self) -> None:
        """Test basic operation."""
        result = MyNewTool.my_operation(10.0, "config")
        assert result["value"] == 20.0

    def test_my_operation_negative(self) -> None:
        """Test with negative input."""
        result = MyNewTool.my_operation(-5.0, "config")
        assert result["value"] == -10.0

    def test_my_operation_edge_case(self) -> None:
        """Test edge case."""
        result = MyNewTool.my_operation(0.0, "config")
        assert result["value"] == 0.0
```

### Step 5: Run Tests

```bash
pytest tests/test_my_new_tool.py -v
pytest tests/ --cov=src/gis_mcp_server --cov-report=term-missing
```

---

## Extending the LangChain Agent

The `GISAgent` is designed to be extended with LangChain capabilities.

### Current Structure

```python
class GISAgent:
    def __init__(self) -> None:
        """Initialize agent."""
        
    async def process_request(self, query: str) -> dict[str, Any]:
        """Process natural language query."""
        
    async def calculate_freight_route(
        self,
        origin: str,
        destination: str,
        waypoints: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Calculate freight route."""
```

### Adding LangChain Integration

```python
from langchain.agents import Tool, AgentExecutor, initialize_agent, AgentType
from langchain_community.llms import OpenAI

class GISAgent:
    def __init__(self) -> None:
        """Initialize GIS Agent with LangChain."""
        self.llm = OpenAI(temperature=0)
        self.tools = self._create_tools()
        self.agent = self._initialize_agent()

    def _create_tools(self) -> list[Tool]:
        """Create LangChain tools from GIS functions."""
        return [
            Tool(
                name="calculate_distance",
                func=self._distance_wrapper,
                description="Calculate distance between two points"
            ),
            Tool(
                name="optimize_route",
                func=self._optimize_wrapper,
                description="Optimize delivery route"
            )
        ]

    def _distance_wrapper(self, origin_dest: str) -> str:
        """Wrapper for distance calculation."""
        parts = origin_dest.split(" to ")
        # Parse location names to coordinates
        # Call DistanceCalculator
        return "Distance: X km"

    def _initialize_agent(self) -> AgentExecutor:
        """Initialize LangChain agent."""
        return initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True
        )

    async def process_request(self, query: str) -> dict[str, Any]:
        """Process natural language query with agent."""
        try:
            result = self.agent.run(query)
            return {
                "status": "success",
                "query": query,
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "query": query,
                "error": str(e)
            }
```

---

## Testing Best Practices

### Unit Test Template

```python
"""Tests for specific module."""

import pytest
from src.gis_mcp_server.tools.my_tool import MyTool


class TestMyTool:
    """Test my tool functionality."""

    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.test_data = {"param": "value"}

    def test_basic_operation(self) -> None:
        """Test basic operation."""
        result = MyTool.operation(self.test_data)
        assert result is not None
        assert result["key"] == "expected_value"

    def test_invalid_input(self) -> None:
        """Test with invalid input."""
        with pytest.raises(ValueError):
            MyTool.operation(None)

    def test_edge_cases(self) -> None:
        """Test edge cases."""
        # Empty input
        # Boundary values
        # Maximum values
        pass

    def teardown_method(self) -> None:
        """Clean up after tests."""
        pass
```

### Running Specific Tests

```bash
# Run single test
pytest tests/test_my_tool.py::TestMyTool::test_basic_operation -v

# Run all tests in class
pytest tests/test_my_tool.py::TestMyTool -v

# Run with detailed output
pytest tests/ -vv -s

# Run with coverage
pytest tests/ --cov=src/gis_mcp_server --cov-report=html
```

---

## Performance Optimization

### Profiling

```python
import cProfile
import pstats
from io import StringIO

def profile_function():
    """Profile tool performance."""
    pr = cProfile.Profile()
    pr.enable()
    
    # Code to profile
    from src.gis_mcp_server.tools.distance_calculator import DistanceCalculator
    for _ in range(1000):
        DistanceCalculator.calculate_distance(
            (40.7128, -74.0060),
            (34.0522, -118.2437)
        )
    
    pr.disable()
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print(s.getvalue())

if __name__ == "__main__":
    profile_function()
```

### Optimization Strategies

1. **Caching**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=1000)
   def calculate_distance_cached(origin: tuple, destination: tuple) -> float:
       return DistanceCalculator.calculate_distance(origin, destination)
   ```

2. **Batch Operations**
   ```python
   def calculate_distances_batch(origins, destinations) -> list[float]:
       """Calculate multiple distances efficiently."""
       return [
           DistanceCalculator.calculate_distance(o, d)
           for o, d in zip(origins, destinations)
       ]
   ```

3. **Async Operations**
   ```python
   import asyncio
   
   async def calculate_routes_async(routes: list) -> list:
       """Calculate routes concurrently."""
       tasks = [
           asyncio.create_task(async_calculate(route))
           for route in routes
       ]
       return await asyncio.gather(*tasks)
   ```

---

## Debugging

### Enable Debug Logging

```python
import logging

# In main.py or test file
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("src.gis_mcp_server")
logger.setLevel(logging.DEBUG)

# Now all DEBUG messages will print
```

### Using pdb

```python
import pdb

def problematic_function():
    x = 10
    pdb.set_trace()  # Debugger will stop here
    y = x * 2
    return y

# Commands in debugger:
# l (list code)
# n (next line)
# c (continue)
# p variable (print variable)
# pp variable (pretty print)
```

### Print Debugging

```python
from src.gis_mcp_server.tools.distance_calculator import DistanceCalculator

distance = DistanceCalculator.calculate_distance(
    (40.7128, -74.0060),
    (34.0522, -118.2437)
)
print(f"DEBUG: distance = {distance}")
print(f"DEBUG: type = {type(distance)}")
```

---

## Documentation Standards

### Docstring Format

```python
def function_name(param1: Type1, param2: Type2) -> ReturnType:
    """
    One-line summary of what function does.
    
    Longer description if needed. Can span multiple lines.
    Include rationale if not obvious.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
        
    Returns:
        Description of return value and its type
        
    Raises:
        ValueError: When parameter validation fails
        TypeError: When parameter types are incorrect
        
    Examples:
        >>> result = function_name(10, "test")
        >>> print(result)
        "result value"
        
    Note:
        Any important notes about usage or behavior
    """
    # Implementation
    pass
```

### README Updates

When adding new features:

1. Add to Feature section
2. Add usage example
3. Add to API Reference
4. Update troubleshooting if needed

---

## Deployment Checklist

- [ ] All tests passing
- [ ] Code formatted with Black
- [ ] Type hints on all functions
- [ ] Documentation complete
- [ ] No TODO comments
- [ ] Logging statements added
- [ ] Dependencies listed in requirements.txt
- [ ] README updated
- [ ] CHANGELOG updated
- [ ] Version bumped in __init__.py

---

## Common Issues & Solutions

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'geopy'`

**Solution**: 
```bash
pip install -r requirements.txt
pip install geopy
```

### Type Checking Failures

**Problem**: mypy reports type errors

**Solution**:
```python
# Add type ignore if acceptable
from typing import Any
result: Any = some_untyped_function()

# Or add type stub
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from some_module import SomeType
```

### Test Coverage Low

**Problem**: Coverage below 70%

**Solution**:
```bash
# Find uncovered lines
pytest --cov=src/gis_mcp_server --cov-report=html tests/

# Open htmlcov/index.html
# Add tests for red lines

# For unreachable code
# Add: # pragma: no cover
```

---

## Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [LangChain Documentation](https://langchain.com)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io)
