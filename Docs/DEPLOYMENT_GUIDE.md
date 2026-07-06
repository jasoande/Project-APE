<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="150"/>
  
  # Deployment Guide
  **Production Deployment Strategies and Best Practices**
  
  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Prerequisites](#prerequisites)
3. [Native Python Deployment](#native-python-deployment)
4. [Container Deployment (Podman/Docker)](#container-deployment-podmandocker)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [OpenShift Deployment](#openshift-deployment)
7. [Cloud Deployments](#cloud-deployments)
8. [High Availability](#high-availability)
9. [Monitoring & Observability](#monitoring--observability)
10. [Backup and Recovery](#backup-and-recovery)
11. [Production Checklist](#production-checklist)
12. [Upgrade Procedures](#upgrade-procedures)
13. [Troubleshooting Deployments](#troubleshooting-deployments)

---

## Deployment Overview

### Supported Deployment Models

| Model | Use Case | Complexity | Scalability |
|-------|----------|------------|-------------|
| **Native Python** | Development, single-user workstations | Low | Single instance |
| **Podman/Docker** | Production single-node, consistent environments | Medium | 1-5 parallel clients |
| **Kubernetes** | Enterprise production, multi-tenant | High | Horizontal scaling |
| **OpenShift** | Enterprise with strict security requirements | High | Auto-scaling, HA |
| **Cloud Managed** | AWS ECS, Azure ACI, Google Cloud Run | Medium | Serverless scaling |

### Architecture Components

```
┌─────────────────────────────────────────────────────────┐
│                  Load Balancer (Optional)               │
│                  nginx / HAProxy / Ingress              │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐            ┌────▼────┐
    │ Flask   │            │ Flask   │
    │Dashboard│            │Dashboard│
    │Instance │            │Instance │
    │  :8765  │            │  :8765  │
    └────┬────┘            └────┬────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────▼────────────┐
         │   Shared Storage       │
         │   - logs/              │
         │   - docs_generated/    │
         │   - .multi_process/    │
         └────────────────────────┘
                     │
         ┌───────────▼────────────┐
         │  OAuth Credentials     │
         │  - NotebookLM tokens   │
         │  - Drive OAuth tokens  │
         │  - Gemini API key      │
         └────────────────────────┘
```

---

## Prerequisites

### Infrastructure Requirements

**Minimum (Single Client, Fast Mode):**
- CPU: 2 cores (x86_64 or ARM64)
- RAM: 2 GB
- Disk: 5 GB available
- Network: 10 Mbps sustained

**Recommended (5 Parallel Clients, Deep Mode):**
- CPU: 8 cores
- RAM: 8 GB
- Disk: 20 GB SSD
- Network: 50 Mbps sustained

**Enterprise (Multi-Tenant, 20+ Clients):**
- CPU: 16+ cores
- RAM: 32 GB
- Disk: 100 GB SSD with backup
- Network: 100 Mbps+ sustained

### Network Requirements

**Outbound Access (HTTPS/443):**
```
notebooklm.googleapis.com          # NotebookLM API
www.googleapis.com                 # Drive API
oauth2.googleapis.com              # OAuth token refresh
generativelanguage.googleapis.com  # Gemini API (optional)
```

**Inbound Access:**
```
Port 8765 (dashboard)  # Localhost only by default
                       # Can expose via reverse proxy for remote access
```

### Software Prerequisites

**All Deployments:**
- Python 3.10+ (3.11+ recommended)
- Google account with NotebookLM access
- Google Cloud project with Drive API enabled

**Container Deployments:**
- Podman 4.0+ or Docker 20.10+
- Container registry access (quay.io or private registry)

**Kubernetes/OpenShift:**
- kubectl 1.24+ or oc 4.10+
- Persistent volume provisioner
- LoadBalancer or Ingress controller

---

## Native Python Deployment

### Installation

**1. Clone Repository**
```bash
git clone https://github.com/jasoande/Project-APE-dev.git
cd Project-APE-dev
```

**2. Run Automated Setup**
```bash
# Launcher handles venv creation and dependencies automatically
python3 launch-project-ape.py

# Or manual setup
./setup-environment.sh
```

**3. Verify Installation**
```bash
# Check Python version
python3 --version  # Should be 3.10+

# Verify virtual environment
ls -la ~/.project-ape-venv/

# Test dashboard
curl -I http://localhost:8765/health
# Expected: HTTP/1.1 200 OK
```

### Configuration

**4. Authenticate Services**
```bash
# Via Web UI (recommended)
python3 launch-project-ape.py
# Browser opens → http://localhost:8765/configure
# Follow 3-step wizard

# Or via terminal
source ~/.project-ape-venv/bin/activate
notebooklm login
python3 setup-oauth-drive.py
```

**5. Configure First Client**
```bash
# Via Web UI: http://localhost:8765/configure
# Add client via form, save configuration

# Or edit vars.py manually
cp example-container.py vars.py
nano vars.py  # Edit client settings
```

### Running

**Start Dashboard**
```bash
python3 launch-project-ape.py
# Dashboard auto-starts on http://localhost:8765
```

**Launch Workflow**
```bash
# Via Web UI: Click "Launch Workflow" button

# Or via command line
python3 main.py  # Uses vars.py configuration
```

### Systemd Service (Linux)

**Create Service File:**
```bash
sudo nano /etc/systemd/system/project-ape.service
```

```ini
[Unit]
Description=Project APE Dashboard
After=network.target

[Service]
Type=simple
User=apeuser
WorkingDirectory=/opt/project-ape
ExecStart=/home/apeuser/.project-ape-venv/bin/python3 /opt/project-ape/dashboard/server.py
Restart=on-failure
RestartSec=10
Environment="PYTHONUNBUFFERED=1"
Environment="GEMINI_API_KEY=your-api-key-here"

# Hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=/opt/project-ape/logs /opt/project-ape/docs_generated

[Install]
WantedBy=multi-user.target
```

**Enable and Start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable project-ape
sudo systemctl start project-ape
sudo systemctl status project-ape
```

---

## Container Deployment (Podman/Docker)

### Pull Container Image

**From Quay.io (Public Registry):**
```bash
# Pull latest
podman pull quay.io/jasoande/project_ape/project-ape:latest

# Pull specific version
podman pull quay.io/jasoande/project_ape/project-ape:4.0.1

# Verify image
podman images | grep project-ape
```

### Setup Credentials Volume

**Create Persistent Volume:**
```bash
# Create named volume for OAuth credentials
podman volume create project-ape-credentials

# Copy credentials into volume
./setup-credentials.sh

# Or manual copy
TEMP=$(podman create -v project-ape-credentials:/creds alpine)
podman cp ~/.notebooklm/credentials.json $TEMP:/creds/
podman cp credentials/token_drive.json $TEMP:/creds/
podman rm $TEMP
```

### Run Container

**Single Client Execution:**
```bash
./ape-run.sh --vars ./vars.py --clients example_client --mode fast
```

**Manual Container Run:**
```bash
podman run -d \
  --name project-ape \
  -p 8765:8765 \
  -v ./client_data:/app/client_data:ro,z \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./logs:/app/logs:rw,z \
  -v ./docs_generated:/app/docs_generated:rw,z \
  -v project-ape-credentials:/opt/app-root/src/.notebooklm:ro,z \
  -e GEMINI_API_KEY="${GEMINI_API_KEY}" \
  quay.io/jasoande/project_ape/project-ape:4.0.1
```

**Volume Mount Breakdown:**
- `client_data:ro` - Read-only client PDFs (if using local files)
- `vars.py:ro` - Read-only configuration
- `logs:rw` - Writable log directory
- `docs_generated:rw` - Writable output directory
- `project-ape-credentials:ro` - Read-only OAuth tokens

### Build Custom Container

**Build from Source:**
```bash
# Build with Podman
podman build -t project-ape:custom -f Containerfile.debian .

# Build with Docker
docker build -t project-ape:custom -f Containerfile.debian .

# Multi-architecture build
podman build \
  --platform linux/amd64,linux/arm64 \
  -t project-ape:custom \
  -f Containerfile.debian .
```

**Tag and Push to Registry:**
```bash
# Tag for registry
podman tag project-ape:custom registry.company.com/project-ape:4.0.1

# Login to registry
podman login registry.company.com

# Push
podman push registry.company.com/project-ape:4.0.1
```

### Container Health Check

**Add Health Check to Container:**
```bash
podman run -d \
  --name project-ape \
  --health-cmd "curl -f http://localhost:8765/health || exit 1" \
  --health-interval 30s \
  --health-timeout 10s \
  --health-retries 3 \
  -p 8765:8765 \
  quay.io/jasoande/project_ape/project-ape:4.0.1
```

**Check Health Status:**
```bash
podman inspect project-ape | jq '.[0].State.Health'
```

---

## Kubernetes Deployment

### Namespace Setup

**Create Namespace:**
```bash
kubectl create namespace project-ape
kubectl config set-context --current --namespace=project-ape
```

### Secrets Configuration

**Create OAuth Secrets:**
```bash
# NotebookLM credentials
kubectl create secret generic notebooklm-credentials \
  --from-file=credentials.json=~/.notebooklm/credentials.json

# Drive OAuth token
kubectl create secret generic drive-oauth \
  --from-file=token_drive.json=credentials/token_drive.json

# Gemini API key (optional)
kubectl create secret generic gemini-api-key \
  --from-literal=api-key="${GEMINI_API_KEY}"
```

**Verify Secrets:**
```bash
kubectl get secrets
kubectl describe secret notebooklm-credentials
```

### ConfigMap for vars.py

**Create ConfigMap:**
```bash
kubectl create configmap project-ape-config \
  --from-file=vars.py=./vars.py
```

**Verify:**
```bash
kubectl get configmap project-ape-config -o yaml
```

### Persistent Volume Claims

**Create PVC for Logs and Outputs:**
```yaml
# pvc-logs.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: project-ape-logs
  namespace: project-ape
spec:
  accessModes:
    - ReadWriteMany  # Required for multi-replica deployments
  resources:
    requests:
      storage: 10Gi
  storageClassName: nfs-storage  # Or your storage class
---
# pvc-outputs.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: project-ape-outputs
  namespace: project-ape
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 50Gi
  storageClassName: nfs-storage
```

**Apply:**
```bash
kubectl apply -f pvc-logs.yaml
kubectl apply -f pvc-outputs.yaml
kubectl get pvc
```

### Deployment Manifest

**Complete Deployment YAML:**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: project-ape
  namespace: project-ape
  labels:
    app: project-ape
    version: "4.0.1"
spec:
  replicas: 1  # Single instance for now (scale later)
  selector:
    matchLabels:
      app: project-ape
  template:
    metadata:
      labels:
        app: project-ape
        version: "4.0.1"
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      
      containers:
      - name: project-ape
        image: quay.io/jasoande/project_ape/project-ape:4.0.1
        imagePullPolicy: IfNotPresent
        
        ports:
        - containerPort: 8765
          name: http
          protocol: TCP
        
        env:
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: gemini-api-key
              key: api-key
              optional: true
        - name: DASHBOARD_PORT
          value: "8765"
        - name: PYTHONUNBUFFERED
          value: "1"
        
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        
        volumeMounts:
        - name: notebooklm-credentials
          mountPath: /opt/app-root/src/.notebooklm
          readOnly: true
        - name: drive-oauth
          mountPath: /app/credentials
          readOnly: true
        - name: config
          mountPath: /app/vars.py
          subPath: vars.py
          readOnly: true
        - name: logs
          mountPath: /app/logs
        - name: outputs
          mountPath: /app/docs_generated
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8765
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /health
            port: 8765
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 2
      
      volumes:
      - name: notebooklm-credentials
        secret:
          secretName: notebooklm-credentials
          defaultMode: 0600
      - name: drive-oauth
        secret:
          secretName: drive-oauth
          defaultMode: 0600
      - name: config
        configMap:
          name: project-ape-config
      - name: logs
        persistentVolumeClaim:
          claimName: project-ape-logs
      - name: outputs
        persistentVolumeClaim:
          claimName: project-ape-outputs
      
      restartPolicy: Always
```

**Deploy:**
```bash
kubectl apply -f deployment.yaml
kubectl get deployment project-ape
kubectl get pods -l app=project-ape
```

### Service Exposure

**ClusterIP Service (Internal Access):**
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: project-ape
  namespace: project-ape
spec:
  type: ClusterIP
  selector:
    app: project-ape
  ports:
  - name: http
    port: 8765
    targetPort: 8765
    protocol: TCP
```

**LoadBalancer Service (External Access):**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: project-ape-external
  namespace: project-ape
spec:
  type: LoadBalancer
  selector:
    app: project-ape
  ports:
  - name: http
    port: 80
    targetPort: 8765
    protocol: TCP
```

**Apply:**
```bash
kubectl apply -f service.yaml
kubectl get svc project-ape
```

### Ingress Configuration

**Nginx Ingress:**
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: project-ape
  namespace: project-ape
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - project-ape.company.com
    secretName: project-ape-tls
  rules:
  - host: project-ape.company.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: project-ape
            port:
              number: 8765
```

**Apply:**
```bash
kubectl apply -f ingress.yaml
kubectl get ingress project-ape
```

---

## OpenShift Deployment

### Security Context Constraints

**Create SCC (if needed):**
```yaml
# scc-project-ape.yaml
apiVersion: security.openshift.io/v1
kind: SecurityContextConstraints
metadata:
  name: project-ape-scc
allowHostDirVolumePlugin: false
allowHostIPC: false
allowHostNetwork: false
allowHostPID: false
allowHostPorts: false
allowPrivilegedContainer: false
allowedCapabilities: []
defaultAddCapabilities: []
fsGroup:
  type: MustRunAs
  ranges:
  - min: 1000
    max: 1000
runAsUser:
  type: MustRunAsRange
  uidRangeMin: 1000
  uidRangeMax: 1000
seLinuxContext:
  type: MustRunAs
supplementalGroups:
  type: RunAsAny
volumes:
- configMap
- downwardAPI
- emptyDir
- persistentVolumeClaim
- projected
- secret
```

**Apply SCC:**
```bash
oc apply -f scc-project-ape.yaml
oc adm policy add-scc-to-user project-ape-scc -z default -n project-ape
```

### DeploymentConfig

**OpenShift-Specific Deployment:**
```yaml
# deploymentconfig.yaml
apiVersion: apps.openshift.io/v1
kind: DeploymentConfig
metadata:
  name: project-ape
  namespace: project-ape
spec:
  replicas: 1
  selector:
    app: project-ape
  template:
    metadata:
      labels:
        app: project-ape
    spec:
      # Same spec as Kubernetes Deployment above
      # ...
  triggers:
  - type: ConfigChange
  - type: ImageChange
    imageChangeParams:
      automatic: true
      containerNames:
      - project-ape
      from:
        kind: ImageStreamTag
        name: project-ape:4.0.1
```

### Route (OpenShift Ingress)

**Create Route:**
```yaml
# route.yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: project-ape
  namespace: project-ape
spec:
  host: project-ape.apps.cluster.company.com
  to:
    kind: Service
    name: project-ape
    weight: 100
  port:
    targetPort: http
  tls:
    termination: edge
    insecureEdgeTerminationPolicy: Redirect
  wildcardPolicy: None
```

**Apply:**
```bash
oc apply -f route.yaml
oc get route project-ape
```

---

## Cloud Deployments

### AWS ECS (Fargate)

**Task Definition:**
```json
{
  "family": "project-ape",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/projectApeTaskRole",
  "containerDefinitions": [
    {
      "name": "project-ape",
      "image": "quay.io/jasoande/project_ape/project-ape:4.0.1",
      "portMappings": [
        {
          "containerPort": 8765,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DASHBOARD_PORT",
          "value": "8765"
        }
      ],
      "secrets": [
        {
          "name": "GEMINI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:gemini-api-key"
        }
      ],
      "mountPoints": [
        {
          "sourceVolume": "logs",
          "containerPath": "/app/logs"
        },
        {
          "sourceVolume": "outputs",
          "containerPath": "/app/docs_generated"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/project-ape",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "volumes": [
    {
      "name": "logs",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-12345678",
        "transitEncryption": "ENABLED"
      }
    },
    {
      "name": "outputs",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-12345678",
        "transitEncryption": "ENABLED"
      }
    }
  ]
}
```

**Create Service:**
```bash
aws ecs create-service \
  --cluster project-ape-cluster \
  --service-name project-ape \
  --task-definition project-ape:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

### Azure Container Instances

**Deploy with Azure CLI:**
```bash
az container create \
  --resource-group project-ape-rg \
  --name project-ape \
  --image quay.io/jasoande/project_ape/project-ape:4.0.1 \
  --cpu 2 \
  --memory 4 \
  --ports 8765 \
  --dns-name-label project-ape-prod \
  --environment-variables DASHBOARD_PORT=8765 \
  --secure-environment-variables GEMINI_API_KEY="${GEMINI_API_KEY}" \
  --azure-file-volume-account-name storageaccount \
  --azure-file-volume-account-key "${STORAGE_KEY}" \
  --azure-file-volume-share-name project-ape-data \
  --azure-file-volume-mount-path /app/logs
```

### Google Cloud Run

**Deploy:**
```bash
gcloud run deploy project-ape \
  --image quay.io/jasoande/project_ape/project-ape:4.0.1 \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --port 8765 \
  --set-env-vars DASHBOARD_PORT=8765 \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest \
  --allow-unauthenticated
```

---

## High Availability

### Multi-Replica Deployment

**Scale Deployment:**
```bash
# Kubernetes
kubectl scale deployment project-ape --replicas=3

# OpenShift
oc scale dc project-ape --replicas=3
```

**Shared Filesystem Requirement:**
- Logs directory: ReadWriteMany PVC (NFS, EFS, Azure Files)
- Outputs directory: ReadWriteMany PVC
- Status files: Shared volume for `.multi_process_status/`

**Load Balancing:**
```yaml
# service.yaml with session affinity
apiVersion: v1
kind: Service
metadata:
  name: project-ape
spec:
  type: LoadBalancer
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3 hours
  selector:
    app: project-ape
  ports:
  - port: 80
    targetPort: 8765
```

### Database Persistence (Future)

**Planned Enhancement:**
- PostgreSQL for status tracking (instead of JSON files)
- Redis for caching Drive downloads
- Horizontal scaling without shared filesystem

---

## Monitoring & Observability

### Prometheus Metrics

**Expose Metrics Endpoint (Future):**
```python
# dashboard/server.py
from prometheus_client import Counter, Histogram, generate_latest

workflow_counter = Counter('project_ape_workflows_total', 'Total workflows executed')
workflow_duration = Histogram('project_ape_workflow_duration_seconds', 'Workflow execution time')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### Grafana Dashboard

**Example Metrics:**
- Workflows per hour
- Average execution time (Fast vs Deep)
- API error rate
- Quality score distribution
- Source import count

### Log Aggregation

**Fluentd Configuration:**
```yaml
# fluentd-configmap.yaml
<source>
  @type tail
  path /app/logs/*.log
  pos_file /var/log/fluentd-project-ape.pos
  tag project-ape.*
  <parse>
    @type json
    time_key timestamp
    time_format %Y-%m-%dT%H:%M:%S.%L%z
  </parse>
</source>

<match project-ape.**>
  @type elasticsearch
  host elasticsearch.logging.svc.cluster.local
  port 9200
  index_name project-ape
  type_name _doc
</match>
```

---

## Backup and Recovery

### Backup Strategy

**What to Backup:**
1. OAuth credentials (`~/.notebooklm/credentials.json`, `credentials/token_drive.json`)
2. Generated outputs (`docs_generated/`)
3. Configuration (`vars.py`)
4. Logs (optional, for audit)

**Backup Script:**
```bash
#!/bin/bash
# backup-project-ape.sh

BACKUP_DIR="/backup/project-ape/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Credentials
cp -r ~/.notebooklm "$BACKUP_DIR/"
cp -r credentials "$BACKUP_DIR/"

# Outputs
tar -czf "$BACKUP_DIR/docs_generated.tar.gz" docs_generated/

# Configuration
cp vars.py "$BACKUP_DIR/"

# Logs (last 7 days)
find logs/ -mtime -7 -type f -exec cp {} "$BACKUP_DIR/logs/" \;

echo "Backup completed: $BACKUP_DIR"
```

**Automate with Cron:**
```bash
# Daily backup at 2 AM
0 2 * * * /opt/project-ape/backup-project-ape.sh
```

### Recovery Procedure

**1. Restore Credentials:**
```bash
cp -r /backup/project-ape/20260706_020000/.notebooklm ~/
cp -r /backup/project-ape/20260706_020000/credentials ./
chmod 600 ~/.notebooklm/credentials.json
chmod 600 credentials/token_drive.json
```

**2. Restore Configuration:**
```bash
cp /backup/project-ape/20260706_020000/vars.py ./
```

**3. Restore Outputs (if needed):**
```bash
tar -xzf /backup/project-ape/20260706_020000/docs_generated.tar.gz
```

**4. Verify:**
```bash
python3 launch-project-ape.py
# Check http://localhost:8765/health
```

---

## Production Checklist

### Pre-Deployment

- [ ] Python 3.10+ installed and verified
- [ ] Network access to googleapis.com confirmed
- [ ] OAuth credentials generated and tested
- [ ] vars.py configuration validated
- [ ] Firewall rules configured (if exposing dashboard)
- [ ] SSL/TLS certificates obtained (if using HTTPS)
- [ ] Backup strategy defined and tested
- [ ] Monitoring/alerting configured
- [ ] Resource limits set (CPU, memory)
- [ ] Log rotation configured

### Post-Deployment

- [ ] Dashboard accessible at configured URL
- [ ] Health endpoint returns 200 OK
- [ ] Authentication working (NotebookLM, Drive)
- [ ] Test workflow completes successfully
- [ ] Logs are being written correctly
- [ ] Outputs saved to expected directory
- [ ] Metrics/monitoring data flowing
- [ ] Backup job executed successfully
- [ ] Documentation updated with deployment details
- [ ] Runbook tested by operations team

---

## Upgrade Procedures

### Native Python Upgrade

**1. Backup Current Installation:**
```bash
./backup-project-ape.sh
```

**2. Pull Latest Code:**
```bash
git fetch origin
git checkout production
git pull origin production
```

**3. Update Dependencies:**
```bash
source ~/.project-ape-venv/bin/activate
pip install --upgrade -r requirements.txt
```

**4. Test:**
```bash
python3 launch-project-ape.py
# Verify dashboard at http://localhost:8765
```

### Container Upgrade

**1. Pull New Image:**
```bash
podman pull quay.io/jasoande/project_ape/project-ape:4.0.2
```

**2. Stop Existing Container:**
```bash
podman stop project-ape
podman rm project-ape
```

**3. Start New Container:**
```bash
./ape-run.sh --vars ./vars.py --clients test_client --mode fast
```

**4. Verify:**
```bash
podman ps | grep project-ape
curl -I http://localhost:8765/health
```

### Kubernetes Rolling Update

**1. Update Deployment:**
```bash
kubectl set image deployment/project-ape \
  project-ape=quay.io/jasoande/project_ape/project-ape:4.0.2
```

**2. Monitor Rollout:**
```bash
kubectl rollout status deployment/project-ape
kubectl get pods -l app=project-ape
```

**3. Rollback (if needed):**
```bash
kubectl rollout undo deployment/project-ape
```

---

## Troubleshooting Deployments

### Container Won't Start

**Symptom:** Container exits immediately after start

**Diagnosis:**
```bash
# Check logs
podman logs project-ape

# Inspect container
podman inspect project-ape

# Verify image
podman images | grep project-ape
```

**Common Causes:**
- Missing credentials volume
- Incorrect volume paths
- Permission issues (UID mismatch)
- Port already in use

**Solution:**
```bash
# Recreate credentials volume
./setup-credentials.sh

# Fix permissions
chmod -R 755 logs/
chmod -R 755 docs_generated/

# Check port availability
lsof -i :8765
```

### Kubernetes Pod CrashLoopBackOff

**Diagnosis:**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl get events --sort-by='.lastTimestamp'
```

**Common Causes:**
- Secret not mounted correctly
- PVC not bound
- Resource limits too low
- Health check failing

**Solution:**
```bash
# Check secrets
kubectl get secret notebooklm-credentials -o yaml

# Check PVC status
kubectl get pvc

# Increase resources
kubectl edit deployment project-ape
# Update resources.limits
```

### Dashboard Not Accessible

**Symptom:** Cannot reach http://localhost:8765

**Diagnosis:**
```bash
# Check if process running
ps aux | grep "dashboard/server.py"

# Check port binding
netstat -tulpn | grep 8765

# Test locally
curl -I http://127.0.0.1:8765/health
```

**Solutions:**
```bash
# Restart dashboard
pkill -f "dashboard/server.py"
python3 launch-project-ape.py

# Check firewall
sudo ufw status
sudo ufw allow 8765/tcp

# Verify no other service on port
lsof -i :8765
```

---

<div align="center">
  
  **Ready for Production?**
  
  Use this guide with [OPERATIONS_RUNBOOK.md](OPERATIONS_RUNBOOK.md) for day-to-day operations.
  
  ---
  
  **Questions?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | [Report Issues](https://github.com/jasoande/Project-APE-dev/issues)
  
  *Last Updated: July 2026 | Version 4.0.1*
  
</div>
