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

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();

        // Only show error if the API returned an explicit error
        if (data.success === false) {
            console.error('OAuth status check failed:', data.error);
            // Don't show scary error on fresh install - just log it
            updateStatusBadgeWizard('creds-status-badge', false);
            updateStatusBadgeWizard('token-status-badge', false);
            updateStatusBadgeWizard('access-status-badge', false);
            return;
        }

        // Check if Google OAuth packages are available
        if (data.google_packages_available === false) {
            showMessage('error', '⚠️ Google OAuth packages not available. Please restart dashboard using: python3 launch-project-ape.py');
            updateStatusBadgeWizard('creds-status-badge', false);
            updateStatusBadgeWizard('token-status-badge', false);
            updateStatusBadgeWizard('access-status-badge', false);
            return;
        }

        // Update status badges
        updateStatusBadgeWizard('creds-status-badge', data.credentials_exist);
        updateStatusBadgeWizard('token-status-badge', data.token_exist);
        updateStatusBadgeWizard('access-status-badge', data.authenticated);

        if (data.authenticated) {
            showMessage('success', '✅ OAuth already configured! You can skip this wizard or reconfigure.');
        }
    } catch (error) {
        // Don't show error banner on page load - just log to console
        // This is normal for fresh installations
        console.log('OAuth status check (expected on fresh install):', error.message);

        // Set all badges to "Not Configured" state
        updateStatusBadgeWizard('creds-status-badge', false);
        updateStatusBadgeWizard('token-status-badge', false);
        updateStatusBadgeWizard('access-status-badge', false);
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
 * Handle OAuth credentials file upload with progress tracking
 */
async function handleOAuthFileUpload(file) {
    if (!file || !file.name.endsWith('.json')) {
        showMessage('error', 'Please upload a JSON file (client_secret_*.json)');
        return;
    }

    const progressDiv = document.getElementById('oauth-upload-progress');
    const progressFill = document.getElementById('oauth-progress-fill');
    const progressPercent = document.getElementById('oauth-progress-percent');
    const progressStatus = document.getElementById('oauth-progress-status');
    const uploadZone = document.getElementById('oauth-upload-zone');

    // Reset progress bar
    progressFill.style.width = '0%';
    progressFill.className = 'progress-fill';
    progressPercent.textContent = '0%';
    progressStatus.textContent = 'Uploading...';
    progressDiv.classList.add('visible');

    const formData = new FormData();
    formData.append('file', file);

    let uploadStartTime = Date.now();
    let uploadedBytes = 0;

    try {
        // Use XMLHttpRequest for progress tracking
        const xhr = new XMLHttpRequest();

        // Upload progress handler
        xhr.upload.addEventListener('loadstart', () => {
            uploadStartTime = Date.now();
        });

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                progressFill.style.width = percent + '%';
                progressPercent.textContent = percent + '%';

                if (percent < 100) {
                    const elapsed = (Date.now() - uploadStartTime) / 1000; // seconds
                    const speed = elapsed > 0 ? e.loaded / elapsed : 0;

                    const sizeText = formatFileSize(e.loaded) + ' / ' + formatFileSize(e.total);
                    const speedText = speed > 0 ? formatFileSize(speed) + '/s' : '';

                    progressStatus.textContent = speedText ? `${sizeText} (${speedText})` : sizeText;
                } else {
                    progressStatus.textContent = 'Processing...';
                }
            }
        });

        // Success handler
        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                try {
                    const data = JSON.parse(xhr.responseText);

                    if (data.success) {
                        // Update to success state
                        progressFill.classList.add('success');
                        progressFill.style.width = '100%';
                        progressPercent.textContent = '100%';
                        progressStatus.textContent = 'Upload complete!';

                        // Show success state in upload zone
                        uploadZone.querySelector('.upload-placeholder').style.display = 'none';
                        uploadZone.querySelector('.upload-success').style.display = 'block';
                        document.getElementById('uploaded-filename').textContent = file.name;
                        document.getElementById('upload-next-btn').disabled = false;

                        uploadedOAuthFile = file;
                        showMessage('success', '✅ ' + data.message);

                        // Hide progress bar after 2 seconds
                        setTimeout(() => {
                            progressDiv.classList.remove('visible');
                        }, 2000);
                    } else {
                        throw new Error(data.error || 'Failed to upload credentials');
                    }
                } catch (parseError) {
                    throw new Error('Invalid response from server');
                }
            } else {
                throw new Error(`Upload failed with status ${xhr.status}`);
            }
        });

        // Error handler
        xhr.addEventListener('error', () => {
            progressFill.classList.add('error');
            progressStatus.textContent = 'Network error';
            showMessage('error', '❌ Upload failed: Network error');
        });

        // Abort handler
        xhr.addEventListener('abort', () => {
            progressFill.classList.add('error');
            progressStatus.textContent = 'Upload cancelled';
            showMessage('error', '❌ Upload cancelled');
        });

        // Send the request
        xhr.open('POST', '/api/upload-oauth-credentials');
        xhr.send(formData);

    } catch (error) {
        progressFill.classList.add('error');
        progressStatus.textContent = 'Upload failed';
        showMessage('error', '❌ Upload failed: ' + error.message);
    }
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * Start OAuth authentication flow (Step 4)
 */
async function startOAuthFlow() {
    const statusDiv = document.getElementById('auth-flow-status');
    const startBtn = document.getElementById('start-oauth-btn');

    // Mark that user intentionally started the flow
    startBtn.setAttribute('data-flow-started', 'true');

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

            // Only show error if user actually tried to authenticate (not on page load)
            if (startBtn.getAttribute('data-flow-started') === 'true') {
                showMessage('error', '❌ OAuth flow failed. Check that credentials are uploaded (Step 3).');
            }
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
