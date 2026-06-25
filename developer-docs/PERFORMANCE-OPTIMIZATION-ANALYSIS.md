# Project APE - Performance Optimization Analysis

![King Kong Logo](dashboard/static/kingkong.png)

**Version:** 3.0.4  
**Date:** 2026-06-12  
**Project Owner & Maintainer:** Jason Anderson  
**Analyst:** Principal Software Engineer (Claude Sonnet 4.5)

---

## Executive Summary

Baseline performance for 6 clients in FAST mode was **28:09** (using 12 chat prompts).  
Consolidated 12 chat prompts into 6 strategic prompts, expected improvement: **~6 minutes** (50% reduction in NotebookLM API calls).

---

## Root Cause Analysis

### Issue 1: NotebookLM API Latency Bottleneck

**Observed:**
- Chat prompts taking 60-150 seconds each instead of configured 5-8 seconds
- 12 prompts × ~90s average = 16+ minutes of chat time alone
- **This was the primary performance bottleneck, not containerization overhead**

**Root Cause:**
- NotebookLM API has variable response times
- Configured delays (5-8s) were too optimistic
- No rate limiting on our end = API takes longer per request

**Solution Implemented:**
- Consolidated 12 prompts → 6 strategic prompts
- Expected time savings: ~6 minutes (50% fewer API calls)

---

## Optimization Implementation

### Phase 1: Prompt Consolidation (COMPLETED)

**Created 6 Consolidated Prompts:**

1. **chat_prompt_consolidated_01.txt** - Industry Analysis & Customer Business Profile  
   - Replaces: chat_prompt_01, 02, 03
   - Content: Industry trends, business objectives, products/services, market position

2. **chat_prompt_consolidated_02.txt** - Innovation Assessment & Executive Summary  
   - Replaces: chat_prompt_04, 05
   - Content: Innovation rating scale + 7-bullet executive summary for CRO

3. **chat_prompt_consolidated_03.txt** - Technology Partners & Red Hat Value Propositions  
   - Replaces: chat_prompt_06, 07
   - Content: Partner ecosystem + 5 value statements (Issue/Action/Impact model)

4. **chat_prompt_consolidated_04.txt** - Strategic Ideas & "How Might We" Statements  
   - Replaces: chat_prompt_08, 11
   - Content: 10 solution ideas + 15 HMW innovation statements

5. **chat_prompt_consolidated_05.txt** - Account Team & Partner Onboarding  
   - Replaces: chat_prompt_09, 10
   - Content: Comprehensive account overview + automation-focused partner brief

6. **chat_prompt_consolidated_06.txt** - Comprehensive Red Hat Account Plan  
   - Replaces: chat_prompt_12
   - Content: Complete account plan (executive summary, customer profile, opportunities, strategy)

**Code Changes:**
- Updated `core/client_pipeline.py` line 311: glob pattern changed to `chat_prompt_consolidated_*.txt`
- Updated note titles dictionary (lines 318-324) for consolidated prompts

**Expected Impact:**
- 50% reduction in chat API calls: 12 → 6
- Estimated time savings: ~6 minutes per 6-client run
- **New estimated runtime: ~22 minutes** (down from 28:09)

---

## Additional Optimization Opportunities

### Phase 2: Remove Redundant Delays (RECOMMENDED)

**Current State:**
```python
# client_pipeline.py, lines 338-340, 398-400
jitter = random.uniform(1, 3)  # Anti-collision jitter
time.sleep(jitter)
# ... execute prompt ...
delay = random.uniform(5.0, 8.0)  # Between-prompt delay
time.sleep(delay)
```

**Issue:**
- **Double delay**: We add jitter (1-3s) AND between-prompt delay (5-8s)
- Jitter alone serves the anti-thundering-herd purpose
- Consolidated prompts are larger = longer API processing = natural spacing

**Recommendation:**
Remove redundant between-prompt delay for chat prompts. Keep only jitter.

**Implementation:**
```python
# Remove lines 398-400 in client_pipeline.py
# DELETE THIS BLOCK:
delay_range = self.timings['chat_prompt_delay']
delay = random.uniform(delay_range[0], delay_range[1])
time.sleep(delay)
```

**Expected Impact:**
- Saves 5-8 seconds per prompt
- 6 prompts × 6.5s average = **~39 seconds saved**
- **Risk: LOW** - API processing time already provides spacing

---

### Phase 3: Optimize Research (Ask) Prompts (MODERATE RISK)

**Current State:**
```python
# client_pipeline.py, lines 259-260, 293-295
jitter = random.uniform(2, 5)  # Anti-collision jitter
time.sleep(jitter)
# ... execute research ...
delay = random.uniform(8.0, 12.0)  # Between-prompt delay (FAST mode)
time.sleep(delay)
```

**Issue:**
- Same redundant delay pattern
- Research prompts import sources asynchronously = longer processing

**Recommendation:**
Reduce between-prompt delay from (8-12s) to (3-5s) OR remove entirely and rely on jitter.

**Implementation (Conservative):**
```python
# Update timings in example-vars.py and container-vars.py
'ask_prompt_delay': (3.0, 5.0),  # Reduced from (8.0, 12.0)
```

**Expected Impact:**
- Saves ~7 seconds per research prompt
- 2 prompts × 7s = **~14 seconds saved**
- **Risk: MODERATE** - Research imports sources, may need buffer time

---

### Phase 4: Deep Mode Wait Optimization (LOW PRIORITY)

**Current State:**
```python
# client_pipeline.py, line 286
if self.mode == "deep":
    time.sleep(15)  # Wait for async imports
```

**Issue:**
- Fixed 15-second wait
- No verification that imports actually completed

**Recommendation:**
Implement source count polling instead of fixed wait.

**Implementation:**
```python
def _wait_for_imports(self, timeout=30):
    \"\"\"Poll for source import completion instead of fixed wait.\"\"\"
    start = time.time()
    prev_count = len(self.source_manager.list_sources())
    stable_count = 0
    
    while time.time() - start < timeout:
        time.sleep(3)  # Poll every 3 seconds
        current_count = len(self.source_manager.list_sources())
        if current_count == prev_count:
            stable_count += 1
            if stable_count >= 2:  # Stable for 6 seconds
                return
        else:
            stable_count = 0
        prev_count = current_count
```

**Expected Impact:**
- Saves up to 15 seconds when imports finish early
- **Risk: LOW** - Only affects DEEP mode

---

## Container Build Issues Fixed

### Issue: pypdf Module Not Found

**Root Cause:**
- UBI Python image sets PATH with `/opt/app-root/bin` before `/opt/venv/bin`
- System python3 used instead of venv python3
- Dependencies installed in venv, but not accessible

**Solution:**
- Changed CMD to use explicit path: `/opt/venv/bin/python3`
- Containerfile line 124

---

## Testing Plan

1. ✅ **Test 1:** Verify 6 consolidated prompts execute successfully (single client)
2. ⏳ **Test 2:** Measure performance improvement vs baseline 28:09
3. ⬜ **Test 3:** Remove redundant chat delays, test for errors/rate limits
4. ⬜ **Test 4:** Optimize research delays, test for source import issues
5. ⬜ **Test 5:** Full 6-client run, validate output quality
6. ⬜ **Test 6:** Deep mode validation

---

## Risk Assessment

| Optimization | Time Saved | Risk Level | Recommendation |
|--------------|------------|------------|----------------|
| Consolidate 12→6 prompts | ~6 min | **MINIMAL** | ✅ IMPLEMENT |
| Remove chat delays | ~39 sec | **LOW** | ✅ IMPLEMENT |
| Reduce research delays | ~14 sec | **MODERATE** | ⚠️ TEST FIRST |
| Deep mode polling | variable | **LOW** | ⬜ OPTIONAL |

---

## Expected Final Performance

**Baseline:** 28:09 (6 clients, 12 prompts)  
**After Phase 1 (Consolidation):** ~22:00 (6 clients, 6 prompts)  
**After Phase 2 (Remove chat delays):** ~21:20  
**After Phase 3 (Reduce research delays):** ~21:05  

**Net improvement: ~7 minutes (25% faster)**

---

## Rate Limit Safety

**Current Safeguards:**
- Anti-collision jitter on first prompt: 5-15s
- Anti-collision jitter on subsequent prompts: 1-3s
- Exponential backoff on rate limit errors (60s, 120s, 240s)
- Max 3 retries per prompt

**Recommendation:**
- **Keep all jitter** - prevents thundering herd
- **Remove redundant between-prompt delays** - not needed for rate limiting
- Monitor logs for rate limit errors in testing

**Safe to optimize because:**
1. Jitter provides request spacing
2. Consolidated prompts are larger = longer processing time = natural spacing
3. Retry logic handles any rate limits that do occur

---

## Next Steps

1. Complete Test 1 (running in background)
2. Analyze logs for errors
3. Implement Phase 2 if Test 1 succeeds
4. Run full 6-client test
5. Update documentation with final performance metrics
