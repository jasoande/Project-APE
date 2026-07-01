# Service Account Configuration Fix

## Problem Identified

**Root Cause**: The `.env` file contained a **container path** for the service account key, but the application was running **locally**.

```bash
# OLD (container path - INCORRECT for local execution)
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json

# NEW (local absolute path - CORRECT)
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/Users/jasona/test/Project-APE-dev/service-account-key.json
```

## Error Message

```
❌ Authentication failed: Service account key not found: /app/service-account.json
```

## Technical Analysis

### Why This Happened

1. **Environment File Generated for Container**: The `.env` file was created with container paths (`/app/...`)
2. **Local Execution Context**: Running `python3 main.py` locally doesn't mount `/app/` directory
3. **Path Mismatch**: Code tried to access `/app/service-account.json` which doesn't exist locally

### Code Path

```
client_pipeline.py:64 __init__()
  → _setup_client_folder() 
    → DriveManager()
      → authenticate()
        → _service_account_authenticate()
          → Checks: GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY from .env
          → Tries to open: /app/service-account.json
          → FAILS: FileNotFoundError
```

### Service Account Files Found

```bash
/Users/jasona/test/Project-APE-dev/service-account-key.json  ✅ (2.3K, valid)
/Users/jasona/test/Project-APE-dev/service-account.json      ✅ (2.3K, duplicate)
/Users/jasona/test/Project-APE-dev/jasoande-3aec1043e544.json ✅ (2.3K, original)
```

**Validation**: All files are valid JSON with proper service account structure.

## Solution Applied

### 1. Updated .env File

```bash
# File: /Users/jasona/test/Project-APE-dev/.env

# Google Drive Service Account
# Local path (use absolute path for local execution)
GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/Users/jasona/test/Project-APE-dev/service-account-key.json
# Container path (commented out for local development)
# GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json
```

### 2. Backup Created

```bash
.env.backup  # Original file saved for reference
```

## Verification

```bash
# Check file exists
ls -lh /Users/jasona/test/Project-APE-dev/service-account-key.json

# Validate JSON structure
python3 -c "import json; json.load(open('service-account-key.json'))"

# Check .env configuration
cat .env | grep GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY

# Test authentication
python3 << 'EOF'
from core.drive_manager import DriveManager
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
print(f"Service account path: {os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY')}")
print(f"File exists: {Path(os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY')).exists()}")
EOF
```

## Best Practices for Dual Environment Support

### Option 1: Environment Detection (Recommended)

Add to your setup script:

```bash
# Auto-detect environment and set correct path
if [ -d "/app" ]; then
    # Container environment
    export GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=/app/service-account.json
else
    # Local environment
    export GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY=$(pwd)/service-account-key.json
fi
```

### Option 2: Separate .env Files

```bash
.env.local      # For local development
.env.container  # For container deployment
```

Then in your setup:
```bash
# Local
cp .env.local .env

# Container
cp .env.container .env
```

### Option 3: Relative Paths in Code

Modify `drive_manager.py` to check multiple locations:

```python
def find_service_account_key():
    """Find service account key in common locations."""
    paths = [
        os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY'),  # From .env
        '/app/service-account.json',                     # Container
        'service-account-key.json',                      # Local relative
        Path(__file__).parent.parent / 'service-account-key.json',  # Project root
    ]
    
    for path in paths:
        if path and Path(path).exists():
            return path
    
    raise FileNotFoundError("Service account key not found in any common location")
```

## Container vs Local Path Reference

| Environment | Path | Use Case |
|-------------|------|----------|
| **Local** | `/Users/jasona/test/Project-APE-dev/service-account-key.json` | Development, testing |
| **Container** | `/app/service-account.json` | Production, deployment |
| **Relative** | `./service-account-key.json` | Portable (works in both) |

## Testing the Fix

```bash
# 1. Verify .env is correct
cat .env | grep GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY

# 2. Test authentication
source ~/.project-ape-venv/bin/activate
python3 << 'EOF'
from dotenv import load_dotenv
from core.drive_manager import DriveManager
import os

load_dotenv()
print(f"✅ Service account path: {os.getenv('GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY')}")

# Try to authenticate
try:
    dm = DriveManager(
        client_id='test',
        folder_spec='drive://test',
        config={'auth_method': 'service_account'}
    )
    dm.authenticate()
    print("✅ Authentication successful!")
except Exception as e:
    print(f"❌ Authentication failed: {e}")
EOF

# 3. Run pipeline test
python3 main.py --mode fast --clients merck_test blue_yonder_test
```

## Expected Behavior After Fix

**Before Fix:**
```
❌ Authentication failed: Service account key not found: /app/service-account.json
```

**After Fix:**
```
✅ Google Drive authentication successful
✅ Service account: project-ape-service@jasoande.iam.gserviceaccount.com
```

## Related Files

- **Configuration**: `.env` (fixed)
- **Service Account Keys**: 
  - `service-account-key.json` (primary)
  - `service-account.json` (duplicate)
  - `jasoande-3aec1043e544.json` (original)
- **Code**: `core/drive_manager.py` (lines 200, 273)
- **Environment Loading**: `main.py` (line 30: `load_dotenv()`)

## Prevention for Future

1. **Document environment differences** in setup guides
2. **Auto-detect environment** in setup scripts
3. **Use relative paths** where possible
4. **Validate .env on startup** with helpful error messages
5. **Template .env files** with comments explaining paths

---

**Status**: ✅ **FIXED**

The `.env` file now points to the correct local path. Pipeline should authenticate successfully with Google Drive.

**Next**: Run `./validate_pipeline.sh` to test the complete pipeline.
