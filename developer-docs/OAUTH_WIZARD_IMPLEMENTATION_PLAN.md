# OAuth Setup Wizard - Implementation Plan

**Goal:** Eliminate terminal dependency for Google Drive OAuth setup

**Current State:** Users must manually:
1. Visit GCP console
2. Create OAuth credentials
3. Download JSON file
4. Run `python3 setup-oauth-drive.py` in terminal

**Target State:** Complete OAuth setup via web UI only

---

## Design Overview

### Multi-Step Wizard Flow

```
┌─────────────────────────────────────────────────────────┐
│ Google Drive OAuth Setup Wizard                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Step 1: Check Prerequisites                            │
│  ├─ Check if OAuth already configured                   │
│  ├─ Check if drive_credentials.json exists              │
│  └─ Show status: ✅ Ready / ⚠️ Needs Setup             │
│                                                          │
│  Step 2: Create OAuth Credentials                       │
│  ├─ Instructions with screenshots                       │
│  ├─ Link to GCP console                                 │
│  ├─ Checklist to track progress                         │
│  └─ "Open GCP Console" button (new tab)                 │
│                                                          │
│  Step 3: Upload Credentials                             │
│  ├─ File upload dropzone                                │
│  ├─ Validate JSON format                                │
│  ├─ Extract client ID and verify                        │
│  └─ Save to ~/.project-ape/drive_credentials.json       │
│                                                          │
│  Step 4: Authenticate                                   │
│  ├─ Button: "Authenticate with Google Drive"            │
│  ├─ Backend triggers OAuth flow                         │
│  ├─ Opens browser window automatically                  │
│  ├─ User grants permissions                             │
│  └─ Callback saves token                                │
│                                                          │
│  Step 5: Verify Access                                  │
│  ├─ Test Drive API access                               │
│  ├─ Show list of accessible folders                     │
│  ├─ Status: ✅ Success / ❌ Failed                      │
│  └─ "Complete Setup" button                             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Tasks

### Backend API Endpoints (4 new endpoints)

#### 1. Check OAuth Status
```python
@app.route('/api/oauth-status', methods=['GET'])
def oauth_status():
    """
    Check if OAuth is already configured.
    
    Returns:
    {
        "credentials_exist": bool,
        "token_exist": bool,
        "authenticated": bool,
        "email": str | null,
        "scopes": list | null
    }
    """
```

#### 2. Upload Credentials
```python
@app.route('/api/upload-oauth-credentials', methods=['POST'])
def upload_oauth_credentials():
    """
    Accept client_secret_*.json file upload.
    
    Request: multipart/form-data with 'file' field
    
    Validates:
    - JSON format
    - Contains required OAuth fields
    - Client ID and secret present
    
    Saves to: ~/.project-ape/drive_credentials.json
    
    Returns:
    {
        "success": bool,
        "message": str,
        "client_id": str (partial, for display)
    }
    """
```

#### 3. Start OAuth Flow
```python
@app.route('/api/start-oauth-flow', methods=['POST'])
def start_oauth_flow():
    """
    Trigger OAuth authentication flow.
    
    Uses google_auth_oauthlib.flow.InstalledAppFlow to:
    1. Start local callback server
    2. Generate authorization URL
    3. Open browser automatically
    4. Wait for callback
    5. Save token to ~/.project-ape/drive_token.json
    
    Returns (SSE stream):
    - "starting" - Flow initiated
    - "url_generated" - Auth URL ready
    - "browser_opened" - Browser launched
    - "waiting" - Waiting for user to grant permissions
    - "callback_received" - User authorized
    - "token_saved" - Token persisted
    - "complete" - Success
    - "error" - Failure with details
    """
```

#### 4. Test Drive Access
```python
@app.route('/api/test-drive-access', methods=['GET'])
def test_drive_access():
    """
    Verify Drive API access with saved credentials.
    
    Tests:
    1. Load token from ~/.project-ape/drive_token.json
    2. Refresh if expired
    3. Call Drive API to list files (limit 10)
    4. Verify read permissions
    
    Returns:
    {
        "success": bool,
        "authenticated": bool,
        "email": str,
        "sample_files": list[dict],  // First 10 files
        "total_accessible": int,
        "error": str | null
    }
    """
```

### Frontend UI Components

#### 1. OAuth Setup Tab (configure.html)

Add new tab to existing tabs:
```html
<div class="tab" data-tab="oauth-setup">🔑 Google Drive Setup</div>
```

#### 2. Step-by-Step Wizard

```html
<div class="tab-content" id="oauth-setup-tab" style="display: none;">
    <div class="wizard-container">
        
        <!-- Progress Indicator -->
        <div class="wizard-progress">
            <div class="step active">1. Check</div>
            <div class="step">2. Create</div>
            <div class="step">3. Upload</div>
            <div class="step">4. Authenticate</div>
            <div class="step">5. Verify</div>
        </div>

        <!-- Step 1: Check Prerequisites -->
        <div class="wizard-step active" data-step="1">
            <h3>Step 1: Check Prerequisites</h3>
            <div id="oauth-status">
                <div class="status-item">
                    <span class="status-label">OAuth Credentials:</span>
                    <span id="creds-status" class="status-badge">Checking...</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Authentication Token:</span>
                    <span id="token-status" class="status-badge">Checking...</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Drive Access:</span>
                    <span id="access-status" class="status-badge">Checking...</span>
                </div>
            </div>
            <div class="wizard-actions">
                <button class="btn btn-primary" onclick="nextStep()">Next</button>
            </div>
        </div>

        <!-- Step 2: Create Credentials -->
        <div class="wizard-step" data-step="2">
            <h3>Step 2: Create OAuth Credentials</h3>
            <div class="instructions">
                <p>Follow these steps to create OAuth credentials in Google Cloud Console:</p>
                <ol>
                    <li>
                        <input type="checkbox" id="check-gcp-project">
                        <label for="check-gcp-project">
                            Create or select a GCP project
                            <a href="https://console.cloud.google.com/projectcreate" target="_blank">Open GCP Console →</a>
                        </label>
                    </li>
                    <li>
                        <input type="checkbox" id="check-enable-api">
                        <label for="check-enable-api">
                            Enable Google Drive API
                            <a href="https://console.cloud.google.com/apis/library/drive.googleapis.com" target="_blank">Enable API →</a>
                        </label>
                    </li>
                    <li>
                        <input type="checkbox" id="check-oauth-consent">
                        <label for="check-oauth-consent">
                            Configure OAuth consent screen (External, test users)
                            <a href="https://console.cloud.google.com/apis/credentials/consent" target="_blank">Configure →</a>
                        </label>
                    </li>
                    <li>
                        <input type="checkbox" id="check-create-creds">
                        <label for="check-create-creds">
                            Create OAuth Client ID (Application type: Desktop app)
                            <a href="https://console.cloud.google.com/apis/credentials/oauthclient" target="_blank">Create →</a>
                        </label>
                    </li>
                    <li>
                        <input type="checkbox" id="check-download">
                        <label for="check-download">
                            Download the JSON file (client_secret_*.json)
                        </label>
                    </li>
                </ol>
            </div>
            <div class="wizard-actions">
                <button class="btn btn-secondary" onclick="prevStep()">Back</button>
                <button class="btn btn-primary" onclick="nextStep()">Next</button>
            </div>
        </div>

        <!-- Step 3: Upload Credentials -->
        <div class="wizard-step" data-step="3">
            <h3>Step 3: Upload Credentials</h3>
            <div class="upload-zone" id="oauth-upload-zone">
                <div class="upload-placeholder">
                    <div class="upload-icon">📁</div>
                    <div class="upload-text">
                        Drag and drop client_secret_*.json here
                        <br>or click to browse
                    </div>
                    <input type="file" id="oauth-file-input" accept=".json" hidden>
                </div>
                <div class="upload-success" style="display: none;">
                    <div class="success-icon">✅</div>
                    <div class="success-text">
                        Credentials uploaded successfully!
                        <br>
                        <span id="uploaded-filename"></span>
                    </div>
                </div>
            </div>
            <div class="wizard-actions">
                <button class="btn btn-secondary" onclick="prevStep()">Back</button>
                <button class="btn btn-primary" id="upload-next-btn" disabled onclick="nextStep()">Next</button>
            </div>
        </div>

        <!-- Step 4: Authenticate -->
        <div class="wizard-step" data-step="4">
            <h3>Step 4: Authenticate with Google</h3>
            <div class="auth-container">
                <p>Click the button below to open a browser window and grant Project APE access to your Google Drive.</p>
                <div class="auth-status" id="auth-flow-status">
                    <div class="status-message">Ready to authenticate</div>
                </div>
                <button class="btn btn-primary btn-large" id="start-oauth-btn" onclick="startOAuthFlow()">
                    🔐 Authenticate with Google Drive
                </button>
            </div>
            <div class="wizard-actions">
                <button class="btn btn-secondary" onclick="prevStep()">Back</button>
                <button class="btn btn-primary" id="auth-next-btn" disabled onclick="nextStep()">Next</button>
            </div>
        </div>

        <!-- Step 5: Verify -->
        <div class="wizard-step" data-step="5">
            <h3>Step 5: Verify Drive Access</h3>
            <div class="verify-container">
                <div id="verify-status">
                    <div class="status-checking">
                        <div class="spinner"></div>
                        <div>Testing Drive API access...</div>
                    </div>
                </div>
                <div id="verify-results" style="display: none;">
                    <div class="result-item">
                        <span class="label">Authenticated as:</span>
                        <span id="auth-email" class="value"></span>
                    </div>
                    <div class="result-item">
                        <span class="label">Accessible files:</span>
                        <span id="file-count" class="value"></span>
                    </div>
                    <div id="sample-files"></div>
                </div>
            </div>
            <div class="wizard-actions">
                <button class="btn btn-secondary" onclick="prevStep()">Back</button>
                <button class="btn btn-success" id="complete-btn" onclick="completeSetup()">
                    ✅ Complete Setup
                </button>
            </div>
        </div>

    </div>
</div>
```

#### 3. JavaScript Wizard Logic

```javascript
// Wizard state management
let currentStep = 1;
let uploadedFile = null;
let oauthComplete = false;

// Step navigation
function nextStep() {
    if (currentStep < 5) {
        document.querySelector(`[data-step="${currentStep}"]`).classList.remove('active');
        currentStep++;
        document.querySelector(`[data-step="${currentStep}"]`).classList.add('active');
        updateProgress();
        
        // Auto-run actions for certain steps
        if (currentStep === 1) checkOAuthStatus();
        if (currentStep === 5) testDriveAccess();
    }
}

function prevStep() {
    if (currentStep > 1) {
        document.querySelector(`[data-step="${currentStep}"]`).classList.remove('active');
        currentStep--;
        document.querySelector(`[data-step="${currentStep}"]`).classList.add('active');
        updateProgress();
    }
}

function updateProgress() {
    document.querySelectorAll('.wizard-progress .step').forEach((step, idx) => {
        if (idx + 1 <= currentStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

// Step 1: Check OAuth status
async function checkOAuthStatus() {
    try {
        const response = await fetch('/api/oauth-status');
        const data = await response.json();
        
        updateStatusBadge('creds-status', data.credentials_exist);
        updateStatusBadge('token-status', data.token_exist);
        updateStatusBadge('access-status', data.authenticated);
        
        if (data.authenticated) {
            // Already configured, show success
            showAlert('success', 'OAuth already configured! You can skip this wizard.');
        }
    } catch (error) {
        console.error('Failed to check OAuth status:', error);
    }
}

function updateStatusBadge(elementId, status) {
    const badge = document.getElementById(elementId);
    badge.textContent = status ? '✅ Configured' : '❌ Not Configured';
    badge.className = status ? 'status-badge success' : 'status-badge error';
}

// Step 3: File upload
function initFileUpload() {
    const uploadZone = document.getElementById('oauth-upload-zone');
    const fileInput = document.getElementById('oauth-file-input');
    
    // Click to upload
    uploadZone.addEventListener('click', () => fileInput.click());
    
    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('drag-over');
    });
    
    uploadZone.addEventListener('drop', async (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
        const file = e.dataTransfer.files[0];
        await handleFileUpload(file);
    });
    
    // File input change
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        await handleFileUpload(file);
    });
}

async function handleFileUpload(file) {
    if (!file || !file.name.endsWith('.json')) {
        showAlert('error', 'Please upload a JSON file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload-oauth-credentials', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Show success
            document.querySelector('.upload-placeholder').style.display = 'none';
            document.querySelector('.upload-success').style.display = 'block';
            document.getElementById('uploaded-filename').textContent = file.name;
            document.getElementById('upload-next-btn').disabled = false;
            
            uploadedFile = file;
            showAlert('success', data.message);
        } else {
            showAlert('error', data.error || 'Failed to upload credentials');
        }
    } catch (error) {
        showAlert('error', 'Upload failed: ' + error.message);
    }
}

// Step 4: Start OAuth flow
async function startOAuthFlow() {
    const statusDiv = document.getElementById('auth-flow-status');
    const startBtn = document.getElementById('start-oauth-btn');
    
    startBtn.disabled = true;
    statusDiv.innerHTML = '<div class="status-message">Starting OAuth flow...</div>';
    
    try {
        const response = await fetch('/api/start-oauth-flow', {
            method: 'POST'
        });
        
        // Handle SSE stream
        const eventSource = new EventSource('/api/start-oauth-flow');
        
        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'starting':
                    statusDiv.innerHTML = '<div class="status-message">🔄 Initializing OAuth flow...</div>';
                    break;
                case 'url_generated':
                    statusDiv.innerHTML = '<div class="status-message">🌐 Opening browser for authentication...</div>';
                    break;
                case 'browser_opened':
                    statusDiv.innerHTML = '<div class="status-message">⏳ Waiting for you to grant permissions in the browser...</div>';
                    break;
                case 'callback_received':
                    statusDiv.innerHTML = '<div class="status-message">✅ Authorization received! Saving token...</div>';
                    break;
                case 'token_saved':
                    statusDiv.innerHTML = '<div class="status-message success">✅ Authentication successful!</div>';
                    document.getElementById('auth-next-btn').disabled = false;
                    oauthComplete = true;
                    eventSource.close();
                    break;
                case 'error':
                    statusDiv.innerHTML = `<div class="status-message error">❌ Error: ${data.message}</div>`;
                    startBtn.disabled = false;
                    eventSource.close();
                    break;
            }
        };
        
        eventSource.onerror = function(error) {
            console.error('OAuth flow error:', error);
            statusDiv.innerHTML = '<div class="status-message error">❌ OAuth flow failed. Please try again.</div>';
            startBtn.disabled = false;
            eventSource.close();
        };
        
    } catch (error) {
        statusDiv.innerHTML = `<div class="status-message error">❌ Failed to start OAuth flow: ${error.message}</div>`;
        startBtn.disabled = false;
    }
}

// Step 5: Test Drive access
async function testDriveAccess() {
    const statusDiv = document.getElementById('verify-status');
    const resultsDiv = document.getElementById('verify-results');
    
    statusDiv.style.display = 'block';
    resultsDiv.style.display = 'none';
    
    try {
        const response = await fetch('/api/test-drive-access');
        const data = await response.json();
        
        statusDiv.style.display = 'none';
        resultsDiv.style.display = 'block';
        
        if (data.success) {
            document.getElementById('auth-email').textContent = data.email;
            document.getElementById('file-count').textContent = data.total_accessible;
            
            // Show sample files
            const filesHtml = data.sample_files.map(file => `
                <div class="file-item">
                    <span class="file-icon">📄</span>
                    <span class="file-name">${file.name}</span>
                </div>
            `).join('');
            
            document.getElementById('sample-files').innerHTML = `
                <div class="sample-files">
                    <h4>Sample accessible files:</h4>
                    ${filesHtml}
                </div>
            `;
            
            document.getElementById('complete-btn').disabled = false;
        } else {
            resultsDiv.innerHTML = `
                <div class="error-message">
                    ❌ Failed to access Drive: ${data.error}
                </div>
            `;
        }
    } catch (error) {
        statusDiv.style.display = 'none';
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = `
            <div class="error-message">
                ❌ Test failed: ${error.message}
            </div>
        `;
    }
}

function completeSetup() {
    showAlert('success', 'OAuth setup complete! You can now use Google Drive folders in your configuration.');
    // Close wizard or navigate to clients tab
    document.querySelector('[data-tab="clients"]').click();
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initFileUpload();
    checkOAuthStatus();
});
```

---

## CSS Styling

```css
/* Wizard Container */
.wizard-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 30px;
}

/* Progress Indicator */
.wizard-progress {
    display: flex;
    justify-content: space-between;
    margin-bottom: 40px;
    position: relative;
}

.wizard-progress::before {
    content: '';
    position: absolute;
    top: 20px;
    left: 0;
    right: 0;
    height: 2px;
    background: rgba(255,255,255,0.1);
    z-index: 0;
}

.wizard-progress .step {
    background: #161b22;
    border: 2px solid rgba(255,255,255,0.1);
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.85rem;
    font-weight: 600;
    color: #8b949e;
    z-index: 1;
    position: relative;
}

.wizard-progress .step.active {
    border-color: #ee0000;
    color: #ee0000;
    background: rgba(238,0,0,0.1);
}

/* Wizard Steps */
.wizard-step {
    display: none;
    animation: fadeIn 0.3s;
}

.wizard-step.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.wizard-step h3 {
    font-size: 1.5rem;
    margin-bottom: 20px;
    color: #fff;
}

/* Instructions */
.instructions {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
}

.instructions ol {
    list-style: none;
    counter-reset: step-counter;
    padding: 0;
}

.instructions li {
    counter-increment: step-counter;
    margin-bottom: 15px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
}

.instructions li::before {
    content: counter(step-counter);
    background: #ee0000;
    color: #fff;
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    flex-shrink: 0;
}

.instructions input[type="checkbox"] {
    margin-right: 8px;
}

.instructions a {
    color: #58a6ff;
    text-decoration: none;
    margin-left: 8px;
}

.instructions a:hover {
    text-decoration: underline;
}

/* Upload Zone */
.upload-zone {
    border: 2px dashed rgba(255,255,255,0.3);
    border-radius: 12px;
    padding: 60px 40px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    margin-bottom: 20px;
}

.upload-zone:hover {
    border-color: #ee0000;
    background: rgba(238,0,0,0.05);
}

.upload-zone.drag-over {
    border-color: #ee0000;
    background: rgba(238,0,0,0.1);
}

.upload-icon {
    font-size: 3rem;
    margin-bottom: 15px;
}

.upload-text {
    color: #8b949e;
    font-size: 1rem;
    line-height: 1.6;
}

.upload-success .success-icon {
    font-size: 3rem;
    margin-bottom: 15px;
}

.upload-success .success-text {
    color: #3fb950;
    font-size: 1.1rem;
    font-weight: 600;
}

/* Status Items */
.status-item {
    display: flex;
    justify-content: space-between;
    padding: 12px 16px;
    background: rgba(255,255,255,0.03);
    border-radius: 6px;
    margin-bottom: 8px;
}

.status-badge {
    font-size: 0.85rem;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 12px;
}

.status-badge.success {
    background: rgba(63,185,80,0.2);
    color: #3fb950;
}

.status-badge.error {
    background: rgba(248,81,73,0.2);
    color: #f85149;
}

/* Auth Container */
.auth-container {
    text-align: center;
    padding: 40px 20px;
}

.auth-status {
    margin: 30px 0;
    min-height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.status-message {
    font-size: 1rem;
    color: #e6edf3;
    padding: 12px 24px;
    background: rgba(255,255,255,0.05);
    border-radius: 6px;
}

.status-message.success {
    color: #3fb950;
    background: rgba(63,185,80,0.1);
}

.status-message.error {
    color: #f85149;
    background: rgba(248,81,73,0.1);
}

.btn-large {
    font-size: 1.1rem;
    padding: 16px 32px;
}

/* Wizard Actions */
.wizard-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.1);
}

/* Verify Results */
.result-item {
    display: flex;
    justify-content: space-between;
    padding: 12px 16px;
    background: rgba(255,255,255,0.03);
    border-radius: 6px;
    margin-bottom: 8px;
}

.result-item .label {
    color: #8b949e;
    font-weight: 600;
}

.result-item .value {
    color: #e6edf3;
}

.sample-files {
    margin-top: 20px;
    padding: 16px;
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
}

.sample-files h4 {
    font-size: 0.9rem;
    color: #8b949e;
    margin-bottom: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.file-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: rgba(0,0,0,0.2);
    border-radius: 4px;
    margin-bottom: 4px;
}

.file-icon {
    font-size: 1.2rem;
}

.file-name {
    color: #e6edf3;
    font-size: 0.9rem;
}

/* Spinner */
.spinner {
    border: 3px solid rgba(255,255,255,0.1);
    border-top: 3px solid #ee0000;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 0 auto 15px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.status-checking {
    text-align: center;
    color: #8b949e;
}
```

---

## Testing Plan

### Unit Tests

1. **Backend Tests**
   - [ ] `/api/oauth-status` returns correct status
   - [ ] File upload validates JSON format
   - [ ] Invalid credentials rejected
   - [ ] OAuth flow completes successfully
   - [ ] Token saved to correct location
   - [ ] Drive access test works with valid token

2. **Frontend Tests**
   - [ ] Wizard navigation works
   - [ ] File upload accepts .json files
   - [ ] Drag and drop works
   - [ ] Progress indicator updates
   - [ ] Error messages display correctly
   - [ ] Success states show properly

### Integration Tests

1. **Complete Flow**
   - [ ] Start with no credentials
   - [ ] Complete all 5 steps
   - [ ] Verify Drive access works
   - [ ] Configuration can use Drive folders

2. **Edge Cases**
   - [ ] Already authenticated user sees success
   - [ ] Invalid credentials file shows error
   - [ ] OAuth canceled by user
   - [ ] Network failure during upload
   - [ ] Drive API returns error

### User Acceptance Tests

1. **New User**
   - [ ] Can complete setup without terminal
   - [ ] Instructions are clear
   - [ ] Links open correctly
   - [ ] File upload is intuitive
   - [ ] OAuth flow is smooth

2. **Existing User**
   - [ ] Can re-authenticate if needed
   - [ ] Can update credentials
   - [ ] Can verify access anytime

---

## Rollout Plan

### Phase 1: Backend Implementation (3 hours)
- Implement 4 API endpoints
- Add OAuth flow logic using google_auth_oauthlib
- Test with manual API calls

### Phase 2: Frontend Implementation (2 hours)
- Add OAuth setup tab to configure.html
- Implement wizard UI with 5 steps
- Add CSS styling

### Phase 3: Integration (1 hour)
- Wire up frontend to backend
- Test complete flow
- Handle error cases

### Phase 4: Testing (1 hour)
- Unit tests for all endpoints
- Integration test for full flow
- User acceptance testing

### Phase 5: Documentation (1 hour)
- Update README with new wizard
- Update QUICK_START to remove manual OAuth step
- Add screenshots to documentation
- Create troubleshooting guide

**Total Estimated Time: 8 hours**

---

## Success Criteria

- ✅ User can complete OAuth setup without opening terminal
- ✅ Clear visual feedback at each step
- ✅ Error messages guide user to resolution
- ✅ Works on Chrome, Safari, Firefox, Edge
- ✅ Mobile-responsive (bonus)
- ✅ Credentials saved to correct location
- ✅ Drive access verified automatically
- ✅ Documentation updated
- ✅ Zero terminal commands for OAuth setup

---

## Future Enhancements

1. **Visual Progress Bar** - Show percentage complete
2. **Screenshot Overlays** - Inline GCP console screenshots
3. **Video Tutorial** - Embedded walkthrough video
4. **Quick Mode** - Skip wizard if credentials already exist
5. **Troubleshooting Panel** - Common issues and solutions
6. **Multiple Accounts** - Support switching between Google accounts
7. **Scope Customization** - Choose which Drive permissions to grant

---

**Document Version:** 1.0  
**Last Updated:** 2026-06-25  
**Implementation Status:** Ready for development
