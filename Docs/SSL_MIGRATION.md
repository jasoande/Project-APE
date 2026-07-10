# SSL Migration Guide - Version 3.0

## Overview

Starting with version 3.0, **SSL/HTTPS is always enabled** in Account Intelligence. HTTP mode has been removed for security.

## What Changed

### Breaking Changes

1. **SSL_ENABLED configuration removed**
   - The `SSL_ENABLED` flag in vars.py is no longer used
   - SSL is now always enabled (cannot be disabled)
   - If present in your vars.py, it will be ignored with a deprecation warning

2. **Automatic certificate generation**
   - SSL certificates are now auto-generated on first launch
   - No manual setup required (no need to run setup-ssl-local.py)
   - Certificates auto-renew when expiring (<30 days remaining)

3. **All URLs changed to HTTPS**
   - Dashboard: `https://localhost:8765` (was `http://`)
   - All API endpoints use HTTPS
   - All internal communication uses HTTPS

4. **server.py (HTTP-only) deprecated**
   - Application now uses only `server_gevent.py` (HTTPS-capable)
   - `server.py` is kept for backward compatibility but not used

## Migration Paths

### If You Currently Use SSL (SSL_ENABLED=True)

**✅ No action required!**

Your existing setup will continue to work:
- Existing certificates will be used
- Auto-renewal will prevent expiration
- No configuration changes needed

**Optional cleanup:**
- You can remove `SSL_ENABLED = True` from vars.py (it's ignored now)
- The SSL_CERT_PATH and SSL_KEY_PATH settings are still respected

### If You Currently Use HTTP (SSL_ENABLED=False)

**⚠️ Action required**

SSL will be enabled automatically on next launch:

1. **Certificates will auto-generate**
   - On first launch after upgrade, certificates are created automatically
   - No manual intervention needed

2. **Update bookmarks/scripts**
   - Change any `http://localhost:8765` bookmarks to `https://localhost:8765`
   - Update external scripts that reference the dashboard URL

3. **Browser security warnings**
   - You'll see a security warning for self-signed certificates
   - Click "Advanced" → "Proceed to localhost" (this is safe for local development)

**Your vars.py will show a warning:**
```
⚠️  WARNING: SSL_ENABLED=False detected in vars.py
   SSL is now always enabled for security (SSL_ENABLED is deprecated).
   Your configuration will be ignored - all communication uses HTTPS.
```

### If You Don't Have SSL Configured

**✅ Everything happens automatically!**

On first launch:
1. Certificates are generated automatically
2. Dashboard starts on HTTPS
3. Browser opens to `https://localhost:8765`

No configuration file edits required.

## Technical Details

### Certificate Management

**Auto-generation:**
- 4096-bit RSA self-signed certificates
- Valid for 365 days (1 year)
- Common Name: localhost
- Stored in `certs/` directory

**Auto-renewal:**
- Certificates checked on every launch
- Auto-renewed if <30 days remaining
- Auto-renewed if expired or corrupted

**File locations:**
- Certificate: `certs/cert.pem`
- Private key: `certs/key.pem`

### Configuration Changes

**Before (v2.x):**
```python
# vars.py
SSL_ENABLED = True  # Optional setting
SSL_CERT_PATH = "certs/cert.pem"
SSL_KEY_PATH = "certs/key.pem"
```

**After (v3.0):**
```python
# vars.py
# SSL_ENABLED removed (always enabled)
SSL_CERT_PATH = "certs/cert.pem"  # Optional (uses default if not specified)
SSL_KEY_PATH = "certs/key.pem"    # Optional (uses default if not specified)
```

### URL Changes

All HTTP URLs have been changed to HTTPS:

| Component | Old URL | New URL |
|-----------|---------|---------|
| Dashboard | `http://localhost:8765` | `https://localhost:8765` |
| Configuration | `http://localhost:8765/configure` | `https://localhost:8765/configure` |
| API endpoints | `http://localhost:8765/api/*` | `https://localhost:8765/api/*` |
| Health check | `http://localhost:8765/ping` | `https://localhost:8765/ping` |

## Troubleshooting

### "OpenSSL not found" error

**Symptom:**
```
❌ Error: OpenSSL not found
   OpenSSL is required for SSL certificate generation.
```

**Solution:**
- **macOS:** `brew install openssl`
- **Ubuntu:** `sudo apt-get install openssl`
- **Windows:** Install Git for Windows (includes OpenSSL)

### Browser shows security warning

**Symptom:**
```
Your connection is not private
NET::ERR_CERT_AUTHORITY_INVALID
```

**Solution:**
This is normal for self-signed certificates. Click:
- "Advanced" → "Proceed to localhost (unsafe)"

This is safe for local development. The warning appears because the certificate is self-signed rather than issued by a trusted Certificate Authority.

### "SSL certificate files not found" error

**Symptom:**
```
❌ Error: SSL certificate files not found
   Expected:
   - Certificate: /path/to/certs/cert.pem
   - Key: /path/to/certs/key.pem
```

**Solution:**
```bash
# Run the launcher (will auto-generate certificates)
python3 launch-project-ape.py

# Or manually generate
python3 ssl_manager.py test
```

### Cannot connect to dashboard

**Symptom:**
- Port shows as listening but browser can't connect
- "Connection refused" or "Unable to connect"

**Solution:**

Check if you're using the correct protocol:
```bash
# Wrong (won't work anymore)
http://localhost:8765

# Correct
https://localhost:8765
```

## Production Deployments

For production use with a real domain name, you should use proper SSL certificates:

### Option 1: Let's Encrypt (Free)

```bash
# Install certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Update vars.py
SSL_CERT_PATH = "/etc/letsencrypt/live/yourdomain.com/fullchain.pem"
SSL_KEY_PATH = "/etc/letsencrypt/live/yourdomain.com/privkey.pem"
```

### Option 2: Nginx Reverse Proxy (Recommended)

Use nginx to handle SSL termination:

```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass https://127.0.0.1:8765;
        proxy_ssl_verify off;  # Self-signed cert from dashboard
    }
}
```

See `Docs/SSL_SETUP_GUIDE.md` for detailed production deployment instructions.

## Rollback Instructions

If you need to temporarily revert to HTTP mode (not recommended):

**This is not supported in v3.0.** If you absolutely must use HTTP, you would need to:

1. Downgrade to v2.x
2. Set `SSL_ENABLED = False` in vars.py
3. Be aware this is insecure and will be removed in future versions

**We strongly recommend using HTTPS** for all deployments, even local development.

## FAQ

**Q: Why was HTTP mode removed?**
A: Security by default. SSL/HTTPS protects all dashboard communication, prevents credential exposure, and aligns with modern security best practices.

**Q: Can I use my own SSL certificates?**
A: Yes! Set `SSL_CERT_PATH` and `SSL_KEY_PATH` in vars.py to point to your certificate files.

**Q: Do I need to manually renew certificates?**
A: No. Self-signed certificates auto-renew. For Let's Encrypt, set up auto-renewal with certbot.

**Q: What if I delete the certs/ directory?**
A: No problem. Certificates will be auto-generated on next launch.

**Q: Can I disable the deprecation warning for SSL_ENABLED?**
A: Yes. Simply remove the `SSL_ENABLED` line from vars.py.

**Q: How do I increase the max Drive file size?**
A: Edit vars.py and set:
```python
DRIVE_CONFIG = {
    'max_file_size_mb': 500,  # Increase from default 50MB
}
```
Google Drive API supports up to 5GB per file.

## Support

For issues related to the SSL migration:

- **Documentation:** See `Docs/SSL_SETUP_LOCAL.md` for detailed SSL setup
- **Troubleshooting:** See `Docs/NETWORK_TROUBLESHOOTING.md` for connection issues
- **GitHub Issues:** https://github.com/jasoande/Project-APE/issues

## Summary

Version 3.0 makes SSL mandatory for improved security. Key points:

- ✅ Certificates auto-generate (zero manual setup)
- ✅ Certificates auto-renew (no expiration issues)
- ✅ SSL always enabled (no insecure HTTP mode)
- ✅ Backward compatible (existing SSL setups work unchanged)
- ⚠️ HTTP mode removed (deprecated SSL_ENABLED ignored)
- ⚠️ Update bookmarks to use `https://` URLs

Most users will experience a seamless upgrade with no action required.
