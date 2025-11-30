# Demo UI - Quick Start

## Run the Streamlit Demo

```bash
streamlit run demo_ui.py
```

This will open a browser at `http://localhost:8501`

## Demo Features

### 📍 Distance Tab
- Select two cities
- Choose km or miles
- See distance + travel time
- Single click calculation

### 🛣️ Route Tab
- Select up to 6 cities
- Automatically optimizes order
- Shows total distance and fuel cost
- Multi-waypoint logistics planning

### ⛽ Fuel Cost Tab
- Input distance, fuel price, efficiency
- Get instant fuel cost estimate
- Useful for budget planning
- Supports custom parameters

### 💬 Natural Query Tab
- Ask anything in natural language
- System interprets your intent
- Works with distance, route, or cost queries
- Great for showcasing NLP capability

### ℹ️ About Tab
- System information
- Supported cities list
- Performance metrics
- Integration details

## Features Demonstrated

✅ **Real-time Calculations** - All results instant (~150ms)  
✅ **Natural Language** - NLP query parsing  
✅ **Route Optimization** - AI-powered multi-stop routing  
✅ **Professional UI** - Clean, modern, responsive design  
✅ **18 US Cities** - Pre-configured major metros  

## Client Demo Script (10 minutes)

1. **Open the app**
   ```bash
   streamlit run demo_ui.py
   ```

2. **Distance Demo**
   - Go to "📍 Distance" tab
   - Select NYC → LA
   - Click "Calculate Distance"
   - Show: 3,944 km, 49.3 hours
   - Talk point: "Accurate geodesic calculation"

3. **Route Demo**
   - Go to "🛣️ Route" tab
   - Select: NYC → Denver → Las Vegas → LA
   - Click "Optimize Route"
   - Show: Total distance, fuel cost, optimized order
   - Talk point: "Smart multi-stop optimization"

4. **Natural Language Demo**
   - Go to "💬 Natural Query" tab
   - Type: "What's the fuel cost for 500 km at $2 per liter?"
   - System shows result
   - Talk point: "AI understands freight logistics language"

5. **Technical Details**
   - Go to "ℹ️ About" tab
   - Show tech stack, performance, integrations
   - Talk point: "Production-ready via MCP protocol"

## Customization Ideas

### Add Your Company Branding
Edit `demo_ui.py` line 20-40 (styling section):
```python
st.markdown(
    """
<style>
    .main-header {
        color: #YOUR_COMPANY_COLOR;  # Change this
    }
</style>
    """
)
```

### Add More Cities
Edit the `CITIES` list (line 223):
```python
CITIES = [
    "New York",
    "YOUR_NEW_CITY",  # Add here
    ...
]
```

### Change Default Values
Edit around line 311, 370, 431:
```python
st.number_input(
    "Distance (km):",
    value=500,  # Change this
)
```

### Customize Welcome Message
Edit the header section (lines 80-90):
```python
st.write("### Custom Company Name Here")
```

## Requirements

- Python 3.12+
- Streamlit 1.28.1+
- All packages from `requirements.txt`

Already installed if you followed project setup!

## Troubleshooting

**"ModuleNotFoundError: No module named 'src'"**
- Make sure you run from project root: `cd /path/to/gis-getting-started`
- Then: `streamlit run demo_ui.py`

**Port 8501 already in use**
```bash
streamlit run demo_ui.py --server.port=8502
```

**Slow calculations**
- First query will be slower (~500ms) due to GIS Agent initialization
- Subsequent queries will be ~100-200ms
- This is normal

## Deployment Options

### Local Demo
```bash
streamlit run demo_ui.py
```

### Share with Team
```bash
# Install ngrok
brew install ngrok

# Run in one terminal
streamlit run demo_ui.py --server.enableXsrfProtection=false

# In another terminal
ngrok http 8501

# Share ngrok URL with your team
```

### Deploy to Streamlit Cloud
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub repo
4. Deploy with one click

### Docker Container
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "demo_ui.py"]
```

```bash
docker build -t gis-demo .
docker run -p 8501:8501 gis-demo
```

## Performance Tips

- **First load**: ~2 seconds (agent initialization)
- **Subsequent loads**: ~100-500ms per query
- **UI is responsive**: No lag during calculations
- **Can handle concurrent requests**: Streamlit manages this

## What's Happening Behind the Scenes

1. User enters query in UI
2. Streamlit passes to `GISAgent.process_request()`
3. Agent uses NLP to parse query type
4. Routes to appropriate tool (distance, route, cost)
5. Tool calculates result using Geopy
6. Result returned to UI as JSON
7. UI formats and displays to user

All **without needing the MCP server running** - direct tool access!

## Next Steps

After client demo:

1. **Show Architecture Docs**
   - Point to `ARCHITECTURE.md`
   - Show `INTERACTION_FLOW.md`

2. **Discuss Customization**
   - Add your company locations
   - Integrate with your systems
   - Custom pricing models

3. **Technical Integration**
   - Show how it works via MCP protocol
   - Discuss Claude Desktop integration
   - Plan API integration

4. **Deployment**
   - Offer hosted version options
   - Discuss licensing/support
   - Plan pilot program

---

**Demo UI created with ❤️**
