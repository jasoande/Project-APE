<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="150"/>
</div>

# Project APE - Complete Documentation Index

**Central hub for all Project APE documentation**

Version: 3.2.2  
Last Updated: June 30, 2026  
Status: ✅ Complete and Tested

---

## Quick Navigation

| I Want To... | Read This |
|--------------|-----------|
| **Get started quickly** | [QUICK_START.md](QUICK_START.md) |
| **Understand the system** | [README.md](README.md) |
| **Fix problems** | [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) |
| **Setup OAuth authentication** | [Docs/OAUTH_QUICK_START.md](Docs/OAUTH_QUICK_START.md) |
| **Complete OAuth guide** | [Docs/OAUTH_COMPLETE_GUIDE.md](Docs/OAUTH_COMPLETE_GUIDE.md) |
| **Configure environment** | [Docs/ENVIRONMENT_SETUP.md](Docs/ENVIRONMENT_SETUP.md) |
| **Use the API** | [API_REFERENCE.md](API_REFERENCE.md) |
| **Understand architecture** | [CLAUDE.md](CLAUDE.md) |

---

## Documentation Structure

### User Documentation

**Essential guides for getting started and daily use:**

1. **[README.md](README.md)** - Project overview and introduction
   - What is Project APE?
   - Key features and capabilities
   - High-level architecture
   - Quick start summary

2. **[QUICK_START.md](QUICK_START.md)** - Step-by-step getting started guide
   - Environment setup (2-5 minutes)
   - First workflow execution
   - Expected results and validation
   - Common next steps

3. **[Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md)** - Problem resolution guide
   - Authentication issues
   - Dashboard connectivity problems
   - Workflow failures
   - Quality score issues
   - Platform-specific problems
   - Error message reference

### Setup Guides

**Detailed setup and configuration documentation:**

1. **[Docs/OAUTH_QUICK_START.md](Docs/OAUTH_QUICK_START.md)** - Fast OAuth setup
   - Quick OAuth configuration (5 minutes)
   - Essential steps only
   - Troubleshooting quick fixes

2. **[Docs/OAUTH_COMPLETE_GUIDE.md](Docs/OAUTH_COMPLETE_GUIDE.md)** - Complete OAuth guide
   - GCP project setup
   - OAuth consent screen configuration
   - Credential creation and download
   - Multi-user setup
   - Advanced troubleshooting

3. **[Docs/ENVIRONMENT_SETUP.md](Docs/ENVIRONMENT_SETUP.md)** - Environment configuration
   - Python environment setup
   - Dependency installation
   - NotebookLM authentication
   - Platform-specific configuration
   - Verification steps

4. **[Docs/WEB_CONFIGURATION_GUIDE.md](Docs/WEB_CONFIGURATION_GUIDE.md)** - Web interface guide
   - Configuration page usage
   - Client management
   - Settings customization
   - OAuth setup via web UI

### Reference Documentation

**Technical reference and architecture:**

1. **[CLAUDE.md](CLAUDE.md)** - Codebase reference for AI assistants
   - Project architecture overview
   - Core components and responsibilities
   - Development commands
   - File naming conventions
   - Configuration system details

2. **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation
   - vars.py configuration reference
   - Dashboard API endpoints
   - Command-line interface
   - Environment variables
   - Status file format
   - Log format

3. **[Architecture Documentation](README.md#architecture)**
   - System components
   - Data flow
   - Integration points
   - Technology stack

### Platform-Specific Guides

**Operating system specific documentation:**

1. **[MACOS_COMPLETE_GUIDE.md](MACOS_COMPLETE_GUIDE.md)** - macOS complete guide
   - macOS prerequisites and installation
   - Launcher options (double-click vs terminal)
   - Gatekeeper and security permissions
   - macOS-specific troubleshooting

2. **[LINUX_QUICK_START.md](LINUX_QUICK_START.md)** - Linux installation guide
   - Ubuntu/Debian setup
   - Desktop launcher installation
   - systemd service configuration

3. **[CROSS_PLATFORM_LAUNCHER.md](CROSS_PLATFORM_LAUNCHER.md)** - Launcher comparison
   - Windows, Linux, macOS launchers
   - Platform-specific considerations

---

## Developer Documentation

**Technical documentation for contributors (see developer-docs/ directory):**

Developer-specific documentation is maintained separately in the `developer-docs/` directory and is not indexed here. See [developer-docs/README.md](developer-docs/README.md) for the developer documentation index.

Key developer resources:
- [developer-docs/INSTALLATION.md](developer-docs/INSTALLATION.md) - Manual installation
- [developer-docs/requirements.txt](developer-docs/requirements.txt) - Python dependencies
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [TESTING_RESULTS.md](TESTING_RESULTS.md) - Test results and validation

---

## Documentation by Topic

### Getting Started

- **First Time Setup**:
  - [README.md](README.md) - Start here for overview
  - [QUICK_START.md](QUICK_START.md) - Step-by-step guide
  - [Docs/ENVIRONMENT_SETUP.md](Docs/ENVIRONMENT_SETUP.md) - Environment configuration

### Authentication & OAuth

- **Quick Setup**:
  - [Docs/OAUTH_QUICK_START.md](Docs/OAUTH_QUICK_START.md) - Fast OAuth setup (5 minutes)

- **Complete Setup**:
  - [Docs/OAUTH_COMPLETE_GUIDE.md](Docs/OAUTH_COMPLETE_GUIDE.md) - Comprehensive OAuth guide
  - [setup-oauth-drive.py](setup-oauth-drive.py) - OAuth setup wizard script

### Platform-Specific Installation

- **macOS**:
  - [MACOS_COMPLETE_GUIDE.md](MACOS_COMPLETE_GUIDE.md) - Complete macOS guide
  - [launch-project-ape.command](launch-project-ape.command) - Double-click launcher

- **Linux**:
  - [LINUX_QUICK_START.md](LINUX_QUICK_START.md) - Linux installation
  - [install-linux-launcher.sh](install-linux-launcher.sh) - Desktop integration

- **Cross-Platform**:
  - [CROSS_PLATFORM_LAUNCHER.md](CROSS_PLATFORM_LAUNCHER.md) - Launcher comparison
  - [launch-project-ape.sh](launch-project-ape.sh) - Shell launcher
  - [launch-project-ape.py](launch-project-ape.py) - Python launcher

### Configuration & Usage

- **Web Configuration**:
  - [Docs/WEB_CONFIGURATION_GUIDE.md](Docs/WEB_CONFIGURATION_GUIDE.md) - Web UI guide
  - [README.md § Web Configuration](README.md#web-configuration)

- **Manual Configuration**:
  - [API_REFERENCE.md](API_REFERENCE.md) - Complete configuration reference
  - [example-vars.py](example-vars.py) - Configuration template

- **Execution**:
  - [README.md § Execution Modes](README.md#execution-modes) - Fast vs Deep mode
  - [run-workflow.sh](run-workflow.sh) - Workflow execution script
  - Dashboard monitoring at `http://localhost:8765`

### Troubleshooting

- **Primary Resource**:
  - [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) - Comprehensive troubleshooting

- **Platform-Specific**:
  - [MACOS_COMPLETE_GUIDE.md § Troubleshooting](MACOS_COMPLETE_GUIDE.md#troubleshooting-macos-issues)
  - [LINUX_QUICK_START.md § Troubleshooting](LINUX_QUICK_START.md#troubleshooting)

### Technical Reference

- **Architecture**:
  - [CLAUDE.md](CLAUDE.md) - Codebase architecture and AI assistant reference
  - [README.md § Architecture](README.md#architecture) - System overview

- **API Documentation**:
  - [API_REFERENCE.md](API_REFERENCE.md) - Complete API reference
  - Dashboard endpoints, status files, log formats

- **Core Components**:
  - client_pipeline.py - Workflow orchestration
  - drive_manager.py - Google Drive integration
  - notebook_manager.py - NotebookLM management
  - gemini_agent.py - AI agent coordination

---

## Complete File Index

### User Documentation (Root)

| File | Purpose |
|------|---------|
| [README.md](README.md) | Project overview, features, quick start |
| [QUICK_START.md](QUICK_START.md) | Step-by-step getting started guide |
| [CLAUDE.md](CLAUDE.md) | Codebase architecture reference |

### Setup Guides (Docs/)

| File | Purpose |
|------|---------|
| [Docs/OAUTH_QUICK_START.md](Docs/OAUTH_QUICK_START.md) | Fast OAuth setup (5 minutes) |
| [Docs/OAUTH_COMPLETE_GUIDE.md](Docs/OAUTH_COMPLETE_GUIDE.md) | Complete OAuth configuration |
| [Docs/ENVIRONMENT_SETUP.md](Docs/ENVIRONMENT_SETUP.md) | Environment configuration |
| [Docs/WEB_CONFIGURATION_GUIDE.md](Docs/WEB_CONFIGURATION_GUIDE.md) | Web UI configuration |
| [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) | Problem resolution |

### Reference Documentation

| File | Purpose |
|------|---------|
| [API_REFERENCE.md](API_REFERENCE.md) | Complete API documentation |
| [CLAUDE.md](CLAUDE.md) | Architecture and component reference |
| [example-vars.py](example-vars.py) | Configuration template |

### Platform-Specific Guides

| File | Purpose |
|------|---------|
| [MACOS_COMPLETE_GUIDE.md](MACOS_COMPLETE_GUIDE.md) | macOS installation and usage |
| [LINUX_QUICK_START.md](LINUX_QUICK_START.md) | Linux installation |
| [CROSS_PLATFORM_LAUNCHER.md](CROSS_PLATFORM_LAUNCHER.md) | Launcher comparison |

### Launcher Scripts

| File | Platform |
|------|---------|
| [launch-project-ape.command](launch-project-ape.command) | macOS (double-click) |
| [launch-project-ape.sh](launch-project-ape.sh) | Linux/macOS (shell) |
| [launch-project-ape.py](launch-project-ape.py) | Cross-platform (Python) |

### Setup & Utility Scripts

| File | Purpose |
|------|---------|
| [setup-environment.sh](setup-environment.sh) | Environment setup |
| [setup-oauth-drive.py](setup-oauth-drive.py) | OAuth configuration wizard |
| [run-workflow.sh](run-workflow.sh) | Workflow execution |
| [install-linux-launcher.sh](install-linux-launcher.sh) | Linux desktop integration |

### Additional Documentation

| File | Purpose |
|------|---------|
| [PRODUCTION_RELEASE_v3.2.2.md](PRODUCTION_RELEASE_v3.2.2.md) | Release notes |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution guidelines |
| [TESTING_RESULTS.md](TESTING_RESULTS.md) | Test validation results |
| [LICENSE](LICENSE) | MIT License |

### Developer Documentation (Not Indexed Here)

Developer-specific documentation is maintained in `developer-docs/`. See [developer-docs/README.md](developer-docs/README.md) for the complete developer documentation index.

---

## Documentation Status

### ✅ User Documentation - Complete

- ✅ README.md - Project overview
- ✅ QUICK_START.md - Getting started guide
- ✅ Docs/TROUBLESHOOTING.md - Problem resolution

### ✅ Setup Guides - Complete

- ✅ Docs/OAUTH_QUICK_START.md - Fast OAuth setup
- ✅ Docs/OAUTH_COMPLETE_GUIDE.md - Complete OAuth guide
- ✅ Docs/ENVIRONMENT_SETUP.md - Environment configuration
- ✅ Docs/WEB_CONFIGURATION_GUIDE.md - Web UI guide

### ✅ Reference Documentation - Complete

- ✅ CLAUDE.md - Architecture reference
- ✅ API_REFERENCE.md - API documentation
- ✅ Platform-specific guides (macOS, Linux)

### 📝 Developer Documentation - See developer-docs/

Developer documentation is maintained separately. See [developer-docs/README.md](developer-docs/README.md).

---

## Getting Help

### Recommended Path

1. **Start**: [README.md](README.md) - Project overview
2. **Setup**: [QUICK_START.md](QUICK_START.md) - Getting started
3. **Troubleshoot**: [Docs/TROUBLESHOOTING.md](Docs/TROUBLESHOOTING.md) - Problem resolution
4. **Platform Guide**: [MACOS_COMPLETE_GUIDE.md](MACOS_COMPLETE_GUIDE.md) or [LINUX_QUICK_START.md](LINUX_QUICK_START.md)

### Still Need Help?

- **Search Issues**: Check existing GitHub issues
- **Open New Issue**: Include OS version, Python version, logs, screenshots
- **Discussions**: Community support and questions

---

## Quick Reference

### First Time Setup
```
1. README.md (overview)
2. QUICK_START.md (step-by-step)
3. Docs/OAUTH_QUICK_START.md (authentication)
4. Docs/ENVIRONMENT_SETUP.md (configuration)
```

### Common Tasks
```
Configure OAuth → Docs/OAUTH_COMPLETE_GUIDE.md
Fix Problems → Docs/TROUBLESHOOTING.md
API Reference → API_REFERENCE.md
Understand Architecture → CLAUDE.md
```

### Platform-Specific
```
macOS → MACOS_COMPLETE_GUIDE.md
Linux → LINUX_QUICK_START.md
Cross-Platform → CROSS_PLATFORM_LAUNCHER.md
```

---

**Documentation Version**: 3.2.2  
**Last Updated**: June 30, 2026  
**Status**: ✅ Complete and Tested  
**Maintainer**: Jason Anderson
