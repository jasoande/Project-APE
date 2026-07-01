# NotebookLM Authentication Validation

## Problem

Users run setup.sh only once, but NotebookLM authentication credentials can expire after 30-90 days. This causes workflow failures when:
- Google session cookies expire
- Browser profile is cleared
- Google invalidates the session

## Solution

Added automatic authentication validation to `launch_ape.sh` that:

1. **Checks auth before every workflow launch**
   - Runs `notebooklm auth check` automatically
   - Validates cookies and session state
   - Fails fast if authentication is invalid

2. **Provides clear remediation steps**
   - Explains why authentication might expire
   - Shows exact command to fix: `notebooklm auth refresh`
   - Offers to run refresh interactively

3. **Interactive refresh option**
   - Prompts user to refresh auth immediately
   - Opens browser for re-authentication
   - Validates success before continuing

## How It Works

### Authentication Check Function

```bash
check_notebooklm_auth() {
    # Check if CLI is available
    # Run: notebooklm auth check
    # If invalid:
    #   - Show error message
    #   - Explain why it happens
    #   - Offer to run refresh
    #   - Validate refresh succeeded
}
```

### Integration Point

Added to `launch_ape.sh` main function:
- Runs AFTER argument parsing
- Runs BEFORE container launch
- Fails fast if auth is invalid
- Prevents wasted time launching containers with invalid credentials

## User Experience

### Valid Authentication
```
[STEP] Checking NotebookLM authentication...
[INFO] ✅ NotebookLM authentication valid

[INFO] Detected architecture: arm64
[INFO] Detected runtime: podman
...
```

### Expired Authentication
```
[STEP] Checking NotebookLM authentication...
[ERROR] NotebookLM authentication expired or invalid

Your NotebookLM credentials need to be refreshed.
This happens when:
  • Cookies expire (typically after 30-90 days)
  • Google session is invalidated
  • Browser profile is cleared

To fix this, run:
  notebooklm auth refresh

This will:
  1. Open your browser
  2. Sign in to NotebookLM
  3. Save fresh credentials

Run auth refresh now? (y/n)
```

### Manual Refresh (if user declines)
```
Please refresh authentication before launching workflows.

Cannot proceed without valid NotebookLM authentication.
```

## Benefits

1. **Prevents wasted time** - Validates auth before launching containers
2. **Clear error messages** - Users know exactly what's wrong and how to fix it
3. **Self-service recovery** - Users can fix auth issues without re-running setup
4. **No manual intervention** - Automatic check on every launch
5. **Graceful failure** - Stops before any work is done if auth is invalid

## Authentication Storage

NotebookLM stores credentials in:
```
~/.notebooklm/profiles/default/
```

Contains:
- Google session cookies (SID, HSID, SSID, etc.)
- Domain-specific cookies (.google.com, .notebooklm.google.com)
- OAuth tokens

## Credential Lifetime

- **Typical expiration**: 30-90 days
- **Refresh method**: `notebooklm auth refresh`
- **Validation**: `notebooklm auth check`
- **Manual intervention**: Browser sign-in required

## Related Files

- `launch_ape.sh` - Contains `check_notebooklm_auth()` function
- `setup.sh` - Initial authentication during first-time setup
- `~/.notebooklm/profiles/default/` - Credential storage

## Testing

Test authentication validation:

```bash
# Check current status
notebooklm auth check

# Simulate expired auth
rm -rf ~/.notebooklm/profiles/default/

# Try to launch (should prompt for refresh)
./launch_ape.sh fast hershey

# Refresh credentials
notebooklm auth refresh

# Verify success
notebooklm auth check
```

## Maintenance

The authentication check is **permanent** - it runs on every workflow launch without requiring setup.sh to be re-run.

If authentication validation needs to be updated:
1. Edit `check_notebooklm_auth()` in `launch_ape.sh`
2. Test with both valid and invalid credentials
3. Verify error messages are clear
4. Ensure refresh flow works end-to-end
