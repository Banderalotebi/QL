# 🚀 Railway Deployment Quick Start

**Estimated Time**: 15-20 minutes  
**Cost**: Free ($5/month credit from Railway)

## What is Railway?

Railway is a modern deployment platform that makes it easy to deploy full-stack applications. It handles containerization, scaling, and monitoring automatically.

**Why Railway for this project?**
- ✅ Free $5/month credit (covers our stack easily)
- ✅ Python-first deployment experience
- ✅ Built-in environment variable management
- ✅ One-command deployment from Git
- ✅ Health checks and auto-restart
- ✅ Simple database integration (PostgreSQL, Redis)

## Prerequisites

1. **Railway Account**: https://railway.app (free)
2. **Railway CLI**: `npm install -g @railway/cli`
3. **Code Pushed to GitHub**: Repository must be public or Railway connected
4. **API Keys Ready**:
   - Anthropic API key (for LLM integration)
   - Neo4j password configured

## Quick Start (5 minutes)

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Login to Railway
```bash
railway login
```
This opens a browser window to authenticate your account.

### Step 3: Connect Repository
```bash
cd /workspaces/QL
railway link --projectName muqattaat-lab
```

### Step 4: Configure Secrets
```bash
railway variable set ANTHROPIC_API_KEY "your_key_here"
railway variable set NEO4J_PASSWORD "your_password"
railroad variable set OLLAMA_BASE_URL "http://localhost:11434"
```

### Step 5: Deploy
```bash
railway deploy
```

**That's it!** Your site will be live in 2-5 minutes.

## Detailed Configuration

### Environment Variables (Required)

Set these in Railway dashboard or via CLI:

```bash
# Application Settings
railway variable set APP_ENV production
railway variable set LOG_LEVEL INFO
railway variable set DEBUG false

# API Configuration
railway variable set API_HOST 0.0.0.0
railway variable set API_PORT 8000

# Streamlit Configuration
railway variable set STREAMLIT_SERVER_PORT 8501
railway variable set STREAMLIT_SERVER_HEADLESS true

# Services (use Railway plugins, see next section)
railway variable set NEO4J_URI bolt://localhost:7687
railway variable set NEO4J_USER neo4j
railway variable set NEO4J_PASSWORD "your_secure_password"

# Secrets (SENSITIVE - use dashboard UI)
# DO NOT commit these to code
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://...
OLLAMA_BASE_URL=http://...
```

### Using Railway Dashboard

**Easier method for secrets:**

1. Go to https://railway.app
2. Select your project: `muqattaat-lab`
3. Click "Variables" tab
4. Add new variable:
   - **Key**: `ANTHROPIC_API_KEY`
   - **Value**: `sk-ant-...` (your key)
   - Click "Add"
5. Repeat for other secrets

Variables are encrypted and secured automatically.

## Multi-Service Setup (Recommended)

Deploy multiple services for better 24/7 operation:

### API Service
```bash
# Create API service
railway service create ql-api

# Configure
railway variable set PYTHONUNBUFFERED 1 -s ql-api
railway env ql-api
railway deploy -s ql-api
```

### Dashboard Service
```bash
# Create Dashboard service
railway service create ql-dashboard

# Configure to run Streamlit
railway env ql-dashboard
# Override CMD: streamlit run frontend/sovereign_dashboard.py --server.port=8501
railway deploy -s ql-dashboard
```

### Worker Service
```bash
# Create Worker service (background processing)
railway service create ql-worker

# Configure
railway env ql-worker
# Override CMD: python hive_continuous.py
railway deploy -s ql-worker
```

## Using Deployment Script

We've created `scripts/deploy-railway.sh` for automated setup:

```bash
# Interactive guided deployment
./scripts/deploy-railway.sh

# Dry-run (see what would happen)
./scripts/deploy-railway.sh --dry-run

# Specific project/environment
./scripts/deploy-railway.sh --project my-project --env staging

# Only setup environment without deploying
./scripts/deploy-railway.sh --setup-env
```

## Monitoring

### View Logs
```bash
# Real-time logs
railway logs

# Last 50 lines
railway logs --tail 50

# Follow specific service
railway logs -s ql-api --follow
```

### Check Health
```bash
# Use our health check script
./scripts/health-check.sh --url https://your-railway-domain.up.railway.app

# Continuous monitoring
./scripts/health-check.sh --continuous --interval 60
```

### Dashboard
Visit Railway dashboard: https://railway.app
- View metrics (CPU, Memory, Disk)
- Check logs in real-time
- Monitor uptime
- View deployment history

## Testing Locally First

**Strongly Recommended**: Test with Railway's production config locally

```bash
# Use production docker-compose
docker-compose -f deploy/docker-compose.production.yml up

# Services will start:
# - API on :8000
# - Dashboard on :8501
# - Neo4j on :7687
# - Worker running in background

# Test health
curl http://localhost:8000/system/health

# Test API
curl http://localhost:8000/research/status

# Test dashboard
open http://localhost:8501
```

When tests pass locally, deployment to Railway will work.

## Accessing Your Deployed App

### URLs (provided by Railway)

After deployment, you get unique URLs:

```
API:       https://api-ql-prod.up.railway.app
Dashboard: https://dashboard-ql-prod.up.railway.app
Worker:    (background, no URL)
```

Open these in your browser:

- **API**: https://api-ql-prod.up.railway.app/docs (Swagger UI)
- **Health**: https://api-ql-prod.up.railway.app/system/health
- **Dashboard**: https://dashboard-ql-prod.up.railway.app

## Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| Free Tier | FREE | $5/month credit from Railway |
| Base VM (512MB RAM) | Covered | Included with free tier |
| Bandwidth | 160GB/month | First 160GB free each month |
| Additional Storage | $1/GB/month | Usually not needed |
| **Total** | **FREE** | Easily within free tier |

**Pro Tip**: Railway gives $5/month credit, which covers:
- 1 small VM running 24/7
- 160GB monthly bandwidth
- All database operations

## Troubleshooting

### Deployment Fails: "docker build error"
```bash
# Check Dockerfile syntax
docker build -f Dockerfile -t test .

# Check if all files exist
ls requirements.txt Dockerfile orchestrator.py
```

### Services Not Running: "502 Bad Gateway"
```bash
# View logs
railway logs -s ql-api

# Check health endpoint
curl https://your-url/system/health

# Rebuild service
railway redeploy
```

### Database Connection Issues
```bash
# Verify database variables
railway variable list

# Check connection string
railway variable get DATABASE_URL

# Restart service
railway service restart ql-api
```

### Server Running Out of Memory
- Upgrade to larger VM: Railway Dashboard → Settings
- Reduce batch sizes in environment
- Enable garbage collection for Python: `PYTHONUNBUFFERED=1`

### Changes Not Deployed
```bash
# Force redeploy
git push origin main
railway redeploy

# Or manual redeploy
railway deploy --force
```

## Advanced Configuration

### Custom Domain
1. Railway Dashboard → Project Settings
2. Add custom domain
3. Update DNS records
4. SSL certificate auto-configured

### Auto-Scaling
Railway doesn't support auto-scaling on free tier, but you can:
1. Upgrade to paid tier
2. Or manually add more services/VMs

### Backup Strategy
```bash
# Export Neo4j data
railway run neo4j-admin dump \
  --database=neo4j \
  --to=/data/backup.dump

# Download to local
railway Download /data/backup.dump
```

### Persistent Storage
```bash
# Create volume
railway volume create ql-data

# Attach to service
railway volume attach ql-data:/data ql-api
```

## Continuous Deployment

### Auto-Deploy from Git
1. Connect Railway to GitHub
2. Select repository and branch (main)
3. Enable "Auto-redeploy on push"
4. Every git push will auto-deploy!

### Staging vs Production
```bash
# Deploy to staging
railway env staging
railway deploy

# Deploy to production
railway env production
railway deploy -f
```

## Useful Commands Reference

```bash
# Project Management
railway link                    # Connect to project
railway unlink                  # Disconnect
railway list                    # List projects
railway cd <project>           # Switch project

# Service Management
railway service list           # List services
railway service create         # Create service
railway service rename         # Rename service
railway service delete         # Delete service

# Variables & Secrets
railway variable list          # Show all variables
railway variable get <name>    # Get specific variable
railway variable set <k> <v>   # Set variable
railway variable delete <name> # Delete variable

# Deployment
railway deploy                 # Deploy changes
railway redeploy              # Force redeploy
railway service restart       # Restart service

# Monitoring
railway logs                  # View logs
railway status                # Show status
railway domains               # List domains

# Local Testing
railway run <command>         # Run command in service
railway shell                 # Interactive shell
```

## Next Steps

1. ✅ Complete this deployment
2. ⏳ Test health endpoints
3. 📊 Set up monitoring alerts
4. 🔄 Enable auto-redeploy from git
5. 🛡️ Configure backup strategy

## Support & Resources

- **Railway Docs**: https://docs.railway.app
- **Python Deployment**: https://docs.railway.app/guides/python
- **Docker**: https://docs.railway.app/deploy/deployments
- **Troubleshooting**: https://docs.railway.app/help/faq

---

**Ready to deploy?** Run this command:

```bash
./scripts/deploy-railway.sh
```

Or open Railway dashboard: https://railway.app
