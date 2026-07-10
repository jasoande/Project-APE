# SSL/HTTPS Setup Guide
**Account Intelligence - Dashboard Security**

## Overview

The Account Intelligence dashboard supports optional SSL/HTTPS encryption for secure access. This guide shows you how to enable HTTPS for the web dashboard.

## Quick Start

### 1. Generate SSL Certificates

For development/testing, create self-signed certificates:

```bash
# Create certs directory
mkdir -p certs

# Generate self-signed certificate (valid for 365 days)
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem \
  -out certs/cert.pem \
  -days 365 \
  -subj "/CN=localhost"
```

For production, use certificates from a trusted Certificate Authority (Let's Encrypt, DigiCert, etc.).

### 2. Enable SSL in vars.py

Edit your `vars.py` file and add:

```python
# SSL/HTTPS Configuration
SSL_ENABLED = True
SSL_CERT_PATH = "certs/cert.pem"
SSL_KEY_PATH = "certs/key.pem"
```

Or if using the web configuration GUI, the SSL settings will be included automatically in generated `vars.py` files.

### 3. Start the Dashboard with SSL Support

**Option 1: Use Gevent Server (Recommended for SSL)**

```bash
python dashboard/server_gevent.py
```

Output:
```
🔒 SSL/HTTPS enabled
🚀 Dashboard (Gevent mode) starting on https://127.0.0.1:8765
```

**Option 2: Use Waitress with Reverse Proxy**

Waitress doesn't support SSL natively. For HTTPS with waitress:

```bash
# Start dashboard on HTTP
python dashboard/server.py

# Put nginx/Apache in front with SSL termination (see below)
```

### 4. Access Dashboard

Open your browser to:
```
https://localhost:8765
```

**Note:** For self-signed certificates, your browser will show a security warning. Click "Advanced" → "Proceed to localhost" to continue.

## Production Setup

### Option 1: Gevent with Let's Encrypt

1. **Obtain Let's Encrypt Certificate:**

```bash
# Install certbot
sudo apt-get install certbot  # Debian/Ubuntu
brew install certbot          # macOS

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com
```

2. **Configure vars.py:**

```python
SSL_ENABLED = True
SSL_CERT_PATH = "/etc/letsencrypt/live/yourdomain.com/fullchain.pem"
SSL_KEY_PATH = "/etc/letsencrypt/live/yourdomain.com/privkey.pem"
```

3. **Run with Gevent:**

```bash
python dashboard/server_gevent.py
```

### Option 2: Nginx Reverse Proxy (Recommended for Production)

This is the recommended approach for production deployments.

**1. Configure Nginx:**

```nginx
# /etc/nginx/sites-available/project-ape

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # SSL Configuration (Mozilla Modern)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to Dashboard
    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE Support
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
    }

    # Log Files
    access_log /var/log/nginx/project-ape-access.log;
    error_log /var/log/nginx/project-ape-error.log;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

**2. Enable and Restart Nginx:**

```bash
sudo ln -s /etc/nginx/sites-available/project-ape /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**3. Start Dashboard (HTTP only, nginx handles HTTPS):**

```bash
# Leave SSL_ENABLED = False in vars.py
python dashboard/server.py
```

## Container Deployment with SSL

### Podman/Docker with Gevent

```bash
podman run -d \
  --name project-ape \
  -p 8765:8765 \
  -v ./vars.py:/app/vars.py:ro,z \
  -v ./certs:/app/certs:ro,z \
  -v ./logs:/app/logs:rw,z \
  -e SSL_ENABLED=True \
  -e SSL_CERT_PATH=/app/certs/cert.pem \
  -e SSL_KEY_PATH=/app/certs/key.pem \
  quay.io/jasoande/project_ape/project-ape:latest \
  python3 dashboard/server_gevent.py
```

### Kubernetes with Ingress

```yaml
apiVersion: v1
kind: Service
metadata:
  name: project-ape
spec:
  selector:
    app: project-ape
  ports:
  - port: 8765
    targetPort: 8765
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: project-ape-ingress
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

## Troubleshooting

### Certificate Not Found

```
⚠️  SSL enabled but certificate files not found:
   Certificate: /path/to/cert.pem (not found)
```

**Solution:**
- Verify paths in vars.py are correct
- Use absolute paths or paths relative to project root
- Check file permissions (readable by dashboard user)

### Browser Security Warning

```
NET::ERR_CERT_AUTHORITY_INVALID
```

**Solution:**
- Self-signed certificates trigger this warning (normal for development)
- For production, use certificates from trusted CA (Let's Encrypt)
- Or add exception in browser for development

### Gevent Not Installed

```
ModuleNotFoundError: No module named 'gevent'
```

**Solution:**
```bash
pip install gevent>=24.0.0
```

### Permission Denied

```
PermissionError: [Errno 13] Permission denied: '/etc/letsencrypt/...'
```

**Solution:**
```bash
# Make certificates readable by dashboard user
sudo chmod 644 /etc/letsencrypt/live/yourdomain.com/fullchain.pem
sudo chmod 640 /etc/letsencrypt/live/yourdomain.com/privkey.pem
sudo chown root:apeuser /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

## Security Best Practices

### 1. Use Strong Certificates

- **Development:** Self-signed 4096-bit RSA
- **Production:** Let's Encrypt or commercial CA
- **Minimum:** TLS 1.2 (prefer TLS 1.3)

### 2. Protect Private Keys

```bash
# Restrict key permissions
chmod 600 certs/key.pem
chown apeuser:apeuser certs/key.pem

# Never commit to git
echo "certs/*.pem" >> .gitignore
```

### 3. Enable HSTS

Add to nginx or application headers:
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

### 4. Regular Rotation

- **Self-signed:** Regenerate annually
- **Let's Encrypt:** Auto-renews every 90 days
- **Commercial:** Follow CA renewal schedule

### 5. Monitor Expiration

```bash
# Check certificate expiration
openssl x509 -in certs/cert.pem -noout -enddate

# Set up renewal alerts
0 0 1 * * /usr/bin/certbot renew --quiet
```

## Configuration Reference

### vars.py SSL Options

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `SSL_ENABLED` | bool | `False` | Enable HTTPS |
| `SSL_CERT_PATH` | str | `""` | Path to SSL certificate |
| `SSL_KEY_PATH` | str | `""` | Path to SSL private key |

### Server Comparison

| Server | SSL Support | Performance | Use Case |
|--------|-------------|-------------|----------|
| **Gevent** | ✅ Native | Excellent (10k+ conn) | Production with SSL |
| **Waitress** | ❌ No | Good (200 conn) | Behind reverse proxy |
| **Flask Dev** | ❌ No | Poor (limited) | Development only |

### Recommended Setup

| Environment | Recommendation |
|-------------|----------------|
| **Development** | Self-signed cert + Gevent OR HTTP only |
| **Production (single server)** | Let's Encrypt + Nginx reverse proxy |
| **Production (Kubernetes)** | Ingress controller + cert-manager |
| **Production (containers)** | HAProxy/Traefik with SSL termination |

## Examples

### Development (Self-Signed)

```bash
# Generate cert
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout certs/key.pem -out certs/cert.pem \
  -days 365 -subj "/CN=localhost"

# Configure
cat >> vars.py << EOF
SSL_ENABLED = True
SSL_CERT_PATH = "certs/cert.pem"
SSL_KEY_PATH = "certs/key.pem"
EOF

# Run
python dashboard/server_gevent.py
```

### Production (Let's Encrypt + Nginx)

```bash
# Get certificate
sudo certbot certonly --nginx -d yourdomain.com

# Configure nginx (see above)
sudo nano /etc/nginx/sites-available/project-ape

# Start dashboard (HTTP, nginx handles HTTPS)
python dashboard/server.py
```

## Support

For SSL/HTTPS issues:
- Check logs: `tail -f logs/dashboard.log`
- Verify certificate: `openssl x509 -in certs/cert.pem -text -noout`
- Test SSL: `openssl s_client -connect localhost:8765 -showcerts`
- Nginx test: `sudo nginx -t`

See also:
- [CONTAINER_SECURITY_GUIDE.md](./CONTAINER_SECURITY_GUIDE.md)
- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- [SECURITY.md](./SECURITY.md)
