# GIS MCP Server - Demo UI Designs

## Option 1: Web Dashboard (Recommended for Client Demo)

A clean, professional web interface built with React/HTML that demonstrates all three core capabilities.

### Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│  GIS FREIGHT OPTIMIZER                                    [?] [⚙] [×] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ Quick Query Input                                              │ │
│  │ ┌──────────────────────────────────────────────────────────┐  │ │
│  │ │ "Distance from NYC to LA" or ask anything...            │  │ │
│  │ │                                                          │  │ │
│  │ └──────────────────────────────────────────────────────────┘  │ │
│  │                                      [SEND] [CLEAR]            │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ DEMO SCENARIOS                                                 │ │
│  │ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │ │
│  │ │ 📍 Distance  │  │ 🛣️  Route     │  │ ⛽ Fuel Cost │          │ │
│  │ │              │  │               │  │              │          │ │
│  │ │ NYC → LA     │  │ NYC → Denver  │  │ 500 km route │          │ │
│  │ │              │  │ → LA          │  │ @ $1.50/L    │          │ │
│  │ └──────────────┘  └──────────────┘  └──────────────┘          │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │ RESULTS                                                        │ │
│  │                                                                │ │
│  │ Query: "What's the distance from New York to Los Angeles?"   │ │
│  │                                                                │ │
│  │ ✓ SUCCESS                                                      │ │
│  │                                                                │ │
│  │  FROM: New York                                               │ │
│  │  TO: Los Angeles                                              │ │
│  │  DISTANCE: 3,944.05 km                                        │ │
│  │  TRAVEL TIME: 49.3 hours (at 80 km/h)                         │ │
│  │                                                                │ │
│  │  📊 Explanation:                                               │ │
│  │  "The distance from New York to Los Angeles is 3,944.05 km,  │ │
│  │   which takes approximately 49.3 hours at 80 km/h."          │ │
│  │                                                                │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  Response Time: 145ms | Protocol: MCP 1.0 | Status: Connected     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Features Demonstrated

1. **Distance Calculation Card**
   - Shows origin/destination
   - Displays distance + travel time
   - Visual indicator (green check for success)
   - Performance metric

2. **Route Optimization Card**
   - Multi-waypoint visualization
   - Total distance
   - Estimated fuel cost
   - Sequential stop order

3. **Fuel Cost Calculator Card**
   - Distance input
   - Customizable fuel price/efficiency
   - Total cost breakdown
   - Cost per km

4. **Interactive Map** (Optional enhancement)
   - US map with 18 city markers
   - Clickable cities for quick selection
   - Route visualization with polylines
   - Distance overlay

---

## Option 2: Terminal UI (Fast Demo, No Dependencies)

Python-based rich TUI for quick terminal demonstration:

```
╔════════════════════════════════════════════════════════════════════╗
║                   GIS FREIGHT OPTIMIZER v1.0                      ║
╚════════════════════════════════════════════════════════════════════╝

┌─ DISTANCE CALCULATOR ──────────────────────────────────────────────┐
│                                                                    │
│  From: ┌──────────────────────────────────────┐                  │
│        │ New York                    ▼        │                  │
│        └──────────────────────────────────────┘                  │
│                                                                    │
│  To:   ┌──────────────────────────────────────┐                  │
│        │ Los Angeles                 ▼        │                  │
│        └──────────────────────────────────────┘                  │
│                                                                    │
│  Unit: ◉ km  ○ miles                                              │
│                                                                    │
│                                      [CALCULATE] [RESET]          │
│                                                                    │
│  ✓ RESULT: 3,944.05 km  |  Travel: 49.3 hrs  |  Speed: 80 km/h   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌─ ROUTE OPTIMIZER ──────────────────────────────────────────────────┐
│                                                                    │
│  Route Stops:                                                      │
│  1. ☐ New York                                                    │
│  2. ☐ Denver                                                      │
│  3. ☐ Las Vegas                                                   │
│  4. ☐ Los Angeles                                                 │
│                                                                    │
│  Add Stop:  ┌──────────────────────────────────────┐              │
│             │ Select city...                   ▼   │              │
│             └──────────────────────────────────────┘              │
│                                                  [+]               │
│                                                                    │
│                                    [OPTIMIZE ROUTE] [CLEAR]       │
│                                                                    │
│  ✓ OPTIMIZED ROUTE:                                               │
│  NYC → Denver → Las Vegas → LA                                    │
│  Total: 5,234.87 km  |  Fuel Cost: $418.79  |  Time: 65.4 hrs    │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

┌─ FUEL COST CALCULATOR ─────────────────────────────────────────────┐
│                                                                    │
│  Distance (km): ┌──────────────────────────────────────┐          │
│                 │ 1000                                 │          │
│                 └──────────────────────────────────────┘          │
│                                                                    │
│  Fuel Price ($/L): ┌──────────────────────────────────────┐       │
│                    │ 1.50                                │       │
│                    └──────────────────────────────────────┘       │
│                                                                    │
│  Efficiency (km/L): ┌──────────────────────────────────────┐      │
│                     │ 8                                    │      │
│                     └──────────────────────────────────────┘      │
│                                                                    │
│                                          [CALCULATE] [RESET]      │
│                                                                    │
│  ✓ RESULT: $187.50                                               │
│             (1000 km ÷ 8 km/L × $1.50/L)                         │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

Available Locations (18): NYC, LA, Denver, SF, Chicago, Houston, Phoenix,
Philadelphia, San Antonio, San Diego, Dallas, Seattle, Atlanta, Boston, Miami

[ESC] Quit  [?] Help  [C] Clear All  Connected to: localhost:8000
```

---

## Option 3: Streamlit App (Quickest to Build)

Lightweight Python web app, run with: `streamlit run demo_ui.py`

```python
# demo_ui.py
import streamlit as st
import asyncio
from src.gis_mcp_server.agents.gis_agent import GISAgent

st.set_page_config(
    page_title="GIS Freight Optimizer",
    page_icon="📍",
    layout="wide"
)

st.title("🚚 GIS Freight Optimizer")
st.markdown("_Natural language interface for distance calculations and route optimization_")

# Initialize agent
agent = GISAgent()

# Tabs for different query types
tab1, tab2, tab3, tab4 = st.tabs(
    ["📍 Distance", "🛣️ Route", "⛽ Fuel Cost", "🤖 Natural Query"]
)

# --- TAB 1: Distance ---
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        origin = st.selectbox(
            "From:",
            ["New York", "Los Angeles", "Denver", "San Francisco", "Chicago",
             "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego",
             "Dallas", "Seattle", "Atlanta", "Boston", "Miami"],
            key="distance_from"
        )
    
    with col2:
        destination = st.selectbox(
            "To:",
            ["Los Angeles", "New York", "Denver", "San Francisco", "Chicago",
             "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego",
             "Dallas", "Seattle", "Atlanta", "Boston", "Miami"],
            key="distance_to"
        )
    
    unit = st.radio("Unit:", ["km", "miles"], horizontal=True)
    
    if st.button("Calculate Distance", key="calc_distance"):
        result = asyncio.run(
            agent.process_request(
                f"distance from {origin} to {destination}"
            )
        )
        
        if result["status"] == "success":
            st.success("✓ Calculation Complete")
            cols = st.columns(2)
            with cols[0]:
                st.metric("Distance", f"{result['result']['distance_km']} km")
            with cols[1]:
                st.metric("Travel Time", f"{result['result']['travel_hours']} hrs")
            st.info(result['result']['explanation'])
        else:
            st.error(f"Error: {result.get('error', 'Unknown error')}")

# --- TAB 2: Route ---
with tab2:
    st.subheader("Multi-Stop Route Optimization")
    
    stops = []
    for i in range(4):
        col1, col2 = st.columns([3, 1])
        with col1:
            city = st.selectbox(
                f"Stop {i+1}:",
                ["New York", "Los Angeles", "Denver", "San Francisco", "Chicago",
                 "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego",
                 "Dallas", "Seattle", "Atlanta", "Boston", "Miami"],
                key=f"route_stop_{i}"
            )
            stops.append(city)
        with col2:
            st.write("")  # spacer
    
    if st.button("Optimize Route"):
        query = f"optimize route with stops in {', '.join(stops)}"
        result = asyncio.run(agent.process_request(query))
        
        if result["status"] == "success":
            st.success("✓ Route Optimized")
            cols = st.columns(3)
            with cols[0]:
                st.metric("Total Distance", f"{result['result']['total_distance_km']} km")
            with cols[1]:
                st.metric("Fuel Cost", f"${result['result']['estimated_fuel_cost']}")
            with cols[2]:
                st.metric("Stops", len(result['result']['stops']))
            st.info(result['result']['explanation'])
        else:
            st.error(f"Error: {result.get('error')}")

# --- TAB 3: Fuel Cost ---
with tab3:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        distance = st.number_input("Distance (km):", min_value=1, value=500)
    
    with col2:
        price = st.number_input("Fuel Price ($/L):", min_value=0.1, value=1.50, step=0.10)
    
    with col3:
        efficiency = st.number_input("Efficiency (km/L):", min_value=1.0, value=8.0, step=0.5)
    
    if st.button("Estimate Fuel Cost"):
        query = f"fuel cost for {distance} km at ${price} per liter"
        result = asyncio.run(agent.process_request(query))
        
        if result["status"] == "success":
            st.success("✓ Cost Calculated")
            st.metric("Estimated Fuel Cost", f"${result['result']['estimated_fuel_cost']}")
            st.info(result['result']['explanation'])
        else:
            st.error(f"Error: {result.get('error')}")

# --- TAB 4: Natural Query ---
with tab4:
    st.subheader("Ask Anything (Natural Language)")
    query = st.text_area(
        "Your query:",
        placeholder="E.g., 'What's the distance from NYC to LA?'",
        height=100
    )
    
    if st.button("Ask"):
        result = asyncio.run(agent.process_request(query))
        
        if result["status"] == "success":
            st.success("✓ Query Understood")
            st.write(f"**Type:** {result['type'].title()}")
            st.json(result["result"])
        elif result["status"] == "unrecognized":
            st.warning("❌ Query Not Recognized")
            st.write(result.get("message"))
            with st.expander("See Examples"):
                for example in result.get("examples", []):
                    st.write(f"• {example}")
        else:
            st.error(f"Error: {result.get('error')}")

# Footer
st.divider()
st.markdown("""
**GIS MCP Server v1.0** | [GitHub](https://github.com/gpad1234/gis-vigilant-memory)

Supported Cities (18): New York, Los Angeles, Denver, San Francisco, Chicago, Houston, 
Phoenix, Philadelphia, San Antonio, San Diego, Dallas, Seattle, Atlanta, Boston, Miami

**MCP Protocol:** JSON-RPC over Stdio | **Response Time:** ~100-500ms
""")
```

---

## Option 4: Claude Desktop Integration (Most Polished)

Integrate directly with Claude Desktop via `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gis": {
      "command": "python",
      "args": ["/path/to/main.py"]
    }
  }
}
```

**Demo Script for Client**:

```
User: "I need to ship freight from New York to Los Angeles. How far is it?"
Claude: "Let me calculate that for you..."
[Uses GIS MCP Server]
Claude: "The distance from New York to Los Angeles is 3,944.05 km, 
which would take approximately 49.3 hours of driving at 80 km/h."

User: "What if I need to stop in Denver and Las Vegas along the way?"
Claude: "I'll optimize that route for you..."
[Uses route optimizer]
Claude: "The optimized route would be:
- New York → Denver (1,780 km)
- Denver → Las Vegas (1,224 km)  
- Las Vegas → Los Angeles (434 km)
Total distance: 5,234 km
Estimated fuel cost: $418.79"

User: "How much would fuel cost for this trip at $2 per liter?"
Claude: "Based on the optimized route distance of 5,234 km..."
[Uses fuel calculator]
Claude: "At $2 per liter with standard 8 km/L efficiency, fuel would cost $1,308.50"
```

---

## Recommended Demo Flow

### For Executive/Client Presentation (10 minutes)

1. **Open Streamlit UI** (Option 3)
   - Live, interactive, impressive
   - No terminal visibility

2. **Demo Scenario 1: Distance**
   - Select NYC → LA
   - Show instant result with visualization
   - Highlight: Accurate geodesic calculation

3. **Demo Scenario 2: Route Optimization**
   - Select 4 cities
   - Show optimized sequence
   - Highlight: AI-powered route optimization

4. **Demo Scenario 3: Natural Language**
   - Type complex query in natural language
   - Show system interprets and responds
   - Highlight: NLP capability differentiates from simple calculators

5. **Discuss Capabilities**
   - "Works with 18 US cities, easily expandable"
   - "Real-time calculations, ~100ms response"
   - "Integration-ready via MCP protocol"

### For Technical Demo (5 minutes)

1. **Show INTERACTION_FLOW.md** diagram
2. **Run Terminal UI** (Option 2)
3. **Open main.py** to show architecture
4. **Run pytest** to show 15 passing tests
5. **Point to GIS_AGENT_SPEC.md** for extensibility

---

## Implementation Priority

| UI Option | Build Time | Impression | Complexity | Recommended For |
|-----------|-----------|-----------|-----------|----------------|
| **Streamlit** | 30 min | High ⭐⭐⭐ | Low | Immediate demo |
| **Web Dashboard** | 2-3 hrs | Highest ⭐⭐⭐⭐⭐ | Medium | Production client demo |
| **Terminal UI** | 1 hr | Medium ⭐⭐ | Low | Technical audience |
| **Claude Desktop** | 5 min setup | High ⭐⭐⭐⭐ | None | Ongoing use |

---

## Quick Start: Streamlit Demo

```bash
# Install Streamlit
pip install streamlit

# Create demo_ui.py (use code from Option 3 above)

# Run it
streamlit run demo_ui.py

# Opens browser at http://localhost:8501
```

No additional server setup needed - uses existing GIS Agent directly!

---

## Future Enhancements

1. **Interactive Map Visualization**
   - Folium/Leaflet map showing routes
   - Polylines connecting cities
   - Marker pop-ups with city info

2. **Export Results**
   - PDF route report
   - CSV data download
   - Share-able result link

3. **Historical Tracking**
   - Save favorite routes
   - Compare fuel price scenarios
   - Cost analysis over time

4. **Real-time Integrations**
   - Live traffic data
   - Current gas prices
   - Weather conditions along route

5. **Mobile Responsive**
   - Mobile-optimized version
   - GPS auto-location
   - PWA for offline capability
