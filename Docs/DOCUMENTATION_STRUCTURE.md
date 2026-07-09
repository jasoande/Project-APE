# Account Intelligence - Documentation Architecture

## Documentation Philosophy

**Goal:** Users should find what they need in < 2 minutes, docs should be accurate and complete.

**Audience Tiers:**
1. **End Users** - Sales ops, account managers (need GUI guide)
2. **Administrators** - IT ops deploying/managing the system
3. **Developers** - Engineers extending or integrating the platform

## New Structure

```
project-ape/
├── README.md                    # Landing page, quick start, key features
├── LICENSE                      # MIT License
├── SECURITY.md                  # Security policy and vulnerability reporting
│
├── docs/                        # All documentation (lowercase for consistency)
│   ├── getting-started/
│   │   ├── INSTALLATION.md      # Installation for all platforms
│   │   ├── QUICKSTART.md        # 5-minute tutorial
│   │   └── FIRST_WORKFLOW.md    # End-to-end first workflow guide
│   │
│   ├── user-guide/
│   │   ├── WEB_UI.md            # Web configuration guide
│   │   ├── DRIVE_INTEGRATION.md # Google Drive setup
│   │   ├── WORKFLOWS.md         # Running workflows (fast/deep mode)
│   │   └── RESULTS.md           # Understanding outputs
│   │
│   ├── admin-guide/
│   │   ├── DEPLOYMENT.md        # Container deployment (Podman/Docker)
│   │   ├── AUTHENTICATION.md    # NotebookLM + Drive OAuth setup
│   │   ├── CONFIGURATION.md     # vars.py reference
│   │   ├── MONITORING.md        # Health checks, logs, metrics
│   │   └── TROUBLESHOOTING.md   # Common issues and fixes
│   │
│   ├── developer-guide/
│   │   ├── ARCHITECTURE.md      # System architecture overview
│   │   ├── API_REFERENCE.md     # Module and function reference
│   │   ├── CONTRIBUTING.md      # How to contribute code
│   │   ├── TESTING.md           # Running tests, writing tests
│   │   └── EXTENDING.md         # Adding features, custom integrations
│   │
│   ├── reference/
│   │   ├── CLI_COMMANDS.md      # All command-line options
│   │   ├── CONFIGURATION.md     # Complete vars.py reference
│   │   ├── API_ENDPOINTS.md     # Dashboard REST API
│   │   └── PROMPTS.md           # Prompt engineering guide
│   │
│   └── operations/
│       ├── PERFORMANCE.md       # Tuning and optimization
│       ├── SECURITY.md          # Security hardening guide
│       ├── BACKUP.md            # Backup and disaster recovery
│       └── SCALING.md           # Multi-instance deployment
│
└── CHANGELOG.md                 # Version history and release notes
```

## Files to Remove

**Duplicate/Redundant:**
- `/Docs/CONTRIBUTING.md` (duplicate of `/CONTRIBUTING.md`)
- `/Docs/screenshots/README.md` (no screenshots exist)
- `/Docs/videos/README.md` (no videos exist)

**Developer-only (move to CLAUDE.md or remove):**
- `DASHBOARD_CRASH_ANALYSIS.md` (internal analysis, not user-facing)

**Obsolete:**
- Test files in root: `test_*.py` (should be in tests/ only)
- `vars.py` (example only, users generate via web UI)

## Documentation Standards

### Formatting
- **Headers:** Title case (# Getting Started)
- **Code blocks:** Always specify language (```bash, ```python)
- **Paths:** Use forward slashes, absolute when possible
- **Commands:** Show full command with expected output

### Style
- **Active voice:** "Run the command" not "The command should be run"
- **Second person:** "You can configure..." not "Users can configure..."
- **Short paragraphs:** 3-4 sentences max
- **Examples first:** Show usage before explaining theory

### Structure
Every guide should have:
1. **Purpose** - What this doc covers (1 sentence)
2. **Prerequisites** - What you need before starting
3. **Steps** - Numbered instructions with code blocks
4. **Verification** - How to confirm it worked
5. **Next Steps** - Links to related docs

## King Kong Branding

**Locations for artwork:**
- README.md header
- docs/getting-started/QUICKSTART.md
- Dashboard web UI (already has kingkong.png)
- Error pages (friendly King Kong with red fedora)

**New artwork needed:**
- `dashboard/static/kingkong-fedora.png` - King Kong in red fedora
- `dashboard/static/kingkong-error.png` - Apologetic King Kong (for errors)
- ASCII art version for terminal output
