# Gemini AI Integration Guide

## Overview

Project APE now includes intelligent industry detection and subsegment generation powered by Google's Gemini AI. This eliminates the need to manually configure industry and subsegments for each client.

## Features

- **Automatic Industry Detection**: AI determines the client's industry from their company name
- **Intelligent Subsegment Generation**: AI identifies 3-4 relevant business subsegments for technical account planning
- **Session-Level Caching**: Results are cached during multi-client runs to minimize API calls
- **Retry Logic**: Exponential backoff handles rate limits and transient errors gracefully
- **Manual Override Support**: Option to provide manual values when needed

## Quick Start

### 1. Get a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/apikey)
2. Click "Create API Key"
3. Choose your Google Cloud project (or create one)
4. Copy the API key (format: `AQ.Ab8...`)

### 2. Configure Environment

Add your API key to `.env`:

```bash
GEMINI_API_KEY=AQ.Ab8RN6IV86r68TlVZTjZF34Hxmqjw...
```

### 3. Enable Gemini in Configuration

In `vars.py` or `container-vars.py`:

```python
GEMINI_CONFIG = {
    'enabled': True,
    'model': 'gemini-2.5-flash',
    'temperature': 0.3,
    'max_retries': 5,
    'retry_base_delay': 10.0,
    'timeout': 60,
    'cache_per_session': True,
}
```

### 4. Configure Clients

**New simplified format** (Gemini auto-detects industry/subsegments):

```python
clients = ["tesla_test"]

tesla_test_name = "Tesla"
tesla_test_folder = "/app/client_data/Tesla"
# Industry and subsegments auto-detected by Gemini AI
```

**Traditional format with manual override** (Gemini is skipped):

```python
clients = ["merck_test"]

merck_test_name = "Merck"
merck_test_industry = "pharmaceuticals and healthcare"
merck_test_subsegments = "oncology, vaccines, rare diseases"
merck_test_folder = "/app/client_data/Merck"
```

## How It Works

### Priority Logic

1. **Manual configuration** in `vars.py` (if provided) → use these values
2. **Gemini AI detection** (if enabled and no manual config) → call AI API
3. **Error** (if Gemini disabled and no manual config) → require configuration

### Pipeline Integration

When the pipeline runs for each client:

```
Step 0.5: Determine Industry & Subsegments
  ├─ Check for manual configuration in vars.py
  ├─ If missing: Call Gemini API
  │   ├─ Step 1: Detect industry from company name
  │   ├─ Step 2: Generate subsegments for that industry
  │   └─ Cache results for session
  └─ Log results to console and dashboard
```

### Example Output

```
[tesla_test] Determining industry and subsegments...
[GEMINI] Detecting industry for client: Tesla
[GEMINI] API call successful (1/1)
[GEMINI] Industry detected: automotive and clean energy
[GEMINI] Generating subsegments for Tesla in automotive and clean energy
[GEMINI] API call successful (1/1)
[GEMINI] Subsegments: electric vehicles, energy storage, autonomous driving software
[tesla_test] Industry: automotive and clean energy
[tesla_test] Subsegments: electric vehicles, energy storage, autonomous driving software
```

## Configuration Reference

### GEMINI_CONFIG Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `True` | Enable/disable Gemini AI detection |
| `model` | str | `gemini-2.5-flash` | Gemini model to use |
| `temperature` | float | `0.3` | Response randomness (0-1, lower = more deterministic) |
| `max_retries` | int | `5` | Max retry attempts for failed API calls |
| `retry_base_delay` | float | `10.0` | Base delay for exponential backoff (seconds) |
| `timeout` | int | `60` | API call timeout (seconds) |
| `cache_per_session` | bool | `True` | Cache results during multi-client runs |

### Recommended Models

| Model | Use Case | Speed | Accuracy | Cost |
|-------|----------|-------|----------|------|
| `gemini-2.5-flash` | **Recommended** | Fast | High | Low |
| `gemini-2.5-pro` | Maximum accuracy | Slower | Highest | Higher |
| `gemini-2.0-flash` | Legacy fallback | Fast | Good | Low |

## Testing

### Standalone Test

Test Gemini integration without running the full pipeline:

```bash
python3 test_gemini_integration.py
```

Expected output:

```
======================================================================
  Gemini Integration Test
======================================================================
  This test validates industry detection and subsegment generation
  for sample companies using Google's Gemini AI.

✅ Found GEMINI_API_KEY: AQ.Ab8RN6IV86r68TlVZ...
✅ Configuration loaded:
  Model: gemini-2.5-flash
  Temperature: 0.3
  Max retries: 5

✅ Testing 4 companies...

======================================================================
  Test 1/4: Merck
======================================================================
  Industry            : pharmaceuticals and healthcare
  Subsegments         : pharmaceutical research and development, biologics manufacturing
  ✅ Success!

======================================================================
  🎉 ALL TESTS PASSED!
  Gemini integration is working correctly.
======================================================================
```

### Pipeline Test

Test with a single client in fast mode:

```bash
python3 main.py --mode fast --clients tesla_test --no-dashboard
```

## Troubleshooting

### API Key Issues

**Error**: `GEMINI_API_KEY not found in environment`

**Solution**: Add your API key to `.env` file:
```bash
GEMINI_API_KEY=your-key-here
```

### Quota Exceeded

**Error**: `429 RESOURCE_EXHAUSTED ... quota exceeded`

**Solutions**:
1. **Switch to gemini-2.5-flash** (higher free tier quota)
2. **Wait for quota reset** (quotas reset daily/hourly)
3. **Enable billing** in Google Cloud Console for unlimited quota

### Model Not Found

**Error**: `404 models/gemini-X is not found`

**Solution**: Use a supported model:
- ✅ `gemini-2.5-flash` (recommended)
- ✅ `gemini-2.5-pro`
- ❌ `gemini-1.5-pro-002` (deprecated)

### Rate Limits

**Error**: `Rate limit exceeded`

**Behavior**: Automatic retry with exponential backoff
- Attempt 1: Wait 10 seconds
- Attempt 2: Wait 20 seconds
- Attempt 3: Wait 40 seconds
- Attempt 4: Wait 80 seconds
- Attempt 5: Wait 160 seconds

If all retries fail, the pipeline will exit with an error.

### Invalid Response

**Error**: `Gemini returned invalid industry: unknown`

**Causes**:
- Company name is too generic or ambiguous
- API returned an error response

**Solution**: Provide manual override:
```python
client_name_industry = "specific industry name"
client_name_subsegments = "subseg1, subseg2, subseg3"
```

## Best Practices

### Company Names

Use full, official company names for best results:
- ✅ "Merck" → pharmaceuticals and healthcare
- ✅ "Blue Yonder" → supply chain management software
- ✅ "Tesla" → automotive and clean energy
- ❌ "ABC Corp" → too generic
- ❌ "Smith Industries" → ambiguous

### Manual Overrides

Use manual configuration when:
- Company name is ambiguous or generic
- You want specific custom subsegments
- Industry classification is highly specialized
- API quota is limited

### Caching

Session-level caching is enabled by default:
- **Multi-client runs**: Same client reuses cached results
- **New sessions**: Fresh API calls for latest data
- **Clear cache**: Restart Python process

## API Costs

### Free Tier

Gemini API offers generous free tier quotas:
- **gemini-2.5-flash**: 15 requests/minute, 1,500 requests/day
- **gemini-2.5-pro**: 2 requests/minute, 50 requests/day

### Cost Estimates

**Per client** (2 API calls: industry + subsegments):
- **gemini-2.5-flash**: ~$0.0001 USD (essentially free)
- **gemini-2.5-pro**: ~$0.001 USD

**100 clients/day**:
- **gemini-2.5-flash**: ~$0.01 USD
- **gemini-2.5-pro**: ~$0.10 USD

## Security

### API Key Protection

1. **Never commit** `.env` to git (already in `.gitignore`)
2. **Restrict API key** to Gemini API only in Google Cloud Console
3. **Rotate keys** periodically
4. **Use service accounts** for production deployments

### Service Account Setup

For production (container deployments):

1. Create service account: `project-ape-gemini@project.iam.gserviceaccount.com`
2. Enable Gemini API in Google Cloud Console
3. Create API key bound to service account
4. Add key to container environment

## Migration Guide

### From Manual Configuration

**Before** (manual configuration for 6 clients):

```python
clients = ["merck_test", "blue_yonder_test", "organon_test", ...]

merck_test_name = "Merck"
merck_test_industry = "pharmaceuticals and healthcare"
merck_test_subsegments = "oncology, vaccines, rare diseases"
merck_test_folder = "/app/client_data/Merck"

blue_yonder_test_name = "Blue Yonder"
blue_yonder_test_industry = "AI-driven supply chain management"
blue_yonder_test_subsegments = "warehouse management systems, transportation management"
blue_yonder_test_folder = "/app/client_data/Blue_Yonder"
```

**After** (Gemini auto-detection for new clients):

```python
# Enable Gemini
GEMINI_CONFIG = {'enabled': True, 'model': 'gemini-2.5-flash'}

# Keep existing clients unchanged (manual config still works)
clients = ["merck_test", "blue_yonder_test", "tesla_test"]

# Existing clients keep manual values
merck_test_name = "Merck"
merck_test_industry = "pharmaceuticals and healthcare"
merck_test_subsegments = "oncology, vaccines, rare diseases"
merck_test_folder = "/app/client_data/Merck"

# New client uses Gemini (no industry/subsegments)
tesla_test_name = "Tesla"
tesla_test_folder = "/app/client_data/Tesla"
```

## Support

For issues or questions:
- Check logs in `/logs/{client_id}.log`
- Review error messages in dashboard
- Run `python3 test_gemini_integration.py` for diagnostics
- Check Google Cloud Console for API quota status
