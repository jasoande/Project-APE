/**
 * OAuth Wizard JavaScript
 * Handles 5-step OAuth setup wizard for Google Drive access
 */

// Wizard state
let currentWizardStep = 1;
let uploadedOAuthFile = null;
let oauthFlowComplete = false;

/**
 * Navigate to next wizard step
 */
function nextWizardStep() {
    if (currentWizardStep < 5) {
        // Hide current step
        document.querySelector(`.wizard-step[data-step="${currentWizardStep}"]`).classList.remove('active');

        // Increment step
        currentWizardStep++;

        // Show next step
        document.querySelector(`.wizard-step[data-step="${currentWizardStep}"]`).classList.add('active');

        // Update progress indicator
        updateWizardProgress();

        // Auto-run actions for certain steps
        if (currentWizardStep === 1) checkOAuthStatusWizard();
        if (currentWizardStep === 5) testDriveAccessWizard();
    }
}

/**
 * Navigate to previous wizard step
 */
function prevWizardStep() {
    if (currentWizardStep > 1) {
        // Hide current step
        document.querySelector(`.wizard-step[data-step="${currentWizardStep}"]`).classList.remove('active');

        // Decrement step
        currentWizardStep--;

        // Show previous step
        document.querySelector(`.wizard-step[data-step="${currentWizardStep}"]`).classList.add('active');

        // Update progress indicator
        updateWizardProgress();
    }
}

/**
 * Update wizard progress indicator
 */
function updateWizardProgress() {
    document.querySelectorAll('.wizard-progress .step').forEach((step, idx) => {
        if (idx + 1 <= currentWizardStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

/**
 * Check OAuth status (Step 1)
 */
async function checkOAuthStatusWizard() {
    try {
        const response = await fetch('/api/oauth-status');
        const data = await response.json();

        // Update status badges
        updateStatusBadgeWizard('creds-status-badge', data.credentials_exist);
        updateStatusBadgeWizard('token-status-badge', data.token_exist);
        updateStatusBadgeWizard('access-status-badge', data.authenticated);

        if (data.authenticated) {
            showMessage('success', '✅ OAuth already configured! You can skip this wizard or reconfigure.');
        }
    } catch (error) {
        console.error('Failed to check OAuth status:', error);
        showMessage('error', 'Failed to check OAuth status: ' + error.message);
    }
}

/**
 * Update status badge display
 */
function updateStatusBadgeWizard(elementId, status) {
    const badge = document.getElementById(elementId);
    if (!badge) return;

    badge.textContent = status ? '✅ Configured' : '❌ Not Configured';
    badge.className = status ? 'status-badge success' : 'status-badge error';
}

/**
 * Initialize file upload handlers (Step 3)
 */
function initOAuthFileUpload() {
    const uploadZone = document.getElementById('oauth-upload-zone');
    const fileInput = document.getElementById('oauth-file-input');

    if (!uploadZone || !fileInput) return;

    // Click to upload
    uploadZone.addEventListener('click', () => {
        if (!uploadZone.querySelector('.upload-success').style.display ||
            uploadZone.querySelector('.upload-success').style.display === 'none') {
            fileInput.click();
        }
    });

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
        await handleOAuthFileUpload(file);
    });

    // File input change
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        await handleOAuthFileUpload(file);
    });
}

/**
 * Handle OAuth credentials file upload
 */
async function handleOAuthFileUpload(file) {
    if (!file || !file.name.endsWith('.json')) {
        showMessage('error', 'Please upload a JSON file (client_secret_*.json)');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        showMessage('info', 'Uploading credentials...');

        const response = await fetch('/api/upload-oauth-credentials', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            // Show success state
            const uploadZone = document.getElementById('oauth-upload-zone');
            uploadZone.querySelector('.upload-placeholder').style.display = 'none';
            uploadZone.querySelector('.upload-success').style.display = 'block';
            document.getElementById('uploaded-filename').textContent = file.name;
            document.getElementById('upload-next-btn').disabled = false;

            uploadedOAuthFile = file;
            showMessage('success', '✅ ' + data.message);
        } else {
            showMessage('error', '❌ ' + (data.error || 'Failed to upload credentials'));
        }
    } catch (error) {
        showMessage('error', '❌ Upload failed: ' + error.message);
    }
}

/**
 * Start OAuth authentication flow (Step 4)
 */
async function startOAuthFlow() {
    const statusDiv = document.getElementById('auth-flow-status');
    const startBtn = document.getElementById('start-oauth-btn');

    startBtn.disabled = true;
    statusDiv.innerHTML = '<div class="status-message">🔄 Starting OAuth flow...</div>';

    try {
        // Use EventSource for SSE stream
        const eventSource = new EventSource('/api/start-oauth-flow');

        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);

            switch(data.status) {
                case 'starting':
                    statusDiv.innerHTML = '<div class="status-message">🔄 ' + data.message + '</div>';
                    break;
                case 'browser_opening':
                    statusDiv.innerHTML = '<div class="status-message">🌐 ' + data.message + '</div>';
                    break;
                case 'token_saving':
                    statusDiv.innerHTML = '<div class="status-message">💾 ' + data.message + '</div>';
                    break;
                case 'complete':
                    statusDiv.innerHTML = '<div class="status-message success">✅ ' + data.message + '</div>';
                    document.getElementById('auth-next-btn').disabled = false;
                    oauthFlowComplete = true;
                    eventSource.close();
                    showMessage('success', '✅ Authentication complete!');
                    break;
                case 'error':
                    statusDiv.innerHTML = `<div class="status-message error">❌ ${data.message}</div>`;
                    startBtn.disabled = false;
                    eventSource.close();
                    showMessage('error', '❌ ' + data.message);
                    break;
            }
        };

        eventSource.onerror = function(error) {
            console.error('OAuth flow error:', error);
            statusDiv.innerHTML = '<div class="status-message error">❌ OAuth flow failed. Please try again.</div>';
            startBtn.disabled = false;
            eventSource.close();
            showMessage('error', '❌ OAuth flow connection failed');
        };

    } catch (error) {
        statusDiv.innerHTML = `<div class="status-message error">❌ Failed to start OAuth flow: ${error.message}</div>`;
        startBtn.disabled = false;
        showMessage('error', '❌ ' + error.message);
    }
}

/**
 * Test Drive access (Step 5)
 */
async function testDriveAccessWizard() {
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
            document.getElementById('auth-email').textContent = 'Yes';
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
                    ${filesHtml || '<p style="color: #8b949e;">No files found (this is normal for empty Drive)</p>'}
                </div>
            `;

            document.getElementById('complete-btn').disabled = false;
            showMessage('success', '✅ Drive access verified successfully!');
        } else {
            resultsDiv.innerHTML = `
                <div class="status-message error">
                    ❌ Failed to access Drive: ${data.error}
                </div>
            `;
            showMessage('error', '❌ ' + data.error);
        }
    } catch (error) {
        statusDiv.style.display = 'none';
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = `
            <div class="status-message error">
                ❌ Test failed: ${error.message}
            </div>
        `;
        showMessage('error', '❌ Test failed: ' + error.message);
    }
}

/**
 * Complete OAuth setup
 */
function completeOAuthSetup() {
    showMessage('success', '✅ OAuth setup complete! You can now use Google Drive folders in your configuration.');

    // Navigate to clients tab
    const clientsTab = document.querySelector('[data-tab="clients"]');
    if (clientsTab) {
        clientsTab.click();
    }
}

/**
 * Initialize OAuth wizard when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the OAuth tab
    const oauthPanel = document.getElementById('oauth-setup-panel');
    if (oauthPanel) {
        initOAuthFileUpload();

        // Check status on page load
        checkOAuthStatusWizard();
    }
});
