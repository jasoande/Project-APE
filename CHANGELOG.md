# Changelog

All notable changes to Project APE will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-06-10

### Added
- **Deep Mode**: Comprehensive research mode with 100+ sources per client
- **Incremental Deduplication**: Deep mode deduplicates after each research prompt
- **Dual-Mode Execution**: Fast (<16 min) and Deep (30-90 min) modes
- **Dashboard Mode Detection**: Dynamic mode display (Fast/Deep)
- **Timer Persistence**: Dashboard timer survives page refreshes
- **Quality Scoring**: 0-10 scale based on sources, notes, completeness
- **Descriptive Note Titles**: Professional naming for all 12 sections
- **Smart Rerun**: Reuse existing PDFs, refresh research data
- **Variable Substitution**: $name and $industry in prompts
- **Status File Cleanup**: Removes stale status files before runs
- **Fresh Authentication**: Force check at start of every run
- **Comprehensive Retry Logic**: 5 attempts with exponential backoff
- **None Value Handling**: Graceful handling of null URLs (PDFs)
- **JSON Parsing Flexibility**: Handles both dict and list formats
- **Process-based PDF Conversion**: Parallel processing for speed

### Changed
- **Timing Configuration**: Separate TIMINGS and DEEP_TIMINGS
- **Dashboard Title**: Dynamic based on mode (was hardcoded)
- **PDF Consolidation**: Single `{Client}-One.pdf` format
- **Source Manager**: Enhanced retry logic for deep research
- **Notebook Naming**: Format `DEV_{folder_name}-TEST`
- **Version**: Bumped to 2.0.0 (production ready)

### Fixed
- **Deep Research API**: Uses correct `--mode deep` flag
- **Deduplication**: JSON parsing handles `{"sources": [...]}` format
- **Dashboard Timer**: Age-based resume logic (<120s)
- **Stale Clients**: Status file cleanup prevents old data
- **NoneType Errors**: Handles `url: null` for uploaded PDFs
- **RPC Errors**: Retry logic for codes 3, 9
- **Source Import**: Waits for async imports to complete

### Security
- **No Hardcoded Credentials**: All authentication via `notebooklm login`
- **Path Validation**: Client folders validated before access
- **Process Isolation**: Multi-process architecture prevents crosstalk

## [1.0.0] - 2026-06-01

### Added
- Initial multi-process architecture
- Flask dashboard with real-time updates
- PDF consolidation (all file types)
- NotebookLM integration
- Research prompts (2x ask prompts)
- Chat prompts (12x descriptive notes)
- Mind map generation
- Fast mode execution
- Red Hat themed dashboard
- Comprehensive logging
- Configuration via vars.py
- Multi-client parallel execution

### Documentation
- README.md with installation guide
- ARCHITECTURE.md for technical details
- PROJECT_PLAN.md for project management
- EXECUTIVE_SUMMARY.md for business case
- PRESENTATION_5_SLIDES.md for stakeholders

## [3.0.3] - 2026-06-12

### Critical Fixes - Session Refresh & Deep Mode Quota Management

**Problem 1:** Version 3.0.2 attempted to fix token expiration by calling `notebooklm refresh`, but this command does not exist in the notebooklm-py CLI, causing warnings throughout workflows.

**Root Cause:** The original token expiration issue was caused by container credential isolation, not token lifetime. Persistent volume solution (implemented in 3.0.2) already solved the authentication problem.

**Solution:** 
- Removed all calls to non-existent `notebooklm refresh` command
- Persistent volume credentials maintain session state correctly
- No refresh needed - tokens last full workflow duration when properly authenticated

**Problem 2:** Deep mode workflows hitting "Quota exceeded" errors from NotebookLM API.

**Root Cause:** Deep mode makes intensive API calls (100+ sources + 14 prompts per client). NotebookLM has quota limits that weren't being handled.

**Solution:**
- Added "quota" detection to retryable error patterns
- Added RPC_CODE=8 (RESOURCE_EXHAUSTED) to retry logic
- Increased deep mode delays: research 90-120s (was 45-60s), chat 120-180s (was 60-90s)
- Increased retry attempts: 7 for research (was 5), 5 for chat (was 3)
- Increased base retry delays: 30s for research (was 15s), 10s for chat (was 5s)
- Exponential backoff handles quota recovery time

### Changed
- **core/source_manager.py**: Removed `_refresh_session()` method, added quota error detection
- **core/client_pipeline.py**: Removed session refresh call, added quota error detection
- **vars.py**: Increased DEEP_TIMINGS delays by 2-3x for quota management
- **vars.py**: Increased RETRY_CONFIG attempts and base delays for quota recovery

### Fixed
- ✅ **Session refresh warnings** - Removed broken refresh calls
- ✅ **Authentication persistence** - Persistent volume maintains valid session
- ✅ **Clean workflow logs** - No more "No such command 'refresh'" warnings
- ✅ **Deep mode quota errors** - Handles RESOURCE_EXHAUSTED with retry and longer delays
- ✅ **Quota detection** - Detects "quota" and RPC_CODE=8 as retryable errors

---

## [3.0.2] - 2026-06-12

### Persistent Volume Credential Solution

**Problem:** Container credential isolation prevented NotebookLM authentication from working reliably.

**Solution:** Implemented persistent volume-based credential storage:
- Created `setup-credentials.sh` for one-time credential setup
- Credentials stored in `project-ape-credentials` named volume
- Volume automatically mounted by `ape-run.sh`
- Credentials persist across container runs

### Added
- **setup-credentials.sh**: One-time credential setup script
- **Persistent volume support**: Named volume for credential storage
- **Automatic credential detection**: ape-run.sh checks for volume, prompts setup if needed

### Changed
- **ape-run.sh**: Switched from host mount to persistent volume for credentials
- **ape-run.sh**: Fixed container ID capture issue (now captures from podman run output)
- **container-entrypoint.sh**: Detects persistent volume vs legacy host mount
- **core/auth_manager.py**: Reduced check_interval from 300s to 60s for faster auth checks

### Fixed
- ✅ **Container authentication** - Persistent volume maintains valid session
- ✅ **Permission issues** - No more host directory permission conflicts
- ✅ **Container ID capture** - ape-run.sh now correctly follows container logs

---

## [3.0.1] - 2026-06-12

### Major Changes - Containerized Edition
- **Complete containerization** using Podman/Docker
- **Switched from Node.js NotebookLM CLI to Python notebooklm-py 0.7.1**
- **Image optimization:** 1.17 GB → 808 MB (31% reduction)
- **Registry distribution:** Available at quay.io/jasoande/project_ape/project-ape:latest

### Added
- **Container Support**: Full Podman/Docker containerization
- **Python NotebookLM SDK**: notebooklm-py 0.7.1 replaces Node.js CLI
- **Container Entrypoint**: Automatic credential copying and environment setup
- **SELinux Compatibility**: Full support for RHEL/Fedora/CentOS with :z volume labels
- **ape-run.sh**: Simple container runner script with pre-flight checks
- **Cross-platform Support**: macOS, Linux, and Windows WSL2
- **Dashboard Accessibility**: Bind to 0.0.0.0 for container access
- **Read-only Mounts**: Config and client data mounted read-only for security
- **Non-root Execution**: Container runs as unprivileged user (apeuser, UID 1000)
- **Credential Isolation**: NotebookLM credentials copied, not shared
- **Automated Testing**: test-container-structure.sh validation script

### Changed
- **Base Image**: python:3.13-slim (Debian-based)
- **Authentication**: Python SDK OAuth instead of Playwright browser automation
- **Path Resolution**: Container-aware paths with fallback to host paths
- **Dashboard Server**: Loads config dynamically, binds to all interfaces
- **Volume Mounts**: All volumes use SELinux labels (:z flag)
- **Configuration**: Separate vars-container.py template for containers
- **Dependencies**: Removed Node.js, Playwright, unused Python packages

### Removed - Optimization
- **Node.js and npm**: No longer needed (saved ~200 MB)
- **Playwright browsers**: Chromium not required (saved ~1.3 GB)
- **pandas**: Not used (saved 74 MB)
- **numpy**: Only pandas dependency (saved 67 MB)
- **python-docx**: Not used (saved 2.7 MB)
- **openpyxl**: Not used (saved 2.8 MB)
- **PyPDF2**: Duplicate, using pypdf instead (saved 2.4 MB)

### Fixed - 9 Critical Containerization Issues
1. **vars.py directory creation**: Removed mkdir() calls (read-only mount issue)
2. **main.py path resolution**: Added config-driven paths with fallback
3. **Dashboard path resolution**: Dynamic config loading for container paths
4. **SELinux volume labels**: Added :z flag to all volume mounts
5. **Logs directory permissions**: Universal chmod 777 for UID 1000 access
6. **Dashboard bind address**: Changed localhost → 0.0.0.0 for external access
7. **Platform-specific chmod**: Removed OS conditionals, runs on all platforms
8. **NotebookLM auth check**: Uses working 'list' command instead of 'status'
9. **Python SDK integration**: Switched from Node.js CLI to Python SDK

### Security
- **Non-root container**: Runs as apeuser (UID 1000), not root
- **Read-only config**: vars.py and client_data mounted read-only
- **Credential copying**: Credentials copied to container, not shared
- **No persistence**: Container ephemeral, dies after execution
- **SELinux support**: Full compatibility with mandatory access control
- **Network isolation**: Only dashboard port (8765) exposed

### Performance
- **Image size**: 808 MB (down from 1.17 GB)
- **Build time**: ~4 minutes
- **Startup time**: <5 seconds
- **Memory per client**: ~200 MB (fast), ~300 MB (deep)
- **Parallel clients**: Up to 5 (fast), 3 (deep)

### Documentation
- **README.md**: Complete rewrite with King Kong branding
- **QUICKSTART.md**: 5-minute quick start guide
- **CONTAINER_GUIDE.md**: Container operations guide
- **CHANGELOG.md**: This file - version history
- **Professional Branding**: King Kong logo on all documentation
- **Project Owner**: Jason Anderson listed as maintainer

### Infrastructure
- **Registry**: quay.io/jasoande/project_ape/project-ape
- **Tags**: 3.0.1 (stable), latest (current)
- **Platforms**: linux/arm64, linux/amd64
- **Distribution**: Pull once, run anywhere

---

## [Unreleased]

### Planned for v3.1
- Multi-language support
- Enhanced mind map customization
- Slack integration for notifications
- Batch export to PowerPoint
- CRM integration (Salesforce)

### Planned for v3.2
- Custom prompt templates
- Advanced analytics dashboard
- Historical trend analysis
- Web-based configuration UI
- API endpoints for integrations

---

## Version History Summary

- **3.0.1** (2026-06-12): Containerized edition with Python SDK
- **2.0.0** (2026-06-10): Production release with deep mode
- **1.0.0** (2026-06-01): Initial release

---

**Legend:**
- `Added`: New features
- `Changed`: Changes to existing functionality
- `Deprecated`: Soon-to-be removed features
- `Removed`: Removed features
- `Fixed`: Bug fixes
- `Security`: Security improvements
