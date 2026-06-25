# Project APE - NotebookLM Quota Management

<p align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE Logo" width="120"/>
</p>

<h3 align="center">Understanding and Managing NotebookLM API Quotas</h3>

<p align="center">
  Jason Anderson | Project Owner & Maintainer
</p>

---

## The Reality of Quotas

NotebookLM API has quota limits to prevent abuse and ensure fair usage across all users. Project APE, especially in **deep mode**, can hit these limits when processing multiple clients.

---

## What Are the Limits?

While Google doesn't publicly document exact quota limits, empirical testing shows:

- **Research queries (`notebooklm ask --mode deep`)**: Most quota-intensive operations
- **Chat prompts (`notebooklm ask --save-as-note`)**: Moderate quota consumption
- **Source uploads**: Low quota consumption
- **Deduplication**: Low quota consumption

**Estimated Safe Limits** (per hour):
- **Fast Mode**: 5-6 clients safely (2 research + 12 chat prompts each = ~84 operations)
- **Deep Mode**: 1-2 clients safely (6+ research + 12 chat prompts = ~108+ operations)

---

## Quota Errors

When you hit quota limits, you'll see:

```
Error: rpc error: code = ResourceExhausted desc = Quota exceeded
```

Or:

```
Error: Quota exceeded for quota metric 'Read requests' and limit 'Read requests per minute'
```

Project APE automatically retries these with exponential backoff.

---

## How Project APE Handles Quotas

### Automatic Detection

The pipeline detects quota errors via:
- Error message contains "quota"
- RPC error code 8 (RESOURCE_EXHAUSTED)
- RPC error code 3 (deadline exceeded from quota wait)

### Automatic Retry with Backoff

**Research Prompts** (most quota-intensive):
- Max attempts: 7 (was 5)
- Base delay: 30 seconds (was 15s)
- Exponential backoff: 30s → 60s → 120s → 240s → 480s

**Chat Prompts**:
- Max attempts: 5 (was 3)
- Base delay: 10 seconds (was 5s)
- Exponential backoff: 10s → 20s → 40s → 80s

### Mode-Specific Delays

**Fast Mode** (optimized for speed):
- Research delays: 8-12 seconds between prompts
- Chat delays: 5-8 seconds between prompts
- Target: <16 minutes per client

**Deep Mode** (optimized for quota compliance):
- Research delays: 90-120 seconds between prompts (2-3x slower)
- Chat delays: 120-180 seconds between prompts (2-3x slower)
- Target: 30-90 minutes per client

---

## Best Practices

### 1. Use Fast Mode for Multiple Clients

If processing 3+ clients, use **fast mode**:

```bash
./ape-run.sh --vars ./vars.py --clients client1,client2,client3 --mode fast
```

Fast mode stays well under quota limits.

### 2. Use Deep Mode for Single Client

For comprehensive research on ONE client:

```bash
./ape-run.sh --vars ./vars.py --clients important_client --mode deep
```

Deep mode can hit quotas with 2+ clients running simultaneously.

### 3. Stagger Deep Mode Runs

Don't run multiple deep mode clients in parallel. Instead, run them sequentially:

```bash
# Run one at a time
./ape-run.sh --vars ./vars.py --clients client1 --mode deep
# Wait for completion, then:
./ape-run.sh --vars ./vars.py --clients client2 --mode deep
```

### 4. Monitor Logs for Quota Warnings

Watch for log messages like:

```
WARNING | Quota/rate limit hit, waiting 60s (attempt 2/7)
```

If you see these frequently, you're pushing quota limits.

### 5. Spread Work Across Hours

NotebookLM quotas are likely **per-hour** limits. If you hit quota:

- Wait 30-60 minutes
- Resume the workflow
- Or schedule deep mode runs to start on the hour

### 6. Adjust Delays for Your Quota

If you frequently hit quotas even in deep mode, increase delays in `vars.py`:

```python
DEEP_TIMINGS = {
    'ask_prompt_delay': (120.0, 180.0),  # Increase to (180.0, 240.0)
    'chat_prompt_delay': (180.0, 240.0),  # Increase to (240.0, 300.0)
}
```

---

## Quota Recovery

When Project APE hits quota limits:

1. **Automatic retry** - Waits with exponential backoff
2. **Logs the wait time** - Shows "waiting Xs (attempt Y/Z)"
3. **Eventually succeeds** - Most quota errors resolve within 2-3 retries
4. **Fails gracefully** - After max retries, logs error and continues to next prompt

The pipeline **does not stop** on quota errors - it retries until success or max attempts.

---

## Troubleshooting

### Quota Errors Won't Clear

**Symptom:** Retry after retry, still hitting quota

**Solution:**
1. Check if multiple Project APE instances are running (quota is shared)
2. Wait a full hour for quota reset
3. Reduce parallel clients (use `--clients client1` instead of processing all)

### Deep Mode Takes Forever

**Symptom:** Deep mode runs for 2+ hours per client

**Solution:** This is normal with conservative quota delays. Deep mode prioritizes **quota compliance over speed**:
- 6 research prompts × 90-120s = 9-12 minutes just for research
- 12 chat prompts × 120-180s = 24-36 minutes for chat
- Source processing, dedup, etc. adds another 5-10 minutes
- **Total: 40-60 minutes per client is expected**

If this is too slow, use **fast mode** instead.

### Fast Mode Hitting Quotas

**Symptom:** Even fast mode shows quota warnings

**Solution:** You're processing too many clients simultaneously. Reduce to 2-3 clients:

```bash
./ape-run.sh --vars ./vars.py --clients client1,client2 --mode fast
```

---

## Quota-Friendly Workflows

### Scenario 1: Process 10 Clients Quickly

```bash
# Run in batches of 3-4 clients
./ape-run.sh --vars ./vars.py --clients client1,client2,client3 --mode fast
# After completion (~45 min):
./ape-run.sh --vars ./vars.py --clients client4,client5,client6 --mode fast
# After completion (~45 min):
./ape-run.sh --vars ./vars.py --clients client7,client8,client9,client10 --mode fast
```

**Total time:** ~2-3 hours for 10 clients

### Scenario 2: Deep Research on 1 VIP Client

```bash
./ape-run.sh --vars ./vars.py --clients vip_client --mode deep
```

**Total time:** 40-60 minutes for thorough research

### Scenario 3: Mixed Priority

```bash
# VIP gets deep mode
./ape-run.sh --vars ./vars.py --clients vip_client --mode deep

# Others get fast mode in batch
./ape-run.sh --vars ./vars.py --clients client2,client3,client4,client5 --mode fast
```

---

## Understanding the Delays

### Why So Conservative in Deep Mode?

Deep mode delays seem extreme (2-3 minutes between prompts), but they ensure:

1. **Quota compliance** - Stay under hourly limits
2. **High success rate** - Minimize retries and failures
3. **Unattended operation** - Can run overnight without babysitting
4. **Quality over speed** - Deep mode prioritizes thoroughness

### Can I Make It Faster?

**Yes**, but at risk of quota errors. Edit `vars.py`:

```python
# Aggressive deep mode (faster but may hit quota)
DEEP_TIMINGS = {
    'ask_prompt_delay': (30.0, 45.0),  # Risky for quota
    'chat_prompt_delay': (45.0, 60.0),  # Risky for quota
}
```

**Recommended:** Start conservative, then gradually reduce delays until you find your quota sweet spot.

---

## Future Improvements

Planned for v3.1+:
- **Quota monitoring** - Track quota usage in real-time
- **Adaptive delays** - Slow down when quota warnings appear
- **Queue management** - Pause and resume on quota exhaustion
- **Multi-account support** - Distribute load across accounts
- **Quota dashboard** - Visualize quota consumption

---

## Summary

| Mode | Clients | Time/Client | Quota Risk | Use Case |
|------|---------|-------------|------------|----------|
| **Fast** | 1-5 | ~12-16 min | Low | Multiple clients, quick turnaround |
| **Deep** | 1 | ~40-60 min | Medium | Single VIP client, comprehensive research |
| **Deep** | 2+ | ~40-60 min | **High** | Not recommended - stagger instead |

**Golden Rule:** When in doubt, use **fast mode** for multiple clients, **deep mode** for single clients.

---

**Project APE - Quota Management Guide**  
Version 3.0.3 | Jason Anderson | 2026
