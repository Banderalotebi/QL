
# Implementation Plan: Free Deployment Options for 24/7 Operation

[Overview]
Create a comprehensive deployment strategy using free cloud services to run the Muqattaat Cryptanalytic Lab continuously (24/7). This plan analyzes multiple free deployment options suitable for Python applications with background workers, API servers, and Streamlit dashboards, selecting the optimal combination for cost-effectiveness and functionality.

The current system consists of:
- FastAPI backend (port 8000)
- Streamlit dashboard (port 8501)
- Continuous background worker (hive_continuous.py)
- Neo4j graph database
- PostgreSQL database

[Types]
**Deployment Architecture Types:**
1. **Server-based**: Persistent VM running 24/7
2. **Serverless**: Event-driven, scales to zero (not ideal for continuous worker)
3. **Container-based**: Docker with orchestration
4. **Hybrid**: Combination of serverless APIs + persistent worker

**Recommended Options:**
| Option | Type | Free Tier | Best For |
|--------|------|-----------|----------|
| Railway | Server | $5 credit/month | Easy setup, Python support |
| Render | Server | 750 hours/month | Web services, background workers |
| Fly.io | Container | 3 VMs, 160GB bandwidth | Docker-first apps |
| Hetzner Cloud | Server | €20 credit/month | Best value, EU/US regions |
| Oracle Cloud | Server | Always free | Enterprise-grade, 2 VMs |
| DigitalOcean | Server | $200/60 days | Droplets, App Platform |
| Google Cloud | Serverless | $300/90 days | Cloud Run, Cloud Functions |
| AWS Free Tier | Serverless | 12 months | ECS Fargate, Lambda |

[Files]
**New files to be created:**
1. `deploy/railway.json` - Railway deployment config
2. `deploy/render.yaml` - Render deployment config  
3. `deploy/Dockerfile.worker` - Dedicated worker container
4. `deploy/docker-compose.production.yml` - Production docker-compose
5. `scripts/deploy-railway.sh` - Railway deployment script
6. `scripts/deploy-render.sh` - Render deployment script
7. `.env.example` - Environment variable template
8. `k8s/` - Kubernetes manifests (optional)

**Existing files to be modified:**
1. `Dockerfile` - Add multi-stage build optimization
2. `docker-compose.yml` - Add production configuration
3. `hive_continuous.py` - Add health check endpoint
4. `src/unified_research_api.py` - Add production settings
5. `requirements.txt` - Add gunicorn for production

[Functions]
**New functions:**
- `health_check()` - Kubernetes/health check endpoint for all services
- `graceful_shutdown()` - Signal handling for zero-downtime deploys
- `metrics_endpoint()` - Prometheus metrics for monitoring
- `deploy_railway()` - Railway CLI deployment automation
- `deploy_render()` - Render deployment automation

**Modified functions:**
- `main()` in `hive_continuous.py` - Add `--health-port` flag
- `app` in `src/unified_research_api.py` - Add production middleware

[Classes]
**New classes:**
- `HealthMonitor` - Monitors all service components
- `DeploymentManager` - Orchestrates multi-service deployment

[Dependencies]
**New packages:**
- `gunicorn` - Production WSGI server
- `uvicorn[standard]` - Production ASGI server
- `prometheus-client` - Metrics collection
- `httpx` - Health check client
- `python-dotenv` - Environment variable loading

**Version changes:**
- Update FastAPI for production stability
- Add explicit version pins for reproducibility

[Testing]
- Add deployment configuration tests
- Test docker-compose production startup
- Validate health check endpoints
- Test graceful shutdown sequences

[Implementation Order]
1. **Step 1**: Create environment configuration (.env.example, config.py)
2. **Step 2**: Update Dockerfile with multi-stage build and health checks
3. **Step 3**: Create docker-compose.production.yml
4. **Step 4**: Add health check endpoints to API and worker
5. **Step 5**: Create deployment scripts for Railway
6. **Step 6**: Create deployment scripts for Render
7. **Step 7**: Add Prometheus metrics support
8. **Step 8**: Test deployment locally with production compose
9. **Step 9**: Document deployment steps

**Recommended Deployment Path (Priority Order):**
1. **Railway** - Easiest setup, $5/month credit, great DX
2. **Render** - Good free tier, background worker support
3. **Hetzner** - Best raw compute value (€20 credit)
4. **Oracle Cloud** - Always free 2 VMs, enterprise grade

