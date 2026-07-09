<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Account Intelligence - King Kong Logo" width="150"/>
  
  # Operations Runbook
  **Day-to-Day Operations and Incident Response**
  
  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

1. [Operations Overview](#operations-overview)
2. [Daily Health Checks](#daily-health-checks)
3. [Routine Maintenance](#routine-maintenance)
4. [Credential Management](#credential-management)
5. [Log Management](#log-management)
6. [Incident Response](#incident-response)
7. [Performance Monitoring](#performance-monitoring)
8. [Backup and Recovery](#backup-and-recovery)
9. [Capacity Planning](#capacity-planning)

---

## Operations Overview

### Operational Model

**Roles and Responsibilities:**
- **Platform Owner:** Overall system health, upgrades, capacity planning
- **Operators:** Daily health checks, incident response, user support
- **Users:** Self-service via web UI, escalate issues to operators

**Service Level Objectives (SLOs):**
- Dashboard availability: 99.5% (3.6 hours downtime/month acceptable)
- Workflow success rate: 95%+ (Fast mode), 90%+ (Deep mode)
- Average workflow time: <25 min (Fast), <70 min (Deep)
- Mean time to resolution (MTTR): <2 hours for P1 incidents

---

## Daily Health Checks

### Morning Checklist (5 minutes)

**1. Dashboard Status:**
```bash
# Check dashboard is running
curl -f http://localhost:8765/health || echo "ALERT: Dashboard down"

# Expected response: {"status": "healthy", "pid": 12345}
```

**2. Recent Workflow Status:**
```bash
# Check workflows from last 24 hours
find .multi_process_status/ -name "*.json" -mtime -1 -exec cat {} \;

# Look for status: "COMPLETE" (success) vs "FAILED"
```

**3. Error Log Review:**
```bash
# Check for critical errors in last 24 hours
grep -i "ERROR\|CRITICAL\|FAILED" logs/*.log | grep "$(date +%Y-%m-%d)"

# Expected: Few or no errors
```

**4. OAuth Token Health:**
```bash
# NotebookLM credentials exist and not expired
ls -la ~/.notebooklm/credentials.json | grep "$(date +%b\ %e)"

# Drive OAuth token expiry check
python3 -c "
import json
from datetime import datetime
with open('credentials/token_drive.json') as f:
    token = json.load(f)
    expiry = datetime.fromisoformat(token['expiry'].replace('Z', '+00:00'))
    days_left = (expiry - datetime.now()).days
    print(f'Drive token expires in {days_left} days')
    if days_left < 7:
        print('WARNING: Drive token expiring soon, re-auth needed')
"
```

**5. Disk Space Check:**
```bash
# Check available disk space
df -h | grep -E "/$|/app"

# Alert if <10% free space
```

### Escalation Criteria

**Escalate to Platform Owner if:**
- Dashboard down >15 minutes
- Workflow success rate <80% (5+ failures in 24 hours)
- Disk space <5% remaining
- OAuth tokens expired and cannot refresh
- Performance degradation >50% (workflows taking 2x normal time)

---

## Routine Maintenance

### Weekly Tasks (30 minutes)

**1. Log Rotation:**
```bash
# Rotate logs older than 7 days
cd logs/
for log in *.log; do
  if [ "$(find "$log" -mtime +7)" ]; then
    gzip "$log"
    mv "$log.gz" archive/
  fi
done
```

**2. Cache Cleanup:**
```bash
# Clear Drive cache older than 14 days
find .drive_cache/ -type f -mtime +14 -delete

# Expected: Reclaim 500MB-2GB
```

**3. Status File Cleanup:**
```bash
# Archive completed workflow status files older than 30 days
find .multi_process_status/ -name "*.json" -mtime +30 \
  -exec mv {} .multi_process_status/archive/ \;
```

**4. Performance Metrics:**
```bash
# Generate weekly workflow stats
cat logs/*.log | grep "Workflow complete" | \
  awk '{print $5}' | \
  awk '{sum+=$1; count++} END {print "Avg time:", sum/count, "min"}'

# Track quality score trends
cat docs_generated/*/Quality_Score.json | \
  jq '.overall_score' | \
  awk '{sum+=$1; count++} END {print "Avg quality:", sum/count}'
```

### Monthly Tasks (1-2 hours)

**1. Dependency Updates:**
```bash
# Update Python packages
source ~/.project-ape-venv/bin/activate
pip list --outdated
pip install --upgrade -r requirements.txt

# Test after upgrade
python3 launch-project-ape.py
```

**2. Container Image Update:**
```bash
# Pull latest image
podman pull quay.io/jasoande/project_ape/project-ape:latest

# Security scan
trivy image quay.io/jasoande/project_ape/project-ape:latest

# Expected: No HIGH or CRITICAL vulnerabilities
```

**3. Backup Verification:**
```bash
# Test restore from last backup
./test-restore-backup.sh /backup/project-ape/latest

# Verify OAuth tokens work after restore
```

**4. Capacity Review:**
```bash
# Review growth trends
ls -lhR docs_generated/ | tail -1  # Total size
du -sh logs/  # Log volume
df -h  # Disk usage trend
```

### Quarterly Tasks (2-4 hours)

**1. OAuth Credential Rotation:**
```bash
# Rotate Drive OAuth (expires every 90 days)
python3 setup-oauth-drive.py

# Test workflow with new credentials
```

**2. Security Audit:**
```bash
# Review access logs
grep "Authentication" logs/security.log | sort | uniq -c

# Check file permissions
find ~/.notebooklm credentials/ -type f -not -perm 600
# Expected: Empty (all files should be 0600)

# Verify SELinux contexts (RHEL/Fedora)
ls -Z ~/.notebooklm/credentials.json
```

**3. Performance Baseline:**
```bash
# Run benchmark workflow
time ./ape-run.sh --vars ./benchmark.py --clients benchmark_client --mode fast

# Compare to historical baseline (should be within 10%)
```

---

## Credential Management

### Token Refresh Schedule

**NotebookLM:**
- **Access token:** Auto-refreshes hourly (no action needed)
- **Refresh token:** Monitor for revocation (rare)
- **Manual refresh:** Only if `notebooklm login` returns error

**Google Drive:**
- **Access token:** Auto-refreshes hourly
- **Refresh token:** Expires every 90 days
- **Manual refresh:** Required every ~85 days (calendar reminder)

**Gemini API Key:**
- **Expiry:** None (unless manually revoked)
- **Rotation:** Annually recommended

### Token Refresh Procedures

**NotebookLM Re-Authentication:**
```bash
# Via Web UI (recommended)
python3 launch-project-ape.py
# http://localhost:8765/configure → Click "Authenticate NotebookLM"

# Via Terminal
notebooklm auth logout
notebooklm login
./setup-credentials.sh  # If using containers
```

**Drive OAuth Renewal:**
```bash
# Via Web UI
# http://localhost:8765/configure → Click "Setup Drive OAuth"
# Upload credentials.json → Generate Token

# Via Terminal
rm credentials/token_drive.json
python3 setup-oauth-drive.py
```

**Verification:**
```bash
# Test NotebookLM access
notebooklm list

# Test Drive access
curl -H "Authorization: Bearer $(jq -r .token credentials/token_drive.json)" \
  "https://www.googleapis.com/drive/v3/about?fields=user"
```

---

## Log Management

### Log Files

**Primary Logs:**
- `logs/{client_id}.log` - Per-client workflow execution
- `logs/dashboard.log` - Flask server logs
- `.multi_process_status/{client_id}.json` - Real-time workflow status

**Log Rotation Strategy:**
- **Daily:** Compress logs >1 MB
- **Weekly:** Move logs >7 days to archive/
- **Monthly:** Delete archive logs >90 days

**Rotation Script:**
```bash
#!/bin/bash
# log-rotation.sh

LOG_DIR="logs"
ARCHIVE_DIR="logs/archive"
COMPRESS_AGE=1  # Days
ARCHIVE_AGE=7
DELETE_AGE=90

# Create archive directory
mkdir -p "$ARCHIVE_DIR"

# Compress large recent logs
find "$LOG_DIR" -maxdepth 1 -name "*.log" -size +1M -mtime +"$COMPRESS_AGE" \
  -exec gzip {} \;

# Move old logs to archive
find "$LOG_DIR" -maxdepth 1 \( -name "*.log" -o -name "*.log.gz" \) -mtime +"$ARCHIVE_AGE" \
  -exec mv {} "$ARCHIVE_DIR/" \;

# Delete very old archives
find "$ARCHIVE_DIR" -type f -mtime +"$DELETE_AGE" -delete

echo "Log rotation complete: $(date)"
```

**Automate with Cron:**
```bash
# Run daily at 2 AM
0 2 * * * /opt/project-ape/log-rotation.sh >> /var/log/project-ape-rotation.log 2>&1
```

### Log Analysis

**Common Log Queries:**
```bash
# Find failed workflows
grep "FAILED" logs/*.log

# Count retries per client
grep "Retry attempt" logs/{client_id}.log | wc -l

# Average workflow duration
grep "Workflow complete in" logs/*.log | awk '{sum+=$5; count++} END {print sum/count " min"}'

# Top error messages
grep ERROR logs/*.log | cut -d: -f4- | sort | uniq -c | sort -rn | head -10

# API quota errors
grep -i "quota\|rate limit" logs/*.log
```

---

## Incident Response

### Incident Severity Levels

| Priority | Impact | Response Time | Examples |
|----------|--------|---------------|----------|
| **P1 - Critical** | Service down, multiple users affected | <30 min | Dashboard crashed, OAuth tokens revoked |
| **P2 - High** | Degraded service, some users affected | <2 hours | Slow workflows, high error rate |
| **P3 - Medium** | Minor impact, workaround available | <24 hours | Single client failure, quality score low |
| **P4 - Low** | No user impact | <72 hours | Cosmetic UI issue, verbose logging |

### Incident Response Playbooks

#### P1: Dashboard Not Accessible

**Symptoms:** HTTP 500, connection refused, timeout

**Triage (5 minutes):**
```bash
# 1. Check process running
ps aux | grep "dashboard/server.py"

# 2. Check port binding
lsof -i :8765

# 3. Check recent errors
tail -50 dashboard-startup.log
```

**Resolution:**
```bash
# 1. Restart dashboard
pkill -f "dashboard/server.py"
python3 launch-project-ape.py

# 2. Verify health
curl -f http://localhost:8765/health

# 3. Check logs
tail -f logs/dashboard.log
```

**Escalation:** If restart fails after 2 attempts, escalate to Platform Owner

---

#### P1: OAuth Authentication Failure

**Symptoms:** "Token refresh failed", "Invalid credentials", 401/403 errors

**Triage:**
```bash
# 1. Check credential files exist
ls -la ~/.notebooklm/credentials.json
ls -la credentials/token_drive.json

# 2. Check file permissions
stat -c "%a %n" ~/.notebooklm/credentials.json  # Should be 600

# 3. Test token validity
notebooklm list  # NotebookLM
# Drive: Check expiry in token_drive.json
```

**Resolution:**
```bash
# 1. NotebookLM re-auth
notebooklm auth logout
notebooklm login

# 2. Drive OAuth refresh
python3 setup-oauth-drive.py

# 3. Verify
notebooklm list
curl -H "Authorization: Bearer $(jq -r .token credentials/token_drive.json)" \
  "https://www.googleapis.com/drive/v3/about?fields=user"
```

**Prevention:** Set calendar reminder for Drive OAuth renewal every 85 days

---

#### P2: High Workflow Failure Rate

**Symptoms:** >20% workflows failing in last 24 hours

**Triage:**
```bash
# 1. Count failures
find .multi_process_status/ -name "*.json" -mtime -1 \
  -exec jq -r '.status' {} \; | grep -c FAILED

# 2. Identify common errors
grep ERROR logs/*.log | tail -20

# 3. Check API status
curl https://status.cloud.google.com/incidents.json
```

**Common Causes:**
- API quota exceeded → Wait for quota reset or increase delays
- Network issues → Check internet connectivity
- Malformed Drive URLs → Validate folder URLs
- Insufficient disk space → Clear cache, expand disk

**Resolution:**
```bash
# If quota exceeded, increase delays
# Edit vars.py:
TIMINGS = {
    'ask_prompt_delay': (15.0, 20.0),  # Increase from (8, 12)
    'chat_prompt_delay': (8.0, 12.0),  # Increase from (5, 8)
}

# Restart workflows
```

---

## Performance Monitoring

### Key Performance Indicators (KPIs)

**1. Workflow Success Rate:**
```bash
# Target: >95% (Fast mode), >90% (Deep mode)
success=$(find .multi_process_status/ -name "*.json" -mtime -1 -exec jq -r '.status' {} \; | grep -c COMPLETE)
total=$(find .multi_process_status/ -name "*.json" -mtime -1 | wc -l)
echo "Success rate: $(echo "scale=2; $success/$total*100" | bc)%"
```

**2. Average Execution Time:**
```bash
# Target: <25 min (Fast), <70 min (Deep)
grep "Workflow complete" logs/*.log | grep "$(date +%Y-%m-%d)" | \
  awk '{print $5}' | awk '{sum+=$1; count++} END {print "Avg:", sum/count, "min"}'
```

**3. Quality Score Distribution:**
```bash
# Target: >80% scores above 8.0
find docs_generated/ -name "Quality_Score.json" -mtime -7 -exec jq '.overall_score' {} \; | \
  awk '{if($1>=8.0) good++; total++} END {print "High quality:", good/total*100 "%"}'
```

**4. API Error Rate:**
```bash
# Target: <5% (Fast mode), <30% (Deep mode)
errors=$(grep -c "Retry attempt" logs/*.log)
total=$(grep -c "API call" logs/*.log)
echo "Error rate: $(echo "scale=2; $errors/$total*100" | bc)%"
```

### Performance Alerts

**Set up alerts for:**
- Workflow time >40 min (Fast mode) or >90 min (Deep mode)
- Success rate <90% over 24-hour period
- Disk space <10% remaining
- Dashboard response time >2 seconds

---

## Backup and Recovery

### Backup Frequency

**Daily (automated):**
- OAuth credentials
- vars.py configuration
- Status files

**Weekly (automated):**
- Generated outputs (docs_generated/)
- Recent logs (last 7 days)

**Monthly (manual):**
- Full system backup
- Disaster recovery test

### Backup Script

```bash
#!/bin/bash
# backup-daily.sh

BACKUP_ROOT="/backup/project-ape"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

mkdir -p "$BACKUP_DIR"/{credentials,config,status,outputs}

# Credentials (critical)
cp -r ~/.notebooklm "$BACKUP_DIR/credentials/"
cp -r credentials "$BACKUP_DIR/credentials/"

# Configuration
cp vars.py "$BACKUP_DIR/config/"

# Status files (last 7 days)
find .multi_process_status/ -name "*.json" -mtime -7 \
  -exec cp {} "$BACKUP_DIR/status/" \;

# Outputs (conditional - can be regenerated)
if [ "$1" == "--with-outputs" ]; then
  tar -czf "$BACKUP_DIR/outputs/docs_generated.tar.gz" docs_generated/
fi

# Prune old backups (keep last 30 days)
find "$BACKUP_ROOT" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;

echo "Backup complete: $BACKUP_DIR"
```

**Schedule:**
```bash
# Crontab entry - daily at 1 AM
0 1 * * * /opt/project-ape/backup-daily.sh

# Weekly with outputs - Sunday 1 AM
0 1 * * 0 /opt/project-ape/backup-daily.sh --with-outputs
```

### Recovery Test Procedure

**Monthly DR Test:**
```bash
# 1. Select recent backup
BACKUP_DIR="/backup/project-ape/$(ls -t /backup/project-ape | head -1)"

# 2. Simulate fresh install
rm -rf ~/.project-ape-test
mkdir ~/.project-ape-test

# 3. Restore credentials
cp -r "$BACKUP_DIR/credentials/.notebooklm" ~/.project-ape-test/
cp -r "$BACKUP_DIR/credentials/credentials" ~/.project-ape-test/

# 4. Verify tokens work
notebooklm list --credentials ~/.project-ape-test/.notebooklm/credentials.json

# 5. Test workflow
cp "$BACKUP_DIR/config/vars.py" ./vars-test.py
./ape-run.sh --vars ./vars-test.py --clients test_client --mode fast

# 6. Document results
echo "DR test passed: $(date)" >> dr-test-log.txt
```

---

## Capacity Planning

### Resource Usage Trends

**Monitor monthly:**
```bash
# Disk usage growth
du -sh docs_generated/ logs/ .drive_cache/

# Workflow volume
find .multi_process_status/ -name "*.json" -mtime -30 | wc -l

# Average resource utilization
top -bn1 | grep "python3" | awk '{print $9}' | head -1  # CPU %
free -h | grep Mem | awk '{print $3}'  # Memory used
```

**Capacity Thresholds:**
- Disk: Alert at 80% full, upgrade at 90%
- Memory: Alert at 75% utilization
- CPU: Alert at 85% sustained for >10 minutes
- Workflow queue: Alert if >10 pending clients

### Scaling Recommendations

**Vertical Scaling (single instance):**
- 0-50 workflows/month: 2 vCPU, 4 GB RAM, 20 GB disk
- 50-200 workflows/month: 4 vCPU, 8 GB RAM, 50 GB disk
- 200-500 workflows/month: 8 vCPU, 16 GB RAM, 100 GB disk

**Horizontal Scaling (multi-instance):**
- >500 workflows/month: Deploy Kubernetes cluster
- Shared NFS/EFS for logs and outputs
- Load balancer with session affinity
- Auto-scaling based on queue depth

---

<div align="center">
  
  **Operational Excellence**
  
  Follow this runbook with [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) and [SECURITY_GUIDE.md](SECURITY_GUIDE.md)
  
  ---
  
  *Last Updated: July 2026 | Version 4.0.1*
  
</div>
