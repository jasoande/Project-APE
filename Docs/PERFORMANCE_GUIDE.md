<div align="center">
  <img src="../dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="150"/>
  
  # Performance Guide
  **Optimization and Scalability Best Practices**
  
  Version 4.0.1 | July 2026
</div>

---

## Table of Contents

1. [Performance Overview](#performance-overview)
2. [Benchmarks](#benchmarks)
3. [Execution Time Breakdown](#execution-time-breakdown)
4. [Resource Requirements](#resource-requirements)
5. [Scalability Analysis](#scalability-analysis)
6. [Performance Tuning](#performance-tuning)
7. [Optimization Techniques](#optimization-techniques)
8. [Capacity Planning](#capacity-planning)
9. [Performance Testing](#performance-testing)
10. [Known Performance Issues](#known-performance-issues)

---

## Performance Overview

### Performance Targets

| Metric | Fast Mode Target | Deep Mode Target |
|--------|------------------|------------------|
| **Execution Time** | 15-20 minutes | 45-60 minutes |
| **External Sources** | 40-80 sources | 90-180 sources |
| **Quality Score** | 8.0+ | 8.5+ |
| **API Retry Rate** | <10% | <30% |
| **Memory Usage** | <800 MB per client | <1.2 GB per client |
| **Success Rate** | >95% | >90% |

### Key Performance Indicators

**1. Throughput:**
- Fast mode: 3-4 workflows/hour (sequential)
- Parallel (3 clients): 9 workflows/hour

**2. Latency:**
- API response time: <2 seconds (p95)
- Dashboard load time: <500ms
- Status update frequency: 2 seconds

**3. Efficiency:**
- CPU utilization: 20-40% (single client)
- Network bandwidth: 350 MB/workflow (Fast), 800 MB/workflow (Deep)
- Disk I/O: Minimal (streaming, not buffering)

---

## Benchmarks

### Fast Mode Performance

**Single Client Workflow:**
```
Platform: macOS (M1, 16GB RAM)
Mode: Fast
Client: Acme Corporation (8 PDFs, 42 MB)

Phase 1: PDF Download & Consolidation    45 seconds   (4%)
Phase 2: Notebook Creation                12 seconds   (1%)
Phase 3: Research Queries                 312 seconds  (28%)
Phase 4: Analysis Prompts                 720 seconds  (65%)
Phase 5: Quality Validation               30 seconds   (2%)

Total: 1,119 seconds (18.6 minutes)
External Sources Imported: 82
Quality Score: 8.5/10
API Retry Rate: 6%
Memory Peak: 750 MB
```

**3 Parallel Clients:**
```
Total Time: 22 minutes (vs 56 min sequential)
Time Savings: 61%
Memory Peak: 1.8 GB
CPU Utilization: 35% average
```

### Deep Mode Performance

**Single Client Workflow:**
```
Platform: Linux (8 vCPU, 16GB RAM)
Mode: Deep
Client: TechCo Industries (12 PDFs, 65 MB)

Phase 1: PDF Download & Consolidation    52 seconds   (2%)
Phase 2: Notebook Creation                15 seconds   (1%)
Phase 3: Research Queries                 980 seconds  (30%)
Phase 4: Analysis Prompts                 2,100 seconds (65%)
Phase 5: Quality Validation               55 seconds   (2%)

Total: 3,202 seconds (53.4 minutes)
External Sources Imported: 165
Quality Score: 9.1/10
API Retry Rate: 25%
Memory Peak: 1.1 GB
```

### Container vs Native Performance

| Environment | Fast Mode Time | Deep Mode Time | Overhead |
|-------------|----------------|----------------|----------|
| **Native Python** | 18.6 min | 53.4 min | Baseline |
| **Podman (rootless)** | 19.2 min | 54.8 min | +3% |
| **Docker** | 19.5 min | 55.2 min | +5% |
| **Kubernetes (single pod)** | 20.1 min | 56.5 min | +8% |

**Container overhead:** 3-8% (acceptable for deployment flexibility)

---

## Execution Time Breakdown

### Phase-by-Phase Analysis

**Phase 1: PDF Download & Consolidation (30-60 seconds)**

**Fast factors:**
- Drive cache hit (7-day TTL): Instant (~0s)
- Small PDFs (<5 MB each): 30s
- Few files (5-10 PDFs): 35s

**Slow factors:**
- Cache miss: Full download
- Large PDFs (>50 MB each): 60s+
- Many files (>20 PDFs): 90s+

**Optimization:**
```python
# Use Drive caching (automatic)
# First run: 60s download
# Subsequent runs (within 7 days): 0s (cache hit)

# Reduce file count
recommended_pdfs = 5-15  # Sweet spot
```

---

**Phase 2: Notebook Creation (10-15 seconds)**

**Breakdown:**
- API call to create notebook: 3-5s
- Upload consolidated PDF: 5-8s
- Wait for source processing: Variable (30-45s in Fast, 45-60s in Deep)

**Optimization:**
```python
# Minimal optimization available (API-bound)
# Can reduce source_processing_wait in vars.py (risky)

TIMINGS = {
    'source_processing_wait': (25, 35),  # Aggressive (may cause errors)
    # Default: (30, 45) for Fast mode
}
```

---

**Phase 3: Research Queries (3-5 min Fast, 12-18 min Deep)**

**This is the bottleneck phase** - 25-30% of total time

**Breakdown (Fast mode, 2 queries):**
- Query 1 execution: 90-120s
- Sources import (40 sources): 30-60s
- Delay before Query 2: 8-12s
- Query 2 execution: 90-120s
- Sources import (40 sources): 30-60s

**Total: 248-372 seconds (4-6 minutes)**

**Optimization:**
```python
# Reduce delays (increases retry rate)
TIMINGS = {
    'ask_prompt_delay': (5.0, 8.0),  # Aggressive (default: 8-12)
}

# Expected impact:
# Time saved: 30-60s (10-15% faster)
# Retry rate increase: 5% → 15%
```

---

**Phase 4: Analysis Prompts (8-12 min Fast, 25-35 min Deep)**

**This is the longest phase** - 60-65% of total time

**Breakdown (Fast mode, 6 prompts):**
- Prompt 1 (Industry + Challenges): 120-150s
- Delay: 5-8s
- Prompt 2 (Technology + Competitive): 120-150s
- Delay: 5-8s
- Prompt 3 (Pain Points + Opportunities): 120-150s
- Delay: 5-8s
- Prompt 4 (Decision Makers + Buying): 120-150s
- Delay: 5-8s
- Prompt 5 (Value Prop + Metrics): 120-150s
- Delay: 5-8s
- Prompt 6 (Risks + Recommendations): 120-150s

**Total: 720-900 seconds (12-15 minutes)**

**Optimization:**
```python
# Reduce delays
TIMINGS = {
    'chat_prompt_delay': (3.0, 5.0),  # Aggressive (default: 5-8)
}

# Expected impact:
# Time saved: 120-180s (15-20% faster)
# Risk: Higher retry rate if API rate-limited
```

---

**Phase 5: Quality Validation (1-2 minutes)**

**Breakdown:**
- Gemini API call (if configured): 20-30s
- Generate quality report: 10-20s
- Save outputs: 5s

**Optimization:**
```python
# Skip quality validation (not recommended)
# Set GEMINI_API_KEY="" to disable

# Time saved: 30-45s
# Trade-off: No quality score (manual assessment needed)
```

---

## Resource Requirements

### CPU Requirements

**Single Client:**
```
Fast Mode:
- Baseline: 15-20% (1 core)
- Peaks: 40-50% during PDF processing
- Average: 25%

Deep Mode:
- Baseline: 20-25%
- Peaks: 50-60%
- Average: 35%
```

**Parallel Clients:**
```
3 Clients (Fast):
- Baseline: 30-40%
- Peaks: 70-80%
- Average: 50%

5 Clients (Fast):
- Baseline: 50-60%
- Peaks: 90-100%
- Average: 75%
- ⚠️ CPU-bound at this level
```

**Recommendations:**
- 2 cores minimum (single client)
- 4 cores for 3 parallel clients
- 8 cores for 5 parallel clients

---

### Memory Requirements

**Per-Client Memory Breakdown:**
```
Python runtime:                50 MB
Flask dashboard:              100 MB
PDF processing (PyPDF):       150 MB
NotebookLM CLI:                50 MB
API response buffers:         100 MB
Drive cache overhead:          50 MB

Total per client (Fast):      500 MB
Total per client (Deep):      700 MB (more sources)
```

**System-Wide Memory:**
```
Base (dashboard only):        500 MB
+ 1 client (Fast):          1,000 MB (1 GB)
+ 3 clients (Fast):         2,000 MB (2 GB)
+ 5 clients (Fast):         3,000 MB (3 GB)
+ 3 clients (Deep):         2,600 MB (2.6 GB)
```

**Memory Planning:**
```python
def calculate_memory(num_clients, mode="fast"):
    base = 500  # MB (dashboard)
    per_client = 500 if mode == "fast" else 700
    total_mb = base + (num_clients * per_client)
    
    # Add 20% safety margin
    recommended_mb = int(total_mb * 1.2)
    
    return {
        "minimum_mb": total_mb,
        "recommended_mb": recommended_mb,
        "recommended_gb": round(recommended_mb / 1024, 1)
    }

# Examples
calculate_memory(1, "fast")   # {"minimum_mb": 1000, "recommended_mb": 1200, "recommended_gb": 1.2}
calculate_memory(3, "fast")   # {"minimum_mb": 2000, "recommended_mb": 2400, "recommended_gb": 2.4}
calculate_memory(5, "deep")   # {"minimum_mb": 4000, "recommended_mb": 4800, "recommended_gb": 4.8}
```

---

### Disk I/O Requirements

**Per-Workflow I/O:**
```
Read Operations:
- Client PDFs:                50-200 MB
- Prompt files:               50 KB
- Configuration:              20 KB

Write Operations:
- Consolidated PDF:           60-250 MB
- Logs:                       5-20 MB
- Generated analysis:         1-5 MB
- Status files:               50-200 KB

Total I/O per workflow:       ~300-500 MB
```

**Sustained I/O Rate:**
```
Fast Mode (18 min):
- Average: 500 MB / 1080s = 0.46 MB/s (negligible)

Parallel (3 clients):
- Average: 1500 MB / 1080s = 1.4 MB/s

Deep Mode (53 min):
- Average: 800 MB / 3180s = 0.25 MB/s
```

**Recommendation:** Any modern SSD sufficient (>100 MB/s sustained)

---

### Network Bandwidth

**Per-Workflow Network Usage:**
```
Fast Mode:
  Inbound:
    - PDF downloads (Drive API):      50-200 MB
    - NotebookLM API responses:       10-30 MB
    - Source imports metadata:        10-20 MB
  
  Outbound:
    - NotebookLM API requests:        5-10 MB
    - Drive API requests:             2-5 MB
  
  Total: ~170-350 MB

Deep Mode:
  Inbound:
    - PDF downloads:                  50-200 MB
    - NotebookLM API responses:       30-80 MB
    - Source imports metadata:        30-60 MB
  
  Outbound:
    - NotebookLM API requests:        15-30 MB
    - Drive API requests:             5-10 MB
  
  Total: ~400-800 MB
```

**Bandwidth Planning:**
```
20 clients/day (Fast mode):
  - Daily bandwidth: 20 × 350 MB = 7 GB/day
  - Monthly bandwidth: 7 GB × 30 = 210 GB/month

Minimum sustained speed:
  - Fast mode: 350 MB / 1080s = 0.32 Mbps (2.6 Mbps with overhead)
  - Recommended: 10+ Mbps for comfortable margin
```

---

## Scalability Analysis

### Vertical Scaling (Single Instance)

**Scaling Limits:**
```
1 client:   ✅ Any modern laptop (2 cores, 4 GB RAM)
3 clients:  ✅ Desktop/server (4 cores, 8 GB RAM)
5 clients:  ⚠️ Server-grade (8 cores, 16 GB RAM) - Maximum recommended
10 clients: ❌ Not supported (API quota, memory exhaustion)
```

**Why 5-client limit?**
1. **API quota:** NotebookLM rate limit (60 requests/min)
2. **Memory:** 3 GB + overhead risks OOM on 4 GB systems
3. **Quality degradation:** >30% retry rate at 5+ parallel

---

### Horizontal Scaling (Multi-Instance)

**Current Limitations (v4.0.1):**
- Status files are local (`.multi_process_status/*.json`)
- No distributed locking
- Dashboard assumes single instance

**Workaround (Shared Filesystem):**
```
┌──────────────┐       ┌──────────────┐
│  Instance 1  │       │  Instance 2  │
│ (3 clients)  │       │ (3 clients)  │
└──────┬───────┘       └──────┬───────┘
       │                       │
       └───────────┬───────────┘
                   │
         ┌─────────▼──────────┐
         │  NFS / EFS Share   │
         │ - logs/            │
         │ - docs_generated/  │
         │ - .multi_process/  │
         └────────────────────┘

Total capacity: 6 parallel clients
Requirement: ReadWriteMany PVC (Kubernetes)
```

**Future (v4.2+):**
- PostgreSQL for status tracking
- Redis for caching
- Stateless dashboard
- True horizontal scaling

---

## Performance Tuning

### Timing Optimization Matrix

| Priority | Fast Mode Timing | Expected Result |
|----------|------------------|-----------------|
| **Speed** | `ask_delay: (5, 8)`, `chat_delay: (3, 5)` | 12-15 min, 15% retry rate |
| **Balanced** | `ask_delay: (8, 12)`, `chat_delay: (5, 8)` | 18-20 min, 5-10% retry (default) |
| **Reliability** | `ask_delay: (12, 18)`, `chat_delay: (8, 12)` | 22-25 min, <3% retry |

**Tuning Script:**
```python
# performance_tune.py

def tune_for_speed(vars_file='vars.py'):
    """Optimize for fastest execution (trade-off: higher retry rate)"""
    config = {
        'TIMINGS': {
            'ask_prompt_delay': (5.0, 8.0),
            'chat_prompt_delay': (3.0, 5.0),
            'source_processing_wait': (25, 35),
            'initial_offset': (0, 20),
        },
        'RETRY_CONFIG': {
            'max_attempts': 3,  # Fail faster
            'base_delay': 5,
            'ask_max_attempts': 5,
            'ask_base_delay': 15,
        }
    }
    write_config(vars_file, config)
    print("✓ Tuned for SPEED (12-15 min, 15% retry rate)")

def tune_for_reliability(vars_file='vars.py'):
    """Optimize for maximum reliability (trade-off: slower)"""
    config = {
        'TIMINGS': {
            'ask_prompt_delay': (15.0, 20.0),
            'chat_prompt_delay': (10.0, 15.0),
            'source_processing_wait': (45, 60),
            'initial_offset': (0, 40),
        },
        'RETRY_CONFIG': {
            'max_attempts': 7,
            'base_delay': 15,
            'ask_max_attempts': 10,
            'ask_base_delay': 45,
        }
    }
    write_config(vars_file, config)
    print("✓ Tuned for RELIABILITY (22-25 min, <3% retry rate)")
```

---

## Optimization Techniques

### 1. Drive Caching Optimization

**Automatic 7-day caching:**
```python
# First run (cache miss)
Download 8 PDFs: 60 seconds

# Second run within 7 days (cache hit)
Download 8 PDFs: 0 seconds (instant)

Time saved: 60 seconds per workflow
```

**Best practice:** Schedule recurring workflows for same clients to leverage cache.

---

### 2. Parallel Execution Strategy

**Sequential vs Parallel:**
```
Sequential (5 clients, Fast mode):
  Client 1: 18 min
  Client 2: 18 min
  Client 3: 18 min
  Client 4: 18 min
  Client 5: 18 min
  Total: 90 minutes

Parallel (5 clients, Fast mode):
  All 5 clients simultaneously
  Total: 25 minutes (anti-thundering-herd offset + max client time)
  
Time saved: 65 minutes (72% reduction)
```

---

### 3. Timing Auto-Tuning (Future)

**Planned feature (v4.2):**
```python
# Auto-adjust delays based on observed retry rate
if retry_rate > 15%:
    increase_delays_by(20%)  # More conservative
elif retry_rate < 3%:
    decrease_delays_by(10%)  # More aggressive
```

---

### 4. Skip Quality Scoring (Optional)

**If Gemini API unavailable:**
```bash
# Unset API key
unset GEMINI_API_KEY

# Time saved per workflow: 30-45 seconds
# Trade-off: No automated quality score (manual assessment needed)
```

---

## Capacity Planning

### Growth Projections

**Monthly Workflow Volume:**
```
Year 1 (10 users):       50 workflows/month
Year 2 (30 users):      180 workflows/month
Year 3 (100 users):     600 workflows/month
```

**Infrastructure Requirements:**

**Year 1 (50 workflows/month):**
```
Deployment: Single instance (native Python)
Resources: 4 vCPU, 8 GB RAM, 50 GB disk
Cost: $0 (laptop/workstation)
```

**Year 2 (180 workflows/month):**
```
Deployment: Container (Podman/Docker)
Resources: 8 vCPU, 16 GB RAM, 100 GB disk
Cost: ~$100/month (cloud VM)
```

**Year 3 (600 workflows/month):**
```
Deployment: Kubernetes (3-node cluster)
Resources: 24 vCPU total, 48 GB RAM, 500 GB disk
Cost: ~$400/month (managed Kubernetes)
```

---

## Performance Testing

### Benchmark Workflow

**Create benchmark configuration:**
```python
# benchmark-vars.py

clients = ["benchmark_client"]

benchmark_client_name = "Benchmark Test Client"
benchmark_client_folder = "https://drive.google.com/drive/folders/..."  # 10 PDFs, 50 MB
benchmark_client_industry = "technology"
benchmark_client_subsegments = "cloud, software, AI"

MODE = "fast"
```

**Run benchmark:**
```bash
# Warm-up run (populate cache)
time ./ape-run.sh --vars benchmark-vars.py --clients benchmark_client --mode fast

# Benchmark run
time ./ape-run.sh --vars benchmark-vars.py --clients benchmark_client --mode fast

# Expected: 18-20 minutes (second run with cache hit: 17-19 min)
```

**Record metrics:**
```bash
# Execution time
grep "Workflow complete" logs/benchmark_client.log

# Quality score
jq '.overall_score' docs_generated/benchmark_client/Quality_Score.json

# Sources imported
jq '.sources.total' docs_generated/benchmark_client/Quality_Score.json

# Retry rate
total=$(grep -c "API call" logs/benchmark_client.log)
retries=$(grep -c "Retry attempt" logs/benchmark_client.log)
echo "Retry rate: $(echo "scale=2; $retries/$total*100" | bc)%"
```

---

## Known Performance Issues

### Issue 1: High Retry Rate in Parallel Execution

**Symptom:** >30% retry rate when running 5 clients in Fast mode

**Cause:** NotebookLM API rate limit (60 requests/min)

**Workaround:**
```python
# Reduce parallel clients
clients = ["client1", "client2", "client3"]  # 3 instead of 5

# Or increase delays
TIMINGS = {
    'ask_prompt_delay': (12.0, 18.0),  # More conservative
    'chat_prompt_delay': (8.0, 12.0),
}
```

---

### Issue 2: Memory Exhaustion with Deep Mode + 5 Clients

**Symptom:** OOM (Out of Memory) errors, system swap thrashing

**Cause:** 5 × 700 MB = 3.5 GB + OS overhead exceeds 4 GB RAM

**Workaround:**
```python
# Limit Deep mode to 2-3 parallel clients
clients = ["client1", "client2"]  # Max 2 in Deep mode

# Or upgrade to 8+ GB RAM
```

---

### Issue 3: Drive API Quota Exceeded

**Symptom:** "Quota exceeded" errors during Phase 1 (PDF download)

**Cause:** Exceeded 1000 requests/100 seconds Drive API quota

**Workaround:**
```python
# Use Drive cache (automatic after first run)
# Or reduce parallel clients downloading simultaneously
```

---

<div align="center">
  
  **Performance at Scale**
  
  Combine with [CONFIGURATION_BEST_PRACTICES.md](CONFIGURATION_BEST_PRACTICES.md) for optimization.
  
  ---
  
  *Last Updated: July 2026 | Version 4.0.1*
  
</div>
