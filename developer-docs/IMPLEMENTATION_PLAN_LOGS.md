# Implementation Plan: First-Run Marker & Logs Tab

**Date**: June 24, 2026  
**Features**: 
1. Add first-run marker system to setup.sh
2. Add Logs tab to configuration UI

---

## Part 1: First-Run Marker System in setup.sh

### Current State
- Launcher (`launch-project-ape.command`) creates `~/.ape_setup_complete` marker after setup finishes
- setup.sh doesn't create any marker file

### Desired State
- setup.sh creates the marker file itself upon successful completion
- Launcher just checks for the marker (simpler, more reliable)
- Marker contains metadata about setup (timestamp, version, platform)

### Implementation Steps

#### Step 1.1: Modify setup.sh to Create Marker

**Location**: End of setup.sh (after "Setup Complete" message)

**Add**:
```bash
################################################################################
# Create Setup Completion Marker
################################################################################

log_step "Creating Setup Completion Marker"

MARKER_FILE="$HOME/.ape_setup_complete"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cat > "$MARKER_FILE" <<EOF
{
  "setup_completed": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "setup_version": "3.3.0",
  "platform": "$(uname -s)",
  "script_dir": "$SCRIPT_DIR",
  "components_installed": {
    "podman": true,
    "gcloud": true,
    "python": true,
    "notebooklm_cli": true,
    "service_account": true,
    "container_credentials": true
  }
}
EOF

if [ -f "$MARKER_FILE" ]; then
    log_info "✅ Setup marker created: $MARKER_FILE"
    log_info "You can reset setup by deleting this file: rm $MARKER_FILE"
else
    log_error "Failed to create setup marker"
fi
```

#### Step 1.2: Update Launcher to Remove Marker Creation

**Location**: launch-project-ape.command, after setup.sh execution

**Current Code**:
```bash
if ./setup.sh; then
    # Create marker file on success
    cat > "$MARKER_FILE" <<EOF
{
  "setup_completed": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  ...
}
EOF
    ...
fi
```

**New Code**:
```bash
if ./setup.sh; then
    # setup.sh creates the marker file itself
    if [ -f "$MARKER_FILE" ]; then
        log_info "✅ Setup complete!"
    else
        log_error "Setup completed but marker file not created"
        exit 1
    fi
    echo ""
    pause_for_input
else
    log_error "Setup failed. Please check errors above."
    exit 1
fi
```

#### Step 1.3: Create Reset Script

**New File**: `reset-setup.sh`

**Purpose**: Allow users to reset the first-run state for testing

```bash
#!/bin/bash
################################################################################
# Reset Project APE Setup State
# Removes the first-run marker to allow setup to run again
################################################################################

MARKER_FILE="$HOME/.ape_setup_complete"

if [ -f "$MARKER_FILE" ]; then
    echo "Current setup marker:"
    cat "$MARKER_FILE"
    echo ""
    echo "This will remove the setup marker and allow setup to run again."
    echo "WARNING: This does NOT uninstall dependencies or remove configurations."
    echo ""
    read -p "Continue? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm "$MARKER_FILE"
        echo "✅ Setup marker removed: $MARKER_FILE"
        echo ""
        echo "Next time you run launch-project-ape.command, setup will run again."
    else
        echo "Cancelled."
    fi
else
    echo "No setup marker found at: $MARKER_FILE"
    echo "Setup has not been completed yet, or marker was already removed."
fi
```

**Testing**:
```bash
chmod +x reset-setup.sh
./reset-setup.sh
```

---

## Part 2: Logs Tab in Configuration UI

### Current State
- Dashboard has real-time log streaming at `/logs/<client_token>`
- No way to view logs from configuration page
- No unified logs viewer

### Desired State
- New "Logs" tab in configuration UI
- Dropdown to select log source:
  - "Overall" - Combined logs from all components
  - Individual client logs (one per client)
- Real-time streaming log viewer
- Auto-scroll to bottom
- Pause/resume streaming
- Clear logs button
- Download logs button

### Architecture

#### Backend Changes

**New Endpoint**: `GET /logs/overall`
- Streams combined logs from main.py and all components
- Uses Server-Sent Events (SSE) like existing client logs endpoint

**New Endpoint**: `GET /api/available-logs`
- Returns list of available log files
- Format: `[{"type": "overall", "label": "Overall Logs"}, {"type": "client", "token": "client_id", "label": "Client Name"}]`

#### Frontend Changes

**New Tab**: Logs tab in configure.html
**New JavaScript**: Log streaming logic in configure.js

### Implementation Steps

#### Step 2.1: Add Backend Endpoints

**File**: `dashboard/server.py`

**Add after existing `/logs/<client_token>` endpoint**:

```python
@app.route('/logs/overall')
def stream_overall_logs():
    """Stream combined logs from all components."""
    def generate():
        # Find all log files
        log_files = []
        
        # Add main log if exists
        main_log = LOGS_DIR / "main.log"
        if main_log.exists():
            log_files.append(main_log)
        
        # Add client logs
        for log_file in LOGS_DIR.glob("*.log"):
            if log_file != main_log:
                log_files.append(log_file)
        
        if not log_files:
            yield f"data: No log files found in {LOGS_DIR}\n\n"
            return
        
        # Send existing content from all files
        for log_file in log_files:
            try:
                with open(log_file, 'r') as f:
                    yield f"data: === {log_file.name} ===\n\n"
                    for line in f:
                        yield f"data: {line}\n\n"
                    yield f"data: \n\n"
            except Exception as e:
                yield f"data: Error reading {log_file.name}: {e}\n\n"
        
        # Stream new content (watch all files)
        # For simplicity, we'll watch the main log file
        # A more sophisticated implementation would use inotify
        if main_log.exists():
            with open(main_log, 'r') as f:
                f.seek(0, 2)  # Go to end
                while True:
                    line = f.readline()
                    if line:
                        yield f"data: {line}\n\n"
                    else:
                        time.sleep(0.5)
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/available-logs')
def available_logs():
    """Return list of available log files."""
    logs = []
    
    # Add overall option
    logs.append({
        'type': 'overall',
        'token': 'overall',
        'label': 'Overall Logs (All Components)',
        'path': str(LOGS_DIR)
    })
    
    # Add client logs from status files
    if STATUS_DIR.exists():
        for status_file in STATUS_DIR.glob("*.json"):
            try:
                with open(status_file, 'r') as f:
                    client_data = json.load(f)
                    client_name = client_data.get('name', 'Unknown')
                    client_token = client_data.get('token', status_file.stem)
                    log_file = LOGS_DIR / f"{client_token}.log"
                    
                    if log_file.exists():
                        logs.append({
                            'type': 'client',
                            'token': client_token,
                            'label': f"{client_name}",
                            'path': str(log_file)
                        })
            except Exception:
                pass
    
    # Add any standalone log files not in status
    for log_file in LOGS_DIR.glob("*.log"):
        token = log_file.stem
        # Skip if already added
        if not any(l['token'] == token for l in logs):
            logs.append({
                'type': 'standalone',
                'token': token,
                'label': f"{log_file.stem} (standalone)",
                'path': str(log_file)
            })
    
    return jsonify({
        'success': True,
        'logs': logs
    })
```

#### Step 2.2: Add Logs Tab HTML

**File**: `dashboard/templates/configure.html`

**Add new tab button** (after Preview tab):
```html
<button class="tab" data-tab="logs">📋 Logs</button>
```

**Add new tab panel** (after Preview panel):
```html
<!-- Logs Tab -->
<div id="logs-panel" class="tab-panel">
    <div class="settings-section">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
            <h3>📋 Real-Time Logs</h3>
            <div style="display: flex; gap: 12px; align-items: center;">
                <select class="form-select" id="logSelector" style="width: 300px;">
                    <option value="overall">Overall Logs (All Components)</option>
                </select>
                <button type="button" class="btn btn-secondary" id="pauseLogsBtn">
                    ⏸️ Pause
                </button>
                <button type="button" class="btn btn-secondary" id="clearLogsBtn">
                    🗑️ Clear
                </button>
                <button type="button" class="btn btn-secondary" id="downloadLogsBtn">
                    📥 Download
                </button>
            </div>
        </div>
        
        <div class="log-viewer" id="logViewer">
            <div class="log-content" id="logContent">
                <!-- Logs will stream here -->
            </div>
        </div>
        
        <div class="form-help" style="margin-top: 10px;">
            Logs update in real-time. Select a log source from the dropdown above.
        </div>
    </div>
</div>
```

**Add CSS styles** (in `<style>` section):
```css
/* Log Viewer */
.log-viewer {
    background: #0a0d14;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 8px;
    height: 600px;
    overflow-y: auto;
    font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
    font-size: 0.85rem;
    line-height: 1.4;
    padding: 0;
}

.log-content {
    padding: 16px;
    color: #e6edf3;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.log-viewer::-webkit-scrollbar {
    width: 12px;
}

.log-viewer::-webkit-scrollbar-track {
    background: rgba(0,0,0,0.3);
    border-radius: 0 8px 8px 0;
}

.log-viewer::-webkit-scrollbar-thumb {
    background: rgba(238,0,0,0.5);
    border-radius: 6px;
}

.log-viewer::-webkit-scrollbar-thumb:hover {
    background: rgba(238,0,0,0.7);
}

/* Auto-scroll indicator */
.log-viewer.auto-scroll {
    border-color: rgba(0,208,132,0.5);
}

.log-viewer.paused {
    border-color: rgba(255,185,0,0.5);
}

/* Log line types */
.log-line-error {
    color: #ff6b6b;
    font-weight: 600;
}

.log-line-warning {
    color: #ffb900;
}

.log-line-success {
    color: #00d084;
}

.log-line-info {
    color: #93c5fd;
}
```

#### Step 2.3: Add Logs Tab JavaScript

**File**: `dashboard/static/configure.js`

**Add at the end, before event listeners section**:

```javascript
// ========================================================================
// Logs Streaming
// ========================================================================

let logsEventSource = null;
let logsAutoScroll = true;
let logsPaused = false;

async function initLogsTab() {
    // Load available logs
    await loadAvailableLogs();
    
    // Set up log selector change handler
    document.getElementById('logSelector').addEventListener('change', (e) => {
        switchLogSource(e.target.value);
    });
    
    // Set up control buttons
    document.getElementById('pauseLogsBtn').addEventListener('click', toggleLogsPause);
    document.getElementById('clearLogsBtn').addEventListener('click', clearLogs);
    document.getElementById('downloadLogsBtn').addEventListener('click', downloadLogs);
    
    // Start streaming overall logs by default
    switchLogSource('overall');
    
    // Set up auto-scroll detection
    const logViewer = document.getElementById('logViewer');
    logViewer.addEventListener('scroll', () => {
        const isAtBottom = logViewer.scrollHeight - logViewer.scrollTop <= logViewer.clientHeight + 50;
        logsAutoScroll = isAtBottom;
        
        if (isAtBottom) {
            logViewer.classList.add('auto-scroll');
        } else {
            logViewer.classList.remove('auto-scroll');
        }
    });
}

async function loadAvailableLogs() {
    try {
        const response = await fetch('/api/available-logs');
        const data = await response.json();
        
        if (data.success && data.logs) {
            const selector = document.getElementById('logSelector');
            selector.innerHTML = '';
            
            data.logs.forEach(log => {
                const option = document.createElement('option');
                option.value = log.token;
                option.textContent = log.label;
                selector.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Failed to load available logs:', error);
    }
}

function switchLogSource(logToken) {
    // Close existing stream
    if (logsEventSource) {
        logsEventSource.close();
    }
    
    // Clear log content
    document.getElementById('logContent').textContent = '';
    
    // Start new stream
    const url = logToken === 'overall' 
        ? '/logs/overall'
        : `/logs/${logToken}`;
    
    logsEventSource = new EventSource(url);
    
    logsEventSource.onmessage = (event) => {
        if (!logsPaused) {
            appendLogLine(event.data);
        }
    };
    
    logsEventSource.onerror = (error) => {
        console.error('Log stream error:', error);
        appendLogLine('--- Log stream disconnected ---');
    };
}

function appendLogLine(line) {
    const logContent = document.getElementById('logContent');
    const logViewer = document.getElementById('logViewer');
    
    // Add line with optional styling
    let styledLine = line;
    if (line.includes('ERROR') || line.includes('FAILED')) {
        styledLine = `<span class="log-line-error">${line}</span>`;
    } else if (line.includes('WARNING') || line.includes('WARN')) {
        styledLine = `<span class="log-line-warning">${line}</span>`;
    } else if (line.includes('SUCCESS') || line.includes('✅')) {
        styledLine = `<span class="log-line-success">${line}</span>`;
    } else if (line.includes('INFO')) {
        styledLine = `<span class="log-line-info">${line}</span>`;
    }
    
    logContent.innerHTML += styledLine + '\n';
    
    // Auto-scroll if enabled
    if (logsAutoScroll) {
        logViewer.scrollTop = logViewer.scrollHeight;
    }
}

function toggleLogsPause() {
    logsPaused = !logsPaused;
    const btn = document.getElementById('pauseLogsBtn');
    const logViewer = document.getElementById('logViewer');
    
    if (logsPaused) {
        btn.textContent = '▶️ Resume';
        btn.classList.add('btn-success');
        btn.classList.remove('btn-secondary');
        logViewer.classList.add('paused');
    } else {
        btn.textContent = '⏸️ Pause';
        btn.classList.remove('btn-success');
        btn.classList.add('btn-secondary');
        logViewer.classList.remove('paused');
    }
}

function clearLogs() {
    if (confirm('Clear current log display? (This does not delete log files)')) {
        document.getElementById('logContent').textContent = '';
        showMessage('info', '🗑️ Log display cleared');
    }
}

function downloadLogs() {
    const logContent = document.getElementById('logContent');
    const logSelector = document.getElementById('logSelector');
    const selectedLog = logSelector.options[logSelector.selectedIndex].text;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `${selectedLog.replace(/[^a-z0-9]/gi, '_')}_${timestamp}.log`;
    
    downloadFile(logContent.textContent, filename);
    showMessage('success', `✅ Logs downloaded as ${filename}`);
}
```

**Update DOMContentLoaded** event listener to initialize logs:

```javascript
window.addEventListener('DOMContentLoaded', () => {
    // ... existing initialization code ...
    
    // Initialize logs tab
    initLogsTab();
    
    // ... rest of code ...
});
```

#### Step 2.4: Update Tab Switching Logic

**File**: `dashboard/static/configure.js`

**Modify `initTabs()` function**:

```javascript
function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    const panels = document.querySelectorAll('.tab-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;

            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Update visible panel
            panels.forEach(p => p.classList.remove('active'));
            document.getElementById(`${targetTab}-panel`).classList.add('active');

            // Tab-specific actions
            if (targetTab === 'preview') {
                updatePreview();
            } else if (targetTab === 'logs') {
                // Refresh available logs when switching to logs tab
                loadAvailableLogs();
            }
        });
    });
}
```

---

## Testing Plan

### Test 1: First-Run Marker System

```bash
# Test marker creation
rm ~/.ape_setup_complete
./setup.sh
# Expected: Marker file created at end of setup

# Verify marker content
cat ~/.ape_setup_complete
# Expected: Valid JSON with timestamp, version, platform

# Test launcher with marker
./launch-project-ape.command
# Expected: Skips setup, goes directly to config/workflow

# Test reset script
./reset-setup.sh
# Expected: Removes marker, next launch runs setup again
```

### Test 2: Logs Tab

```bash
# Start dashboard
python3 dashboard/server.py

# Open browser
open http://localhost:8765/configure

# Test overall logs
1. Click "Logs" tab
2. Verify "Overall Logs" selected by default
3. Verify logs appear in viewer
4. Verify auto-scroll works

# Test client logs
1. Select a client from dropdown
2. Verify client-specific logs stream
3. Verify selector updates with available logs

# Test controls
1. Click "Pause" - verify logs stop streaming
2. Click "Resume" - verify logs resume
3. Click "Clear" - verify display clears
4. Click "Download" - verify file downloads

# Test real-time updates
1. Keep logs tab open
2. In another terminal: echo "TEST LOG MESSAGE" >> logs/test.log
3. Verify message appears in viewer (if watching that log)
```

---

## Success Criteria

### First-Run Marker
- [ ] setup.sh creates `~/.ape_setup_complete` on success
- [ ] Marker contains valid JSON metadata
- [ ] Launcher detects marker correctly
- [ ] Launcher skips setup when marker exists
- [ ] reset-setup.sh removes marker successfully

### Logs Tab
- [ ] New "Logs" tab appears in UI
- [ ] Dropdown shows all available logs
- [ ] Overall logs stream correctly
- [ ] Client logs stream correctly
- [ ] Auto-scroll works when at bottom
- [ ] Pause/Resume works correctly
- [ ] Clear logs works
- [ ] Download logs works
- [ ] Logs update in real-time
- [ ] Log styling (colors for errors/warnings) works

---

## Implementation Order

1. ✅ Create implementation plan (this document)
2. Implement first-run marker system
3. Implement logs backend endpoints
4. Implement logs frontend tab
5. Test marker system
6. Test logs tab
7. Iterate and fix any issues
8. Create final test suite
9. Update documentation

---

**Estimated Time**: 2-3 hours
**Priority**: High (completes Phase 3 polish)
**Risk Level**: Low (isolated changes, no breaking changes)
