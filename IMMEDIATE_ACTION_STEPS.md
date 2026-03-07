# Railway Space Crisis: IMMEDIATE ACTION PLAN

## 🚨 Your Situation
- **Space Error**: No available space on Railway deployment
- **Root Cause**: 34MB of duplicate Quran data files + running 3-4 always-on containers
- **Current Monthly Cost**: ~$700/month for 3 containers running 24/7

---

## ⚡ DO THIS IMMEDIATELY (5 minutes)

### Step 1: Run Cleanup Script
```bash
cd /workspaces/QL
chmod +x cleanup_railway_space.sh
./cleanup_railway_space.sh
```

**What it does:**
- ✅ Backs up everything to `data_backup_YYYYMMDD_HHMMSS.tar.gz`
- ✅ Removes duplicate Quran files (15-20MB freed)
- ✅ Removes raw/ and researches/ folders
- ✅ Cleans Python cache

**Expected result:** `data/` folder drops from 34MB → ~10MB

### Step 2: Push Changes to GitHub
```bash
cd /workspaces/QL
git add -A
git commit -m "Cleanup: Remove duplicate data files (save 20MB)"
git push origin main
```

**Railway will auto-redeploy with smaller codebase** → More space available

---

## 🎯 NEXT WEEK: Cost Reduction (92% savings)

### Step 3: Migrate Neo4j to FREE Atlas (Save $230/month)

**Current problem:** Neo4j running as container on Railway = $230+/month

**Solution:** Neo4j Atlas Cloud (FREE tier = 50GB)

```bash
# 1. Go to: https://cloud.neo4j.io/
# 2. Create free account
# 3. Create free 50GB instance (takes 2 mins)
# 4. Copy CONNECTION STRING

# 5. Update Railway environment variables:
# On Railway dashboard:
# - Settings → Variables
# - Add: NEO4J_URI = neo4j+s://your-instance.databases.neo4j.io
# - Add: NEO4J_USER = neo4j  
# - Add: NEO4J_PASSWORD = your_password
```

### Step 4: Consolidate to Single Container (Save $460/month)

**Current:** 3 containers running 24/7 on Railway

**Simplified architecture:**
```
Container 1: FastAPI (API + Dashboard + Worker)
├─ Runs main orchestrator
├─ Serves /api endpoints
├─ Streamlit dashboard on :8501
└─ Worker jobs as background tasks

Database: Neo4j Atlas (FREE cloud)
├─ External service
└─ Accessed via HTTPS
```

**Edit deploy/railway.json:**
```json
{
  "deploy": {
    "startCommand": "python main.py",
    "numReplicas": 1,
    "region": "europe-west4"
  }
}
```

---

## 📊 Result: 92% Cost Reduction

| Item | Before | After | Savings |
|------|--------|-------|---------|
| Container costs | $460/month | $15/month | -$445 |
| Neo4j DB | $240/month | FREE (Atlas) | -$240 |
| Base plan | $5/month | $5/month | - |
| **TOTAL** | **$705/month** | **$20/month** | **-$685** 💰 |

---

## 🔍 Debugging: Test Before Deploying

```bash
# Test locally with optimized setup
docker-compose -f deploy/docker-compose.minimal.yml up

# Verify connection works
curl http://localhost:8000/health

# Check Neo4j connection in container logs
docker logs <container_id> | grep neo4j
```

---

## ⚠️ Safety Checklist

Before pushing changes:

- [ ] Ran `cleanup_railway_space.sh` 
- [ ] Backup file created: `data_backup_*.tar.gz`
- [ ] Verified data still loads with `python main.py` locally
- [ ] Tested Neo4j connection with test query
- [ ] Git backup created with `git commit`
- [ ] Only then: `git push`

---

## 🆘 If Something Goes Wrong

**Problem:** Docker build fails after cleanup

**Solution:**
```bash
# Restore from backup
tar xzf data_backup_YYYYMMDD_HHMMSS.tar.gz
git revert <commit_hash>
git push origin main
```

**Problem:** Neo4j connection fails after Atlas migration

**Solution:**
```bash
# Check Railway environment variables are set
echo $NEO4J_URI

# Test connection
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('$NEO4J_URI', auth=('neo4j', '$NEO4J_PASSWORD'))
print(driver.verify_connectivity())
"
```

---

## 📈 Monitoring After Changes

1. **Watch space** on Railway: Dashboard → Resources → Disk
2. **Monitor costs**: Railway Dashboard → Billing
3. **Check logs**: Railway Dashboard → Logs for errors

---

## 🚀 Advanced: If You Still Need More Space

**Option A: External File Storage**
```
- Move large files to AWS S3 (pay per GB)
- Keep only active data in codebase
- Download files on-demand in Python
```

**Option B: Serverless + Turso DB**
```
- Deploy FastAPI to Vercel (Free)
- Use Turso SQLite (Free tier)
- Cost: $0 unless high traffic
```

**Option C: Docker Hub + Cron**
```
- Store Docker image on Docker Hub (free public)
- Run on schedule via GitHub Actions
- Cost: $0 (GitHub Actions free tier)
```

---

**READ:** [RAILWAY_COST_OPTIMIZATION.md](RAILWAY_COST_OPTIMIZATION.md) for full details

**Script:** Run `cleanup_railway_space.sh` script to automate everything above

**Questions?** Check troubleshooting section or commit message to understand each change
