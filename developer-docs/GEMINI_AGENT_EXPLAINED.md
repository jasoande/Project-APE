# What is the Gemini Agent?

## Overview

The **Gemini Orchestration Agent** is an **optional AI-powered wrapper** around the standard pipeline that adds intelligent monitoring, error recovery, and quality validation.

## Current Status

**🔴 NOT ACTIVE** - Requires `GEMINI_API_KEY` environment variable (currently missing)

When the API key is missing, you see this log message:
```
WARNING | Gemini agent enabled but API key missing - falling back to standard execution
```

## What It Does

### 1. **Intelligent Error Analysis**
Uses Gemini AI to analyze NotebookLM CLI errors and determine:
- Is the error retryable?
- What category of error is it? (auth, rate limit, network, etc.)
- What recovery action should be taken?
- How long to wait before retry?
- Success probability of retry

**Example:**
```python
# Error occurs during research prompt
ERROR: "Rate limit exceeded"

# Gemini analyzes:
- Category: RATE_LIMIT
- Action: WAIT_AND_RETRY
- Wait: 60 seconds
- Probability: 95%
- Reasoning: "Rate limits reset after 60s, high success rate"
```

### 2. **Automatic Retry with Intelligence**
Instead of dumb retries, Gemini decides:
- Should we retry at all?
- How long to wait?
- Should we try a different approach?

### 3. **Quality Validation**
After pipeline completes, uses Gemini to:
- Validate all artifacts were created
- Check source quality and completeness
- Calculate enhanced quality scores
- Suggest improvements

### 4. **Self-Healing**
If quality score is below target:
- Analyzes what went wrong
- Suggests fixes
- Can attempt to re-run failed steps

### 5. **Checkpoint Monitoring**
Tracks each pipeline step:
- Success/failure
- Duration
- Retry count
- Output validation

## Standard vs Gemini Mode Comparison

### Standard Mode (Currently Active)
```
1. Download files
2. Add files to notebook
3. Run research → If fails, retry 5 times with exponential backoff
4. Generate notes → If fails, retry 3 times
5. Create mindmap → If fails, stop
6. Calculate quality score
```

**Error Handling:** Simple exponential backoff retry

### Gemini Agent Mode (Inactive)
```
1. Pre-execution validation
2. Download files
3. Consolidate PDFs ← USES pypdf/Pillow
4. Upload PDF
5. Run research → If fails, Gemini analyzes error and suggests recovery
6. Validate sources with Gemini
7. Generate notes → Gemini monitors quality
8. Create mindmap → Gemini verifies
9. Post-execution artifact verification
10. Gemini-powered quality scoring
11. Attempt quality improvement if below target
```

**Error Handling:** AI-powered analysis + intelligent recovery

## Architecture

```
┌─────────────────────────────────────────────┐
│         GeminiOrchestrationAgent            │
│  - Wraps standard pipeline                  │
│  - Adds monitoring & validation             │
│  - Uses Gemini AI for decisions             │
└─────────────────────────────────────────────┘
          │
          ├──> GeminiErrorAnalyzer
          │    - Analyzes errors
          │    - Suggests recovery
          │
          ├──> GeminiQualityScorer  
          │    - Enhanced quality scoring
          │    - Validation checks
          │
          └──> ArtifactVerifier
               - Ensures all artifacts exist
               - Validates completeness
```

## Dependencies

### Additional Gemini Agent Dependencies:
```python
# Required for Gemini AI
google-genai>=0.1.0  # NOT in requirements.txt

# Required for PDF consolidation (Gemini mode only)
pypdf>=4.0.0
Pillow>=10.0.0
```

## Configuration

Located in `vars.py`:

```python
GEMINI_AGENT_CONFIG = {
    'enabled': True,              # Flag to enable
    'model': 'gemini-2.5-flash',  # Gemini model to use
    'temperature': 0.2,
    'max_retries': 5,
    'quality_target': 8.5,        # Min quality score
    'enable_self_healing': True,
    'enable_quality_validation': True,
}
```

## Enabling Gemini Agent

To activate:

1. **Get Gemini API Key** (from Google AI Studio)
2. **Set environment variable:**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```
3. **Install additional dependency:**
   ```bash
   pip install google-genai
   ```
4. **Run pipeline:**
   ```bash
   ./launch_ape.sh fast merck_test
   ```

It will automatically detect the API key and use Gemini mode.

## Cost Implications

### Standard Mode (Current)
- **Cost:** $0 (no API calls)
- **Speed:** Fast
- **Reliability:** Good (simple retry logic)

### Gemini Agent Mode
- **Cost:** ~$0.01-0.05 per client run
  - Error analysis: ~1-5 Gemini API calls
  - Quality validation: ~2-3 Gemini API calls
  - Self-healing: ~0-5 Gemini API calls
- **Speed:** Slightly slower (Gemini API latency)
- **Reliability:** Better (intelligent recovery)

## When to Use Gemini Agent

### Use Gemini Agent When:
- ✅ Running production workflows requiring max reliability
- ✅ Dealing with flaky APIs or network issues
- ✅ Need detailed quality validation
- ✅ Want AI-powered error recovery
- ✅ Have Gemini API credits to spend

### Don't Need Gemini Agent When:
- ❌ Testing/development (standard mode is fine)
- ❌ No API budget for Gemini calls
- ❌ Pipeline already runs reliably
- ❌ Simple use cases

## Current Recommendation

**Keep it DISABLED** because:

1. ✅ Standard mode works well (8.0/10 quality scores)
2. ✅ No Gemini API costs
3. ✅ Faster execution
4. ✅ Simpler (less moving parts)
5. ✅ UpdateManager already provides smart file handling

**Consider enabling if:**
- You get frequent pipeline failures
- You need maximum reliability
- You have Gemini API credits
- You want AI-powered quality validation

## Summary

| Feature | Standard Mode | Gemini Agent Mode |
|---------|--------------|-------------------|
| Error Analysis | Simple retry | AI-powered |
| Quality Scoring | Basic calculation | Gemini validation |
| Self-Healing | No | Yes |
| PDF Consolidation | No (individual files) | Yes (consolidated) |
| Cost | Free | ~$0.01-0.05/run |
| Speed | Fast | Slightly slower |
| Reliability | Good | Better |
| Currently Active | ✅ YES | ❌ NO |

## Files Involved

- `core/gemini_agent.py` - Main orchestration agent
- `core/error_analyzer.py` - Gemini-powered error analysis
- `core/quality_scorer.py` - Gemini quality validation
- `core/artifact_verifier.py` - Artifact completeness checks

## Conclusion

The Gemini Agent is a **premium feature** that adds AI-powered intelligence to the pipeline. It's currently **disabled and optional**. The standard mode (which you're using) works great without it.

**You don't need it unless you want maximum reliability and have API budget for Gemini calls.**
