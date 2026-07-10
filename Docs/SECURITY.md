# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 4.1.x   | ✅ Yes             |
| 4.0.x   | ✅ Yes             |
| < 4.0   | ❌ No              |

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

### How to Report

Send vulnerability reports to: **jason.anderson@redhat.com**

**Include:**
1. **Description** — What is the vulnerability?
2. **Impact** — What can an attacker do?
3. **Steps to Reproduce** — Detailed reproduction steps
4. **Affected Versions** — Which versions are vulnerable?
5. **Suggested Fix** (optional) — Proposed mitigation

**Response Timeline:**
- **24 hours:** Acknowledgment of your report
- **7 days:** Initial assessment and severity classification
- **30 days:** Fix developed, tested, and released (for critical issues)
- **90 days:** Full public disclosure (after fix is released)

### Security Researcher Recognition

We maintain a **Hall of Fame** for security researchers who responsibly disclose vulnerabilities:

- Your name will be added to SECURITY_CREDITS.md
- We'll provide attribution in release notes
- Swag/bounties may be available for critical findings (on a case-by-case basis)

## Security Best Practices

### For Users

**Authentication:**
- ✅ Use OAuth2 flows (never embed API keys in code)
- ✅ Rotate credentials every 90 days
- ✅ Use separate Google accounts for dev/staging/production
- ❌ Never commit `credentials.json` or `token_drive.json` to git

**Network:**
- ✅ Run dashboard on `127.0.0.1` (localhost only) by default
- ✅ Use reverse proxy (nginx/Caddy) for external access
- ✅ Enable HTTPS in production (Let's Encrypt)
- ❌ Never expose port 8765 directly to the internet

**File Permissions:**
- ✅ Set `chmod 600` on all credential files
- ✅ Run containers as non-root user (UID 1000)
- ✅ Use `:z` SELinux labels on volume mounts (RHEL/Fedora)

**Configuration:**
- ✅ Use environment variables for secrets (not vars.py)
- ✅ Enable CSRF protection (default in 4.1+)
- ✅ Validate all user input (Drive URLs, client IDs)

### For Developers

**Code Review:**
- All PRs require security review before merge
- Use GitHub security scanning (Dependabot, CodeQL)
- Run `pytest tests/test_server_security.py` before every release

**Dependencies:**
- Update dependencies monthly: `pip list --outdated`
- Never install from untrusted sources
- Pin versions in `requirements.txt` (no `>=` wildcards)

**Input Validation:**
- Use `_validate_client_token()` for all user-provided tokens
- Use `is_relative_to()` for all file path operations
- Never use `shell=True` in `subprocess` calls
- Sanitize error messages with `_safe_error()`

## Known Security Considerations

### 1. SSE Thread Exhaustion (CVE-TBD)

**Fixed in:** 4.1.1  
**Impact:** Denial of service via rapid SSE connection attempts  
**Mitigation:** Rate limiting (10 connections/IP) + increased thread pool (200)

### 2. CSRF on Configuration Endpoints (CVE-TBD)

**Fixed in:** 4.0.2  
**Impact:** Cross-site request forgery on `/api/add-client`, `/api/start-workflow`  
**Mitigation:** `flask-wtf` CSRF protection on all POST endpoints

### 3. Path Traversal in Log Streaming (CVE-TBD)

**Fixed in:** 4.0.1  
**Impact:** Arbitrary file read via `/logs/<client_token>` with `../../` sequences  
**Mitigation:** Regex validation + `is_relative_to()` check

## Security Features

### Built-In Protections

**Application Layer:**
- ✅ CSRF protection via flask-wtf
- ✅ Path traversal prevention (regex + path validation)
- ✅ Error message sanitization (no stack traces to users)
- ✅ Rate limiting on SSE endpoints (10/IP)
- ✅ Input validation on all user-provided data

**Container Layer:**
- ✅ Non-root user (UID 1000, username: apeuser)
- ✅ Read-only root filesystem (where possible)
- ✅ No setuid/setgid binaries
- ✅ SELinux labels for volume mounts

**Network Layer:**
- ✅ Localhost-only binding by default
- ✅ No external services called without user consent
- ✅ OAuth2 for all authentication (no API keys)

### Security Audits

**Last audit:** 2026-07-01  
**Next scheduled:** 2026-10-01  
**Auditor:** Internal Red Hat Security Team

**Audit Scope:**
- Static analysis (Bandit, pylint --security)
- Dynamic analysis (OWASP ZAP)
- Dependency scanning (Safety, Dependabot)
- Manual code review (OWASP Top 10)

## Compliance

**Frameworks:**
- OWASP Top 10 (Web Application Security)
- CWE Top 25 (Common Weakness Enumeration)
- NIST Cybersecurity Framework

**Certifications:**
- None (open-source project, no formal certification)

## Security Contacts

- **Primary:** jason.anderson@redhat.com
- **GPG Key:** [Coming Soon]
- **GitHub Security Advisory:** https://github.com/jasoande/Project-APE/security/advisories

---

**Last Updated:** 2026-07-09  
**Version:** 1.0.0
