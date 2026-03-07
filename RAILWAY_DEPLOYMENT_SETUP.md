# Railway Deployment - Configuration Setup

**Status**: ✅ Deployed | ⏳ Pending Configuration  
**Region**: europe-west4 (GCP Belgium)  
**Replicas**: 1  
**Restart Policy**: On failure (max 10 retries)

## ⚠️ Next Steps: Add Environment Variables

Your Railway deployment is live but needs configuration. Currently showing **0 Variables** set.

### Quick Setup (2 minutes)

#### Option 1: Via Railway CLI (Recommended)
```bash
cd /workspaces/QL

# Set Anthropic API key (REQUIRED)
railway variable set ANTHROPIC_API_KEY "sk-ant-your_key_here"

# Set Neo4j password (REQUIRED)
railway variable set NEO4J_PASSWORD "your_secure_password"

# Set Ollama base URL (if using external Ollama)
railway variable set OLLAMA_BASE_URL "http://ollama-server:11434"

# Verify
railway variable list
```

#### Option 2: Via Railway Dashboard
1. Go to https://railway.app
2. Select your project
3. Click **"Variables"** tab
4. Add each variable (see table below)

### Required Variables

| Variable | Value | Required | Example |
|----------|-------|----------|---------|
| `ANTHROPIC_API_KEY` | Your API key | ✅ YES | `sk-ant-xxxxx` |
| `NEO4J_PASSWORD` | Database password | ✅ YES | `SecurePass123!` |
| `OLLAMA_BASE_URL` | Ollama endpoint | ❌ Optional | `http://localhost:11434` |
| `DATABASE_URL` | PostgreSQL connection | ❌ Optional | `postgresql://user:pass@host/db` |

### Optional Variables (Already Set)

These are pre-configured in `deploy/railway.json`:

```
✓ PYTHONUNBUFFERED=1
✓ APP_ENV=production
✓ LOG_LEVEL=INFO
✓ API_HOST=0.0.0.0
✓ API_PORT=8000
✓ STREAMLIT_SERVER_PORT=8501
✓ STREAMLIT_SERVER_HEADLESS=true
✓ HIVE_BATCH_SIZE=3
✓ HIVE_INTERVAL=300
✓ OLLAMA_MODEL=llama3.1
```

## 🔍 Verify Deployment

After adding variables, verify your services are running:

```bash
# Check status
railway status

# View logs
railway logs --tail 50

# Test API
railway open  # Opens in browser

# Or manually
curl https://your-railway-domain.up.railway.app/system/health
```

## 📊 Current Deployment Config

```
Builder:        Dockerfile
Dockerfile:     ./Dockerfile
Start Command:  python orchestrator.py
Region:         europe-west4 (Belgium)
Replicas:       1
Restart Policy: on-failure (max 10 retries)
```

## 🚀 Expected Services

| Service | Port | URL |
|---------|------|-----|
| API (FastAPI) | 8000 | `https://your-domain.up.railway.app:8000` |
| Dashboard (Streamlit) | 8501 | `https://your-domain.up.railway.app:8501` |
| Health Check | 8000 | `https://your-domain.up.railway.app:8000/system/health` |

## 📋 Checklist

- [ ] Set ANTHROPIC_API_KEY
- [ ] Set NEO4J_PASSWORD
- [ ] Verify `railway variable list` shows variables
- [ ] Check logs: `railway logs`
- [ ] Test health endpoint
- [ ] Test API endpoints
- [ ] Access Streamlit dashboard
- [ ] Monitor worker processing

## 🔧 Troubleshooting

### "CrashLoopBackOff" or restart loop
**Cause**: Missing required environment variables  
**Solution**: Add ANTHROPIC_API_KEY and NEO4J_PASSWORD

```bash
railway variable set ANTHROPIC_API_KEY "your_key"
railway variable set NEO4J_PASSWORD "your_password"
railway redeploy
```

### "Module not found" errors
**Cause**: Dockerfile issues or missing dependencies  
**Solution**: Check logs and rebuild

```bash
railway logs
railway redeploy --force
```

### Health check failing
**Cause**: Services not ready yet  
**Solution**: Wait 30-60 seconds and retry

```bash
# Wait for startup
sleep 60
railway logs
```

## 📈 Monitoring

### View Real-time Logs
```bash
railway logs --follow
```

### Check Service Health
```bash
# Via API
curl https://your-domain/system/health

# Via CLI
railway status
```

### Get Project Info
```bash
railway list
railway info
```

## 🔄 Redeploy After Changes

After updating variables or code:

```bash
# Push code changes to git
git add .
git commit -m "Configuration update"
git push origin main

# Or manual redeploy
railway redeploy

# Force rebuild
railway redeploy --force
```

## 📞 Support

| Topic | Command |
|-------|---------|
| View logs | `railway logs` |
| Check status | `railway status` |
| List variables | `railway variable list` |
| Open dashboard | `railway open` |
| Redeploy | `railway redeploy` |
| Get help | `railway help` |

## ✅ Success Indicators

You'll know it's working when:

✅ `railway logs` shows no repeated error messages  
✅ `/system/health` returns HTTP 200  
✅ Dashboard loads in browser  
✅ API responds to requests  
✅ Worker logs show pattern processing  

---

## 🎯 What's Next?

1. **Immediate**: Add required environment variables (ANTHROPIC_API_KEY, NEO4J_PASSWORD)
2. **Verify**: Check logs and health endpoints
3. **Monitor**: Set up continuous health monitoring
4. **Optimize**: Adjust batch sizes and intervals based on performance
5. **Backup**: Configure database backups

---

**Need help?** 
- Railway Docs: https://docs.railway.app
- CLI Reference: `railway help`
- View logs: `railway logs --follow`

**Last command**: `railway up`  
**Next command**: `railway variable set ANTHROPIC_API_KEY "your_key"`
