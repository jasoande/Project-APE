# SSL/HTTPS Security

**Account Intelligence uses HTTPS for all dashboard communication.**

## Overview

All communication with the Account Intelligence dashboard is encrypted using SSL/HTTPS. SSL certificates are automatically generated and managed—no manual configuration required.

### Key Features

- **Automatic certificate generation** - Self-signed certificates created on first launch
- **Automatic renewal** - Certificates regenerate before expiration (<30 days remaining)
- **Zero configuration** - No manual setup steps required
- **Cross-platform** - Works on Windows, macOS, and Linux
- **Production ready** - Supports Let's Encrypt and commercial certificates

---

## Quick Start

### First Launch

```bash
python3 launch-project-ape.py
```

On first launch, the application automatically:
1. Checks for OpenSSL availability
2. Generates 4096-bit RSA self-signed certificate (365-day validity)
3. Stores certificates in `certs/` directory
4. Sets secure file permissions (key: 600, certificate: 644)
5. Starts dashboard on https://localhost:8765

**No configuration required.**

### Browser Security Warning

When accessing https://localhost:8765, your browser will show a security warning:

```
Your connection is not private
NET::ERR_CERT_AUTHORITY_INVALID
```

**This is normal and expected for self-signed certificates.**

**To proceed:**
1. Click "Advanced" or "Show Details"
2. Click "Proceed to localhost (unsafe)" or "Accept the Risk"

**Why this happens:** Self-signed certificates are not issued by a trusted Certificate Authority. This is safe for localhost development.

---

## How It Works

### Certificate Lifecycle

**Generation:**
- 4096-bit RSA encryption
- Self-signed X.509 certificate
- Common Name: localhost
- Validity: 365 days (1 year)
- Algorithm: SHA-256

**Storage:**
```
project-ape/
├── certs/
│   ├── cert.pem  (2KB, permissions: 644)
│   └── key.pem   (3KB, permissions: 600)
```

**Auto-Renewal:**
- Checked on every launcher startup
- Regenerates if:
  - Missing or corrupted
  - Expired (validity < 0 days)
  - Expiring soon (validity < 30 days)

### Certificate Manager

The `ssl_manager.py` module handles all certificate operations:

**Functions:**
- `check_openssl_available()` - Verifies OpenSSL is installed
- `check_certificate_validity()` - Returns validity status and days remaining
- `generate_certificate()` - Creates self-signed certificate
- `ensure_certificates()` - Main lifecycle management (auto-generate/renew)

**Example usage:**
```python
from ssl_manager import ensure_certificates
from pathlib import Path

if ensure_certificates(Path("certs")):
    print("Certificates ready")
```

---

## Configuration

### Default Configuration

SSL is always enabled. Certificates use default paths:

```python
# vars.py (automatically generated)
SSL_CERT_PATH = "certs/cert.pem"
SSL_KEY_PATH = "certs/key.pem"
```

### Custom Certificate Paths

To use certificates in a different location:

```python
# vars.py
SSL_CERT_PATH = "/path/to/custom/cert.pem"
SSL_KEY_PATH = "/path/to/custom/key.pem"
```

Paths can be absolute or relative to project root.

### Using Your Own Certificates

Replace auto-generated certificates with your own:

**Option 1: Replace files**
```bash
# Backup auto-generated certificates
mv certs/cert.pem certs/cert.pem.bak
mv certs/key.pem certs/key.pem.bak

# Copy your certificates
cp /path/to/your/cert.pem certs/cert.pem
cp /path/to/your/key.pem certs/key.pem

# Set permissions
chmod 644 certs/cert.pem
chmod 600 certs/key.pem
```

**Option 2: Custom paths**
```python
# vars.py
SSL_CERT_PATH = "/etc/ssl/certs/mycert.pem"
SSL_KEY_PATH = "/etc/ssl/private/mykey.pem"
```

---

## Production Deployment

For production environments with a real domain name, use proper SSL certificates.

### Option 1: Let's Encrypt (Free, Automated)

**Install certbot:**
```bash
# Ubuntu/Debian
sudo apt-get install certbot

# macOS
brew install certbot

# RHEL/CentOS
sudo dnf install certbot
```

**Generate certificate:**
```bash
sudo certbot certonly --standalone -d yourdomain.com
```

**Configure Account Intelligence:**
```python
# vars.py
SSL_CERT_PATH = "/etc/letsencrypt/live/yourdomain.com/fullchain.pem"
SSL_KEY_PATH = "/etc/letsencrypt/live/yourdomain.com/privkey.pem"
```

**Auto-renewal:**
```bash
# Add to crontab
0 3 * * * certbot renew --quiet --post-hook "systemctl restart project-ape"
```

### Option 2: Nginx Reverse Proxy (Recommended)

Use nginx for SSL termination:

**Benefits:**
- Better performance under high load
- Centralized certificate management
- Additional security features (rate limiting, WAF)
- Industry-standard approach

**Nginx configuration:**
```nginx
# /etc/nginx/sites-available/project-ape
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Proxy to Dashboard
    location / {
        proxy_pass https://127.0.0.1:8765;
        proxy_ssl_verify off;  # Dashboard uses self-signed cert
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;

        # SSE Support
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

**Enable and start:**
```bash
sudo ln -s /etc/nginx/sites-available/project-ape /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 3: Kubernetes Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: project-ape
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - yourdomain.com
    secretName: project-ape-tls
  rules:
  - host: yourdomain.com
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

---

## Troubleshooting

### OpenSSL Not Found

**Error:**
```
❌ Error: OpenSSL not found
   OpenSSL is required for SSL certificate generation.
```

**Solution - Install OpenSSL:**

**macOS:**
```bash
brew install openssl
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install openssl
```

**RHEL/CentOS/Fedora:**
```bash
sudo dnf install openssl
```

**Windows:**
- Install Git for Windows (includes OpenSSL): https://git-scm.com/download/win
- Or via Chocolatey: `choco install openssl`
- Or direct download: https://slproweb.com/products/Win32OpenSSL.html

### Certificate Files Not Found

**Error:**
```
❌ Error: SSL certificate files not found
   Expected:
   - Certificate: /path/to/certs/cert.pem
   - Key: /path/to/certs/key.pem
```

**Solution:**
```bash
# Run launcher (auto-generates certificates)
python3 launch-project-ape.py

# Or manually generate
python3 ssl_manager.py test
```

### Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied: 'certs/key.pem'
```

**Solution:**
```bash
# Fix permissions
chmod 600 certs/key.pem
chmod 644 certs/cert.pem

# Or fix ownership
sudo chown $(whoami):$(whoami) certs/*.pem
```

### Browser Won't Accept Certificate

**Symptom:** Browser repeatedly shows security warning, won't proceed.

**Solutions:**

**Chrome/Edge:**
- Type `thisisunsafe` while viewing the warning (no input field appears, just type it)
- Or add exception in Settings → Privacy → Manage certificates

**Firefox:**
- Click "Advanced" → "Accept the Risk and Continue"
- Or go to about:config → set `security.enterprise_roots.enabled` to `true`

**Safari:**
- Click "Show Details" → "Visit this website"
- Or add to System Keychain (Keychain Access app)

### Certificate Expired

Certificates auto-renew. If you see expiration errors, restart the launcher:

```bash
python3 launch-project-ape.py
```

This checks certificate validity and auto-renews if needed.

---

## Security Best Practices

### Local Development

✅ **DO:**
- Use auto-generated self-signed certificates
- Accept browser warnings for localhost
- Keep private keys secure (600 permissions)

❌ **DON'T:**
- Commit certificate files to git (already in .gitignore)
- Share private keys
- Disable SSL/HTTPS

### Production Deployment

✅ **DO:**
- Use Let's Encrypt or commercial CA certificates
- Enable auto-renewal for Let's Encrypt (90-day validity)
- Use nginx or HAProxy for SSL termination
- Enable HSTS headers
- Use TLS 1.2+ only (preferably TLS 1.3)

❌ **DON'T:**
- Use self-signed certificates in production
- Use outdated TLS versions (TLS 1.0, TLS 1.1)
- Expose private keys in logs or version control

### Certificate Storage

**Git-ignored paths:**
```
certs/          # SSL certificates (NEVER commit)
*.pem           # All PEM files
*.key           # Private keys
```

**File permissions (Unix):**
```bash
# Private key: owner-only
chmod 600 certs/key.pem

# Certificate: world-readable
chmod 644 certs/cert.pem

# Directory: owner-writable, others readable
chmod 755 certs/
```

---

## Advanced Topics

### Certificate Validation

Check certificate details:

```bash
# View certificate information
openssl x509 -in certs/cert.pem -text -noout

# Check expiration
openssl x509 -in certs/cert.pem -noout -dates

# Verify certificate chain
openssl verify certs/cert.pem
```

### Manual Certificate Generation

For testing or custom use cases:

```bash
# Generate 4096-bit RSA certificate (valid 365 days)
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/C=US/ST=State/L=City/O=Development/OU=Local/CN=localhost"

# Set permissions
chmod 600 certs/key.pem
chmod 644 certs/cert.pem
```

### Subject Alternative Names (SAN)

To support multiple hostnames:

```bash
# Create OpenSSL config
cat > certs/openssl.cnf <<EOF
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

# Generate certificate with SAN
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -config certs/openssl.cnf
```

### Testing SSL Configuration

```bash
# Test SSL handshake
openssl s_client -connect localhost:8765 -showcerts

# Test with curl
curl -k https://localhost:8765/health

# Expected: {"status": "healthy"}
```

---

## Technical Details

### Cipher Suites

**Default configuration:**
- Protocol: TLS 1.2, TLS 1.3
- Ciphers: Modern Mozilla configuration
- Key exchange: ECDHE
- Encryption: AES-256-GCM, AES-128-GCM

**gevent WSGI server:**
- Uses Python's ssl module
- Supports all ciphers available in OpenSSL
- Defaults to secure ciphers

### Certificate Specifications

**Generated certificates:**
```
Subject: C=US, ST=State, L=City, O=Development, OU=Local, CN=localhost
Issuer: (self-signed)
Validity: 365 days
Public Key: RSA 4096 bits
Signature Algorithm: sha256WithRSAEncryption
Key Usage: Digital Signature, Key Encipherment
```

### File Formats

**PEM (Privacy Enhanced Mail):**
- Text-based format
- Base64-encoded certificate/key
- Headers: `-----BEGIN CERTIFICATE-----`
- Supported by all tools and servers

---

## FAQ

**Q: Why is HTTPS required?**
A: HTTPS encrypts all dashboard communication, protecting credentials and data. It's a security best practice.

**Q: Can I disable SSL/HTTPS?**
A: No. SSL is always enabled for security. There is no HTTP mode.

**Q: Do I need to manually renew certificates?**
A: No. Self-signed certificates auto-renew. For Let's Encrypt, set up auto-renewal with certbot.

**Q: Can I use commercial SSL certificates?**
A: Yes. Set custom paths in vars.py (see Configuration section above).

**Q: What if I delete the certs/ directory?**
A: Certificates will be auto-generated on next launch. No manual intervention needed.

**Q: How do I increase Google Drive file size limit?**
A: Edit vars.py:
```python
DRIVE_CONFIG = {
    'max_file_size_mb': 500,  # Default is 50MB, API supports up to 5GB
}
```

**Q: Is this secure for production?**
A: Self-signed certificates are for local development. For production, use Let's Encrypt or commercial CA certificates.

---

## Summary

Account Intelligence uses HTTPS for all communication:

- ✅ Certificates auto-generate (zero setup required)
- ✅ Certificates auto-renew (no expiration issues)
- ✅ Cross-platform support (Windows, macOS, Linux)
- ✅ Production ready (supports Let's Encrypt and commercial CAs)
- ✅ Secure by default (no insecure HTTP mode)

For most users, SSL "just works" with no configuration required.
