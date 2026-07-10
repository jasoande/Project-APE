# Changelog

All notable changes to Account Intelligence will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2026-07-10

### Breaking Changes

- **SSL/HTTPS is now mandatory** - HTTP mode has been removed for security
  - `SSL_ENABLED` configuration option removed (ignored if present in vars.py)
  - All HTTP URLs changed to HTTPS (`https://localhost:8765`)
  - `dashboard/server.py` (HTTP-only) deprecated in favor of `server_gevent.py`
  - Applications must use HTTPS - no HTTP fallback available

### Added

- **Automatic SSL certificate generation** on first launch (zero-configuration setup)
  - Self-signed certificates auto-generated using OpenSSL
  - 4096-bit RSA encryption, 365-day validity
  - Certificates stored in `certs/` directory (git-ignored)
  
- **Certificate auto-renewal** - regenerates if <30 days remaining
  - Prevents certificate expiration issues
  - Checks on every launcher startup
  - Handles expired/corrupted certificates automatically
  
- **New SSL Manager module** (`ssl_manager.py`)
  - `check_openssl_available()` - verifies OpenSSL installation
  - `check_certificate_validity()` - checks expiration dates
  - `generate_certificate()` - creates self-signed certificates
  - `ensure_certificates()` - main certificate lifecycle management
  - `check_legacy_ssl_config()` - backward compatibility warnings
  
- **Improved SSL error messages** with platform-specific installation instructions
  - Clear guidance when OpenSSL is missing
  - Installation commands for macOS, Linux, Windows
  
- **SSL migration guide** (`Docs/SSL_MIGRATION.md`)
  - Step-by-step migration instructions
  - Troubleshooting for common issues
  - Production deployment guidance

### Changed

- **Launcher always uses HTTPS** (`https://localhost:8765`)
  - Auto-generates certificates before starting server
  - Detects legacy `SSL_ENABLED=False` and shows deprecation warning
  - Always launches `server_gevent.py` (HTTPS-capable)
  
- **Configuration generator** removes `SSL_ENABLED` option
  - Generated `vars.py` files no longer include `SSL_ENABLED`
  - SSL certificate paths included by default
  
- **Main workflow orchestrator** always uses HTTPS protocol
  - `DASHBOARD_URL` always uses `https://` scheme
  - SSL context always created for self-signed certificate support
  - Always launches `server_gevent.py` instead of `server.py`
  
- **All dashboard URLs** changed from HTTP to HTTPS
  - `workflow_detector.py` returns HTTPS URLs
  - `dashboard/server.py` defaults to HTTPS URLs
  - API responses use HTTPS in all URL fields

### Fixed

- **Network binding issue** on Linux systems (VM, containers, WSL)
  - Added `DASHBOARD_HOST` configuration option
  - Defaults to `127.0.0.1` (localhost-only) for security
  - Set to `0.0.0.0` for network access
  - Documented in `Docs/NETWORK_TROUBLESHOOTING.md`
  
- **SSL configuration not respected** by main.py when launching workflows
  - main.py now correctly uses SSL configuration from vars.py
  - Browser opens with correct protocol (https://)
  
- **Launcher hardcoded to HTTP** even when SSL enabled
  - Launcher now auto-detects SSL and uses HTTPS
  - Opens browser to `https://localhost:8765`

### Security

- **All communication now encrypted** - HTTP mode removed
  - Dashboard traffic encrypted with TLS
  - Self-signed certificates for local development
  - Production-ready with Let's Encrypt or commercial CA
  
- **Private keys secured** with proper file permissions (600 on Unix)
  - Certificate files in git-ignored `certs/` directory
  - No credentials committed to repository

### Documentation

- **Added:**
  - `Docs/SSL_MIGRATION.md` - Migration guide for v3.0
  - `Docs/NETWORK_TROUBLESHOOTING.md` - Network binding issues
  - `ssl_manager.py` - Comprehensive docstrings and examples
  
- **Updated:**
  - `README.md` - Quick Start now mentions automatic SSL setup
  - `Docs/SSL_SETUP_LOCAL.md` - Documents that manual setup no longer required
  - `CLAUDE.md` - Updated launcher description with SSL auto-generation

### Migration Guide

**If you previously used SSL (`SSL_ENABLED=True`):**
- ✅ No action required - existing certificates will continue to work
- ✅ Auto-renewal will prevent expiration
- Optional: Remove `SSL_ENABLED` line from vars.py (it's ignored now)

**If you previously used HTTP (`SSL_ENABLED=False`):**
- ⚠️ SSL will be enabled automatically on next launch
- ⚠️ Certificates will be auto-generated
- ⚠️ Update bookmarks from `http://` to `https://`
- ⚠️ Browser will show security warning (normal for self-signed certs)

**If you had no SSL configuration:**
- ✅ Everything happens automatically
- ✅ Certificates generated on first launch
- ✅ No configuration edits required

See `Docs/SSL_MIGRATION.md` for detailed migration instructions.

### Known Issues

- Browser security warnings for self-signed certificates (expected behavior)
  - Click "Advanced" → "Proceed to localhost" to continue
  - This is normal and safe for local development
  
- OpenSSL required for certificate generation
  - Pre-installed on most systems
  - Installation instructions provided if missing

---

## [2.x.x] - Previous Versions

See git history for changes in version 2.x and earlier.
