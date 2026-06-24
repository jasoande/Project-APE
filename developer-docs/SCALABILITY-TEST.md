# Project APE - Maximum Concurrent Client Scalability Test

**Date:** June 16, 2026  
**Objective:** Determine maximum number of clients that can run simultaneously

---

## Hypothesis: Limiting Factors

### 1. API Rate Limits (Most Likely Bottleneck)
- **Gemini API**: 50 requests/minute (free tier)
  - Industry detection: 1 call per client
  - Agent orchestration: ~10 calls per client
  - **Estimated limit: ~5 clients before throttling**

- **NotebookLM CLI** (backend quota unknown):
  - Research operations: 2 per client
  - Source operations: ~20 per client
  - Chat operations: 6 per client
  - **Estimated limit: 10-20 clients**

- **Google Drive API**: 300 requests/minute per project
  - File listing: 1-2 per client
  - **Estimated limit: 100+ clients**

### 2. System Resources
- **File Handles**: macOS default limit ~10,000 per process
  - Each client: ~20 subprocesses × 10 handles = 200 handles
  - **Estimated limit: 50 clients (10,000 handles)**

- **Memory**: 16GB typical system
  - Each client: ~300MB peak
  - **Estimated limit: 30-40 clients (12-16GB)**

- **CPU**: Multi-core can handle many parallel processes
  - **Not expected to be bottleneck**

### 3. Disk I/O
- Status file writes: 6 concurrent writes currently safe
- Log files: Buffered writes, should scale
- **Estimated limit: 20+ clients**

---

## Test Plan: Incremental Load Testing

### Test Configuration

**Base Clients (vars.py):**
```python
clients = [
    "merck_test",
    "blue_yonder_test", 
    "organon_test",
    "panasonic_avionics_test",
    "hershey_test",
    "lord_abbett_test"
]
```

**Test Progression:**
1. **6 clients** (baseline - current)
2. **12 clients** (2x - duplicate client list)
3. **18 clients** (3x - triplicate client list)
4. **24 clients** (4x - quadruplicate client list)
5. Continue until failure...

---

## Test Execution

### Round 1: 6 Clients (Baseline)
**Expected:** SUCCESS  
**Status:** RUNNING (current baseline test)

### Round 2: 12 Clients
**Modification:** Duplicate client list
```python
clients = [
    "merck_test", "blue_yonder_test", "organon_test",
    "panasonic_avionics_test", "hershey_test", "lord_abbett_test",
    "merck_test", "blue_yonder_test", "organon_test",
    "panasonic_avionics_test", "hershey_test", "lord_abbett_test"
]
```
**Expected:** Likely hit Gemini rate limits  
**Watch for:** API throttling, notebook name conflicts

### Round 3: 18 Clients
**Expected:** Definite rate limiting  
**Watch for:** Exponential backoff delays, timeouts

---

## Metrics to Track

### Per-Test Metrics:
- **Completion rate**: X/N clients successful
- **Wall-clock time**: Total execution duration
- **Error types**: Rate limit, timeout, crash, etc.
- **Resource peaks**:
  - File handles (via `lsof`)
  - Memory (via `ps aux`)
  - CPU load (via `top`)
- **API call counts**: Gemini, NotebookLM, Drive

### Success Criteria:
- ✅ All clients complete successfully
- ✅ No unhandled errors
- ✅ System remains responsive
- ✅ Execution time < 30 minutes

---

## Predicted Maximum

**Conservative Estimate:** 8-10 clients  
**Optimistic Estimate:** 15-20 clients  
**Theoretical Max:** 30-40 clients (with proper rate limit handling)

**Primary Bottleneck:** Gemini API rate limits (50 req/min)

---

## Results

*Will be filled in as tests execute...*
