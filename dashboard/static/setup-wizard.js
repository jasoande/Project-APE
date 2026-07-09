/**
 * Project APE - Environment Setup Wizard
 * Interactive web UI for automated environment setup
 */

// State management
const state = {
    currentStep: 0,
    totalSteps: 7,
    completedSteps: 0,
    systemInfo: null,
    setupInProgress: false,
    autoMode: true
};

// CSRF token handling
function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

// API helper
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (method === 'POST' && data) {
        options.body = JSON.stringify(data);
        options.headers['X-CSRFToken'] = getCSRFToken();
    }

    const response = await fetch(endpoint, options);
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Request failed');
    }
    return response.json();
}

// UI Updates
function updateProgress() {
    const percentage = (state.completedSteps / state.totalSteps) * 100;
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const overallStatus = document.getElementById('overall-status');

    progressBar.style.width = `${percentage}%`;
    progressText.textContent = `${state.completedSteps} of ${state.totalSteps} steps completed`;

    if (state.completedSteps === state.totalSteps) {
        overallStatus.textContent = 'Setup Complete! ✓';
    } else if (state.setupInProgress) {
        overallStatus.textContent = 'Setup in progress...';
    } else {
        overallStatus.textContent = 'Ready to begin';
    }
}

function setStepStatus(stepNum, status, details = null) {
    const step = document.getElementById(`step-${stepNum}`);
    const number = document.getElementById(`step-${stepNum}-number`);
    const statusEl = document.getElementById(`step-${stepNum}-status`);
    const body = document.getElementById(`step-${stepNum}-body`);
    const detailsEl = document.getElementById(`step-${stepNum}-details`);

    // Remove all status classes
    step.classList.remove('active', 'completed', 'error');
    number.classList.remove('active', 'completed', 'error');
    statusEl.classList.remove('pending', 'running', 'completed', 'error', 'skipped');

    // Apply new status
    if (status === 'running') {
        step.classList.add('active');
        number.classList.add('active');
        statusEl.classList.add('running');
        statusEl.innerHTML = '<span class="spinner"></span> Running...';
        body.classList.add('visible');
        state.currentStep = stepNum;
    } else if (status === 'completed') {
        step.classList.add('completed');
        number.classList.add('completed');
        number.textContent = '✓';
        statusEl.classList.add('completed');
        statusEl.textContent = 'Completed';
        body.classList.add('visible');
        state.completedSteps++;
        updateProgress();
    } else if (status === 'error') {
        step.classList.add('error');
        number.classList.add('error');
        number.textContent = '✗';
        statusEl.classList.add('error');
        statusEl.textContent = 'Error';
        body.classList.add('visible');
    } else if (status === 'skipped') {
        number.textContent = '−';
        statusEl.classList.add('skipped');
        statusEl.textContent = 'Skipped';
        state.completedSteps++;
        updateProgress();
    } else if (status === 'pending') {
        statusEl.classList.add('pending');
        statusEl.textContent = 'Pending';
        number.textContent = stepNum;
    }

    // Update details if provided
    if (details) {
        detailsEl.innerHTML = `<pre>${details}</pre>`;
    }
}

function showAlert(type, message) {
    const container = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} visible`;
    alert.textContent = message;
    container.appendChild(alert);

    // Auto-remove after 5 seconds for non-error alerts
    if (type !== 'error') {
        setTimeout(() => {
            alert.classList.remove('visible');
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    }
}

function addStepAction(stepNum, buttonText, buttonClass, onClick) {
    const actionsEl = document.getElementById(`step-${stepNum}-actions`);
    const button = document.createElement('button');
    button.className = `btn ${buttonClass}`;
    button.textContent = buttonText;
    button.onclick = onClick;
    actionsEl.appendChild(button);
}

function clearStepActions(stepNum) {
    const actionsEl = document.getElementById(`step-${stepNum}-actions`);
    actionsEl.innerHTML = '';
}

// Setup Steps
async function runStep1_SystemDetection() {
    setStepStatus(1, 'running');

    try {
        const result = await apiCall('/api/setup/system-info');

        let details = `Operating System: ${result.os}\n`;
        details += `Architecture: ${result.arch}\n`;
        details += `Platform: ${result.platform}`;

        setStepStatus(1, 'completed', details);
        state.systemInfo = result;

        return true;
    } catch (error) {
        setStepStatus(1, 'error', `Error: ${error.message}`);
        showAlert('error', `System detection failed: ${error.message}`);
        return false;
    }
}

async function runStep2_Homebrew() {
    // Skip on non-macOS
    if (state.systemInfo && state.systemInfo.os !== 'macOS') {
        setStepStatus(2, 'skipped', 'Homebrew is only required on macOS');
        return true;
    }

    setStepStatus(2, 'running');

    try {
        const result = await apiCall('/api/setup/check-homebrew');

        if (result.installed) {
            const details = `Homebrew version: ${result.version}\nLocation: ${result.path}`;
            setStepStatus(2, 'completed', details);
            return true;
        } else {
            const details = 'Homebrew is not installed.\n\nClick "Install Homebrew" to begin installation.\nThis may take 5-10 minutes and will require your password.';
            setStepStatus(2, 'pending', details);

            clearStepActions(2);
            addStepAction(2, 'Install Homebrew', 'btn-primary', async () => {
                await installHomebrew();
            });
            addStepAction(2, 'Skip (Manual Install)', 'btn-secondary', () => {
                setStepStatus(2, 'skipped', 'Skipped - install manually later');
                continueSetup();
            });

            return false; // Pause here for user action
        }
    } catch (error) {
        setStepStatus(2, 'error', `Error: ${error.message}`);
        showAlert('error', `Homebrew check failed: ${error.message}`);
        return false;
    }
}

async function installHomebrew() {
    setStepStatus(2, 'running', 'Installing Homebrew...\n\nThis may take several minutes. Please do not close this window.');

    try {
        const result = await apiCall('/api/setup/install-homebrew', 'POST');

        if (result.success) {
            const details = `Homebrew installed successfully!\n\nVersion: ${result.version}\nLocation: ${result.path}`;
            setStepStatus(2, 'completed', details);
            showAlert('success', 'Homebrew installed successfully!');
            continueSetup();
        } else {
            throw new Error(result.error || 'Installation failed');
        }
    } catch (error) {
        setStepStatus(2, 'error', `Installation failed: ${error.message}\n\nPlease install manually:\n/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`);
        showAlert('error', `Homebrew installation failed: ${error.message}`);
    }
}

async function runStep3_Podman() {
    setStepStatus(3, 'running');

    try {
        const result = await apiCall('/api/setup/check-podman');

        if (result.installed) {
            let details = `Podman version: ${result.version}`;

            // Check Podman machine status on macOS
            if (state.systemInfo.os === 'macOS') {
                if (result.machine_running) {
                    details += '\nPodman machine: Running ✓';
                } else {
                    details += '\nPodman machine: Starting...';
                }
            }

            setStepStatus(3, 'completed', details);
            return true;
        } else {
            const details = 'Podman is not installed.\n\nClick "Install Podman" to begin installation.';
            setStepStatus(3, 'pending', details);

            clearStepActions(3);
            addStepAction(3, 'Install Podman', 'btn-primary', async () => {
                await installPodman();
            });
            addStepAction(3, 'Skip', 'btn-secondary', () => {
                setStepStatus(3, 'skipped', 'Skipped - install manually later');
                continueSetup();
            });

            return false;
        }
    } catch (error) {
        setStepStatus(3, 'error', `Error: ${error.message}`);
        showAlert('error', `Podman check failed: ${error.message}`);
        return false;
    }
}

async function installPodman() {
    setStepStatus(3, 'running', 'Installing Podman...\n\nThis may take a few minutes.');

    try {
        const result = await apiCall('/api/setup/install-podman', 'POST');

        if (result.success) {
            const details = `Podman installed successfully!\n\nVersion: ${result.version}`;
            setStepStatus(3, 'completed', details);
            showAlert('success', 'Podman installed successfully!');
            continueSetup();
        } else {
            throw new Error(result.error || 'Installation failed');
        }
    } catch (error) {
        setStepStatus(3, 'error', `Installation failed: ${error.message}`);
        showAlert('error', `Podman installation failed: ${error.message}`);
    }
}

async function runStep4_GCloud() {
    setStepStatus(4, 'running');

    try {
        const result = await apiCall('/api/setup/check-gcloud');

        if (result.installed) {
            let details = `Google Cloud SDK version: ${result.version}`;
            if (result.authenticated) {
                details += `\nAuthenticated as: ${result.account}`;
            }
            setStepStatus(4, 'completed', details);
            return true;
        } else {
            const details = 'Google Cloud SDK is not installed.\n\nClick "Install gcloud" to begin installation.';
            setStepStatus(4, 'pending', details);

            clearStepActions(4);
            addStepAction(4, 'Install gcloud', 'btn-primary', async () => {
                await installGCloud();
            });
            addStepAction(4, 'Skip', 'btn-secondary', () => {
                setStepStatus(4, 'skipped', 'Skipped - install manually later');
                continueSetup();
            });

            return false;
        }
    } catch (error) {
        setStepStatus(4, 'error', `Error: ${error.message}`);
        showAlert('error', `Google Cloud SDK check failed: ${error.message}`);
        return false;
    }
}

async function installGCloud() {
    setStepStatus(4, 'running', 'Installing Google Cloud SDK...\n\nThis may take a few minutes.');

    try {
        const result = await apiCall('/api/setup/install-gcloud', 'POST');

        if (result.success) {
            const details = `Google Cloud SDK installed successfully!\n\nVersion: ${result.version}`;
            setStepStatus(4, 'completed', details);
            showAlert('success', 'Google Cloud SDK installed successfully!');
            continueSetup();
        } else {
            throw new Error(result.error || 'Installation failed');
        }
    } catch (error) {
        setStepStatus(4, 'error', `Installation failed: ${error.message}`);
        showAlert('error', `Google Cloud SDK installation failed: ${error.message}`);
    }
}

async function runStep5_Python() {
    setStepStatus(5, 'running');

    try {
        const result = await apiCall('/api/setup/check-python');

        if (result.compatible) {
            const details = `Python version: ${result.version}\nLocation: ${result.path}`;
            setStepStatus(5, 'completed', details);
            return true;
        } else {
            const details = result.installed
                ? `Current Python: ${result.version}\n\nPython 3.10+ is required. Click "Install Python 3.14" to upgrade.`
                : 'Python 3 is not installed.\n\nClick "Install Python 3.14" to begin installation.';

            setStepStatus(5, 'pending', details);

            clearStepActions(5);
            addStepAction(5, 'Install Python 3.14', 'btn-primary', async () => {
                await installPython();
            });
            addStepAction(5, 'Skip', 'btn-secondary', () => {
                setStepStatus(5, 'skipped', 'Skipped - install manually later');
                continueSetup();
            });

            return false;
        }
    } catch (error) {
        setStepStatus(5, 'error', `Error: ${error.message}`);
        showAlert('error', `Python check failed: ${error.message}`);
        return false;
    }
}

async function installPython() {
    setStepStatus(5, 'running', 'Installing Python 3.14...\n\nThis may take a few minutes.');

    try {
        const result = await apiCall('/api/setup/install-python', 'POST');

        if (result.success) {
            const details = `Python 3.14 installed successfully!\n\nVersion: ${result.version}\nLocation: ${result.path}`;
            setStepStatus(5, 'completed', details);
            showAlert('success', 'Python 3.14 installed successfully!');
            continueSetup();
        } else {
            throw new Error(result.error || 'Installation failed');
        }
    } catch (error) {
        setStepStatus(5, 'error', `Installation failed: ${error.message}`);
        showAlert('error', `Python installation failed: ${error.message}`);
    }
}

async function runStep6_VirtualEnv() {
    setStepStatus(6, 'running');

    try {
        const result = await apiCall('/api/setup/check-venv');

        if (result.exists && result.compatible) {
            const details = `Virtual environment: ${result.path}\nPython version: ${result.version}`;
            setStepStatus(6, 'completed', details);
            return true;
        } else {
            const details = result.exists
                ? `Existing venv is outdated (Python ${result.version}).\n\nClick "Create Virtual Environment" to recreate with Python 3.10+.`
                : 'Virtual environment does not exist.\n\nClick "Create Virtual Environment" to create at ~/.project-ape-venv';

            setStepStatus(6, 'pending', details);

            clearStepActions(6);
            addStepAction(6, 'Create Virtual Environment', 'btn-primary', async () => {
                await createVirtualEnv();
            });

            return false;
        }
    } catch (error) {
        setStepStatus(6, 'error', `Error: ${error.message}`);
        showAlert('error', `Virtual environment check failed: ${error.message}`);
        return false;
    }
}

async function createVirtualEnv() {
    setStepStatus(6, 'running', 'Creating virtual environment...\n\nThis may take a minute.');

    try {
        const result = await apiCall('/api/setup/create-venv', 'POST');

        if (result.success) {
            const details = `Virtual environment created successfully!\n\nLocation: ${result.path}\nPython version: ${result.version}`;
            setStepStatus(6, 'completed', details);
            showAlert('success', 'Virtual environment created successfully!');
            continueSetup();
        } else {
            throw new Error(result.error || 'Creation failed');
        }
    } catch (error) {
        setStepStatus(6, 'error', `Creation failed: ${error.message}`);
        showAlert('error', `Virtual environment creation failed: ${error.message}`);
    }
}

async function runStep7_NotebookLM() {
    setStepStatus(7, 'running');

    try {
        const result = await apiCall('/api/setup/check-notebooklm');

        if (result.installed) {
            const details = `NotebookLM CLI: ${result.version}\nFlask: ${result.flask_version}\nAll dependencies: Installed ✓`;
            setStepStatus(7, 'completed', details);
            return true;
        } else {
            const details = 'NotebookLM CLI and dependencies not installed.\n\nClick "Install Dependencies" to install NotebookLM CLI, Flask, and all required packages.';
            setStepStatus(7, 'pending', details);

            clearStepActions(7);
            addStepAction(7, 'Install Dependencies', 'btn-primary', async () => {
                await installNotebookLM();
            });

            return false;
        }
    } catch (error) {
        setStepStatus(7, 'error', `Error: ${error.message}`);
        showAlert('error', `NotebookLM CLI check failed: ${error.message}`);
        return false;
    }
}

async function installNotebookLM() {
    setStepStatus(7, 'running', 'Installing NotebookLM CLI and dependencies...\n\nThis may take 3-5 minutes.\n\nInstalling:\n• notebooklm-py[browser]\n• Flask\n• Google API libraries\n• Playwright (Chromium browser)');

    try {
        const result = await apiCall('/api/setup/install-notebooklm', 'POST');

        if (result.success) {
            const details = `All dependencies installed successfully!\n\nNotebookLM CLI: ${result.version}\nFlask: ${result.flask_version}\nPlaywright: Installed ✓`;
            setStepStatus(7, 'completed', details);
            showAlert('success', 'NotebookLM CLI and dependencies installed successfully!');
            continueSetup();
        } else {
            throw new Error(result.error || 'Installation failed');
        }
    } catch (error) {
        setStepStatus(7, 'error', `Installation failed: ${error.message}`);
        showAlert('error', `NotebookLM CLI installation failed: ${error.message}`);
    }
}

// Setup orchestration
async function continueSetup() {
    if (!state.setupInProgress) return;

    const stepFunctions = [
        null, // 0-indexed, step 1 is index 0
        runStep1_SystemDetection,
        runStep2_Homebrew,
        runStep3_Podman,
        runStep4_GCloud,
        runStep5_Python,
        runStep6_VirtualEnv,
        runStep7_NotebookLM
    ];

    // Find next pending step
    for (let i = state.currentStep + 1; i <= state.totalSteps; i++) {
        const stepFunc = stepFunctions[i];
        if (stepFunc) {
            const success = await stepFunc();
            if (!success && state.autoMode) {
                // Step needs user intervention or failed
                state.setupInProgress = false;
                return;
            }
        }
    }

    // All steps complete
    if (state.completedSteps === state.totalSteps) {
        state.setupInProgress = false;
        showSetupComplete();
    }
}

function showSetupComplete() {
    showAlert('success', '🎉 Environment setup complete! You can now configure and run Project APE workflows.');

    const btnStart = document.getElementById('btn-start');
    const btnRestart = document.getElementById('btn-restart');

    btnStart.textContent = 'Go to Configuration';
    btnStart.onclick = () => {
        window.location.href = '/configure';
    };
    btnRestart.style.display = 'inline-flex';
}

async function startSetup() {
    state.setupInProgress = true;
    state.currentStep = 0;
    state.completedSteps = 0;

    const btnStart = document.getElementById('btn-start');
    btnStart.disabled = true;
    btnStart.innerHTML = '<span class="spinner"></span> Setup in Progress...';

    updateProgress();
    await continueSetup();

    btnStart.disabled = false;
}

function restartSetup() {
    // Reset all steps
    for (let i = 1; i <= state.totalSteps; i++) {
        setStepStatus(i, 'pending');
        const number = document.getElementById(`step-${i}-number`);
        number.textContent = i;
        const body = document.getElementById(`step-${i}-body`);
        body.classList.remove('visible');
        clearStepActions(i);
    }

    state.currentStep = 0;
    state.completedSteps = 0;
    state.setupInProgress = false;

    updateProgress();

    const btnStart = document.getElementById('btn-start');
    const btnRestart = document.getElementById('btn-restart');

    btnStart.textContent = 'Start Setup';
    btnStart.onclick = startSetup;
    btnRestart.style.display = 'none';

    // Clear alerts
    document.getElementById('alert-container').innerHTML = '';
}

// Event listeners
document.getElementById('btn-start').addEventListener('click', startSetup);
document.getElementById('btn-restart').addEventListener('click', restartSetup);
document.getElementById('btn-skip').addEventListener('click', () => {
    window.location.href = '/configure';
});

// Auto-start if requested
const urlParams = new URLSearchParams(window.location.search);
if (urlParams.get('auto') === 'true') {
    setTimeout(startSetup, 500);
}
