# Local SSL/HTTPS Setup Guide
**Account Intelligence - Local Development with HTTPS**

## Overview

This guide shows how to enable HTTPS for local development of the Account Intelligence dashboard. For local development on `localhost`, we use **self-signed certificates** (the standard approach). Let's Encrypt requires a publicly accessible domain, so it's only used for production deployments.

---

## Quick Setup (5 minutes)

### Automated Setup (Recommended)

**Cross-platform Python script (works on Windows, macOS, Linux):**
```bash
python3 setup-ssl-local.py
```

**Or bash script (Linux/macOS only):**
```bash
./setup-ssl-local.sh
```

Both scripts automatically:
- Create `certs/` directory
- Generate 4096-bit RSA self-signed certificate
- Set proper file permissions
- Verify certificate details
- Check vars.py configuration
- Provide next steps

**Which script to use:**
| Platform | Recommended | Alternative |
|----------|-------------|-------------|
| **Windows** | `python3 setup-ssl-local.py` | Manual setup below |
| **macOS** | `./setup-ssl-local.sh` | `python3 setup-ssl-local.py` |
| **Linux** | `./setup-ssl-local.sh` | `python3 setup-ssl-local.py` |

### Manual Setup (Alternative)

If you prefer manual setup or the scripts aren't working:

**Step 1: Create Certificate Directory**

```bash
mkdir -p certs
```

**Step 2: Generate Self-Signed Certificate**

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/C=US/ST=State/L=City/O=Development/OU=Local/CN=localhost"
```

**What this does:**
- Creates a 4096-bit RSA self-signed certificate
- Valid for 365 days (1 year)
- No passphrase required (`-nodes`)
- Common Name (CN) set to `localhost`

**Output:**
```
Generating a RSA private key
.......................++++
.......................++++
writing new private key to 'certs/key.pem'
-----
```

### Step 3: Verify Certificate Files

```bash
ls -lh certs/
```

**Expected output:**
```
-rw-r--r--  cert.pem  (2.0K)
-rw-------  key.pem   (3.2K)
```

### Step 4: Configure vars.py

Add these lines to your `vars.py` file (or edit via web UI):

```python
# ==============================================================================
# SSL/HTTPS CONFIGURATION
# ==============================================================================

SSL_ENABLED = True
SSL_CERT_PATH = "certs/cert.pem"
SSL_KEY_PATH = "certs/key.pem"
```

### Step 5: Launch Dashboard

**Option 1: GUI Launcher (Recommended)**
```bash
# Double-click launch-project-ape.command (macOS)
# or
python3 launch-project-ape.py
```

The launcher automatically detects SSL configuration and:
- Starts `server_gevent.py` (supports SSL)
- Opens browser to `https://localhost:8765/configure`

**Option 2: Manual Launch**
```bash
python3 dashboard/server_gevent.py
```

**Expected output:**
```
🔒 SSL/HTTPS enabled

🚀 Dashboard (Gevent mode) starting on https://127.0.0.1:8765
   Using gevent WSGI server (greenlet-based)
   Supports 10,000+ concurrent SSE connections
   Thread exhaustion: ELIMINATED ✅

📊 Dashboard URL: https://127.0.0.1:8765
⚙️  Configure:     https://127.0.0.1:8765/configure
```

### Step 6: Accept Browser Security Warning

When you open `https://localhost:8765`, your browser will show a security warning:

**Chrome/Edge:**
```
Your connection is not private
NET::ERR_CERT_AUTHORITY_INVALID
```

**Firefox:**
```
Warning: Potential Security Risk Ahead
```

**Safari:**
```
This Connection Is Not Private
```

**To proceed:**
1. Click "Advanced" or "Show Details"
2. Click "Proceed to localhost (unsafe)" or "Accept the Risk and Continue"
3. Dashboard loads normally

**Why this happens:** Self-signed certificates aren't issued by a trusted Certificate Authority. This is normal and safe for local development.

---

## Certificate Details

### Verify Certificate Information

```bash
# View certificate subject
openssl x509 -in certs/cert.pem -noout -subject

# Output:
# subject=C=US, ST=State, L=City, O=Development, OU=Local, CN=localhost
```

```bash
# Check expiration dates
openssl x509 -in certs/cert.pem -noout -dates

# Output:
# notBefore=Jul 10 15:11:26 2026 GMT
# notAfter=Jul 10 15:11:26 2027 GMT
```

```bash
# View full certificate details
openssl x509 -in certs/cert.pem -text -noout
```

### Certificate Renewal

Self-signed certificates expire after 365 days. To renew:

```bash
# Regenerate certificate (same command as setup)
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/C=US/ST=State/L=City/O=Development/OU=Local/CN=localhost"

# Restart dashboard server
```

---

## File Permissions and Security

### Verify Permissions

```bash
ls -la certs/
```

**Recommended permissions:**
- `cert.pem`: `644` (readable by all, writable by owner)
- `key.pem`: `600` (readable/writable by owner only)

### Fix Permissions (if needed)

```bash
chmod 644 certs/cert.pem
chmod 600 certs/key.pem
```

### Security Best Practices

1. **Never commit certificates to git:**
   ```bash
   # Already in .gitignore, but verify:
   grep "certs/" .gitignore
   ```

2. **Use separate certificates for each environment:**
   - Local dev: Self-signed
   - Production: Let's Encrypt or commercial CA

3. **Rotate regularly:**
   - Regenerate every 90-365 days
   - Mark calendar for expiration date

---

## Troubleshooting

### Certificate Files Not Found

**Error:**
```
⚠️  SSL enabled but certificate files not found:
   Certificate: certs/cert.pem (not found)
```

**Solution:**
```bash
# Check files exist
ls certs/

# Verify paths in vars.py are correct (relative to project root)
grep SSL_ vars.py

# Regenerate if missing
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem -out certs/cert.pem \
  -days 365 -subj "/C=US/ST=State/L=City/O=Development/OU=Local/CN=localhost"
```

### Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'certs/key.pem'
```

**Solution:**
```bash
# Fix file permissions
chmod 600 certs/key.pem
chmod 644 certs/cert.pem

# Verify ownership
ls -la certs/
```

### Gevent Not Installed

**Error:**
```
ModuleNotFoundError: No module named 'gevent'
```

**Solution:**
```bash
# Install gevent
pip install gevent>=24.0.0

# Or reinstall all dependencies
pip install -r requirements.txt
```

### Browser Won't Accept Certificate

**Symptom:** Browser repeatedly shows security warning, won't proceed.

**Solution:**

**Chrome/Edge (macOS):**
1. Type `thisisunsafe` while viewing the warning (no input field appears, just type it)
2. Or add exception in Keychain Access

**Firefox:**
1. Click "Advanced" → "Accept the Risk and Continue"
2. Or go to `about:config` → set `security.enterprise_roots.enabled` to `true`

**Safari:**
1. Click "Show Details" → "Visit this website"
2. Or add to System Keychain

### Dashboard Still Uses HTTP

**Symptom:** Browser opens to `http://localhost:8765` instead of `https://`

**Solution:**
```bash
# Verify SSL_ENABLED in vars.py
grep SSL_ENABLED vars.py

# Should show: SSL_ENABLED = True

# Restart launcher
python3 launch-project-ape.py
```

---

## Advanced Configuration

### Custom Certificate Subject

Edit the `-subj` parameter to customize certificate details:

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/C=US/ST=California/L=San Francisco/O=MyCompany/OU=Engineering/CN=localhost"
```

**Subject fields:**
- `C` = Country (2-letter code)
- `ST` = State/Province
- `L` = Locality/City
- `O` = Organization
- `OU` = Organizational Unit
- `CN` = Common Name (must be `localhost` for local dev)

### Multiple Hostnames (SAN)

To use the certificate with multiple hostnames:

1. Create a configuration file:

```bash
cat > certs/openssl.cnf << 'EOF'
[req]
default_bits = 4096
prompt = no
default_md = sha256
x509_extensions = v3_req
distinguished_name = dn

[dn]
C = US
ST = State
L = City
O = Development
OU = Local
CN = localhost

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.localhost
DNS.3 = 127.0.0.1
IP.1 = 127.0.0.1
IP.2 = ::1
EOF
```

2. Generate certificate with SAN:

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -config certs/openssl.cnf
```

### Longer Validity Period

For development convenience (avoids frequent renewal):

```bash
# 10-year certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 3650 \
  -subj "/C=US/ST=State/L=City/O=Development/OU=Local/CN=localhost"
```

**Note:** Browsers may warn about very long validity periods.

---

## Production SSL with Let's Encrypt

**For production deployments with a real domain name**, use Let's Encrypt:

### Prerequisites

- Public domain name (e.g., `dashboard.example.com`)
- Server with port 80 and 443 open
- DNS pointing to server IP

### Installation

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install certbot

# macOS
brew install certbot

# RHEL/Fedora
sudo dnf install certbot
```

### Certificate Generation

```bash
# Standalone mode (no web server running)
sudo certbot certonly --standalone -d dashboard.example.com

# Webroot mode (nginx/apache running)
sudo certbot certonly --webroot -w /var/www/html -d dashboard.example.com

# Interactive prompts:
# - Email for renewal notices
# - Agree to Terms of Service
# - Share email with EFF (optional)
```

### Configure vars.py for Production

```python
SSL_ENABLED = True
SSL_CERT_PATH = "/etc/letsencrypt/live/dashboard.example.com/fullchain.pem"
SSL_KEY_PATH = "/etc/letsencrypt/live/dashboard.example.com/privkey.pem"
```

### Auto-Renewal

Let's Encrypt certificates expire every 90 days. Set up auto-renewal:

```bash
# Test renewal
sudo certbot renew --dry-run

# Add cron job for auto-renewal
sudo crontab -e

# Add this line:
0 3 * * * certbot renew --quiet --post-hook "systemctl restart project-ape"
```

### Nginx Reverse Proxy (Recommended for Production)

Instead of native SSL in the dashboard, use nginx as reverse proxy:

```nginx
# /etc/nginx/sites-available/project-ape
server {
    listen 443 ssl http2;
    server_name dashboard.example.com;

    ssl_certificate /etc/letsencrypt/live/dashboard.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dashboard.example.com/privkey.pem;

    # Mozilla Modern SSL Configuration
    ssl_protocols TLSv1.3;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;

        # SSE support
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name dashboard.example.com;
    return 301 https://$server_name$request_uri;
}
```

Enable and start:

```bash
sudo ln -s /etc/nginx/sites-available/project-ape /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

With nginx, keep `SSL_ENABLED = False` in vars.py (nginx handles SSL).

---

## Testing SSL Configuration

### Test Certificate

```bash
# Connect with OpenSSL client
openssl s_client -connect localhost:8765 -showcerts

# Check for:
# - "Verify return code: 0 (ok)" or
# - "Verify return code: 18 (self signed certificate)" (normal for self-signed)
```

### Test HTTPS Response

```bash
# Curl with self-signed cert
curl -k https://localhost:8765/health

# Should return: {"status": "healthy"}
```

### Browser Developer Tools

1. Open browser to `https://localhost:8765`
2. Open DevTools (F12)
3. Go to Security tab
4. Verify connection details:
   - Protocol: TLS 1.3
   - Cipher: Modern cipher suite
   - Certificate: Self-signed

---

## File Structure

```
project-ape/
├── certs/                      # SSL certificates (git-ignored)
│   ├── cert.pem               # Public certificate (2KB)
│   ├── key.pem                # Private key (3KB)
│   └── openssl.cnf            # Optional: SAN config
├── vars.py                     # Configuration (git-ignored)
│   └── SSL_ENABLED = True
├── dashboard/
│   ├── server.py              # HTTP-only (waitress)
│   └── server_gevent.py       # HTTP + HTTPS (gevent)
└── launch-project-ape.py      # Auto-detects SSL
```

---

## Summary

### What We Set Up

1. ✅ Created `certs/` directory
2. ✅ Generated self-signed SSL certificate (4096-bit RSA, 1-year validity)
3. ✅ Configured `vars.py` with SSL settings
4. ✅ Launcher auto-detects SSL and uses gevent server
5. ✅ Dashboard accessible at `https://localhost:8765`

### Security Notes

- **Self-signed certificates** = Normal for local dev, browser warnings expected
- **Let's Encrypt** = Use for production with real domain
- **Nginx reverse proxy** = Recommended for production deployments
- **Certificate files** = Never commit to git, rotate regularly

### Quick Reference

| Task | Command |
|------|---------|
| Generate cert | `openssl req -x509 -newkey rsa:4096 -nodes -keyout certs/key.pem -out certs/cert.pem -days 365 -subj "/CN=localhost"` |
| Check expiry | `openssl x509 -in certs/cert.pem -noout -dates` |
| Start HTTPS | `python3 launch-project-ape.py` or `python3 dashboard/server_gevent.py` |
| Test connection | `curl -k https://localhost:8765/health` |
| Fix permissions | `chmod 600 certs/key.pem && chmod 644 certs/cert.pem` |

### Next Steps

- Access dashboard: `https://localhost:8765/configure`
- Configure clients via web UI
- Launch workflows with SSL encryption
- See `Docs/SSL_SETUP_GUIDE.md` for production SSL deployment

---

## Support

For SSL issues:
- Check dashboard logs: `tail -f logs/dashboard.log`
- Verify certificate: `openssl x509 -in certs/cert.pem -text -noout`
- Test SSL handshake: `openssl s_client -connect localhost:8765`
- Browser console: Check for mixed content warnings

Related documentation:
- `Docs/SSL_SETUP_GUIDE.md` - Production SSL setup
- `Docs/CONTAINER_SECURITY_GUIDE.md` - Container security
- `Docs/DEPLOYMENT_GUIDE.md` - Production deployment
