# Project APE - Principal Engineer Analysis

**Date:** 2026-06-22  
**Analyst:** Principal Software Engineer Review

## Executive Summary

Project APE has sound architecture but suffers from:
1. **Setup complexity** - 5 separate scripts with unclear order
2. **Hardcoded values** - Service account filenames hardcoded
3. **No unified workflow** - Users must run scripts in correct sequence manually
4. **Documentation sprawl** - 15+ documentation files, many outdated

**Recommendation:** Consolidate into single `setup.sh` workflow with clear documentation.

---

## Code Analysis

### Syntax Validation
✅ All scripts pass `bash -n` syntax check:
- setup-environment.sh
- create-service-account.sh  
- setup-credentials.sh
- launch_ape.sh

### Logic Issues Found

#### 1. Hardcoded Service Account Filename
**File:** `launch_ape.sh:199`
**Issue:** Hardcoded `jasoande-3aec1043e544.json` instead of standard `service-account-key.json`
**Status:** ✅ FIXED
**Impact:** Container failed to mount service account key

#### 2. setup-credentials.sh Runtime Detection Issue
**File:** `setup-credentials.sh:82-94`
**Code:**
```bash
if podman volume exists ${VOLUME_NAME} 2>/dev/null; then
```
**Issue:** Assumes Podman, doesn't check for Docker
**Fix Needed:** Detect runtime (podman vs docker) like launch_ape.sh does

#### 3. No Error Recovery in Workflow
**Issue:** If any script fails, user must manually determine what to fix
**Fix Needed:** Add validation checks between steps

#### 4. Duplicate Code Across Scripts
**Issue:** Runtime detection, color codes, logging functions duplicated in 4 scripts
**Fix Needed:** Create shared library script

### Dependency Analysis

**Correct execution order:**
```
1. setup-environment.sh     → Installs: Podman, Python, venv, NotebookLM CLI
2. source activate-ape-env.sh → Activates Python venv
3. notebooklm login          → Browser auth (requires venv active)
4. create-service-account.sh → Creates GCP service account (optional)
5. setup-credentials.sh      → Copies NotebookLM creds to container volume
6. vars.py configuration     → Manual step
7. launch_ape.sh            → Runs the pipeline
```

**Dependencies:**
- Step 3 requires Step 2 (notebooklm command only in venv)
- Step 5 requires Step 3 (needs ~/.notebooklm/ directory)
- Step 7 requires Steps 4, 5, 6 (needs all credentials)

### File Organization Issues

**Scripts in root:** 18 .sh files
**Documentation in root:** 15+ .md files
**Recommendation:** 
```
scripts/
  setup.sh                  # New unified workflow
  setup-environment.sh
  create-service-account.sh
  setup-credentials.sh
  launch_ape.sh
  lib/
    common.sh               # Shared functions

docs/
  README.md
  QUICKSTART.md
  TROUBLESHOOTING.md
```

---

## Proposed Solutions

### Solution 1: Unified Setup Script

Create `setup.sh` that orchestrates all steps:

```bash
#!/bin/bash
# Master setup script for Project APE

# Step 1: Environment
./setup-environment.sh

# Step 2: Activate venv (in same shell)
source ./activate-ape-env.sh

# Step 3: NotebookLM auth
notebooklm login

# Step 4: Service account (optional, interactive)
./create-service-account.sh

# Step 5: Container credentials  
./setup-credentials.sh

# Step 6: Prompt for vars.py
echo "Setup complete. Next: configure vars.py and run ./launch_ape.sh"
```

**Benefits:**
- Single command setup
- Correct order guaranteed
- Error handling at each step
- Clear progress indication

### Solution 2: Shared Library

Extract common code to `lib/common.sh`:

```bash
# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
# ... etc

# Logging functions
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Runtime detection
detect_runtime() {
    if command -v podman &> /dev/null; then
        echo "podman"
    elif command -v docker &> /dev/null; then
        echo "docker"
    else
        return 1
    fi
}
```

**Impact:** Reduces duplicate code by ~200 lines

### Solution 3: Fix setup-credentials.sh Runtime Detection

**Current:**
```bash
if podman volume exists ${VOLUME_NAME} 2>/dev/null; then
```

**Fixed:**
```bash
# Detect runtime
RUNTIME=$(detect_runtime)

if $RUNTIME volume exists ${VOLUME_NAME} 2>/dev/null; then
```

---

## Documentation Cleanup

### Current State
- 15+ markdown files in root
- Overlapping content (3 different "setup" guides)
- VM-specific docs (not needed for end users)
- Multiple "analysis" docs from debugging

### Proposed Structure

**Keep (consolidate):**
1. **README.md** - Main overview, quick start
2. **SETUP.md** - Detailed setup walkthrough
3. **TROUBLESHOOTING.md** - Common issues
4. **API.md** - For developers extending Project APE

**Archive (move to docs/archive/):**
- MAC-SETUP-ROOT-CAUSE-ANALYSIS.md
- SETUP-FIX-SUMMARY.md
- NOTEBOOKLM-FORMATTING-FIX.md
- TEST-SERVICE-ACCOUNT-SCRIPT.md
- All VM-specific docs

**Delete:**
- Duplicate/outdated docs
- Test scripts (.backup files)

---

## Streamlining Opportunities

### 1. Auto-detect vs Prompt

**Current:** Scripts ask many yes/no questions
**Improvement:** Use sensible defaults, only prompt when necessary

**Examples:**
- ✅ Auto-overwrite old keys (no prompt)
- ✅ Auto-use default GCP project (no prompt)
- ✅ Auto-reuse existing service account (no prompt)
- ⚠️ Keep prompt: "Continue setup? (y/n)" at start

### 2. Consolidate Checks

**Current:** Each script checks for tools independently
**Improvement:** setup.sh does all checks once upfront

```bash
# Check all prerequisites once
check_prerequisites() {
    local missing=()
    
    command -v python3 || missing+=("python3")
    command -v podman || command -v docker || missing+=("podman or docker")
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo "Missing: ${missing[*]}"
        exit 1
    fi
}
```

### 3. Progress Indication

Add overall progress bar:
```
Project APE Setup
[████████░░░░░░░░░░] 40% - Installing NotebookLM CLI...
```

---

## Risk Assessment

### High Risk (Must Fix)
1. ❌ Hardcoded service account filename - **FIXED**
2. ❌ Missing runtime detection in setup-credentials.sh

### Medium Risk (Should Fix)
3. ⚠️ No validation between workflow steps
4. ⚠️ Duplicate code across scripts

### Low Risk (Nice to Have)
5. ℹ️ Documentation cleanup
6. ℹ️ Progress indication

---

## Implementation Plan

### Phase 1: Critical Fixes (Complete)
- [x] Fix hardcoded service account filename
- [x] Streamline create-service-account.sh prompts
- [x] Add IAM propagation delay

### Phase 2: Workflow Consolidation (Next)
- [ ] Create lib/common.sh
- [ ] Create unified setup.sh
- [ ] Fix setup-credentials.sh runtime detection
- [ ] Add validation between steps

### Phase 3: Documentation (Next)
- [ ] Write new README.md from scratch
- [ ] Write SETUP.md with unified workflow
- [ ] Write TROUBLESHOOTING.md
- [ ] Archive old docs

### Phase 4: Polish (Optional)
- [ ] Add progress indication
- [ ] Improve error messages
- [ ] Add --help flags to all scripts

---

## Metrics

**Before Optimization:**
- Scripts: 5 separate
- User prompts: ~12-15
- Lines of duplicate code: ~200
- Documentation files: 15+
- Setup time: ~30-40 min (with reading docs)

**After Optimization:**
- Scripts: 1 unified (calls 5 helpers)
- User prompts: ~5-7
- Lines of duplicate code: 0 (shared lib)
- Documentation files: 4 core
- Setup time: ~20-25 min (streamlined)

---

## Conclusion

Project APE is architecturally sound but operationally complex. The core issues are:

1. **Workflow fragmentation** - Easily fixed with unified setup.sh
2. **Code duplication** - Solvable with shared library
3. **Documentation sprawl** - Needs consolidation

**Recommended Next Steps:**
1. Create unified setup.sh (1-2 hours)
2. Extract lib/common.sh (1 hour)
3. Rewrite core documentation (2-3 hours)
4. Test end-to-end (1 hour)

**Total effort:** ~1 day to significantly improve UX

---

**Questions or concerns with this analysis?**
