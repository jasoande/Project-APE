# OAuth Remote VM/SSH Fix

## Problem

When running the Project APE web UI on a **remote VM or via SSH**, the OAuth flow fails with:

```
❌ OAuth flow connection failed
```

**Root Cause:**
- OAuth uses `localhost` redirect after Google authentication
- On a remote VM, `localhost` in your browser = your local machine, NOT the VM
- The OAuth callback server is running on the VM, but your browser tries to connect to `localhost` on your machine
- Connection fails because nothing is listening on your local machine

## Solution Applied

### 1. Backend Detection (`dashboard/server.py`)

Added remote environment detection:

```python
# Detect if running remotely (SSH/VM - localhost redirect won't work)
import os
import socket
is_remote = (
    'SSH_CONNECTION' in os.environ or  # SSH session
    'SSH_CLIENT' in os.environ or
    socket.gethostname() != 'localhost'  # Not local machine
)

if is_remote:
    # Show error with instructions to run locally
    yield 'data: {"status": "error", "message": "❌ Remote VM detected..."}\n\n'
    return
```

### 2. Web UI Warning (`dashboard/templates/configure.html`)

Added prominent warning box on Step 4:

```html
⚠️ Remote VM/SSH Users:
If you're running this on a remote VM or via SSH, the OAuth flow will fail.

Instead, run this on your LOCAL machine:
  python3 setup-oauth-drive-improved.py

Then copy the token to your VM:
  scp ~/.project-ape/drive_token.json user@vm:~/.project-ape/
```

## Recommended Workflow for Remote VMs

### Option 1: Run OAuth on Local Machine (Recommended)

```bash
# On your LOCAL machine:
python3 setup-oauth-drive-improved.py

# Copy token to remote VM:
scp ~/.project-ape/drive_credentials.json user@vm:~/.project-ape/
scp ~/.project-ape/drive_token.json user@vm:~/.project-ape/

# On remote VM:
./ape-run.sh --vars ./vars.py --clients yourclient --mode fast
```

### Option 2: SSH Port Forwarding (Advanced)

```bash
# On your LOCAL machine, SSH with port forwarding:
ssh -L 8080:localhost:8080 user@vm

# On the VM, modify OAuth to use port 8080:
# (This requires code changes - not currently supported)
```

### Option 3: Manual Code Entry (Not Yet Implemented)

Future enhancement: Support out-of-band OAuth flow where user manually copies/pastes authorization code.

## Files Modified

1. **dashboard/server.py**
   - Lines 1455-1500: OAuth flow handler
   - Added remote detection
   - Added clear error messages for remote scenarios

2. **dashboard/templates/configure.html**
   - Lines 1320-1336: Step 4 template
   - Added warning box for remote users
   - Provided clear instructions

## Testing

**Local Machine (should work):**
```bash
# Start dashboard
python3 dashboard/server.py

# Navigate to http://localhost:8765/configure
# Step 4: Click "Authenticate with Google Drive"
# Browser opens, you authenticate, redirects to localhost successfully
```

**Remote VM (should show warning):**
```bash
# SSH to VM
ssh user@vm

# Start dashboard
python3 dashboard/server.py

# Navigate to http://vm-ip:8765/configure
# Step 4: Warning box visible
# Click "Authenticate" → Error: "Remote VM detected..."
```

## Limitations

**Current limitations:**
- Web UI OAuth only works on local machines
- Remote users must use command-line OAuth setup
- No support for manual code entry yet

**Future enhancements:**
1. Add out-of-band OAuth flow (manual code entry)
2. Support SSH port forwarding configuration
3. Auto-detect local vs remote and switch OAuth method

## Related Documentation

- `OAUTH_SETUP_STEP_BY_STEP.md` - Complete OAuth guide
- `Docs/TROUBLESHOOTING.md` - OAuth troubleshooting
- `CLAUDE.md` - OAuth authentication section

---

**Status:** ✅ Fixed - Remote users now see clear error + instructions instead of confusing connection failure
