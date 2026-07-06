<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="150"/>
  
  # API Reference
  **Dashboard REST API and Integration Endpoints**
  
  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

1. [API Overview](#api-overview)
2. [Dashboard Endpoints](#dashboard-endpoints)
3. [Status File API](#status-file-api)
4. [Configuration API](#configuration-api)
5. [WebSocket/SSE Streaming](#websocketsse-streaming)
6. [Error Handling](#error-handling)
7. [Integration Examples](#integration-examples)

---

## API Overview

### Base URL

```
http://localhost:8765
```

**Note:** Dashboard binds to `127.0.0.1` (localhost only) by default for security.

### Authentication

**Current:** None (localhost-only access)

**Future (v4.1+):** Optional API key authentication for remote access

### Response Format

**Success responses:**
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2026-07-06T14:30:15.123Z"
}
```

**Error responses:**
```json
{
  "success": false,
  "error": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2026-07-06T14:30:15.123Z"
}
```

---

## Dashboard Endpoints

### GET /health

**Description:** Health check endpoint for monitoring

**Request:**
```bash
curl -i http://localhost:8765/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "pid": 12345,
  "uptime_seconds": 3600,
  "version": "4.0.1"
}
```

**Use cases:**
- Load balancer health checks
- Monitoring systems (Prometheus, Datadog)
- Deployment validation

---

### GET /

**Description:** Main dashboard UI (redirects to /configure or /status)

**Request:**
```bash
curl -L http://localhost:8765/
```

**Response:** HTML page (redirects based on state)
- No workflows running → Redirects to `/configure`
- Workflows active → Redirects to `/status`

---

### GET /configure

**Description:** Configuration wizard and client management UI

**Request:**
```bash
curl http://localhost:8765/configure
```

**Response:** HTML page with:
- Authentication setup steps
- Client addition form
- Existing client list
- Launch workflow button

**UI Components:**
- NotebookLM OAuth button
- Drive OAuth setup wizard
- Client configuration form (name, Drive URL, industry, subsegments, mode)

---

### GET /status

**Description:** Real-time workflow monitoring dashboard

**Request:**
```bash
curl http://localhost:8765/status
```

**Response:** HTML page with:
- Live progress bars for each client
- Streaming logs via Server-Sent Events (SSE)
- Workflow statistics (time elapsed, quality scores)
- Status indicators (PENDING, IN_PROGRESS, COMPLETE, FAILED)

---

### GET /api/status

**Description:** JSON status summary for all workflows

**Request:**
```bash
curl http://localhost:8765/api/status
```

**Response (200 OK):**
```json
{
  "total_clients": 3,
  "running": 2,
  "completed": 1,
  "failed": 0,
  "clients": [
    {
      "client_id": "acme_corp",
      "client_name": "Acme Corporation",
      "status": "COMPLETE",
      "progress": 100,
      "phase": "Phase 5: Quality Validation",
      "quality_score": 8.5,
      "execution_time_min": 18.5,
      "sources_imported": 82,
      "mode": "fast"
    },
    {
      "client_id": "techco",
      "client_name": "TechCo Industries",
      "status": "IN_PROGRESS",
      "progress": 65,
      "phase": "Phase 4: Analysis Prompts",
      "quality_score": null,
      "execution_time_min": 12.3,
      "sources_imported": 75,
      "mode": "fast"
    }
  ]
}
```

**Polling interval:** 2-5 seconds recommended

---

### GET /stream-logs/{client_id}

**Description:** Server-Sent Events (SSE) stream for real-time logs

**Request:**
```bash
curl -N http://localhost:8765/stream-logs/acme_corp
```

**Response:** SSE stream
```
event: log
data: {"timestamp": "2026-07-06T14:30:15.123Z", "level": "INFO", "message": "Starting workflow for Acme Corporation"}

event: log
data: {"timestamp": "2026-07-06T14:30:20.456Z", "level": "INFO", "message": "Phase 1: Downloading PDFs from Drive"}

event: log
data: {"timestamp": "2026-07-06T14:30:45.789Z", "level": "INFO", "message": "Downloaded 8 PDFs (42 MB total)"}

event: status
data: {"status": "IN_PROGRESS", "progress": 15, "phase": "Phase 2: Creating NotebookLM Notebook"}

event: complete
data: {"status": "COMPLETE", "quality_score": 8.5, "execution_time_min": 18.5}
```

**Client-side JavaScript example:**
```javascript
const eventSource = new EventSource('/stream-logs/acme_corp');

eventSource.addEventListener('log', (event) => {
  const log = JSON.parse(event.data);
  console.log(`[${log.level}] ${log.message}`);
});

eventSource.addEventListener('status', (event) => {
  const status = JSON.parse(event.data);
  updateProgressBar(status.progress, status.phase);
});

eventSource.addEventListener('complete', (event) => {
  const result = JSON.parse(event.data);
  console.log(`Workflow complete! Quality score: ${result.quality_score}`);
  eventSource.close();
});

eventSource.addEventListener('error', (event) => {
  console.error('SSE connection error');
  eventSource.close();
});
```

---

### POST /api/launch-workflow

**Description:** Launch workflow for configured clients

**Request:**
```bash
curl -X POST http://localhost:8765/api/launch-workflow \
  -H "Content-Type: application/json" \
  -d '{
    "clients": ["acme_corp", "techco"],
    "mode": "fast"
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Workflow launched for 2 clients",
  "clients": ["acme_corp", "techco"],
  "mode": "fast",
  "estimated_completion_min": 20
}
```

**Response (400 Bad Request):**
```json
{
  "success": false,
  "error": "Client 'invalid_client' not found in configuration",
  "code": "CLIENT_NOT_FOUND"
}
```

---

### POST /api/stop-workflow/{client_id}

**Description:** Stop running workflow for specific client

**Request:**
```bash
curl -X POST http://localhost:8765/api/stop-workflow/acme_corp
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Workflow stopped for acme_corp",
  "client_id": "acme_corp"
}
```

---

## Status File API

### File Location

```
.multi_process_status/{client_id}.json
```

### Status File Schema

```json
{
  "client_id": "acme_corp",
  "client_name": "Acme Corporation",
  "status": "COMPLETE",
  "progress": 100,
  "phase": "Phase 5: Quality Validation",
  "phase_number": 5,
  "total_phases": 5,
  "start_time": "2026-07-06T14:12:30.123Z",
  "end_time": "2026-07-06T14:31:15.456Z",
  "execution_time_seconds": 1125,
  "mode": "fast",
  "error": null,
  "phases": {
    "phase_1": {
      "name": "PDF Download & Consolidation",
      "status": "COMPLETE",
      "start_time": "2026-07-06T14:12:30.123Z",
      "end_time": "2026-07-06T14:13:15.456Z",
      "duration_seconds": 45,
      "details": {
        "pdfs_downloaded": 8,
        "total_size_mb": 42,
        "consolidated_pdf": "docs/acme_corp/Acme Corporation-One.pdf"
      }
    },
    "phase_2": {
      "name": "Notebook Creation",
      "status": "COMPLETE",
      "start_time": "2026-07-06T14:13:15.456Z",
      "end_time": "2026-07-06T14:13:30.789Z",
      "duration_seconds": 15,
      "details": {
        "notebook_id": "notebook_abc123xyz",
        "sources_uploaded": 1
      }
    },
    "phase_3": {
      "name": "Research Queries",
      "status": "COMPLETE",
      "start_time": "2026-07-06T14:13:30.789Z",
      "end_time": "2026-07-06T14:18:45.123Z",
      "duration_seconds": 314,
      "details": {
        "queries_executed": 2,
        "sources_imported": 82
      }
    },
    "phase_4": {
      "name": "Analysis Prompts",
      "status": "COMPLETE",
      "start_time": "2026-07-06T14:18:45.123Z",
      "end_time": "2026-07-06T14:30:30.456Z",
      "duration_seconds": 705,
      "details": {
        "prompts_executed": 6,
        "analysis_generated": true
      }
    },
    "phase_5": {
      "name": "Quality Validation",
      "status": "COMPLETE",
      "start_time": "2026-07-06T14:30:30.456Z",
      "end_time": "2026-07-06T14:31:15.456Z",
      "duration_seconds": 45,
      "details": {
        "quality_score": 8.5,
        "completeness_checks": {
          "industry_analysis": "complete",
          "swot_analysis": "complete",
          "technology_trends": "complete",
          "competitive_analysis": "complete",
          "pain_points": "complete",
          "recommendations": "complete"
        }
      }
    }
  },
  "outputs": {
    "analysis_file": "docs_generated/acme_corp/Acme Corporation_Analysis.txt",
    "notebooklm_link": "docs_generated/acme_corp/NotebookLM_Link.txt",
    "quality_score": "docs_generated/acme_corp/Quality_Score.json"
  }
}
```

### Reading Status Files

**Python example:**
```python
import json
from pathlib import Path

def get_client_status(client_id):
    status_file = Path(f".multi_process_status/{client_id}.json")
    
    if not status_file.exists():
        return {"error": "Status file not found"}
    
    with open(status_file) as f:
        return json.load(f)

# Usage
status = get_client_status("acme_corp")
print(f"Status: {status['status']}")
print(f"Progress: {status['progress']}%")
print(f"Quality Score: {status['phases']['phase_5']['details']['quality_score']}")
```

**Bash example:**
```bash
# Check if workflow complete
if jq -e '.status == "COMPLETE"' .multi_process_status/acme_corp.json > /dev/null; then
  echo "Workflow complete!"
  quality=$(jq '.phases.phase_5.details.quality_score' .multi_process_status/acme_corp.json)
  echo "Quality score: $quality"
fi
```

---

## Configuration API

### GET /api/config

**Description:** Get current vars.py configuration

**Request:**
```bash
curl http://localhost:8765/api/config
```

**Response (200 OK):**
```json
{
  "success": true,
  "config": {
    "clients": ["acme_corp", "techco"],
    "mode": "fast",
    "persona": "Red Hat solutions architect",
    "dashboard_port": 8765,
    "acme_corp": {
      "name": "Acme Corporation",
      "folder": "https://drive.google.com/drive/folders/1A2B3C...",
      "industry": "pharmaceuticals",
      "subsegments": "drug discovery, clinical trials"
    },
    "techco": {
      "name": "TechCo Industries",
      "folder": "https://drive.google.com/drive/folders/1F7G8H...",
      "industry": "technology",
      "subsegments": "cloud, AI, DevOps"
    }
  }
}
```

---

### POST /api/config/add-client

**Description:** Add new client to configuration

**Request:**
```bash
curl -X POST http://localhost:8765/api/config/add-client \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "newcorp",
    "client_name": "NewCorp Inc",
    "folder_url": "https://drive.google.com/drive/folders/1X2Y3Z...",
    "industry": "financial services",
    "subsegments": "banking, fintech",
    "mode": "fast"
  }'
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Client 'newcorp' added to configuration",
  "client_id": "newcorp"
}
```

---

## WebSocket/SSE Streaming

### Server-Sent Events (SSE)

**Connection:**
```javascript
const eventSource = new EventSource(`http://localhost:8765/stream-logs/${clientId}`);
```

**Event Types:**
- `log` - Log message
- `status` - Status update
- `progress` - Progress percentage
- `complete` - Workflow completion
- `error` - Error occurred

**Reconnection:**
```javascript
eventSource.addEventListener('error', (event) => {
  console.error('Connection lost, reconnecting in 3s...');
  setTimeout(() => {
    eventSource = new EventSource(`/stream-logs/${clientId}`);
  }, 3000);
});
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Workflow launched successfully |
| 400 | Bad Request | Invalid client ID or missing parameters |
| 404 | Not Found | Client not found in configuration |
| 500 | Internal Server Error | Dashboard crash or Python exception |
| 503 | Service Unavailable | Dashboard not running |

### Error Response Format

```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    "parameter": "client_id",
    "value": "invalid_client",
    "expected": "One of: ['acme_corp', 'techco']"
  },
  "timestamp": "2026-07-06T14:30:15.123Z"
}
```

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `CLIENT_NOT_FOUND` | Client ID not in vars.py | Add client via /configure or edit vars.py |
| `AUTH_FAILED` | OAuth tokens invalid | Re-authenticate via /configure |
| `DRIVE_ACCESS_DENIED` | Cannot access Drive folder | Check folder permissions and OAuth scopes |
| `WORKFLOW_RUNNING` | Workflow already in progress | Wait for completion or stop existing workflow |
| `QUOTA_EXCEEDED` | NotebookLM API quota exceeded | Wait for quota reset or increase delays |
| `INVALID_MODE` | Mode not 'fast' or 'deep' | Use valid mode value |

---

## Integration Examples

### Slack Notification Webhook

```python
import requests
import json

def send_slack_notification(client_id, status):
    """Send workflow completion notification to Slack"""
    
    # Read status
    with open(f'.multi_process_status/{client_id}.json') as f:
        workflow = json.load(f)
    
    # Prepare Slack message
    message = {
        "text": f"Project APE Workflow Complete: {workflow['client_name']}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{workflow['client_name']}* workflow completed"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Status:*\n{workflow['status']}"},
                    {"type": "mrkdwn", "text": f"*Quality Score:*\n{workflow['phases']['phase_5']['details']['quality_score']}"},
                    {"type": "mrkdwn", "text": f"*Execution Time:*\n{workflow['execution_time_seconds']/60:.1f} min"},
                    {"type": "mrkdwn", "text": f"*Sources:*\n{workflow['phases']['phase_3']['details']['sources_imported']}"}
                ]
            }
        ]
    }
    
    # Send to Slack
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    response = requests.post(webhook_url, json=message)
    
    return response.status_code == 200

# Usage
send_slack_notification("acme_corp", "COMPLETE")
```

---

### Salesforce Integration

```python
from simple_salesforce import Salesforce

def upload_to_salesforce(client_id, opportunity_id):
    """Upload Project APE analysis to Salesforce Opportunity"""
    
    # Read generated analysis
    with open(f'docs_generated/{client_id}/Analysis.txt') as f:
        analysis = f.read()
    
    # Read quality score
    with open(f'docs_generated/{client_id}/Quality_Score.json') as f:
        quality = json.load(f)
    
    # Connect to Salesforce
    sf = Salesforce(
        username='user@company.com',
        password='password',
        security_token='token'
    )
    
    # Update Opportunity
    sf.Opportunity.update(opportunity_id, {
        'Project_APE_Analysis__c': analysis[:32000],  # Text field limit
        'Quality_Score__c': quality['overall_score'],
        'Sources_Imported__c': quality['sources']['total'],
        'Analysis_Date__c': datetime.now().isoformat()
    })
    
    print(f"Uploaded analysis to Opportunity {opportunity_id}")

# Usage
upload_to_salesforce("acme_corp", "006XXXXXXXXXXXXXXX")
```

---

### Monitoring with Prometheus

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
import json

# Metrics
workflow_total = Counter('project_ape_workflows_total', 'Total workflows executed', ['client_id', 'mode', 'status'])
workflow_duration = Histogram('project_ape_workflow_duration_seconds', 'Workflow execution time', ['client_id', 'mode'])
quality_score = Gauge('project_ape_quality_score', 'Quality score', ['client_id'])
sources_imported = Gauge('project_ape_sources_imported', 'External sources imported', ['client_id'])

def collect_metrics():
    """Collect metrics from status files"""
    status_dir = Path('.multi_process_status')
    
    for status_file in status_dir.glob('*.json'):
        with open(status_file) as f:
            status = json.load(f)
        
        client_id = status['client_id']
        mode = status['mode']
        
        # Increment workflow counter
        workflow_total.labels(
            client_id=client_id,
            mode=mode,
            status=status['status']
        ).inc()
        
        # Record duration
        if status['status'] == 'COMPLETE':
            workflow_duration.labels(
                client_id=client_id,
                mode=mode
            ).observe(status['execution_time_seconds'])
            
            # Update quality score
            quality_score.labels(client_id=client_id).set(
                status['phases']['phase_5']['details']['quality_score']
            )
            
            # Update sources
            sources_imported.labels(client_id=client_id).set(
                status['phases']['phase_3']['details']['sources_imported']
            )

# Start Prometheus metrics server
start_http_server(9090)

# Collect metrics every 60 seconds
while True:
    collect_metrics()
    time.sleep(60)
```

**Prometheus config:**
```yaml
scrape_configs:
  - job_name: 'project-ape'
    static_configs:
      - targets: ['localhost:9090']
```

---

<div align="center">
  
  **API Integration**
  
  Use with [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for detailed integration examples.
  
  ---
  
  *Last Updated: July 2026 | Version 4.0.1*
  
</div>
