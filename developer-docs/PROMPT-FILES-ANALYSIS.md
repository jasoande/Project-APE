<div align="center">
  <img src="../Project-APE/dashboard/static/kingkong.png" alt="Project APE Logo" width="200"/>
</div>

# Prompt Files Analysis - Baked into Container

**Analysis Date:** June 23, 2026  
**Question:** Are prompt files needed in the repo if they're baked into the container?

---

## TL;DR

**YES - Keep them in the repo!**

**Reason:** While they're baked into the container, they're still needed for:
1. ✅ **Local development** - Running without containers
2. ✅ **Version control** - Track changes to prompts over time
3. ✅ **Container builds** - Source files for `COPY *.txt /app/`
4. ✅ **Documentation** - Users can see what prompts are being used
5. ✅ **Customization** - Users can modify prompts for their needs

---

## Current State

### Prompt Files in Repository

**Location:** Project root (`/Users/jasona/test/Project-APE/`)

**Files:**
1. `ask_prompt_01.txt` (2,073 bytes) - Web source research query 1
2. `ask_prompt_02.txt` (1,338 bytes) - Web source research query 2
3. `ask_prompt_03.txt` (5,337 bytes) - Web source research query 3
4. `chat_prompt_consolidated_01.txt` (1,830 bytes) - Industry Analysis & Customer Business Profile
5. `chat_prompt_consolidated_02.txt` (1,742 bytes) - Innovation Assessment & Executive Summary
6. `chat_prompt_consolidated_03.txt` (1,653 bytes) - Technology Partners & Red Hat Value Propositions
7. `chat_prompt_consolidated_04.txt` (2,056 bytes) - Strategic Ideas & How Might We Statements
8. `chat_prompt_consolidated_05.txt` (2,388 bytes) - Account Team & Partner Onboarding
9. `chat_prompt_consolidated_06.txt` (3,361 bytes) - Comprehensive Account Plan

**Total:** 9 files, ~21 KB

---

## How They're Used

### In Containerfile

```dockerfile
# Line 65:
COPY --chown=apeuser:apeuser *.txt /app/
```

**What this does:**
- Copies ALL `.txt` files from project root to `/app/` in container
- Includes: prompt files + requirements.txt
- Files are owned by `apeuser` (non-root)

### In Code

**The prompts are loaded at runtime by the pipeline:**

```python
# Example from core/client_pipeline.py (likely):
prompt_file = Path(__file__).parent.parent / "ask_prompt_01.txt"
with open(prompt_file, 'r') as f:
    prompt_text = f.read()
```

**Location in container:** `/app/ask_prompt_01.txt`, `/app/chat_prompt_consolidated_01.txt`, etc.

---

## Usage Scenarios

### Scenario 1: Container Deployment (Production)

**How prompts are accessed:**
```
Container filesystem:
  /app/ask_prompt_01.txt
  /app/chat_prompt_consolidated_01.txt
  ...
  
Pipeline reads from /app/ directory ✅
```

**Repo needed?** NO - prompts already baked in

---

### Scenario 2: Local Development (No Container)

**How prompts are accessed:**
```
Local filesystem:
  /Users/jasona/test/Project-APE/ask_prompt_01.txt
  /Users/jasona/test/Project-APE/chat_prompt_consolidated_01.txt
  ...

Pipeline reads from project root ✅
```

**Repo needed?** YES - files must exist locally

---

### Scenario 3: Building New Container

**How prompts are accessed:**
```
Build process:
  COPY *.txt /app/
  
Copies from repo root to container ✅
```

**Repo needed?** YES - source files for COPY command

---

## Should They Be in Repo?

### ✅ YES - Keep in Repository

**Reasons:**

#### 1. **Required for Local Development**
Users running `./launch_ape.sh` or `python3 main.py` **without containers** need these files locally.

```bash
# Local execution (no container):
./launch_ape.sh fast
# ↓ Runs main.py which loads prompt files from current directory
```

#### 2. **Required for Container Builds**

The Containerfile needs these files to copy into the image:
```dockerfile
COPY --chown=apeuser:apeuser *.txt /app/
```

Without them in the repo, `./developer-docs/build-and-push.sh` fails.

#### 3. **Version Control History**

Track changes to prompts over time:
- When were prompts updated?
- What changed between versions?
- Who modified which prompt?
- Rollback if needed

**Example:**
```bash
git log -- chat_prompt_consolidated_01.txt
git diff HEAD~1 ask_prompt_01.txt
```

#### 4. **Transparency & Documentation**

Users can see **exactly what prompts** are being used:
- Review before running
- Understand what research is performed
- Verify alignment with their needs
- Trust in the process

#### 5. **Customization & Forking**

Users can modify prompts for their needs:
- Change industry focus
- Add specific questions
- Adjust to company terminology
- Fork and customize

**Example workflow:**
```bash
# User wants custom prompt
git clone <repo>
vi chat_prompt_consolidated_01.txt  # Customize
./developer-docs/build-and-push.sh  # Build with custom prompts
```

---

## What If We Removed Them?

### ❌ Problems Created

**1. Local Development Broken**
```bash
./launch_ape.sh fast
# Error: FileNotFoundError: ask_prompt_01.txt
```

**2. Container Builds Fail**
```dockerfile
COPY *.txt /app/
# Error: no such file or directory
```

**3. No Version History**
- Can't track when prompts changed
- Can't see what changed between versions
- Can't rollback bad prompt updates

**4. Less Transparent**
- Users can't see what prompts are used
- Must inspect container filesystem
- Harder to verify behavior

**5. Harder to Customize**
- Must extract from container
- Modify and rebuild
- No clear workflow

---

## Best Practices

### ✅ Keep Prompts in Repo

**Location:** Project root (current location is correct)

**Reasoning:**
- Accessible to both local and container deployments
- Version controlled
- Easy to find and modify
- Clear documentation

### ✅ Add README for Prompts

**Consider creating:** `PROMPTS.md`

```markdown
# Project APE - Prompt Files

## Overview
These prompt files control what research questions are asked.

## Files

### Ask Prompts (Web Research)
- `ask_prompt_01.txt` - General web research
- `ask_prompt_02.txt` - Industry-specific research
- `ask_prompt_03.txt` - Technology landscape research

### Chat Prompts (Analysis Notes)
- `chat_prompt_consolidated_01.txt` - Industry Analysis
- `chat_prompt_consolidated_02.txt` - Innovation Assessment
- ...

## Customization
To customize prompts:
1. Edit the `.txt` files
2. Test locally: `./launch_ape.sh fast`
3. Rebuild container: `./developer-docs/build-and-push.sh`
```

### ✅ Consider Prompt Versioning

**For future enhancement:**

```
prompts/
  v3.2/
    ask_prompt_01.txt
    chat_prompt_consolidated_01.txt
  v3.3/
    ask_prompt_01.txt  # Updated version
```

**Benefits:**
- Support multiple prompt versions
- A/B testing
- Gradual rollout of new prompts

---

## Alternative: Prompts in Separate Directory

### Current Structure (Flat)
```
Project-APE/
├── ask_prompt_01.txt
├── chat_prompt_consolidated_01.txt
├── main.py
├── requirements.txt
└── ...
```

### Alternative Structure (Organized)
```
Project-APE/
├── prompts/
│   ├── ask_prompt_01.txt
│   ├── chat_prompt_consolidated_01.txt
│   └── ...
├── main.py
├── requirements.txt
└── ...
```

**Pros:**
- Cleaner root directory
- Easier to find all prompts
- Better organization

**Cons:**
- Requires code changes (update file paths)
- Requires Containerfile change (COPY prompts/*.txt)
- Breaking change for existing deployments

**Recommendation:** Keep current flat structure for v3.2.0, consider organizing in v4.0.0

---

## Current Containerfile Pattern

### What Gets Copied

```dockerfile
# Line 65:
COPY --chown=apeuser:apeuser *.txt /app/
```

**Copies:**
- ✅ `ask_prompt_01.txt`
- ✅ `ask_prompt_02.txt`
- ✅ `ask_prompt_03.txt`
- ✅ `chat_prompt_consolidated_01.txt`
- ✅ `chat_prompt_consolidated_02.txt`
- ✅ `chat_prompt_consolidated_03.txt`
- ✅ `chat_prompt_consolidated_04.txt`
- ✅ `chat_prompt_consolidated_05.txt`
- ✅ `chat_prompt_consolidated_06.txt`
- ❌ `requirements.txt` (already copied earlier on line 22)

**Efficient pattern:** `*.txt` catches all prompts in one line

---

## Git Status

### Should Prompts Be Tracked?

**YES** - They should be in git

```bash
git status
# Should show:
#   ask_prompt_01.txt
#   chat_prompt_consolidated_01.txt
#   ...
```

### .gitignore Check

**Make sure they're NOT ignored:**

```bash
# Check .gitignore
grep "\.txt" .gitignore

# Should NOT contain:
#   *.txt  ❌ (would ignore prompts!)
```

**Current .gitignore should have:**
```
# Only ignore specific txt files if needed
# DO NOT ignore *.txt globally
```

---

## Recommendations

### Immediate (v3.2.0)

1. ✅ **Keep prompts in repo** (already done)
2. ✅ **Keep in project root** (already done)
3. ✅ **Ensure in git** (verify not ignored)
4. ⏳ **Add PROMPTS.md** (optional documentation)

### Future (v3.3.0+)

1. ⏳ **Move to prompts/ directory** (better organization)
2. ⏳ **Add prompt versioning** (support multiple versions)
3. ⏳ **Add prompt testing** (validate prompt quality)
4. ⏳ **Document customization workflow** (user guide)

---

## Summary

**Question:** Do we need prompt files in the repo if they're baked into the container?

**Answer:** **YES - Keep them!**

**Why:**
1. ✅ Required for local development (no container)
2. ✅ Required for container builds (source files)
3. ✅ Version control (track changes)
4. ✅ Transparency (users can review)
5. ✅ Customization (users can modify)

**Current state:** ✅ Correct - prompts are in repo root

**Action needed:** ✅ None - keep as-is

**Future enhancement:** Consider moving to `prompts/` directory in v4.0.0

---

**Analysis Complete**  
**Recommendation:** Keep prompt files in repository  
**Current location:** Correct (project root)  
**Action:** None needed
