# GIS MCP Server - Deployment Specification

## Overview

This document provides comprehensive deployment instructions for the GIS Freight Optimizer across multiple platforms and environments.

---

## Table of Contents

1. [Quick Start Deployments](#quick-start-deployments)
2. [Local Deployment](#local-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [MCP Server Integration](#mcp-server-integration)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Quick Start Deployments

### Option A: Streamlit Cloud (Recommended for Quick Demo)

**Time:** 2 minutes  
**Cost:** Free tier available  
**Pros:** No infrastructure, automatic scaling, shareable URL  
**Cons:** Limited customization, always-on limitations

#### Steps:

1. **Ensure GitHub repo is public:**
   ```bash
   # Make repo public at https://github.com/gpad1234/gis-vigilant-memory
   # Settings → Visibility → Change to Public
   ```

2. **Go to Streamlit Cloud:**
   - Visit https://share.streamlit.io
   - Sign in with GitHub account
   - Click "New app"
   - Select:
     - Repository: `gpad1234/gis-vigilant-memory`
     - Branch: `main`
     - Main file path: `demo_ui.py`
   - Click "Deploy"

3. **Your app is live at:**
   ```
   https://gis-vigilant-memory-[hash].streamlit.app
   ```

**Share with clients:** Just send the URL!

---

### Option B: Local Development (For Testing)

**Time:** 5 minutes  
**Cost:** Free  
**Pros:** Full control, fast iteration, offline capable

#### Steps:

```bash
# 1. Clone repo
git clone https://github.com/gpad1234/gis-vigilant-memory.git
cd gis-vigilant-memory

# 2. Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run Streamlit app
streamlit run demo_ui.py

# 5. Open browser
# http://localhost:8501
```

**To share locally:**
```bash
# Install ngrok
brew install ngrok  # or download from ngrok.com

# In one terminal
streamlit run demo_ui.py

# In another terminal
ngrok http 8501

# Share the ngrok URL with clients
# https://xxxx-xx-xxx-xxx-xx.ngrok.io
```

---

## Local Deployment

### Development Environment Setup

```bash
# System Requirements
- Python 3.12+
- pip or poetry
- Virtual environment (venv/conda)

# 1. Clone repository
git clone https://github.com/gpad1234/gis-vigilant-memory.git
cd gis-vigilant-memory

# 2. Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
pytest tests/ -v  # Should show 15/15 passing

# 5. Run demo UI
streamlit run demo_ui.py

# 6. Run MCP Server (in another terminal)
python main.py
```

### Directory Structure

```
gis-getting-started/
├── demo_ui.py                 # Streamlit app entry point
├── main.py                    # MCP server entry point
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Project metadata
├── src/
│   └── gis_mcp_server/
│       ├── __init__.py
│       ├── server.py         # MCP server implementation
│       ├── agents/
│       │   └── gis_agent.py  # NLP query parser
│       └── tools/
│           ├── distance_calculator.py
│           └── route_optimizer.py
├── tests/
│   ├── test_gis_server.py
│   └── test_gis_agent.py
└── docs/
    ├── ARCHITECTURE.md
    ├── INTERACTION_FLOW.md
    ├── GIS_AGENT_SPEC.md
    └── DEPLOYMENT_SPEC.md
```

---

## Docker Deployment

### Build Docker Image

#### 1. Create Dockerfile

```dockerfile
# Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Set environment variables
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Run Streamlit app
CMD ["streamlit", "run", "demo_ui.py"]
```

#### 2. Create .dockerignore

```
.venv
__pycache__
*.pyc
.pytest_cache
.git
.gitignore
README.md
*.md
.env
.env.local
node_modules
```

#### 3. Build Image

```bash
# Build
docker build -t gis-optimizer:latest .

# Tag for registry
docker tag gis-optimizer:latest gpad1234/gis-optimizer:latest
```

#### 4. Run Container Locally

```bash
# Simple run
docker run -p 8501:8501 gis-optimizer:latest

# With volume mount (for development)
docker run -v $(pwd):/app -p 8501:8501 gis-optimizer:latest

# With environment variables
docker run \
  -e STREAMLIT_SERVER_MAXUPLOADSIZE=200 \
  -p 8501:8501 \
  gis-optimizer:latest

# Named container with restart policy
docker run \
  --name gis-demo \
  --restart always \
  -p 8501:8501 \
  gis-optimizer:latest
```

#### 5. Push to Docker Hub

```bash
# Login
docker login

# Push
docker push gpad1234/gis-optimizer:latest

# Pull and run anywhere
docker run -p 8501:8501 gpad1234/gis-optimizer:latest
```

---

## Cloud Platforms

### AWS Deployment

#### Option 1: AWS App Runner (Easiest)

```bash
# 1. Push Docker image to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com

docker tag gis-optimizer:latest \
  123456789.dkr.ecr.us-east-1.amazonaws.com/gis-optimizer:latest

docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/gis-optimizer:latest

# 2. Create App Runner service via AWS Console:
# - Service name: gis-optimizer
# - Image source: ECR private
# - Select pushed image
# - Port: 8501
# - CPU: 1 vCPU
# - Memory: 2 GB
# - Auto deploy: enabled

# 3. Access at: https://[service-id].us-east-1.apprunner.amazonaws.com
```

**Cost:** ~$4/month for minimal configuration

#### Option 2: AWS ECS + Fargate

```yaml
# ecs-task-definition.json
{
  "family": "gis-optimizer",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "gis-optimizer",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/gis-optimizer:latest",
      "portMappings": [
        {
          "containerPort": 8501,
          "hostPort": 8501,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/gis-optimizer",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

```bash
# Deploy
aws ecs create-service \
  --cluster default \
  --service-name gis-optimizer \
  --task-definition gis-optimizer:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

**Cost:** ~$10-20/month

### Azure Deployment

#### Option 1: Azure Container Instances (Simplest)

```bash
# 1. Create resource group
az group create \
  --name gis-optimizer-rg \
  --location eastus

# 2. Create container instance
az container create \
  --resource-group gis-optimizer-rg \
  --name gis-optimizer \
  --image python:3.12-slim \
  --cpu 1 \
  --memory 1.5 \
  --ports 8501 \
  --ip-address Public \
  --command-line "pip install -r requirements.txt && streamlit run demo_ui.py" \
  --environment-variables STREAMLIT_SERVER_HEADLESS=true

# 3. Get public IP
az container show \
  --resource-group gis-optimizer-rg \
  --name gis-optimizer \
  --query ipAddress.ip
```

**Cost:** ~$5-15/month

#### Option 2: Azure App Service

```bash
# 1. Create App Service plan
az appservice plan create \
  --name gis-optimizer-plan \
  --resource-group gis-optimizer-rg \
  --sku B1 \
  --is-linux

# 2. Create web app
az webapp create \
  --resource-group gis-optimizer-rg \
  --plan gis-optimizer-plan \
  --name gis-optimizer \
  --deployment-container-image-name-user gpad1234/gis-optimizer:latest

# 3. Configure deployment
az webapp config container set \
  --name gis-optimizer \
  --resource-group gis-optimizer-rg \
  --docker-custom-image-name gpad1234/gis-optimizer:latest \
  --docker-registry-server-url https://index.docker.io

# 4. Access at: https://gis-optimizer.azurewebsites.net
```

**Cost:** ~$10-20/month

### Google Cloud Deployment

#### Option 1: Cloud Run (Recommended)

```bash
# 1. Set project
gcloud config set project your-project-id

# 2. Build and push to Artifact Registry
gcloud builds submit --tag gcr.io/your-project-id/gis-optimizer:latest

# 3. Deploy to Cloud Run
gcloud run deploy gis-optimizer \
  --image gcr.io/your-project-id/gis-optimizer:latest \
  --platform managed \
  --region us-central1 \
  --memory 512M \
  --cpu 1 \
  --allow-unauthenticated \
  --set-env-vars "STREAMLIT_SERVER_HEADLESS=true"

# 4. Access at: https://gis-optimizer-xxxx.run.app
```

**Cost:** Free tier up to 2M requests/month, then ~$0.00002/request

---

## MCP Server Integration

### Deploy as Claude Desktop Integration

#### 1. Installation on Local Machine

```bash
# Create config directory
mkdir -p ~/.config/Claude

# Create claude_desktop_config.json
cat > ~/.config/Claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "gis": {
      "command": "python",
      "args": ["/path/to/gis-getting-started/main.py"]
    }
  }
}
EOF
```

#### 2. Verify Connection

In Claude Desktop, you should see:
- ✓ MCP Server connected
- ✓ 3 tools available (calculate_distance, optimize_route, estimate_fuel_cost)

#### 3. Test Integration

```
User: "What's the distance from New York to Los Angeles?"
Claude: [Uses MCP server to calculate]
"The distance is 3,944.05 km..."
```

### Deploy to Remote Server

For headless/server deployments:

```bash
# 1. SSH into server
ssh user@your-server.com

# 2. Clone repo
git clone https://github.com/gpad1234/gis-vigilant-memory.git
cd gis-vigilant-memory

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run with nohup (background process)
nohup python main.py > gis-server.log 2>&1 &

# 5. Monitor
tail -f gis-server.log

# 6. Get PID
ps aux | grep main.py

# 7. Kill if needed
kill -9 <PID>
```

Or use systemd service:

```ini
# /etc/systemd/system/gis-mcp.service
[Unit]
Description=GIS MCP Server
After=network.target

[Service]
Type=simple
User=gis-user
WorkingDirectory=/path/to/gis-getting-started
ExecStart=/path/to/.venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl enable gis-mcp
sudo systemctl start gis-mcp
sudo systemctl status gis-mcp
```

---

## Monitoring & Maintenance

### Health Checks

#### Streamlit App

```bash
# Check if responsive
curl -I http://localhost:8501

# Expected response:
# HTTP/1.1 200 OK
```

#### MCP Server

```bash
# Check if running
ps aux | grep main.py

# Check logs
tail -f gis-server.log | grep -i error
```

#### Docker Container

```bash
# Check status
docker ps | grep gis-optimizer

# View logs
docker logs gis-optimizer

# Check health
docker exec gis-optimizer curl http://localhost:8501/_stcore/health
```

### Performance Monitoring

```bash
# CPU/Memory usage
docker stats gis-optimizer

# Request latency
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8501

# Load testing
ab -n 100 -c 10 http://localhost:8501
```

### Logging Strategy

**Development:**
```bash
# Enable debug logging
export STREAMLIT_LOGGER_LEVEL=debug
streamlit run demo_ui.py
```

**Production (Docker):**
```dockerfile
# In Dockerfile
RUN pip install python-json-logger

# Structured logging to stdout
CMD ["streamlit", "run", "demo_ui.py", "--logger.level=info"]
```

### Backup & Recovery

```bash
# Backup configuration
git clone https://github.com/gpad1234/gis-vigilant-memory.git gis-backup-$(date +%Y%m%d)

# Version control
git log --oneline | head -20

# Rollback if needed
git checkout <previous-commit-hash>
```

---

## Environment Variables

### Streamlit Configuration

```bash
# Server settings
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_MAXUPLOADSIZE=200  # MB

# Security
STREAMLIT_CLIENT_TOOLBARMODE=minimal
STREAMLIT_CLIENT_SHOWCOLORCODEFORNESTEDLINES=false

# Performance
STREAMLIT_CLIENT_PAGEALLOCSTRATEGY=multi
STREAMLIT_LOGGER_LEVEL=info

# Custom
GIS_API_KEY=your-key-here  # If needed for future integrations
DEBUG=false
```

### Docker Build Arguments

```dockerfile
ARG PYTHON_VERSION=3.12-slim
ARG PORT=8501

FROM python:${PYTHON_VERSION}
EXPOSE ${PORT}
```

```bash
docker build \
  --build-arg PYTHON_VERSION=3.12-slim \
  --build-arg PORT=8501 \
  -t gis-optimizer:latest .
```

---

## Scaling Considerations

### Single Instance (Current)
- **Capacity:** 100-500 concurrent users
- **Response time:** 100-500ms
- **Cost:** $5-20/month

### Multi-Instance (Future)
```bash
# Docker Compose for local multi-instance
version: '3.8'
services:
  gis-1:
    image: gis-optimizer:latest
    ports:
      - "8501:8501"
  gis-2:
    image: gis-optimizer:latest
    ports:
      - "8502:8501"
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Kubernetes (Enterprise)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gis-optimizer
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gis-optimizer
  template:
    metadata:
      labels:
        app: gis-optimizer
    spec:
      containers:
      - name: gis-optimizer
        image: gpad1234/gis-optimizer:latest
        ports:
        - containerPort: 8501
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /_stcore/health
            port: 8501
          initialDelaySeconds: 30
          periodSeconds: 10
```

---

## Cost Comparison

| Platform | Setup | Monthly | Scalability | Recommendation |
|----------|-------|---------|------------|---|
| **Streamlit Cloud** | 2 min | Free | Limited | Demo/Testing |
| **Local + ngrok** | 5 min | Free | None | Quick demo |
| **Docker Local** | 10 min | Free | Manual | Development |
| **AWS App Runner** | 15 min | $4-10 | Auto | Production |
| **Azure Container** | 15 min | $5-15 | Manual | Enterprise |
| **Google Cloud Run** | 15 min | Free-10 | Auto | Scalable |
| **Kubernetes** | 30 min | $20-50 | Auto | Large-scale |

---

## Recommended Deployment Paths

### For Immediate Demo
```
streamlit run demo_ui.py → ngrok → Share URL
Time: 5 minutes | Cost: Free
```

### For Client Testing
```
Streamlit Cloud (public GitHub repo)
Time: 2 minutes | Cost: Free tier
URL: https://gis-vigilant-memory-xxx.streamlit.app
```

### For Production (Small Team)
```
Docker image → AWS App Runner
Time: 30 minutes | Cost: ~$5-10/month
```

### For Enterprise
```
Docker image → Kubernetes cluster
Time: 1-2 hours | Cost: $20-100+/month
Includes: HA, scaling, monitoring
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8501
lsof -i :8501

# Kill it
kill -9 <PID>

# Or use different port
streamlit run demo_ui.py --server.port=8502
```

### Import Errors in Container
```dockerfile
# Ensure sys.path setup is in demo_ui.py
RUN python -c "import sys; sys.path.insert(0, '.'); from demo_ui import *"
```

### Memory Issues
```bash
# Increase Docker memory
docker run -m 2g gis-optimizer:latest

# Or in docker-compose
services:
  gis:
    mem_limit: 2g
```

### Slow Response Times
```bash
# Check resource usage
docker stats gis-optimizer

# Profile with Python
python -m cProfile -o profile.stats main.py

# View results
python -m pstats profile.stats
```

---

## Support & Documentation

- **GitHub:** https://github.com/gpad1234/gis-vigilant-memory
- **Architecture:** See `ARCHITECTURE.md`
- **Integration:** See `INTERACTION_FLOW.md`
- **API Spec:** See `GIS_AGENT_SPEC.md`

---

**Last Updated:** November 30, 2025  
**Version:** 1.0.0
