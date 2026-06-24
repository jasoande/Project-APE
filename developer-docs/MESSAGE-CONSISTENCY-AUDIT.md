<div align="center">
  <img src="../Project-APE/dashboard/static/kingkong.png" alt="Project APE Logo" width="200"/>
</div>

# Automation Message Consistency Audit

**Audit Date:** June 23, 2026  
**Status:** ⚠️ **INCONSISTENCIES FOUND - NEED FIXES**

---

## Executive Summary

Found messaging inconsistencies in how users are instructed to run Project APE. Different contexts (local vs container, beginner vs advanced) require clear guidance.

**Issues Found:**
1. ⚠️ Mixed usage of `./launch_ape.sh` and `python3 main.py`
2. ⚠️ Not always clear when to use which command
3. ⚠️ Container examples sometimes unclear
4. ✅ Shell script outputs are consistent (all use `./launch_ape.sh`)

---

## Current State Analysis

### ✅ Consistent: Shell Script Outputs

All automation scripts correctly instruct users to use `./launch_ape.sh`:

**setup.sh:**
```bash
echo "  ${GREEN}./launch_ape.sh fast${NC}     # Fast mode (15-20 min/client)"
echo "  ${GREEN}./launch_ape.sh deep${NC}     # Deep mode (35-40 min/client)"
```

**setup-environment.sh:**
```bash
echo "     ./launch_ape.sh fast     # Fast mode (15-20 min)"
echo "     ./launch_ape.sh deep     # Deep mode (35-40 min)"
```

**create-service-account.sh:**
```bash
echo "   ${GREEN}./launch_ape.sh fast${NC}"
```

**setup-credentials.sh:**
```bash
echo "  ./launch_ape.sh fast"
echo "  ./launch_ape.sh deep"
```

**Verdict:** ✅ All automation outputs are consistent

---

### ⚠️ Inconsistent: Documentation

#### README.md Issues

**Container Deployment Section (line ~73):**
```bash
podman run --rm \
  -v $(pwd)/.env:/app/.env:ro \
  ...
  python3 main.py --mode fast    # ✅ CORRECT - inside container
```
**Status:** ✅ Correct - this is inside a container

**Advanced Usage Section (line ~308):**
```bash
python3 main.py --mode fast --no-dashboard
```
**Status:** ⚠️ Should clarify "Advanced: Direct Python execution"

**Common Tasks Section:**
```bash
./launch_ape.sh fast client_name  # ✅ CORRECT - local usage
```
**Status:** ✅ Correct

---

#### QUICKSTART.md Issues

**Advanced Usage Section (line ~308):**
```bash
**Disable dashboard:**
python3 main.py --mode fast --no-dashboard
```
**Status:** ⚠️ Should say "Advanced option:" or show launch_ape.sh equivalent

---

#### DEPLOYMENT-GUIDE.md Issues

Multiple examples use `python3 main.py` without clarifying context:

```bash
python3 main.py --mode fast --clients organon_test  # ⚠️ Context unclear
```

**Should specify:**
- Inside container: `python3 main.py ...`
- Local installation: `./launch_ape.sh ...`

---

## Standard Messaging Rules

### Rule 1: Local Installation (Default)

**PRIMARY METHOD - Always recommend first:**
```bash
./launch_ape.sh fast               # All clients
./launch_ape.sh deep               # All clients, deep mode
./launch_ape.sh fast client1       # Specific client
```

**When to show:**
- Setup completion messages
- README Quick Start
- QUICKSTART guide
- Troubleshooting guides
- 90% of documentation

---

### Rule 2: Container Deployment

**Container run command:**
```bash
podman run ... python3 main.py --mode fast
```

**When to show:**
- Container deployment section
- Dockerfile examples
- Production deployment guides
- Clearly labeled "Container:" or "Inside container:"

---

### Rule 3: Advanced/Direct Python

**Advanced users can call main.py directly:**
```bash
python3 main.py --mode fast --no-dashboard
```

**When to show:**
- Advanced options sections
- Troubleshooting (when launch_ape.sh fails)
- Development guides
- **MUST be labeled:** "Advanced:" or "Direct execution:"

---

## Recommended Fixes

### Fix 1: README.md - Clarify Advanced Usage

**Current (line ~308):**
```bash
**Disable dashboard:**
```bash
python3 main.py --mode fast --no-dashboard
```
```

**Fixed:**
```bash
**Disable dashboard:**
```bash
./launch_ape.sh fast  # Then manually stop dashboard
# OR (Advanced - Direct Python):
python3 main.py --mode fast --no-dashboard
```
```

---

### Fix 2: QUICKSTART.md - Add Context Labels

**Current:**
```bash
**Disable dashboard:**
```bash
python3 main.py --mode fast --no-dashboard
```
```

**Fixed:**
```bash
**Disable dashboard (Advanced):**
```bash
# Method 1: Use launch script (Recommended)
./launch_ape.sh fast
# Dashboard auto-refreshes, just close browser tab

# Method 2: Direct Python execution (Advanced)
python3 main.py --mode fast --no-dashboard
```
```

---

### Fix 3: DEPLOYMENT-GUIDE.md - Separate Local vs Container

**Add clear section headers:**

```markdown
### Local Installation Execution

```bash
./launch_ape.sh fast
./launch_ape.sh deep
./launch_ape.sh fast client1 client2
```

### Container Execution

```bash
# Inside container (via podman run):
python3 main.py --mode fast

# Complete container run command:
podman run ... python3 main.py --mode fast
```

### Direct Python Execution (Advanced)

For developers or troubleshooting:
```bash
python3 main.py --mode fast
python3 main.py --help
```
```

---

## Messaging Hierarchy

### Priority Order (What to Show First)

1. **Primary (90% of users):**
   ```bash
   ./launch_ape.sh fast
   ```

2. **Container (Production deployments):**
   ```bash
   podman run ... python3 main.py --mode fast
   ```

3. **Advanced (Developers/troubleshooting):**
   ```bash
   python3 main.py --mode fast --no-dashboard
   ```

---

## Context Labels

### Use These Labels Consistently

**For local installation:**
```markdown
**Run Project APE:**
```bash
./launch_ape.sh fast
```
```

**For container:**
```markdown
**Container Deployment:**
```bash
podman run ... python3 main.py --mode fast
```
```

**For advanced:**
```markdown
**Advanced - Direct Python:**
```bash
python3 main.py --mode fast --no-dashboard
```
```

---

## Documentation Sections to Update

### High Priority (User-Facing)

1. **README.md**
   - ✅ Container section (already correct)
   - ⚠️ Advanced usage section needs context label
   - ✅ Quick Start section (already correct)

2. **QUICKSTART.md**
   - ⚠️ Advanced usage needs context
   - ⚠️ Disable dashboard section needs clarification
   - ✅ Main flow (already correct)

3. **DEPLOYMENT-GUIDE.md**
   - ⚠️ Needs clear section separation
   - ⚠️ Local vs container examples mixed
   - ⚠️ Add context labels to all examples

### Medium Priority (Developer Docs)

4. **developer-docs/BUILD-COMPLETE-2026-06-23.md**
   - Mixed usage of both commands
   - Add context for each example

5. **developer-docs/CACHE-MANAGEMENT.md**
   - Uses `python main.py` (missing python3)
   - Should recommend `./launch_ape.sh` for users

6. **developer-docs/INITIALIZATION-PERFORMANCE-ANALYSIS.md**
   - Uses direct Python calls (appropriate for dev doc)
   - Add note: "Developer testing - users should use ./launch_ape.sh"

---

## Help/Usage Text Audit

### main.py --help

**Check:**
```bash
python3 main.py --help
```

**Should output:**
```
usage: main.py [-h] [--mode {fast,deep,update}] [--clients CLIENTS [CLIENTS ...]]
               [--no-dashboard]

Project APE - Account Planning Engine

optional arguments:
  --mode {fast,deep,update}
                        Execution mode
  --clients CLIENTS [CLIENTS ...]
                        Specific clients to run
  --no-dashboard        Disable dashboard server

Note: For typical usage, use ./launch_ape.sh instead of calling main.py directly.
```

**Status:** ⚠️ Need to add usage note

---

### launch_ape.sh --help

**Current:** No help text

**Should add:**
```bash
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Project APE - Account Planning Engine"
    echo ""
    echo "Usage:"
    echo "  ./launch_ape.sh fast                    # All clients, fast mode (15-20 min)"
    echo "  ./launch_ape.sh deep                    # All clients, deep mode (35-40 min)"
    echo "  ./launch_ape.sh fast client1 client2    # Specific clients only"
    echo ""
    echo "Modes:"
    echo "  fast     Quick research (15-20 min per client)"
    echo "  deep     Thorough research (35-40 min per client)"
    echo ""
    echo "Examples:"
    echo "  ./launch_ape.sh fast                    # Run all clients in vars.py"
    echo "  ./launch_ape.sh fast merck_test         # Run one client"
    echo "  ./launch_ape.sh deep merck_test blue_yonder_test  # Multiple clients"
    exit 0
fi
```

---

## Error Messages Audit

### Common Error Scenarios

#### 1. User runs wrong command

**Current:** No guidance

**Should add to main.py:**
```python
if __name__ == "__main__":
    # Detect if running outside container
    if not os.path.exists('/.dockerenv') and not os.path.exists('/app'):
        print("Note: For local installations, consider using ./launch_ape.sh")
        print("      (Handles container setup automatically)")
        print("")
```

#### 2. Container not available

**Current (launch_ape.sh):**
```bash
if ! command -v podman &> /dev/null && ! command -v docker &> /dev/null; then
    echo "Error: Neither podman nor docker is installed"
    exit 1
fi
```

**Status:** ✅ Good error message

#### 3. Python version mismatch

**Should add to main.py:**
```python
import sys
if sys.version_info < (3, 11):
    print(f"Error: Python 3.11+ required (you have {sys.version_info.major}.{sys.version_info.minor})")
    print("Please run: ./launch_ape.sh (uses containerized Python)")
    sys.exit(1)
```

---

## Success Messages Audit

### Setup completion (setup.sh)

**Current:**
```bash
echo "  ${GREEN}./launch_ape.sh fast${NC}     # Fast mode (15-20 min/client)"
echo "  ${GREEN}./launch_ape.sh deep${NC}     # Deep mode (35-40 min/client)"
```

**Status:** ✅ Perfect - clear, consistent, color-coded

### Pipeline completion (main.py)

**Current:**
```python
logger.info("🏁 PIPELINE COMPLETE")
logger.info(f"   ⏱️  Duration: {elapsed/60:.1f} minutes")
```

**Should add:**
```python
logger.info("")
logger.info("📊 Dashboard: http://localhost:8765")
logger.info("📓 View results: https://notebooklm.google.com")
logger.info("")
logger.info("To run again: ./launch_ape.sh fast")
```

---

## Beginner vs Advanced Guidance

### Beginner Path (90% of users)

**Setup:**
```bash
./setup.sh
```

**Run:**
```bash
./launch_ape.sh fast
```

**That's it!** Everything else is automatic.

---

### Advanced Path (Developers)

**Direct Python:**
```bash
python3 main.py --mode fast --no-dashboard --clients client1
```

**Container:**
```bash
podman run ... python3 main.py --mode fast
```

**Custom environments:**
```bash
source venv/bin/activate
python3 main.py --mode deep
```

---

## Proposed Standard Messages

### In All Automation Scripts

**✅ Use (Consistent):**
```bash
echo "Run Project APE:"
echo "  ./launch_ape.sh fast     # Recommended"
```

**❌ Don't use (Confusing):**
```bash
echo "Run: python main.py"
echo "Execute: python3 main.py --mode fast"
```

### In User Documentation

**✅ Primary recommendation:**
```markdown
## Run Your First Analysis

```bash
./launch_ape.sh fast
```

**❌ Don't lead with:**
```markdown
```bash
python3 main.py --mode fast
```

### In Developer Documentation

**✅ Acceptable (with context):**
```markdown
### Testing (Developer)

```bash
python3 main.py --mode fast --clients test_client
```

*Note: End users should use `./launch_ape.sh`*
```

---

## Action Items

### Critical (User-Facing Docs)

1. ✅ **README.md**
   - Add "Advanced:" label to direct Python examples
   - Keep container examples (already correct)
   - Verify all Quick Start uses `./launch_ape.sh`

2. ⚠️ **QUICKSTART.md**
   - Fix "Disable dashboard" section
   - Add context labels to advanced options
   - Ensure main path uses `./launch_ape.sh`

3. ⚠️ **main.py**
   - Add `--help` note about launch_ape.sh
   - Add Python version check with helpful message
   - Add completion message with next steps

4. ⚠️ **launch_ape.sh**
   - Add `--help` / `-h` support
   - Add usage examples in help text

### Important (Developer Docs)

5. ⚠️ **DEPLOYMENT-GUIDE.md**
   - Add clear section headers (Local vs Container vs Advanced)
   - Add context labels to all code examples
   - Separate beginner and advanced paths

6. ⚠️ **developer-docs/BUILD-COMPLETE-2026-06-23.md**
   - Add developer context notes
   - Clarify these are testing commands

7. ⚠️ **developer-docs/CACHE-MANAGEMENT.md**
   - Fix `python main.py` → `python3 main.py`
   - Add note about user-facing commands

---

## Testing Checklist

### After Fixes Applied

- [ ] Run `./setup.sh` - verify final message uses `./launch_ape.sh`
- [ ] Run `./launch_ape.sh --help` - verify help text displays
- [ ] Run `python3 main.py --help` - verify usage note present
- [ ] Check README Quick Start - all use `./launch_ape.sh`
- [ ] Check QUICKSTART - primary path uses `./launch_ape.sh`
- [ ] Check all automation scripts - consistent messaging
- [ ] Check container examples - clearly labeled "Container:"
- [ ] Check advanced examples - clearly labeled "Advanced:"

---

## Summary of Required Changes

### Priority 1 - Critical Fixes

1. **README.md** - Add "Advanced:" labels
2. **QUICKSTART.md** - Fix disable dashboard section
3. **main.py** - Add help notes and Python version check
4. **launch_ape.sh** - Add --help support

### Priority 2 - Important Fixes

5. **DEPLOYMENT-GUIDE.md** - Separate local/container/advanced sections
6. **All developer docs** - Add context notes

### Priority 3 - Nice to Have

7. **main.py** - Better completion messages
8. **Error messages** - More helpful guidance

---

## Recommended Standard Phrases

### Use These Consistently

**For beginners:**
- "Run Project APE:" → `./launch_ape.sh fast`
- "Launch the pipeline:" → `./launch_ape.sh fast`
- "Start analysis:" → `./launch_ape.sh fast`

**For containers:**
- "Container deployment:" → `podman run ... python3 main.py ...`
- "Inside container:" → `python3 main.py ...`

**For advanced:**
- "Advanced - Direct Python:" → `python3 main.py ...`
- "Developer testing:" → `python3 main.py ...`
- "Troubleshooting:" → `python3 main.py ...`

**Never use:**
- ❌ "Run: python main.py" (missing python3)
- ❌ "Launch main.py" (unclear method)
- ❌ "Execute the script" (which script?)
- ❌ Mixed commands without context

---

## Conclusion

**Current State:** ⚠️ Inconsistent messaging creates confusion

**Root Cause:** Multiple valid ways to run (local, container, direct) not clearly distinguished

**Solution:** Add clear context labels to all examples

**Impact:** Low-severity issue but affects user experience

**Effort:** ~1-2 hours to fix all documentation

**Priority:** Medium-High (should fix before final release)

---

**Audit Complete**  
**Status:** ⚠️ Fixes Required  
**Estimated Effort:** 1-2 hours  
**Risk:** Low (documentation only)
