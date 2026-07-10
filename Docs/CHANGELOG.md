# Changelog

All notable changes to Account Intelligence will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Multi-language support (Spanish, French, German)
- Azure OpenAI integration as Gemini alternative
- Slack bot interface for workflow triggers
- PDF export of final account plans
- Custom prompt template library

---

## [4.1.1] - 2026-07-09

### Fixed
- **Critical:** Dashboard SSE thread exhaustion crash (68bb84b)
  - Increased thread pool from 100 to 200
  - Added SSE connection rate limiting (10/IP, 60s window)
  - Fixed `/logs/overall` early return leak (60s timeout vs 600s)
  - Proper connection cleanup in finally blocks
- Wizard banner dismissal with localStorage persistence (416620b)
- Real-time Drive URL validation with visual feedback (416620b)

### Changed
- Rebranded from "project ape Account Intelligence" to "Account Intelligence" (416620b)
- Updated all launcher scripts (macOS, Linux, Windows) (416620b)

### Added
- Visual pipeline dashboard with color-coded stages (416620b)
- Progressive disclosure wizard for first-time setup (416620b)
- Dashboard startup optimization (83% faster: 3.0s → 0.5s) (416620b)
- King Kong ASCII art with red fedora (a7611f4)
- Comprehensive root cause analysis documentation (a7611f4)

---

## [4.1.0] - 2026-07-05

### Added
- Security hardening with CSRF protection on all POST endpoints
- Path traversal prevention with regex validation
- Checkpoint/resume system for crash recovery
- Pre-flight health checks before workflow launch
- Workflow stop button for in-progress runs
- Gemini AI quality scorer (6 dimensions, 1.0-10.0 scale)
- Error sanitization (generic messages to users, full logs server-side)

### Changed
- Non-root container execution (UID 1000, username: apeuser)
- Improved retry strategy with exponential backoff
- Enhanced logging with structured formats

### Fixed
- Source verification edge cases
- Container credential volume permissions
- Webhook notification reliability

---

## [4.0.1] - 2026-06-20

### Added
- Setup wizard redesign with polished graphical UI
- Google Drive integration with 7-day intelligent caching
- Auto-conversion of Google Docs/Sheets to PDF
- Real-time dashboard with SSE log streaming

### Fixed
- NotebookLM authentication flow reliability
- Drive OAuth token expiry handling
- Status file race conditions

---

## [4.0.0] - 2026-06-01

### Added
- **Major:** Multi-client parallel execution (up to 5 clients)
- **Major:** Web-based configuration wizard (zero terminal required)
- **Major:** Container deployment support (Podman/Docker)
- Deep mode with 8-9x source coverage (45-90 sources per query)
- Anti-thundering-herd protection for API quota management
- Quality scoring system via Gemini API
- Webhook notifications (Slack, Teams, etc.)

### Changed
- Migrated from single-threaded to multi-process architecture
- Dashboard server upgraded to Waitress (production-grade WSGI)
- Moved from local PDFs to Google Drive folder URLs

### Deprecated
- Manual PDF placement in `client_data/` (still supported, Drive preferred)

---

## [3.0.4] - 2026-04-15

### Added
- Consolidated chat prompts (6 prompts covering 12 dimensions)
- PDF consolidation with table of contents
- Automatic industry detection via Claude API

### Fixed
- Memory leaks in long-running workflows
- PDF merge failures on large files

---

## [3.0.0] - 2026-03-01

### Added
- Initial NotebookLM integration
- Ask prompts for web research
- Chat prompts for analysis generation
- Flask dashboard with manual refresh

### Changed
- Replaced manual research with AI automation
- Switched from local Jupyter notebooks to Google NotebookLM

---

## [2.0.0] - 2026-01-15

### Added
- Jupyter notebook-based analysis
- Template-based account planning framework

### Changed
- Migrated from spreadsheets to programmatic approach

---

## [1.0.0] - 2025-11-01

### Added
- Initial proof of concept
- Manual spreadsheet-based account intelligence
- Basic PDF parsing

---

## Legend

- **Added** — New features
- **Changed** — Changes to existing functionality
- **Deprecated** — Soon-to-be-removed features
- **Removed** — Removed features
- **Fixed** — Bug fixes
- **Security** — Vulnerability fixes

---

**Repository:** https://github.com/jasoande/Project-APE  
**Container Registry:** quay.io/jasoande/project_ape/project-ape  
**Maintainer:** Jason Anderson <jason.anderson@redhat.com>
