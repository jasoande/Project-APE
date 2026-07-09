<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Account Intelligence - King Kong Logo" width="150"/>
  
  # Integration Guide
  **Connecting Account Intelligence to External Systems**
  
  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

1. [Integration Overview](#integration-overview)
2. [CRM Integrations](#crm-integrations)
3. [Workflow Automation](#workflow-automation)
4. [Notification Systems](#notification-systems)
5. [Document Management](#document-management)
6. [Monitoring Integration](#monitoring-integration)
7. [Custom Integrations](#custom-integrations)

---

## Integration Overview

### Integration Patterns

**1. Event-Driven (Recommended)**
- Monitor status files for changes
- Trigger actions on workflow completion
- Asynchronous, non-blocking

**2. Polling**
- Periodic API status checks
- Simple to implement
- Higher latency

**3. Webhook (Future)**
- Account Intelligence calls external endpoint
- Real-time notifications
- Requires external endpoint

### Common Integration Points

```
┌──────────────┐
│  Trigger     │  CRM, Calendar, Email
│  Sources     │  → Start workflow
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Account Intelligence  │  Execute workflow
│  Workflow    │  15-60 minutes
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Outputs     │  → Salesforce, Slack, SharePoint
│ Distribution │     Email, Confluence, PowerPoint
└──────────────┘
```

---

## CRM Integrations

### Salesforce Integration

**Use Case:** Upload analysis to Opportunity records

**Prerequisites:**
```bash
pip install simple-salesforce
```

**Implementation:**
```python
# salesforce_integration.py

from simple_salesforce import Salesforce
import json
from pathlib import Path

class SalesforceIntegration:
    def __init__(self, username, password, security_token):
        self.sf = Salesforce(
            username=username,
            password=password,
            security_token=security_token
        )
    
    def upload_analysis(self, client_id, opportunity_id):
        """Upload Account Intelligence analysis to Salesforce Opportunity"""
        
        # Read analysis
        analysis_file = Path(f'docs_generated/{client_id}/Analysis.txt')
        with open(analysis_file) as f:
            analysis = f.read()
        
        # Read quality score
        quality_file = Path(f'docs_generated/{client_id}/Quality_Score.json')
        with open(quality_file) as f:
            quality = json.load(f)
        
        # Read NotebookLM link
        link_file = Path(f'docs_generated/{client_id}/NotebookLM_Link.txt')
        with open(link_file) as f:
            notebooklm_link = f.read().strip()
        
        # Update Opportunity custom fields
        self.sf.Opportunity.update(opportunity_id, {
            'Project_APE_Analysis__c': analysis[:32000],  # Long text field limit
            'Quality_Score__c': quality['overall_score'],
            'Sources_Count__c': quality['sources']['total'],
            'NotebookLM_Link__c': notebooklm_link,
            'Analysis_Date__c': quality.get('timestamp', ''),
            'Execution_Time__c': quality.get('execution_time', '')
        })
        
        print(f"✓ Analysis uploaded to Opportunity {opportunity_id}")
        return True
    
    def create_task(self, client_id, opportunity_id):
        """Create follow-up task for account team"""
        
        quality_file = Path(f'docs_generated/{client_id}/Quality_Score.json')
        with open(quality_file) as f:
            quality = json.load(f)
        
        task = self.sf.Task.create({
            'WhatId': opportunity_id,
            'Subject': f'Review Account Intelligence Analysis: {quality["client_name"]}',
            'Description': f'Quality Score: {quality["overall_score"]}/10\n'
                          f'Sources: {quality["sources"]["total"]}\n'
                          f'Review analysis and identify next steps.',
            'ActivityDate': datetime.now().date().isoformat(),
            'Priority': 'High' if quality['overall_score'] >= 8.0 else 'Normal'
        })
        
        print(f"✓ Task created: {task['id']}")
        return task['id']

# Usage
sf_integration = SalesforceIntegration(
    username='user@company.com',
    password='password',
    security_token='security_token'
)

# Workflow completion hook
def on_workflow_complete(client_id):
    opportunity_id = get_opportunity_id(client_id)  # Your mapping logic
    sf_integration.upload_analysis(client_id, opportunity_id)
    sf_integration.create_task(client_id, opportunity_id)
```

---

### HubSpot Integration

**Use Case:** Enrich deal records with account intelligence

**Prerequisites:**
```bash
pip install hubspot-api-client
```

**Implementation:**
```python
from hubspot import HubSpot
from hubspot.crm.deals import ApiException

class HubSpotIntegration:
    def __init__(self, access_token):
        self.client = HubSpot(access_token=access_token)
    
    def update_deal(self, client_id, deal_id):
        """Update HubSpot deal with Account Intelligence insights"""
        
        # Read outputs
        with open(f'docs_generated/{client_id}/Analysis.txt') as f:
            analysis = f.read()
        
        with open(f'docs_generated/{client_id}/Quality_Score.json') as f:
            quality = json.load(f)
        
        # Update deal properties
        properties = {
            "project_ape_quality_score": quality['overall_score'],
            "project_ape_sources": quality['sources']['total'],
            "project_ape_analysis_summary": analysis[:5000],  # First 5000 chars
            "project_ape_last_updated": datetime.now().isoformat()
        }
        
        try:
            self.client.crm.deals.basic_api.update(
                deal_id=deal_id,
                simple_public_object_input={"properties": properties}
            )
            print(f"✓ Deal {deal_id} updated")
        except ApiException as e:
            print(f"✗ HubSpot API error: {e}")

# Usage
hubspot = HubSpotIntegration(access_token='your_token')
hubspot.update_deal('acme_corp', '123456789')
```

---

## Workflow Automation

### Apache Airflow DAG

**Use Case:** Scheduled weekly account research

**Implementation:**
```python
# dags/project_ape_weekly.py

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'sales-ops',
    'depends_on_past': False,
    'email': ['sales-ops@company.com'],
    'email_on_failure': True,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'project_ape_weekly_research',
    default_args=default_args,
    description='Weekly account research via Account Intelligence',
    schedule_interval='0 2 * * 1',  # Monday 2 AM
    start_date=datetime(2026, 1, 1),
    catchup=False,
)

# Task 1: Run Account Intelligence workflow
run_workflow = BashOperator(
    task_id='run_project_ape',
    bash_command='cd /opt/project-ape && ./ape-run.sh --vars vars-weekly.py --mode fast',
    dag=dag,
)

# Task 2: Upload to Salesforce
def upload_to_crm(**context):
    from salesforce_integration import SalesforceIntegration
    sf = SalesforceIntegration(username='...', password='...', security_token='...')
    
    clients = ['acme_corp', 'techco', 'pharma_client']
    for client_id in clients:
        opportunity_id = get_opportunity_mapping(client_id)
        sf.upload_analysis(client_id, opportunity_id)

upload_crm = PythonOperator(
    task_id='upload_to_salesforce',
    python_callable=upload_to_crm,
    dag=dag,
)

# Task 3: Send summary email
send_email = BashOperator(
    task_id='send_summary_email',
    bash_command='python /opt/project-ape/integrations/send_summary_email.py',
    dag=dag,
)

# Task dependencies
run_workflow >> upload_crm >> send_email
```

---

### Zapier Integration

**Use Case:** No-code automation for SMB users

**Setup:**

**1. Trigger: Schedule (Weekly)**
- Zapier Schedule trigger: Every Monday 9 AM

**2. Action: Webhook to Start Workflow**
```
POST http://your-server.com:8765/api/launch-workflow
Content-Type: application/json

{
  "clients": ["acme_corp", "techco"],
  "mode": "fast"
}
```

**3. Delay: Wait for Completion**
- Zapier Delay: 25 minutes

**4. Action: Get Status**
```
GET http://your-server.com:8765/api/status
```

**5. Filter: Only if Complete**
- Zapier Filter: `status == "COMPLETE"`

**6. Action: Send Slack Notification**
- Zapier Slack: Post to #sales-intelligence channel

---

## Notification Systems

### Slack Integration

**Use Case:** Real-time workflow notifications

**Implementation:**
```python
# integrations/slack_notifier.py

import requests
import json

class SlackNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_start_notification(self, client_name, mode):
        """Notify workflow started"""
        message = {
            "text": f"🚀 Account Intelligence workflow started",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Account Intelligence Workflow Started*\n"
                               f"Client: {client_name}\n"
                               f"Mode: {mode}\n"
                               f"Expected completion: {15 if mode=='fast' else 60} minutes"
                    }
                }
            ]
        }
        requests.post(self.webhook_url, json=message)
    
    def send_complete_notification(self, client_id):
        """Notify workflow completed with quality score"""
        
        # Read quality score
        with open(f'docs_generated/{client_id}/Quality_Score.json') as f:
            quality = json.load(f)
        
        # Emoji based on quality score
        emoji = "🎉" if quality['overall_score'] >= 8.5 else "✅" if quality['overall_score'] >= 7.5 else "⚠️"
        
        message = {
            "text": f"{emoji} Account Intelligence workflow complete: {quality['client_name']}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{emoji} {quality['client_name']} Analysis Complete*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Quality Score:*\n{quality['overall_score']}/10"},
                        {"type": "mrkdwn", "text": f"*Sources:*\n{quality['sources']['total']}"},
                        {"type": "mrkdwn", "text": f"*Execution Time:*\n{quality['execution_time']}"},
                        {"type": "mrkdwn", "text": f"*Mode:*\n{quality['mode'].upper()}"}
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "View Analysis"},
                            "url": f"http://dashboard.company.com/outputs/{client_id}/"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Open NotebookLM"},
                            "url": quality.get('notebooklm_link', '#')
                        }
                    ]
                }
            ]
        }
        
        requests.post(self.webhook_url, json=message)

# Usage in workflow completion hook
slack = SlackNotifier(webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL")
slack.send_complete_notification('acme_corp')
```

---

### Microsoft Teams Integration

**Use Case:** Enterprise notification to Teams channels

**Implementation:**
```python
import pymsteams

class TeamsNotifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
    
    def send_notification(self, client_id):
        """Send workflow completion card to Teams"""
        
        with open(f'docs_generated/{client_id}/Quality_Score.json') as f:
            quality = json.load(f)
        
        # Create Teams card
        card = pymsteams.connectorcard(self.webhook_url)
        card.title(f"Account Intelligence Analysis Complete: {quality['client_name']}")
        card.text(f"Quality Score: {quality['overall_score']}/10")
        
        # Add sections
        card_section = pymsteams.cardsection()
        card_section.activityTitle("Workflow Results")
        card_section.addFact("Sources Imported", str(quality['sources']['total']))
        card_section.addFact("Execution Time", quality['execution_time'])
        card_section.addFact("Mode", quality['mode'].upper())
        card.addSection(card_section)
        
        # Add action buttons
        card.addLinkButton("View Analysis", f"http://dashboard/outputs/{client_id}/")
        
        card.send()

# Usage
teams = TeamsNotifier(webhook_url="https://outlook.office.com/webhook/...")
teams.send_notification('acme_corp')
```

---

## Document Management

### SharePoint Integration

**Use Case:** Upload analysis to SharePoint document library

**Prerequisites:**
```bash
pip install Office365-REST-Python-Client
```

**Implementation:**
```python
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential

class SharePointIntegration:
    def __init__(self, site_url, client_id, client_secret):
        credentials = ClientCredential(client_id, client_secret)
        self.ctx = ClientContext(site_url).with_credentials(credentials)
    
    def upload_analysis(self, client_id, folder_name="Account Intelligence Reports"):
        """Upload analysis files to SharePoint"""
        
        # Get target folder
        target_folder = self.ctx.web.get_folder_by_server_relative_url(folder_name)
        
        # Upload analysis file
        analysis_file = f'docs_generated/{client_id}/Analysis.txt'
        with open(analysis_file, 'rb') as f:
            target_folder.upload_file(f'{client_id}_Analysis.txt', f.read()).execute_query()
        
        # Upload quality score
        quality_file = f'docs_generated/{client_id}/Quality_Score.json'
        with open(quality_file, 'rb') as f:
            target_folder.upload_file(f'{client_id}_QualityScore.json', f.read()).execute_query()
        
        print(f"✓ Files uploaded to SharePoint: {folder_name}")

# Usage
sharepoint = SharePointIntegration(
    site_url="https://company.sharepoint.com/sites/SalesOps",
    client_id="your_client_id",
    client_secret="your_secret"
)
sharepoint.upload_analysis('acme_corp')
```

---

### Confluence Integration

**Use Case:** Create Confluence page with analysis

**Prerequisites:**
```bash
pip install atlassian-python-api
```

**Implementation:**
```python
from atlassian import Confluence

class ConfluenceIntegration:
    def __init__(self, url, username, api_token):
        self.confluence = Confluence(
            url=url,
            username=username,
            password=api_token
        )
    
    def create_analysis_page(self, client_id, space_key, parent_page_id=None):
        """Create Confluence page with Account Intelligence analysis"""
        
        # Read analysis
        with open(f'docs_generated/{client_id}/Analysis.txt') as f:
            analysis = f.read()
        
        with open(f'docs_generated/{client_id}/Quality_Score.json') as f:
            quality = json.load(f)
        
        # Convert to Confluence storage format (HTML)
        page_body = f"""
        <ac:structured-macro ac:name="info">
          <ac:rich-text-body>
            <p><strong>Quality Score:</strong> {quality['overall_score']}/10</p>
            <p><strong>Sources:</strong> {quality['sources']['total']}</p>
            <p><strong>Generated:</strong> {quality.get('timestamp', 'N/A')}</p>
          </ac:rich-text-body>
        </ac:structured-macro>
        
        <h2>Analysis</h2>
        <pre>{analysis}</pre>
        
        <h2>NotebookLM Link</h2>
        <p><a href="{quality.get('notebooklm_link', '#')}">Open in NotebookLM</a></p>
        """
        
        # Create page
        page = self.confluence.create_page(
            space=space_key,
            title=f"Account Intelligence Analysis: {quality['client_name']}",
            body=page_body,
            parent_id=parent_page_id
        )
        
        print(f"✓ Confluence page created: {page['id']}")
        return page['id']

# Usage
confluence = ConfluenceIntegration(
    url="https://company.atlassian.net/wiki",
    username="user@company.com",
    api_token="your_api_token"
)
confluence.create_analysis_page('acme_corp', space_key='SALES', parent_page_id='123456')
```

---

## Monitoring Integration

### Prometheus Metrics Export

**Use Case:** Monitor workflow performance in Grafana

**Implementation:**
```python
# integrations/prometheus_exporter.py

from prometheus_client import start_http_server, Gauge, Counter, Histogram
import time
import json
from pathlib import Path

# Define metrics
workflow_duration = Histogram(
    'project_ape_workflow_duration_seconds',
    'Workflow execution time',
    ['client_id', 'mode']
)

quality_score = Gauge(
    'project_ape_quality_score',
    'Analysis quality score',
    ['client_id']
)

sources_imported = Gauge(
    'project_ape_sources_imported',
    'Number of external sources imported',
    ['client_id']
)

workflow_total = Counter(
    'project_ape_workflows_total',
    'Total workflows executed',
    ['client_id', 'mode', 'status']
)

def collect_metrics():
    """Collect metrics from status files"""
    status_dir = Path('.multi_process_status')
    
    for status_file in status_dir.glob('*.json'):
        try:
            with open(status_file) as f:
                status = json.load(f)
            
            client_id = status['client_id']
            mode = status['mode']
            
            if status['status'] == 'COMPLETE':
                # Update metrics
                workflow_duration.labels(client_id=client_id, mode=mode).observe(
                    status['execution_time_seconds']
                )
                
                quality_score.labels(client_id=client_id).set(
                    status['phases']['phase_5']['details']['quality_score']
                )
                
                sources_imported.labels(client_id=client_id).set(
                    status['phases']['phase_3']['details']['sources_imported']
                )
                
                workflow_total.labels(
                    client_id=client_id,
                    mode=mode,
                    status='COMPLETE'
                ).inc()
        
        except Exception as e:
            print(f"Error processing {status_file}: {e}")

if __name__ == '__main__':
    # Start Prometheus metrics server on port 9090
    start_http_server(9090)
    print("Prometheus metrics server started on :9090")
    
    # Collect metrics every 30 seconds
    while True:
        collect_metrics()
        time.sleep(30)
```

**Prometheus scrape config:**
```yaml
scrape_configs:
  - job_name: 'project-ape'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 30s
```

**Example Grafana query:**
```promql
# Average workflow duration by mode
avg(project_ape_workflow_duration_seconds) by (mode)

# Quality score trend
project_ape_quality_score

# Success rate (last 24h)
rate(project_ape_workflows_total{status="COMPLETE"}[24h]) /
rate(project_ape_workflows_total[24h])
```

---

## Custom Integrations

### File Watcher Pattern

**Use Case:** Trigger actions when workflow completes

**Implementation:**
```python
# integrations/workflow_watcher.py

import time
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class WorkflowCompletionHandler(FileSystemEventHandler):
    """Watch for workflow completion and trigger integrations"""
    
    def __init__(self):
        self.processed = set()
    
    def on_modified(self, event):
        """Triggered when status file is modified"""
        if not event.src_path.endswith('.json'):
            return
        
        # Read status
        try:
            with open(event.src_path) as f:
                status = json.load(f)
        except:
            return
        
        client_id = status['client_id']
        
        # Check if workflow just completed (not already processed)
        if status['status'] == 'COMPLETE' and client_id not in self.processed:
            self.processed.add(client_id)
            self.on_workflow_complete(status)
    
    def on_workflow_complete(self, status):
        """Execute integrations on workflow completion"""
        client_id = status['client_id']
        
        print(f"✓ Workflow complete: {status['client_name']}")
        
        # Trigger integrations
        try:
            # 1. Upload to Salesforce
            sf_integration.upload_analysis(client_id, get_opportunity_id(client_id))
            
            # 2. Send Slack notification
            slack.send_complete_notification(client_id)
            
            # 3. Upload to SharePoint
            sharepoint.upload_analysis(client_id)
            
            # 4. Create Confluence page
            confluence.create_analysis_page(client_id, space_key='SALES')
            
            print(f"✓ All integrations completed for {client_id}")
        
        except Exception as e:
            print(f"✗ Integration error for {client_id}: {e}")

# Start watcher
if __name__ == '__main__':
    event_handler = WorkflowCompletionHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.multi_process_status', recursive=False)
    observer.start()
    
    print("Workflow watcher started...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
```

---

<div align="center">
  
  **Seamless Integration**
  
  Combine with [API_REFERENCE.md](API_REFERENCE.md) for detailed API documentation.
  
  ---
  
  *Last Updated: July 2026 | Version 4.0.1*
  
</div>
