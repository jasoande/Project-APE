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

## [Unreleased]

### Planned for v2.1
- Email notifications on completion
- Enhanced quality scoring algorithm
- Custom prompt template system
- Multi-language support

### Planned for v2.2
- Slack integration
- PDF report generation from notebooks
- Historical quality score tracking
- Advanced retry strategies

### Planned for v3.0
- Docker containerization
- Cloud deployment (AWS/GCP/Azure)
- Web-based configuration UI
- API endpoints for integrations
- Batch processing mode
- Analytics dashboard

---

## Version History Summary

- **2.0.0** (2026-06-10): Production release with deep mode and quality improvements
- **1.0.0** (2026-06-01): Initial release with multi-process architecture

---

**Legend:**
- `Added`: New features
- `Changed`: Changes to existing functionality
- `Deprecated`: Soon-to-be removed features
- `Removed`: Removed features
- `Fixed`: Bug fixes
- `Security`: Security improvements
