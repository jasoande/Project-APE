# Phase 3: Smart Change Detection and Auto-Sync

## Status: PLANNED (Not Yet Implemented)

## Overview
Phase 3 would add intelligent change detection using Google Drive API's changeToken mechanism and optional automated synchronization on a schedule.

## Planned Features

### 1. Change Detection Using Drive API
- Store last sync `changeToken` in cache metadata
- Query Drive API for changes since last token
- Return only files that were added/modified/deleted
- Update cache and token after successful sync

### 2. Scheduled Auto-Sync  
- Optional cron-like scheduling
- Configurable sync interval (hourly, daily, etc.)
- Email/notification on sync completion
- Sync only when changes detected

## Implementation Steps

### Step 1: Enhance DriveManager with Change Detection

```python
# In core/drive_manager.py

def get_changes_since_token(self, folder_id: str, change_token: Optional[str]) -> Dict:
    """
    Get changes in folder since the last changeToken.
    
    Args:
        folder_id: Google Drive folder ID
        change_token: Previous changeToken (None for full sync)
        
    Returns:
        Dict with 'files' (changed files) and 'new_token' (for next call)
    """
    # Use Drive API changes.list() endpoint
    # Filter to files in folder_id
    # Return changed files and new token
    
def _save_change_token(self, folder_id: str, token: str):
    """Save changeToken to cache metadata for next sync."""
    
def _get_last_change_token(self, folder_id: str) -> Optional[str]:
    """Get last changeToken from cache metadata."""
```

### Step 2: Create Auto-Sync Script

```bash
#!/bin/bash
# auto-sync.sh - Periodically check for and sync Drive changes

SYNC_INTERVAL="${1:-3600}"  # Default: 1 hour
CLIENTS="${2:-all}"

while true; do
    echo "[$(date)] Checking for changes..."
    
    # Run update in change-detection mode
    ./update-sources.sh fast $CLIENTS --check-changes-only
    
    if [ $? -eq 1 ]; then  # Exit code 1 = changes detected
        echo "[$(date)] Changes detected, running full update..."
        ./update-sources.sh fast $CLIENTS
    else
        echo "[$(date)] No changes detected"
    fi
    
    sleep $SYNC_INTERVAL
done
```

### Step 3: Add Change Detection to UpdateManager

```python
# In core/update_manager.py

def check_for_changes(self, folder_id: str) -> bool:
    """
    Check if files have changed since last sync.
    
    Returns:
        True if changes detected, False otherwise
    """
    with DriveManager(...) as drive_mgr:
        last_token = drive_mgr._get_last_change_token(folder_id)
        changes = drive_mgr.get_changes_since_token(folder_id, last_token)
        
        if changes['files']:
            logger.info(f"Changes detected: {len(changes['files'])} files")
            return True
        else:
            logger.info("No changes since last sync")
            return False
```

### Step 4: Systemd Service (Linux) or Launch Agent (Mac)

#### Linux (systemd timer):
```ini
# /etc/systemd/system/project-ape-sync.timer
[Unit]
Description=Project APE Auto-Sync Timer
[Timer]
OnCalendar=hourly
Persistent=true
[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/project-ape-sync.service
[Unit]
Description=Project APE Drive Sync
[Service]
Type=oneshot
ExecStart=/path/to/update-sources.sh fast --all --check-changes
WorkingDirectory=/path/to/Project-APE-dev
[Install]
WantedBy=multi-user.target
```

#### macOS (Launch Agent):
```xml
<!-- ~/Library/LaunchAgents/com.project-ape.sync.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.project-ape.sync</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/update-sources.sh</string>
        <string>fast</string>
        <string>--all</string>
    </array>
    <key>StartInterval</key>
    <integer>3600</integer> <!-- Every hour -->
    <key>WorkingDirectory</key>
    <string>/path/to/Project-APE-dev</string>
</dict>
</plist>
```

## Benefits

1. **Efficient Syncing**: Only download/process changed files
2. **Automated Updates**: Set-and-forget synchronization
3. **Resource Savings**: Skip sync when no changes
4. **Change History**: Track when files were modified
5. **Notification**: Alert on sync completion or errors

## Requirements

- Google Drive API `changes.list` endpoint access
- Persistent storage for changeToken
- System scheduler (cron/systemd/Launch Agent)
- Email/notification service (optional)

## Testing Strategy

1. Add a test file to Google Drive
2. Run change detection: should detect 1 change
3. Run update: should add only the new file
4. Run change detection again: should detect 0 changes
5. Modify existing file: should detect 1 change
6. Run update: should update the modified file

## Estimated Implementation Time

- Change detection: 2-3 hours
- Auto-sync script: 1 hour
- Systemd/Launch Agent setup: 1 hour
- Testing: 2 hours
- **Total: 6-7 hours**

## Notes

Phase 3 is planned but not yet implemented due to:
1. Sufficient functionality with Phases 1 & 2
2. Token budget considerations for this session
3. Need for testing with actual Drive API changeToken functionality
4. User can manually trigger updates using Phase 2 tools

## Current Workaround

Without Phase 3, users can:
1. Manually run `./update-sources.sh fast client_name` when files change
2. Set up a simple cron job to run update-sources.sh periodically
3. Use `--refresh` flag to force fresh downloads (Phase 1)

## Phase 3 Status: PLANNED

Implementation is fully designed and ready to be built when needed.
