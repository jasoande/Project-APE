<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="150"/>
  
  # Security Guide
  **Enterprise Security Architecture and Best Practices**
  
  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

1. [Security Overview](#security-overview)
2. [Authentication & Authorization](#authentication--authorization)
3. [Secrets Management](#secrets-management)
4. [Network Security](#network-security)
5. [Container Security](#container-security)
6. [Data Security](#data-security)
7. [API Security](#api-security)
8. [Audit & Logging](#audit--logging)
9. [Vulnerability Management](#vulnerability-management)
10. [Security Hardening Checklist](#security-hardening-checklist)
11. [Incident Response](#incident-response)
12. [Compliance](#compliance)

---

## Security Overview

### Architecture Security Model

Project APE implements **defense-in-depth** security with multiple layers:

```
┌─────────────────────────────────────────────────────┐
│ Layer 1: Authentication (OAuth 2.0)                 │
│   • NotebookLM OAuth (Google Identity)             │
│   • Drive OAuth (Google Cloud Platform)            │
├─────────────────────────────────────────────────────┤
│ Layer 2: Authorization (Least Privilege)           │
│   • Read-only Drive access                         │
│   • Scoped NotebookLM permissions                  │
├─────────────────────────────────────────────────────┤
│ Layer 3: Network Isolation                         │
│   • Localhost-only dashboard (127.0.0.1:8765)      │
│   • No inbound connections                         │
├─────────────────────────────────────────────────────┤
│ Layer 4: Container Isolation (Optional)            │
│   • Non-root execution (UID 1000)                  │
│   • Read-only filesystem mounts                    │
│   • Restricted capabilities                        │
├─────────────────────────────────────────────────────┤
│ Layer 5: Secrets Protection                        │
│   • Credential file encryption (OS filesystem)     │
│   • 0600 permissions on sensitive files            │
│   • No embedded API keys                           │
├─────────────────────────────────────────────────────┤
│ Layer 6: Data Protection                           │
│   • HTTPS for all external API calls               │
│   • No local data persistence (streaming)          │
│   • Generated docs in controlled directory         │
└─────────────────────────────────────────────────────┘
```

### Threat Model

**In Scope:**
- ✅ Credential theft (OAuth token compromise)
- ✅ Unauthorized API access (Drive, NotebookLM)
- ✅ Network eavesdropping (MITM attacks)
- ✅ Container escape (if using containers)
- ✅ Privilege escalation
- ✅ Data exfiltration via API quota abuse
- ✅ Malicious document injection

**Out of Scope:**
- ❌ Physical access to host system (requires OS-level protection)
- ❌ Browser vulnerabilities (user responsibility)
- ❌ Google infrastructure compromise (trust boundary)

### Security Principles

1. **Zero Trust** - Verify every authentication, never assume
2. **Least Privilege** - Minimal scopes for OAuth tokens
3. **Defense in Depth** - Multiple security layers
4. **Secure by Default** - No insecure configurations required
5. **Fail Closed** - Auth failures stop execution
6. **Audit Everything** - Comprehensive logging
7. **Principle of Least Astonishment** - No hidden behavior

---

## Authentication & Authorization

### OAuth 2.0 Architecture

Project APE uses **OAuth 2.0 Authorization Code Flow** with PKCE for both NotebookLM and Google Drive.

#### NotebookLM Authentication Flow

```
┌──────────┐                                   ┌─────────────┐
│  User    │                                   │   Google    │
│ (Chrome) │                                   │   Identity  │
└────┬─────┘                                   └──────┬──────┘
     │                                                │
     │  1. notebooklm login (CLI command)           │
     ├────────────────────────────────────────────> │
     │                                                │
     │  2. Browser opens to consent screen          │
     │ <───────────────────────────────────────────┤
     │                                                │
     │  3. User grants permissions:                 │
     │     - Create/manage notebooks                │
     │     - Add sources to notebooks               │
     │     - Generate AI content                    │
     ├────────────────────────────────────────────> │
     │                                                │
     │  4. Authorization code (via redirect)        │
     │ <───────────────────────────────────────────┤
     │                                                │
     │  5. Exchange code for tokens                 │
     ├────────────────────────────────────────────> │
     │                                                │
     │  6. Access token + Refresh token             │
     │ <───────────────────────────────────────────┤
     │                                                │
     │  7. Tokens saved to                          │
     │     ~/.notebooklm/credentials.json           │
     └──────────────────────────────────────────────┘

Token Lifecycle:
- Access Token: 1 hour expiry, auto-refresh
- Refresh Token: No expiry (revocable by user)
- Storage: ~/.notebooklm/credentials.json (chmod 600)
```

#### Google Drive OAuth Flow

```
┌──────────┐                                   ┌─────────────┐
│  User    │                                   │   Google    │
│ (Browser)│                                   │   OAuth 2.0 │
└────┬─────┘                                   └──────┬──────┘
     │                                                │
     │  1. Upload credentials.json (OAuth Client)   │
     │     to dashboard                              │
     │                                                │
     │  2. Click "Generate Token" in web UI          │
     ├────────────────────────────────────────────> │
     │                                                │
     │  3. Browser popup: Google consent screen     │
     │ <───────────────────────────────────────────┤
     │                                                │
     │  4. Grant Drive permissions:                 │
     │     - See/download files (read-only)         │
     │     - View file metadata                     │
     ├────────────────────────────────────────────> │
     │                                                │
     │  5. Authorization code                       │
     │ <───────────────────────────────────────────┤
     │                                                │
     │  6. Exchange for access/refresh tokens       │
     ├────────────────────────────────────────────> │
     │                                                │
     │  7. Tokens saved to                          │
     │     credentials/token_drive.json             │
     └──────────────────────────────────────────────┘

Token Lifecycle:
- Access Token: 1 hour expiry, auto-refresh
- Refresh Token: 90-day expiry (requires re-auth)
- Storage: credentials/token_drive.json (chmod 600)
```

### OAuth Scopes (Least Privilege)

**NotebookLM Scopes:**
```
https://www.googleapis.com/auth/notebooklm
https://www.googleapis.com/auth/notebooklm.readonly
```

**Google Drive Scopes (Read-Only):**
```
https://www.googleapis.com/auth/drive.readonly
https://www.googleapis.com/auth/drive.metadata.readonly
```

**✅ Best Practice:** Never request write access to Drive (`drive` scope) - only read access needed.

### Multi-Factor Authentication (MFA)

**Recommended for Production:**
- Enable MFA on Google accounts used for authentication
- Enforces security even if credentials.json is compromised
- MFA prompt during OAuth consent flow

**Enterprise Deployments:**
```bash
# Enforce MFA via Google Workspace admin console
# Settings → Security → 2-Step Verification → Enforcement
```

### Token Management

#### Token Storage Locations

```bash
# NotebookLM credentials (native Python)
~/.notebooklm/credentials.json       # chmod 600

# Drive OAuth credentials
credentials/client_secret.json       # OAuth client ID (not sensitive)
credentials/token_drive.json         # Refresh token (HIGHLY SENSITIVE)

# Container environment (volume mount)
/opt/app-root/src/.notebooklm/credentials.json
/app/credentials/token_drive.json
```

#### Token Permissions (Critical)

```bash
# Set strict permissions on token files
chmod 600 ~/.notebooklm/credentials.json
chmod 600 credentials/token_drive.json
chmod 700 ~/.notebooklm
chmod 700 credentials/

# Verify permissions
ls -la ~/.notebooklm/credentials.json
# Expected: -rw------- (600)

# Wrong permissions - SECURITY RISK
# -rw-r--r-- (644) - readable by all users!
# -rw-rw-r-- (664) - writable by group!
```

**⚠️ Important:** If permissions are not 600, other users on the system can steal OAuth tokens.

#### Token Refresh Strategy

**Automatic Refresh (Default Behavior):**
```python
# core/auth_manager.py handles refresh automatically
# No user intervention needed unless refresh token expires

# Token refresh trigger
if access_token_expired():
    new_access_token = refresh_using_refresh_token()
    save_to_credentials_file(new_access_token)
```

**Manual Refresh (If Auto-Refresh Fails):**
```bash
# NotebookLM re-authentication
notebooklm auth logout
notebooklm login

# Drive token regeneration
cd credentials/
rm token_drive.json
# Then run OAuth flow again via dashboard
```

#### Token Revocation

**User-Initiated Revocation:**
1. Visit https://myaccount.google.com/permissions
2. Find "NotebookLM" or "Project APE" application
3. Click "Remove Access"
4. Tokens immediately invalidated

**Programmatic Revocation:**
```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

credentials = Credentials.from_authorized_user_file('token_drive.json')
credentials.revoke(Request())
```

**Container Cleanup (Delete Volume):**
```bash
# Stop containers using credentials
podman stop $(podman ps -q --filter volume=project-ape-credentials)

# Remove credential volume
podman volume rm project-ape-credentials
```

---

## Secrets Management

### Credential File Structure

#### NotebookLM Credentials

**File:** `~/.notebooklm/credentials.json`

```json
{
  "access_token": "ya29.a0AfH6SMB...",
  "refresh_token": "1//0gZ1X3...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "123456789-abc123.apps.googleusercontent.com",
  "client_secret": "GOCSPX-...",
  "scopes": ["https://www.googleapis.com/auth/notebooklm"]
}
```

**Sensitive Fields:**
- `access_token` - 1-hour validity, auto-refreshed
- `refresh_token` - **CRITICAL** - Long-lived, enables perpetual access
- `client_secret` - OAuth client secret (moderately sensitive)

#### Drive OAuth Credentials

**File:** `credentials/token_drive.json`

```json
{
  "token": "ya29.a0AfH6SMB...",
  "refresh_token": "1//0gZ1X3...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "123456789-xyz789.apps.googleusercontent.com",
  "client_secret": "GOCSPX-...",
  "scopes": [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly"
  ],
  "expiry": "2026-07-06T14:30:00.000000Z"
}
```

### Filesystem Security

#### Permissions Hardening

```bash
# Secure home directory credentials
chmod 700 ~/.notebooklm
chmod 600 ~/.notebooklm/credentials.json

# Secure local credentials directory
chmod 700 credentials/
chmod 600 credentials/*.json

# Verify no world-readable files
find ~/.notebooklm credentials/ -type f -perm /o=r

# Expected output: (empty - no world-readable files)
```

#### SELinux Context (RHEL/Fedora)

```bash
# Verify SELinux context
ls -Z ~/.notebooklm/credentials.json
# Expected: unconfined_u:object_r:user_home_t:s0

# If context is wrong, restore it
restorecon -Rv ~/.notebooklm/
```

### Container Credential Isolation

#### Volume Mount Strategy

**Native Podman (Recommended):**
```bash
# Create named volume for credentials
podman volume create project-ape-credentials

# Copy credentials into volume (one-time setup)
TEMP_CONTAINER=$(podman create -v project-ape-credentials:/creds alpine)
podman cp ~/.notebooklm/credentials.json $TEMP_CONTAINER:/creds/
podman rm $TEMP_CONTAINER

# Mount volume in container (read-only recommended)
podman run -v project-ape-credentials:/opt/app-root/src/.notebooklm:ro,z \
  quay.io/jasoande/project_ape/project-ape:4.0.1
```

**Kubernetes Secrets (Production):**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: project-ape-credentials
type: Opaque
stringData:
  credentials.json: |
    {
      "access_token": "...",
      "refresh_token": "..."
    }
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      volumes:
      - name: notebooklm-creds
        secret:
          secretName: project-ape-credentials
          defaultMode: 0600
      containers:
      - name: project-ape
        volumeMounts:
        - name: notebooklm-creds
          mountPath: /opt/app-root/src/.notebooklm
          readOnly: true
```

### Secret Rotation

**Recommended Rotation Schedule:**
- **Access Tokens:** Auto-rotate hourly (automatic)
- **Refresh Tokens:** Rotate every 90 days (manual re-auth)
- **OAuth Client Secrets:** Rotate annually or on compromise

**Rotation Procedure:**
```bash
# 1. Generate new OAuth client in Google Cloud Console
# 2. Download new credentials.json
# 3. Upload to dashboard
# 4. Generate new token
# 5. Verify new token works
# 6. Revoke old OAuth client
# 7. Delete old credentials files
```

### Integration with Enterprise Secret Managers

#### HashiCorp Vault Integration

```python
# core/vault_secrets.py (example implementation)
import hvac

class VaultCredentialProvider:
    def __init__(self, vault_addr, vault_token):
        self.client = hvac.Client(url=vault_addr, token=vault_token)
    
    def get_notebooklm_credentials(self):
        """Fetch NotebookLM credentials from Vault"""
        secret = self.client.secrets.kv.v2.read_secret_version(
            path='project-ape/notebooklm'
        )
        return secret['data']['data']
    
    def get_drive_credentials(self):
        """Fetch Drive OAuth credentials from Vault"""
        secret = self.client.secrets.kv.v2.read_secret_version(
            path='project-ape/drive-oauth'
        )
        return secret['data']['data']

# Usage in auth_manager.py
if os.getenv('USE_VAULT') == '1':
    vault = VaultCredentialProvider(
        vault_addr=os.getenv('VAULT_ADDR'),
        vault_token=os.getenv('VAULT_TOKEN')
    )
    creds = vault.get_notebooklm_credentials()
else:
    creds = load_from_file('~/.notebooklm/credentials.json')
```

#### AWS Secrets Manager Integration

```python
# core/aws_secrets.py (example)
import boto3
import json

def get_secret(secret_name, region_name='us-east-1'):
    client = boto3.client('secretsmanager', region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Retrieve credentials
notebooklm_creds = get_secret('project-ape/notebooklm-oauth')
drive_creds = get_secret('project-ape/drive-oauth')
```

---

## Network Security

### Dashboard Localhost Binding

**Default Configuration (Secure):**
```python
# dashboard/server.py
if __name__ == '__main__':
    app.run(
        host='127.0.0.1',  # Localhost only - NOT 0.0.0.0
        port=8765,
        debug=False
    )
```

**✅ Security Benefit:** Dashboard only accessible from local machine, not from network.

**⚠️ Insecure Configuration (DO NOT USE):**
```python
# INSECURE - exposes dashboard to network
app.run(host='0.0.0.0', port=8765)
```

### Firewall Rules

**Recommended Firewall Configuration:**
```bash
# Linux (iptables) - Block external access to port 8765
sudo iptables -A INPUT -p tcp --dport 8765 ! -s 127.0.0.1 -j DROP

# macOS (pf.conf) - Already blocked by default (localhost binding)

# Verify no external access
curl -I http://<external-ip>:8765
# Expected: Connection refused
```

### TLS/SSL for External Access (Optional)

**If exposing dashboard externally (NOT RECOMMENDED), use TLS:**

```python
# dashboard/server.py (production configuration)
if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8765,
        ssl_context=('cert.pem', 'key.pem'),  # TLS certificate
        debug=False
    )
```

**Generate self-signed certificate (testing only):**
```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout key.pem -out cert.pem -days 365 \
  -subj "/CN=project-ape.local"
```

**Production TLS (use Let's Encrypt):**
```bash
# Install certbot
sudo apt install certbot

# Generate certificate
sudo certbot certonly --standalone -d project-ape.yourdomain.com

# Use certificates in Flask
ssl_context=('/etc/letsencrypt/live/project-ape.yourdomain.com/fullchain.pem',
             '/etc/letsencrypt/live/project-ape.yourdomain.com/privkey.pem')
```

### API Endpoint Protection

**Rate Limiting (Future Enhancement):**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"]
)

@app.route('/api/launch-workflow', methods=['POST'])
@limiter.limit("5 per minute")  # Prevent workflow spam
def launch_workflow():
    # ...
```

### Outbound Connections (API Calls)

**All External APIs Use HTTPS:**
- ✅ NotebookLM API: `https://notebooklm.googleapis.com`
- ✅ Google Drive API: `https://www.googleapis.com/drive/v3`
- ✅ OAuth 2.0: `https://oauth2.googleapis.com`

**Certificate Verification (Always Enabled):**
```python
# Verify SSL certificates for all requests
import requests
response = requests.get(url, verify=True)  # Never set verify=False
```

**Network Egress Filtering (Optional):**
```bash
# Allowlist only required domains (iptables example)
sudo iptables -A OUTPUT -p tcp -d notebooklm.googleapis.com --dport 443 -j ACCEPT
sudo iptables -A OUTPUT -p tcp -d www.googleapis.com --dport 443 -j ACCEPT
sudo iptables -A OUTPUT -p tcp -d oauth2.googleapis.com --dport 443 -j ACCEPT
sudo iptables -A OUTPUT -p tcp --dport 443 -j DROP  # Block all other HTTPS
```

---

## Container Security

### Non-Root Execution

**Container User Configuration:**
```dockerfile
# Containerfile.debian
FROM registry.access.redhat.com/ubi9/python-311:latest

# Create non-root user
RUN useradd -u 1000 -g 0 -m -d /opt/app-root/src apeuser

# Switch to non-root
USER 1000

# ...
```

**Verify Non-Root:**
```bash
# Check container user
podman run --rm quay.io/jasoande/project_ape/project-ape:4.0.1 id
# Expected: uid=1000(apeuser) gid=0(root) groups=0(root)
```

### Read-Only Filesystem Mounts

**Secure Mount Configuration:**
```bash
podman run \
  -v ./client_data:/app/client_data:ro,z \      # Read-only client data
  -v ./vars.py:/app/vars.py:ro,z \              # Read-only config
  -v ./logs:/app/logs:rw,z \                    # Writable logs only
  -v project-ape-credentials:/opt/app-root/src/.notebooklm:ro,z \  # RO creds
  quay.io/jasoande/project_ape/project-ape:4.0.1
```

**Benefits:**
- Prevents container from modifying source data
- Limits blast radius of container compromise

### Capability Dropping

**Run with Minimal Capabilities:**
```bash
podman run \
  --cap-drop=ALL \                              # Drop all capabilities
  --cap-add=NET_BIND_SERVICE \                  # Add only needed (port 8765)
  --security-opt=no-new-privileges \            # Prevent privilege escalation
  quay.io/jasoande/project_ape/project-ape:4.0.1
```

### SELinux Enforcement (RHEL/Fedora)

**Verify SELinux Context:**
```bash
# Check SELinux mode
getenforce
# Expected: Enforcing

# Verify volume mounts have correct labels (:z flag)
podman inspect <container-id> | jq '.[0].Mounts'
```

**SELinux Policy (if needed):**
```bash
# Allow container to write to logs directory
sudo semanage fcontext -a -t container_file_t '/path/to/logs(/.*)?'
sudo restorecon -Rv /path/to/logs/
```

### Rootless Containers (Recommended)

**Run Containers as Non-Root User:**
```bash
# No sudo needed - rootless podman
podman run \
  -v ~/.notebooklm:/opt/app-root/src/.notebooklm:ro \
  quay.io/jasoande/project_ape/project-ape:4.0.1

# Verify rootless
podman info | grep rootless
# Expected: rootless: true
```

### Image Scanning

**Scan for Vulnerabilities:**
```bash
# Using Trivy scanner
trivy image quay.io/jasoande/project_ape/project-ape:4.0.1

# Expected: No HIGH or CRITICAL vulnerabilities
```

**Automated Scanning (CI/CD):**
```yaml
# .github/workflows/security-scan.yml
name: Container Security Scan
on: [push]
jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Trivy scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'quay.io/jasoande/project_ape/project-ape:4.0.1'
        severity: 'CRITICAL,HIGH'
```

---

## Data Security

### Data at Rest

**Generated Documents:**
```
docs_generated/
├── client_id_1/
│   ├── Client_Analysis.txt          # Plain text (no encryption)
│   ├── NotebookLM_Link.txt          # Contains notebook ID (public)
│   └── Quality_Score.json           # Metrics (non-sensitive)
```

**Data Classification:**
- **PUBLIC** - Notebook IDs, quality scores
- **INTERNAL** - Analysis reports (may contain business-sensitive info)
- **CONFIDENTIAL** - Client PDFs (user-provided data)

**Encryption Recommendations:**
```bash
# Encrypt sensitive outputs (if needed)
# Option 1: Filesystem encryption (LUKS on Linux)
sudo cryptsetup luksFormat /dev/sdb1
sudo cryptsetup luksOpen /dev/sdb1 encrypted-docs
sudo mkfs.ext4 /dev/mapper/encrypted-docs
sudo mount /dev/mapper/encrypted-docs /mnt/docs_generated

# Option 2: Per-file encryption (GPG)
gpg --symmetric --cipher-algo AES256 docs_generated/client/Analysis.txt
# Output: Analysis.txt.gpg

# Option 3: macOS FileVault (full disk encryption)
# Already enabled on most modern Macs

# Option 4: Windows BitLocker
# Encrypt drive containing docs_generated/
```

### Data in Transit

**All External API Calls Use TLS 1.2+:**
```python
# Enforce TLS 1.2 minimum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context()
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

session = requests.Session()
session.mount('https://', TLSAdapter())
```

### PII Handling

**Automatic PII Detection (Future Enhancement):**
```python
import re

def redact_pii(text):
    """Redact common PII from logs"""
    # Email addresses
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 
                  '[EMAIL REDACTED]', text)
    
    # SSN (US format)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN REDACTED]', text)
    
    # Credit cards (simple pattern)
    text = re.sub(r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b', 
                  '[CC REDACTED]', text)
    
    return text

# Apply to logs
logger.info(redact_pii(log_message))
```

### GDPR Compliance

**Right to Erasure (Data Deletion):**
```bash
# Delete all client data
rm -rf docs_generated/client_id/
rm -f logs/client_id.log
rm -f .multi_process_status/client_id.json

# Revoke OAuth tokens (if user requests)
# 1. User visits https://myaccount.google.com/permissions
# 2. Remove "Project APE" access
# 3. Delete local credential files
rm ~/.notebooklm/credentials.json
rm credentials/token_drive.json
```

**Data Retention Policy:**
- Generated docs: Retained indefinitely (user responsibility to delete)
- Logs: Rotate after 30 days (configurable)
- OAuth tokens: Revocable by user anytime

---

## API Security

### Rate Limiting

**Google API Quotas:**
- NotebookLM API: 60 requests/minute/user
- Drive API: 1000 requests/100 seconds/user

**Quota Handling:**
```python
# core/source_manager.py
def execute_with_retry(func, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            return func()
        except QuotaExceeded:
            backoff = min(60, 2 ** attempt)
            logger.warning(f"Quota exceeded, backing off {backoff}s")
            time.sleep(backoff)
    raise MaxRetriesExceeded()
```

### API Scopes (Least Privilege)

**NotebookLM Scopes (Minimal):**
```
https://www.googleapis.com/auth/notebooklm              # Create/manage notebooks
https://www.googleapis.com/auth/notebooklm.readonly     # Read notebook data
```

**Drive Scopes (Read-Only):**
```
https://www.googleapis.com/auth/drive.readonly          # Read files
https://www.googleapis.com/auth/drive.metadata.readonly # Read metadata
```

**❌ Excessive Scopes (Never Request):**
```
https://www.googleapis.com/auth/drive                   # Full Drive access (write)
https://www.googleapis.com/auth/gmail.readonly          # Gmail access (unnecessary)
```

### API Key Security

**Gemini API Key (Optional - Quality Scoring):**
```bash
# Store in environment variable (not in code)
export GEMINI_API_KEY="AIzaSyC..."

# Use in application
gemini_key = os.getenv('GEMINI_API_KEY')
if not gemini_key:
    logger.warning("Gemini API key not set, quality scoring disabled")
```

**Container Secret Injection:**
```bash
# Podman secret
echo "AIzaSyC..." | podman secret create gemini-api-key -

# Use in container
podman run \
  --secret gemini-api-key,type=env,target=GEMINI_API_KEY \
  quay.io/jasoande/project_ape/project-ape:4.0.1
```

---

## Audit & Logging

### Security Event Logging

**Events to Log:**
- ✅ Authentication attempts (success/failure)
- ✅ OAuth token refresh
- ✅ API errors (quota, permission denied)
- ✅ File access (Drive downloads)
- ✅ Workflow execution (start/stop)
- ✅ Configuration changes

**Log Format (Structured JSON):**
```json
{
  "timestamp": "2026-07-06T14:30:15.123Z",
  "level": "INFO",
  "event_type": "auth_success",
  "user": "user@example.com",
  "client_id": "acme_corp",
  "source_ip": "127.0.0.1",
  "message": "NotebookLM authentication successful"
}
```

### Sensitive Data Redaction

**Automatic Redaction:**
```python
import logging
import re

class RedactingFormatter(logging.Formatter):
    def format(self, record):
        original = super().format(record)
        
        # Redact access tokens
        redacted = re.sub(
            r'(access_token["\']?\s*[:=]\s*["\']?)([A-Za-z0-9._-]+)',
            r'\1[REDACTED]',
            original
        )
        
        # Redact OAuth secrets
        redacted = re.sub(
            r'(client_secret["\']?\s*[:=]\s*["\']?)([A-Za-z0-9._-]+)',
            r'\1[REDACTED]',
            redacted
        )
        
        return redacted

# Apply to handlers
handler = logging.FileHandler('logs/security.log')
handler.setFormatter(RedactingFormatter())
```

### SIEM Integration

**Syslog Forwarding (Future):**
```python
from logging.handlers import SysLogHandler

syslog = SysLogHandler(address=('siem.company.com', 514))
syslog.setFormatter(JsonFormatter())
logger.addHandler(syslog)
```

**Splunk Integration:**
```python
# Install splunk-sdk
from splunklib import client

service = client.connect(
    host='splunk.company.com',
    port=8089,
    username='admin',
    password=os.getenv('SPLUNK_PASSWORD')
)

# Send event
index = service.indexes['security']
index.submit(json.dumps(security_event))
```

---

## Vulnerability Management

### CVE Monitoring

**Subscribe to Security Advisories:**
- Google Cloud Security Bulletins: https://cloud.google.com/support/bulletins
- Python Security Advisories: https://www.python.org/news/security/
- Container Base Image Updates: https://access.redhat.com/security/updates/

### Dependency Scanning

**Python Dependency Audit:**
```bash
# Install safety scanner
pip install safety

# Scan for vulnerabilities
safety check --file requirements.txt

# Expected output:
# ╒══════════════════════════════════════════════════════════════════════╕
# │ No known security vulnerabilities found.                             │
# ╘══════════════════════════════════════════════════════════════════════╛
```

**Automated Scanning (GitHub Actions):**
```yaml
name: Security Audit
on: [push, pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Python dependency audit
      run: |
        pip install safety
        safety check -r requirements.txt --exit-code 1
```

### Patch Management

**Patch Schedule:**
- **CRITICAL vulnerabilities:** Patch within 24 hours
- **HIGH vulnerabilities:** Patch within 7 days
- **MEDIUM vulnerabilities:** Patch within 30 days
- **LOW vulnerabilities:** Patch in next release

**Update Procedure:**
```bash
# 1. Update dependencies
pip install --upgrade -r requirements.txt

# 2. Run tests
python -m pytest tests/

# 3. Rebuild container
podman build -t project-ape:latest -f Containerfile.debian .

# 4. Security scan
trivy image project-ape:latest

# 5. Deploy if clean
podman push quay.io/jasoande/project_ape/project-ape:latest
```

---

## Security Hardening Checklist

### Pre-Production Review

**Authentication:**
- [ ] OAuth 2.0 enabled for NotebookLM
- [ ] OAuth 2.0 enabled for Google Drive
- [ ] MFA enforced on Google accounts
- [ ] Least-privilege scopes configured
- [ ] Token expiry validated (90-day refresh)

**Secrets:**
- [ ] Credentials file permissions set to 600
- [ ] No hardcoded API keys in code
- [ ] Environment variables used for secrets
- [ ] Secrets rotation schedule defined

**Network:**
- [ ] Dashboard bound to 127.0.0.1 (localhost only)
- [ ] Firewall rules block external access to 8765
- [ ] TLS 1.2+ enforced for all API calls
- [ ] Certificate validation enabled

**Container:**
- [ ] Non-root user (UID 1000)
- [ ] Read-only mounts for client data and config
- [ ] Capabilities dropped (--cap-drop=ALL)
- [ ] Rootless podman enabled
- [ ] Image scanned for vulnerabilities (no HIGH/CRITICAL)

**Data:**
- [ ] Generated docs directory has restricted permissions
- [ ] PII redaction enabled in logs
- [ ] Data retention policy documented
- [ ] Backup encryption configured (if needed)

**Logging:**
- [ ] Security events logged (auth, API errors)
- [ ] Sensitive data redacted from logs
- [ ] Log rotation configured
- [ ] SIEM integration tested (if applicable)

**Compliance:**
- [ ] GDPR data deletion procedure tested
- [ ] Audit trail reviewed
- [ ] Security documentation complete
- [ ] Incident response plan defined

---

## Incident Response

### Detection

**Indicators of Compromise:**
- ⚠️ Unexpected authentication failures
- ⚠️ OAuth token refresh failures
- ⚠️ API quota exceeded (unusual volume)
- ⚠️ File access from unknown Drive folders
- ⚠️ Unauthorized configuration changes

**Monitoring Alerts:**
```python
# Example alert triggers
if auth_failure_count > 5:
    alert("Repeated authentication failures - possible credential theft")

if api_quota_exceeded:
    alert("API quota exceeded - possible abuse")

if drive_access_denied:
    alert("Drive access denied - check OAuth token validity")
```

### Response Procedure

**1. Immediate Containment (15 minutes):**
```bash
# Stop all workflows
pkill -f "python.*main.py"

# Revoke OAuth tokens
# Visit https://myaccount.google.com/permissions → Remove access

# Rotate credentials
rm ~/.notebooklm/credentials.json
rm credentials/token_drive.json
```

**2. Investigation (1 hour):**
```bash
# Review logs for anomalies
grep -i "error\|failed\|denied" logs/*.log

# Check for unauthorized API calls
grep "Unauthorized\|403\|401" logs/*.log

# Review file access patterns
grep "Downloaded PDF" logs/*.log | sort | uniq -c
```

**3. Recovery (2 hours):**
```bash
# Re-authenticate with fresh credentials
notebooklm login
python3 setup-oauth-drive.py

# Verify new tokens work
notebooklm list

# Restart workflows
python3 launch-project-ape.py
```

**4. Post-Incident (1 week):**
- Document incident timeline
- Identify root cause
- Implement preventive controls
- Update incident response plan

### Credential Revocation

**Emergency Revocation:**
```bash
# 1. Immediate user action
# Visit: https://myaccount.google.com/permissions
# Find: "NotebookLM" and "Project APE"
# Action: Click "Remove Access"

# 2. Delete local credentials
rm -f ~/.notebooklm/credentials.json
rm -f credentials/token_drive.json

# 3. Regenerate OAuth client (if client_secret compromised)
# - Google Cloud Console → APIs & Services → Credentials
# - Delete old OAuth client
# - Create new OAuth client
# - Download new credentials.json

# 4. Re-authenticate
notebooklm login
python3 setup-oauth-drive.py
```

---

## Compliance

### SOC 2 Type II

**Relevant Controls:**
- **CC6.1** - Logical Access Controls: OAuth 2.0, MFA
- **CC6.6** - Encryption: TLS 1.2+ for data in transit
- **CC7.2** - Security Monitoring: Audit logging, SIEM integration

**Audit Evidence:**
- Authentication logs (`logs/security.log`)
- Access control policies (this document)
- Encryption verification (API call logs)

### ISO 27001

**Annex A Controls:**
- **A.9.2.1** - User registration: OAuth onboarding
- **A.9.4.1** - Information access restriction: Least-privilege scopes
- **A.10.1.1** - Cryptographic controls: TLS 1.2+
- **A.12.4.1** - Event logging: Security audit logs
- **A.18.1.5** - Regulation of cryptographic controls: No export-controlled crypto

### NIST Cybersecurity Framework

**Mapping to CSF Functions:**

| NIST CSF | Project APE Implementation |
|----------|----------------------------|
| **Identify (ID)** | Threat model documented, asset inventory |
| **Protect (PR)** | OAuth 2.0, TLS 1.2+, container isolation |
| **Detect (DE)** | Security logging, API error monitoring |
| **Respond (RS)** | Incident response playbooks, token revocation |
| **Recover (RC)** | Credential re-authentication, backup procedures |

---

<div align="center">
  
  **Security is a shared responsibility.**  
  Project APE provides secure defaults—follow this guide to maintain them.
  
  ---
  
  **Questions?** See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | [Report Security Issues](https://github.com/jasoande/Project-APE-dev/security)
  
  *Last Updated: July 2026 | Version 4.0.1*
  
</div>
