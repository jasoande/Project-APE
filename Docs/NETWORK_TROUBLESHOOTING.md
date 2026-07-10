# Network Troubleshooting Guide
**Account Intelligence - Dashboard Connection Issues**

## Problem: Port Open But Browser Can't Load Page

### Symptom

```bash
# Port shows as listening
netstat -lpnut | grep 8765
tcp  0  0  127.0.0.1:8765  0.0.0.0:*  LISTEN

# But browser shows "Problem loading page" or connection refused
```

### Root Cause

The dashboard server is bound to `127.0.0.1` (localhost only) by default. On some Linux systems, especially:
- Headless servers
- Virtual machines
- WSL environments
- Container hosts
- Remote systems accessed via SSH

The browser may not be able to connect to `127.0.0.1:8765` even though the port is listening.

---

## Solution 1: Configure Host Binding (Recommended)

**Edit `vars.py` and change DASHBOARD_HOST:**

```python
# Change from default:
DASHBOARD_HOST = "127.0.0.1"  # Localhost only

# To allow all interfaces:
DASHBOARD_HOST = "0.0.0.0"  # All network interfaces
```

**Then restart the dashboard:**

```bash
# Stop any running instance
pkill -f server_gevent.py

# Restart
python3 launch-project-ape.py
```

**Verify:**

```bash
# Should now show 0.0.0.0:8765
netstat -lpnut | grep 8765
tcp  0  0  0.0.0.0:8765  0.0.0.0:*  LISTEN
```

---

## Solution 2: Environment Variable (Temporary)

For testing or one-time use:

```bash
export DASHBOARD_HOST=0.0.0.0
python3 launch-project-ape.py
```

This overrides the vars.py setting without modifying the file.

---

## Solution 3: SSH Port Forwarding (Remote Systems)

If accessing a remote Linux system via SSH:

```bash
# On your local machine, connect with port forwarding:
ssh -L 8765:localhost:8765 user@remote-server

# Then open browser to:
http://localhost:8765
```

This forwards your local port 8765 to the remote server's port 8765.

---

## Security Considerations

### Binding to 0.0.0.0

**What it means:**
- Dashboard accessible from any network interface
- Allows connections from other machines on the network
- Required for remote access, containers, VMs

**When to use:**
- Production deployments
- Team access to shared dashboard
- Container/VM environments
- Remote development servers

**Security recommendations when using 0.0.0.0:**
1. Enable SSL/HTTPS (see `Docs/SSL_SETUP_LOCAL.md`)
2. Use firewall rules to restrict access:
   ```bash
   # Allow only from specific IP
   sudo ufw allow from 192.168.1.100 to any port 8765
   
   # Or allow only local network
   sudo ufw allow from 192.168.1.0/24 to any port 8765
   ```
3. Consider nginx reverse proxy with authentication
4. Use VPN for remote access

### Binding to 127.0.0.1

**What it means:**
- Dashboard only accessible from the same machine
- More secure (no network exposure)
- Default for local development

**When to use:**
- Single-user local development
- Laptop/desktop development
- When you don't need remote access

---

## Verification Steps

### 1. Check What Interface Server is Bound To

```bash
# Check listening ports
netstat -lpnut | grep 8765

# Or with ss (modern alternative)
ss -lntp | grep 8765
```

**Expected outputs:**

| Binding | Output | Meaning |
|---------|--------|---------|
| `127.0.0.1:8765` | Localhost only | Only local connections |
| `0.0.0.0:8765` | All interfaces | Network accessible |

### 2. Test Local Connection

```bash
# Should work regardless of binding
curl http://127.0.0.1:8765/health
# Expected: {"status": "healthy"}
```

### 3. Test Network Connection (from another machine)

```bash
# Replace SERVER_IP with actual IP
curl http://SERVER_IP:8765/health

# If bound to 127.0.0.1, this will fail
# If bound to 0.0.0.0, this will succeed
```

### 4. Check Firewall

```bash
# Check if port 8765 is allowed
sudo ufw status | grep 8765

# If blocked, allow it:
sudo ufw allow 8765/tcp
```

---

## Common Scenarios

### Scenario 1: Local Development (Default)

**Configuration:**
```python
DASHBOARD_HOST = "127.0.0.1"
SSL_ENABLED = False
```

**Access:**
- From same machine: `http://localhost:8765`
- From other machines: ❌ Not accessible

**Use case:** Personal laptop/desktop development

---

### Scenario 2: VM or Container

**Configuration:**
```python
DASHBOARD_HOST = "0.0.0.0"
SSL_ENABLED = False
```

**Access:**
- From same machine: `http://localhost:8765`
- From host machine: `http://VM_IP:8765`
- From network: `http://VM_IP:8765`

**Use case:** Development in VM/container, access from host

---

### Scenario 3: Remote Development Server

**Configuration:**
```python
DASHBOARD_HOST = "0.0.0.0"
SSL_ENABLED = True
SSL_CERT_PATH = "certs/cert.pem"
SSL_KEY_PATH = "certs/key.pem"
```

**Access:**
- From network: `https://SERVER_IP:8765`
- Or use SSH tunnel for security

**Use case:** Team access to shared dev server

---

### Scenario 4: Production Deployment

**Configuration:**
```python
DASHBOARD_HOST = "127.0.0.1"  # Behind nginx
SSL_ENABLED = False  # Nginx handles SSL
```

**Nginx configuration:**
```nginx
server {
    listen 443 ssl;
    server_name dashboard.example.com;
    
    ssl_certificate /etc/letsencrypt/live/dashboard.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dashboard.example.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8765;
    }
}
```

**Access:**
- Public: `https://dashboard.example.com`

**Use case:** Production with SSL termination at nginx

---

## Quick Diagnostic Script

Save as `diagnose-network.sh`:

```bash
#!/bin/bash

echo "=== Account Intelligence Network Diagnostics ==="
echo ""

echo "1. Checking if dashboard server is running..."
if pgrep -f server_gevent.py > /dev/null; then
    echo "   ✅ Server is running"
else
    echo "   ❌ Server is not running"
    exit 1
fi

echo ""
echo "2. Checking port binding..."
BINDING=$(netstat -lntp 2>/dev/null | grep 8765 | awk '{print $4}')
if [ -z "$BINDING" ]; then
    BINDING=$(ss -lntp 2>/dev/null | grep 8765 | awk '{print $4}')
fi

if [[ "$BINDING" == *"127.0.0.1:8765"* ]]; then
    echo "   ⚠️  Bound to 127.0.0.1 (localhost only)"
    echo "      To allow network access, set DASHBOARD_HOST=0.0.0.0 in vars.py"
elif [[ "$BINDING" == *"0.0.0.0:8765"* ]]; then
    echo "   ✅ Bound to 0.0.0.0 (all interfaces)"
else
    echo "   ❓ Unknown binding: $BINDING"
fi

echo ""
echo "3. Testing local connection..."
if curl -s -f http://127.0.0.1:8765/health > /dev/null 2>&1; then
    echo "   ✅ Local connection works"
else
    echo "   ❌ Local connection failed"
fi

echo ""
echo "4. Checking firewall..."
if command -v ufw > /dev/null; then
    if sudo ufw status | grep -q "8765"; then
        echo "   ✅ Port 8765 allowed in firewall"
    else
        echo "   ⚠️  Port 8765 not in firewall rules"
        echo "      Run: sudo ufw allow 8765/tcp"
    fi
else
    echo "   ℹ️  UFW not installed, skipping firewall check"
fi

echo ""
echo "5. Current configuration:"
if [ -f "vars.py" ]; then
    DASHBOARD_HOST=$(grep "^DASHBOARD_HOST" vars.py 2>/dev/null | cut -d= -f2 | tr -d ' "'"'"'')
    if [ -z "$DASHBOARD_HOST" ]; then
        echo "   ⚠️  DASHBOARD_HOST not set in vars.py (defaults to 127.0.0.1)"
    else
        echo "   DASHBOARD_HOST = $DASHBOARD_HOST"
    fi
else
    echo "   ⚠️  vars.py not found"
fi

echo ""
echo "=== Recommendations ==="
if [[ "$BINDING" == *"127.0.0.1:8765"* ]]; then
    echo "• For network access, add to vars.py:"
    echo "  DASHBOARD_HOST = \"0.0.0.0\""
    echo ""
    echo "• Or use SSH port forwarding:"
    echo "  ssh -L 8765:localhost:8765 user@server"
fi

echo ""
```

**Run it:**

```bash
chmod +x diagnose-network.sh
./diagnose-network.sh
```

---

## Summary

**Problem:** Port listening but can't connect in browser

**Quick Fix:**

1. Edit `vars.py`:
   ```python
   DASHBOARD_HOST = "0.0.0.0"
   ```

2. Restart dashboard:
   ```bash
   pkill -f server_gevent.py
   python3 launch-project-ape.py
   ```

3. Access from browser:
   - Same machine: `http://localhost:8765`
   - Network: `http://SERVER_IP:8765`

**Security:** Enable SSL and firewall when using `0.0.0.0`

---

## See Also

- [SSL Setup Guide](SSL_SETUP_LOCAL.md) - Enable HTTPS
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production deployment
- [Security Guide](SECURITY.md) - Security best practices
