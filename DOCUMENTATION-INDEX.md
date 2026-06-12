# Project APE - Documentation Index

**All documentation in one place** - Find what you need fast!

---

## 🚀 Getting Started (Start Here!)

### For Account Teams (Container)

| Document | Purpose | Time |
|----------|---------|------|
| **[GETTING-STARTED.md](GETTING-STARTED.md)** | Choose deployment method | 2 min |
| **[QUICKSTART.md](QUICKSTART.md)** | Container setup guide | 5 min |
| **[README-CONTAINER.md](README-CONTAINER.md)** | Container deep dive | 15 min |

**Quick path:** GETTING-STARTED → QUICKSTART → Run!

### For Developers (Local Install)

| Document | Purpose | Time |
|----------|---------|------|
| **[GETTING-STARTED.md](GETTING-STARTED.md)** | Choose deployment method | 2 min |
| **[README.md](README.md)** | Full documentation | 30 min |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Technical details | 20 min |

**Quick path:** GETTING-STARTED → README → Install → Run!

---

## 📚 Core Documentation

### Main Guides

| File | Audience | Content |
|------|----------|---------|
| **[README.md](README.md)** | Everyone | Project overview, features, installation |
| **[GETTING-STARTED.md](GETTING-STARTED.md)** | New users | Decision tree, workflows |
| **[QUICKSTART.md](QUICKSTART.md)** | Account teams | 5-minute container setup |
| **[README-CONTAINER.md](README-CONTAINER.md)** | Container users | Container deployment guide |

---

## 🐳 Container Documentation

### Container Deployment

| File | Purpose | Audience |
|------|---------|----------|
| **[QUICKSTART.md](QUICKSTART.md)** | Fast setup | Account teams |
| **[README-CONTAINER.md](README-CONTAINER.md)** | Complete guide | All container users |
| **[GOOGLE_AUTH_GUIDE.md](GOOGLE_AUTH_GUIDE.md)** | NotebookLM authentication | All users |
| **[BUILD_VERIFICATION_RESULTS.md](BUILD_VERIFICATION_RESULTS.md)** | Build validation | DevOps, admins |

### Container Build Docs

| File | Purpose | Audience |
|------|---------|----------|
| **[Containerfile](Containerfile)** | RHEL variant | DevOps |
| **[Containerfile.debian](Containerfile.debian)** | Debian variant | DevOps |
| **[build-container.sh](build-container.sh)** | Build automation | DevOps |
| **[registry-push.sh](registry-push.sh)** | Registry distribution | DevOps |
| **[test-container-deps.sh](test-container-deps.sh)** | Dependency testing | QA |
| **[test-google-auth.sh](test-google-auth.sh)** | Auth testing | QA |

### Container Technical Notes

| File | Purpose | Audience |
|------|---------|----------|
| **[ARM64_LIBREOFFICE_NOTES.md](ARM64_LIBREOFFICE_NOTES.md)** | LibreOffice on ARM64 | Developers |
| **[PYTHON_314_NOTES.md](PYTHON_314_NOTES.md)** | Python 3.14 in RHEL | Developers |

---

## 🔧 Configuration

### Configuration Files

| File | Purpose | When to Use |
|------|---------|-------------|
| **vars.py** | Client configuration | Local installation |
| **container-vars.py** | Container configuration | Container deployment |
| **example-vars.py** | Configuration template | Reference |

### Configuration Guides

See **Configuration** section in:
- [README.md](README.md) - Local config
- [README-CONTAINER.md](README-CONTAINER.md) - Container config
- [QUICKSTART.md](QUICKSTART.md) - Quick examples

---

## 🏗️ Technical Documentation

### Architecture & Design

| File | Purpose | Audience |
|------|---------|----------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System design | Developers |
| **[BUILD_VERIFICATION_RESULTS.md](BUILD_VERIFICATION_RESULTS.md)** | Build details | DevOps |
| Code files (`core/*.py`) | Implementation | Developers |

### Authentication

| File | Purpose | Audience |
|------|---------|----------|
| **[GOOGLE_AUTH_GUIDE.md](GOOGLE_AUTH_GUIDE.md)** | Complete auth guide | All users |

---

## 🔍 Quick References

### By Use Case

#### "I just want to run Project APE"
→ [GETTING-STARTED.md](GETTING-STARTED.md) → [QUICKSTART.md](QUICKSTART.md)

#### "I need to customize the code"
→ [GETTING-STARTED.md](GETTING-STARTED.md) → [README.md](README.md)

#### "How does Google auth work?"
→ [GOOGLE_AUTH_GUIDE.md](GOOGLE_AUTH_GUIDE.md)

#### "I want to build my own container"
→ [README-CONTAINER.md](README-CONTAINER.md) → [build-container.sh](build-container.sh)

#### "How do I configure clients?"
→ [container-vars.py](container-vars.py) (container) or [vars.py](vars.py) (local)

#### "Something's not working"
→ Troubleshooting in [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md)

#### "I want to understand the architecture"
→ [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 📖 By Document Type

### Getting Started Docs

- [GETTING-STARTED.md](GETTING-STARTED.md) - Start here!
- [QUICKSTART.md](QUICKSTART.md) - 5-minute container setup
- [README.md](README.md) - Full project documentation

### Deployment Docs

- [README-CONTAINER.md](README-CONTAINER.md) - Container deployment
- [GOOGLE_AUTH_GUIDE.md](GOOGLE_AUTH_GUIDE.md) - Authentication setup

### Technical Docs

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [BUILD_VERIFICATION_RESULTS.md](BUILD_VERIFICATION_RESULTS.md) - Build validation
- [ARM64_LIBREOFFICE_NOTES.md](ARM64_LIBREOFFICE_NOTES.md) - Platform notes
- [PYTHON_314_NOTES.md](PYTHON_314_NOTES.md) - Python version notes

### Scripts & Tools

- [ape-run.sh](ape-run.sh) - Container runner
- [build-container.sh](build-container.sh) - Build automation
- [registry-push.sh](registry-push.sh) - Registry push
- [test-container-deps.sh](test-container-deps.sh) - Dependency testing
- [test-google-auth.sh](test-google-auth.sh) - Auth testing
- [test-fixes.py](test-fixes.py) - Code validation
- [check_dependencies.py](check_dependencies.py) - Dependency checker

---

## 🎯 By Audience

### Account Teams

**Start:** [GETTING-STARTED.md](GETTING-STARTED.md)

**Must Read:**
1. [QUICKSTART.md](QUICKSTART.md)
2. [GOOGLE_AUTH_GUIDE.md](GOOGLE_AUTH_GUIDE.md)
3. [container-vars.py](container-vars.py) - Example config

**Optional:**
- [README-CONTAINER.md](README-CONTAINER.md) - Deep dive

---

### Developers

**Start:** [GETTING-STARTED.md](GETTING-STARTED.md)

**Must Read:**
1. [README.md](README.md)
2. [ARCHITECTURE.md](ARCHITECTURE.md)
3. [vars.py](vars.py) or [example-vars.py](example-vars.py)

**Optional:**
- [GOOGLE_AUTH_GUIDE.md](GOOGLE_AUTH_GUIDE.md) - Auth details
- Code files in `core/` - Implementation

---

### DevOps / Platform Teams

**Start:** [README-CONTAINER.md](README-CONTAINER.md)

**Must Read:**
1. [Containerfile](Containerfile) or [Containerfile.debian](Containerfile.debian)
2. [build-container.sh](build-container.sh)
3. [registry-push.sh](registry-push.sh)
4. [BUILD_VERIFICATION_RESULTS.md](BUILD_VERIFICATION_RESULTS.md)

**Optional:**
- [ARM64_LIBREOFFICE_NOTES.md](ARM64_LIBREOFFICE_NOTES.md) - Platform notes
- [PYTHON_314_NOTES.md](PYTHON_314_NOTES.md) - Version notes
- [test-container-deps.sh](test-container-deps.sh) - Testing
- [test-google-auth.sh](test-google-auth.sh) - Auth testing

---

### Solutions Architects

**Start:** [GETTING-STARTED.md](GETTING-STARTED.md)

**Must Read:**
1. [QUICKSTART.md](QUICKSTART.md) - Fast setup
2. [README.md](README.md) - Features overview
3. [container-vars.py](container-vars.py) - Configuration

**Optional:**
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical design
- [README-CONTAINER.md](README-CONTAINER.md) - Deployment options

---

## 🆘 Troubleshooting Guides

### Container Issues

**Document:** [QUICKSTART.md](QUICKSTART.md) - Troubleshooting section

**Common Issues:**
- Podman not installed → Installation steps
- Image pull failed → Registry access
- Volume mount errors → Path resolution
- NotebookLM auth → Re-login

---

### Local Installation Issues

**Document:** [README.md](README.md) - Troubleshooting section

**Common Issues:**
- LibreOffice not found → Installation
- Python package errors → Requirements
- NotebookLM auth → Login guide

---

### Authentication Issues

**Document:** [GOOGLE_AUTH_GUIDE.md](GOOGLE_AUTH_GUIDE.md)

**Covers:**
- Initial login
- Token expiration
- Container credential mounting
- Service accounts (enterprise)

---

## 📝 Configuration Examples

### Container Configuration

**File:** [container-vars.py](container-vars.py)

**Example:**
```python
clients = ["acme_corp"]

acme_corp_name = "ACME Corporation"
acme_corp_industry = "technology"
acme_corp_folder = "/app/client_data/ACME"
```

**Note:** Company branding is in prompt templates (`*.txt`).

### Local Configuration

**File:** [vars.py](vars.py) or [example-vars.py](example-vars.py)

**Example:**
```python
clients = ["acme_corp"]

acme_corp_name = "ACME Corporation"
acme_corp_industry = "technology"
acme_corp_folder = str(Path(__file__).parent / "client_data" / "ACME")
```

**Note:** Company branding is in prompt templates (`*.txt`).

---

## 🔄 Update Guides

### Container Updates

**Document:** [README-CONTAINER.md](README-CONTAINER.md) - Updates section

```bash
podman pull quay.io/jasoande/project_ape/project-ape:latest
```

### Local Installation Updates

**Document:** [README.md](README.md)

```bash
git pull
pip install -r requirements.txt --upgrade
```

---

## 🎓 Learning Path

### Beginner (Just Run It)

1. [GETTING-STARTED.md](GETTING-STARTED.md) - Decide container vs local
2. [QUICKSTART.md](QUICKSTART.md) - Setup and run (container)
3. [container-vars.py](container-vars.py) - Example config
4. **Run your first pipeline!**

**Time:** 30 minutes

---

### Intermediate (Customize)

1. **Beginner path** (above)
2. [README.md](README.md) - Full features
3. [GOOGLE_AUTH_GUIDE.md](GOOGLE_AUTH_GUIDE.md) - Auth details
4. Edit prompts and configs
5. **Run multiple clients**

**Time:** 2 hours

---

### Advanced (Development)

1. **Intermediate path** (above)
2. [ARCHITECTURE.md](ARCHITECTURE.md) - System design
3. Code exploration (`core/*.py`)
4. [BUILD_VERIFICATION_RESULTS.md](BUILD_VERIFICATION_RESULTS.md) - Build details
5. **Modify and extend**

**Time:** 1 day

---

### Expert (Platform)

1. **Advanced path** (above)
2. [README-CONTAINER.md](README-CONTAINER.md) - Container deep dive
3. [Containerfile](Containerfile) - Build files
4. [build-container.sh](build-container.sh) - Build automation
5. [registry-push.sh](registry-push.sh) - Distribution
6. **Build and distribute**

**Time:** 2 days

---

## 📞 Getting Help

### Self-Service

1. Check this index for relevant docs
2. Read troubleshooting sections
3. Review examples in config files
4. Check logs in `logs/` directory

### Community

- **GitHub Issues** - Bug reports, feature requests
- **Documentation** - You're reading it!
- **Examples** - See `container-vars.py`, `example-vars.py`

---

## 📊 Document Summary

### Total Documents: 20+

**Getting Started:** 3 docs  
**Container Deployment:** 7 docs  
**Configuration:** 3 files  
**Scripts & Tools:** 7+ scripts  
**Technical:** 4 docs  

---

## 🔖 Quick Links

### Essential Reading

1. **[GETTING-STARTED.md](GETTING-STARTED.md)** ← Start here
2. **[QUICKSTART.md](QUICKSTART.md)** ← Container users
3. **[README.md](README.md)** ← Full docs

### Key Resources

- **Registry:** `quay.io/jasoande/project_ape/project-ape:latest`
- **GitHub:** https://github.com/jasoande/Project-APE
- **Dashboard:** http://localhost:8765

---

## ✅ Documentation Checklist

### Before First Run

- [ ] Read [GETTING-STARTED.md](GETTING-STARTED.md)
- [ ] Choose deployment (container or local)
- [ ] Follow [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md)
- [ ] Configure `vars.py` or `container-vars.py`
- [ ] Read [GOOGLE_AUTH_GUIDE.md](GOOGLE_AUTH_GUIDE.md)
- [ ] Test with one client first

### Before Production Use

- [ ] Review [README-CONTAINER.md](README-CONTAINER.md) (container)
- [ ] Read [ARCHITECTURE.md](ARCHITECTURE.md) (local dev)
- [ ] Understand execution modes (fast vs deep)
- [ ] Test with multiple clients
- [ ] Review quality scores and output

### For Development

- [ ] Clone repository
- [ ] Read [README.md](README.md) - Full installation
- [ ] Read [ARCHITECTURE.md](ARCHITECTURE.md)
- [ ] Explore code in `core/`
- [ ] Review build scripts

---

**Need help?** Start with [GETTING-STARTED.md](GETTING-STARTED.md) and follow the links! 🚀
