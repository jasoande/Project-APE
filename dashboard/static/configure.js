/**
 * Project APE Configuration Tool - Phase 2
 * =========================================
 * Tabbed interface with load/save, global settings, CSV import, and live preview
 */

// Global state
let clients = [];
let globalSettings = {
    persona: 'Red Hat solutions architect',
    default_mode: 'fast',
    DASHBOARD_PORT: 8765,
    DASHBOARD_REFRESH_INTERVAL: 2,
    TIMINGS: {
        notebook_creation_delay: 3.0,
        source_add_delay: [2.0, 4.0],
        source_processing_delay: 30.0,
        ask_prompt_delay: [8.0, 12.0],
        chat_prompt_delay: [5.0, 8.0],
        deduplication_delay: 20.0,
        mindmap_delay: 15.0,
        source_import_wait: 10.0
    },
    DEEP_TIMINGS: {
        notebook_creation_delay: 3.0,
        source_add_delay: [2.0, 4.0],
        source_processing_delay: 45.0,
        ask_prompt_delay: [15.0, 25.0],
        chat_prompt_delay: [10.0, 15.0],
        deduplication_delay: 25.0,
        mindmap_delay: 20.0,
        source_import_wait: 30.0
    },
    DRIVE_CONFIG: {
        enabled: true,
        cache_enabled: true,
        cache_ttl_hours: 24,
        export_google_docs: true,
        recursive: false,
        max_file_size_mb: 50
    }
};

let previewDebounceTimer = null;
let importedClientsPreview = [];

// ========================================================================
// Tab Navigation
// ========================================================================

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

// ========================================================================
// Client Management
// ========================================================================

function sanitizeClientId(name) {
    let id = name.toLowerCase();
    id = id.replace(/[\s-]+/g, '_');
    id = id.replace(/[^a-z0-9_]/g, '');
    if (id && /^\d/.test(id)) {
        id = '_' + id;
    }
    return id.substring(0, 64);
}

function addClient(client = null) {
    const clientId = `client_${Date.now()}`;
    const newClient = client || {
        id: clientId,
        name: '',
        folder: '',
        industry: '',
        subsegments: ''
    };
    clients.push(newClient);
    renderClients();
    debouncedUpdatePreview();
}

function removeClient(clientId) {
    clients = clients.filter(c => c.id !== clientId);
    renderClients();
    debouncedUpdatePreview();
}

function updateClient(clientId, field, value) {
    const client = clients.find(c => c.id === clientId);
    if (client) {
        client[field] = value;

        // Auto-generate client ID from name
        if (field === 'name' && value) {
            const sanitized = sanitizeClientId(value);
            if (sanitized) {
                client.id_generated = sanitized;
            }
        }

        debouncedUpdatePreview();
    }
}

function renderClients() {
    const grid = document.getElementById('clientsGrid');
    grid.innerHTML = '';

    if (clients.length === 0) {
        grid.innerHTML = '<p class="form-help" style="text-align: center; padding: 40px;">No clients configured. Click "Add Client" to get started.</p>';
        return;
    }

    clients.forEach((client, index) => {
        const card = document.createElement('div');
        card.className = 'client-card';
        card.innerHTML = `
            <div class="client-card-header">
                <h3 class="client-card-title">Client ${index + 1}${client.name ? ': ' + client.name : ''}</h3>
                <button type="button" class="client-card-remove" onclick="removeClient('${client.id}')" title="Remove Client">×</button>
            </div>

            <div class="form-group">
                <label class="form-label">
                    Client Name<span class="required">*</span>
                </label>
                <input
                    type="text"
                    class="form-input"
                    id="${client.id}_name"
                    value="${client.name}"
                    placeholder="e.g., Acme Corp, Sample Industries"
                    oninput="updateClient('${client.id}', 'name', this.value)"
                />
                ${client.id_generated ? `<div class="form-help">Client ID: ${client.id_generated}</div>` : ''}
            </div>

            <div class="form-group">
                <label class="form-label">
                    Google Drive Folder URL or Local Path<span class="required">*</span>
                </label>
                <input
                    type="text"
                    class="form-input"
                    id="${client.id}_folder"
                    value="${client.folder}"
                    placeholder="https://drive.google.com/drive/folders/ABC123 or /path/to/folder"
                    oninput="updateClient('${client.id}', 'folder', this.value)"
                />
                <div class="form-help">Paste the full Google Drive folder URL or local folder path</div>
            </div>

            <div class="form-group">
                <label class="form-label">Industry</label>
                <input
                    type="text"
                    class="form-input"
                    id="${client.id}_industry"
                    value="${client.industry}"
                    placeholder="e.g., pharmaceuticals and life sciences"
                    oninput="updateClient('${client.id}', 'industry', this.value)"
                />
                <div class="form-help">Optional - can be left empty for AI auto-detection</div>
            </div>

            <div class="form-group">
                <label class="form-label">Subsegments</label>
                <input
                    type="text"
                    class="form-input"
                    id="${client.id}_subsegments"
                    value="${client.subsegments}"
                    placeholder="e.g., drug discovery, clinical trials, manufacturing"
                    oninput="updateClient('${client.id}', 'subsegments', this.value)"
                />
                <div class="form-help">Optional - comma-separated research areas</div>
            </div>
        `;
        grid.appendChild(card);
    });
}

// ========================================================================
// Global Settings Management
// ========================================================================

function initGlobalSettings() {
    // Populate form fields
    document.getElementById('persona').value = globalSettings.persona;
    document.getElementById('defaultMode').value = globalSettings.default_mode;
    document.getElementById('dashboardPort').value = globalSettings.DASHBOARD_PORT;

    // Add change listeners
    document.getElementById('persona').addEventListener('input', (e) => {
        globalSettings.persona = e.target.value;
        debouncedUpdatePreview();
    });
    document.getElementById('defaultMode').addEventListener('change', (e) => {
        globalSettings.default_mode = e.target.value;
        debouncedUpdatePreview();
    });
    document.getElementById('dashboardPort').addEventListener('input', (e) => {
        globalSettings.DASHBOARD_PORT = parseInt(e.target.value);
        debouncedUpdatePreview();
    });

    // Populate expandable sections
    populateTimingsSection('timings-content', 'TIMINGS');
    populateTimingsSection('deep-timings-content', 'DEEP_TIMINGS');
    populateDriveConfigSection();

    // Add expandable toggle handlers
    document.querySelectorAll('.expandable-header').forEach(header => {
        header.addEventListener('click', () => {
            header.parentElement.classList.toggle('open');
        });
    });
}

function populateTimingsSection(contentId, settingsKey) {
    const content = document.getElementById(contentId);
    const timings = globalSettings[settingsKey];

    const fields = [
        { key: 'notebook_creation_delay', label: 'Notebook Creation Delay', unit: 'seconds' },
        { key: 'source_add_delay', label: 'Source Add Delay', unit: 'seconds (min, max)' },
        { key: 'source_processing_delay', label: 'Source Processing Delay', unit: 'seconds' },
        { key: 'ask_prompt_delay', label: 'Ask Prompt Delay', unit: 'seconds (min, max)' },
        { key: 'chat_prompt_delay', label: 'Chat Prompt Delay', unit: 'seconds (min, max)' },
        { key: 'deduplication_delay', label: 'Deduplication Delay', unit: 'seconds' },
        { key: 'mindmap_delay', label: 'Mindmap Delay', unit: 'seconds' },
        { key: 'source_import_wait', label: 'Source Import Wait', unit: 'seconds' }
    ];

    let html = '<div class="form-row">';
    fields.forEach(field => {
        const value = Array.isArray(timings[field.key])
            ? timings[field.key].join(', ')
            : timings[field.key];

        html += `
            <div class="form-group">
                <label class="form-label">${field.label}</label>
                <input type="text" class="form-input"
                       id="${settingsKey}_${field.key}"
                       value="${value}"
                       placeholder="${field.unit}">
            </div>
        `;
    });
    html += '</div>';
    content.innerHTML = html;

    // Add change listeners
    fields.forEach(field => {
        const input = document.getElementById(`${settingsKey}_${field.key}`);
        input.addEventListener('input', (e) => {
            const value = e.target.value;
            // Check if it's a tuple (contains comma)
            if (value.includes(',')) {
                const parts = value.split(',').map(v => parseFloat(v.trim()));
                globalSettings[settingsKey][field.key] = parts;
            } else {
                globalSettings[settingsKey][field.key] = parseFloat(value);
            }
            debouncedUpdatePreview();
        });
    });
}

function populateDriveConfigSection() {
    const content = document.getElementById('drive-config-content');
    const config = globalSettings.DRIVE_CONFIG;

    content.innerHTML = `
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Enable Cache</label>
                <select class="form-select" id="drive_cache_enabled">
                    <option value="true" ${config.cache_enabled ? 'selected' : ''}>Enabled</option>
                    <option value="false" ${!config.cache_enabled ? 'selected' : ''}>Disabled</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Cache TTL (hours)</label>
                <input type="number" class="form-input" id="drive_cache_ttl_hours"
                       value="${config.cache_ttl_hours}" min="1" max="168">
            </div>
        </div>
        <div class="form-row">
            <div class="form-group">
                <label class="form-label">Export Google Docs</label>
                <select class="form-select" id="drive_export_google_docs">
                    <option value="true" ${config.export_google_docs ? 'selected' : ''}>Yes</option>
                    <option value="false" ${!config.export_google_docs ? 'selected' : ''}>No</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Recursive Scan</label>
                <select class="form-select" id="drive_recursive">
                    <option value="true" ${config.recursive ? 'selected' : ''}>Yes</option>
                    <option value="false" ${!config.recursive ? 'selected' : ''}>No</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Max File Size (MB)</label>
                <input type="number" class="form-input" id="drive_max_file_size_mb"
                       value="${config.max_file_size_mb}" min="1" max="500">
            </div>
        </div>
    `;

    // Add change listeners
    document.getElementById('drive_cache_enabled').addEventListener('change', (e) => {
        globalSettings.DRIVE_CONFIG.cache_enabled = e.target.value === 'true';
        debouncedUpdatePreview();
    });
    document.getElementById('drive_cache_ttl_hours').addEventListener('input', (e) => {
        globalSettings.DRIVE_CONFIG.cache_ttl_hours = parseInt(e.target.value);
        debouncedUpdatePreview();
    });
    document.getElementById('drive_export_google_docs').addEventListener('change', (e) => {
        globalSettings.DRIVE_CONFIG.export_google_docs = e.target.value === 'true';
        debouncedUpdatePreview();
    });
    document.getElementById('drive_recursive').addEventListener('change', (e) => {
        globalSettings.DRIVE_CONFIG.recursive = e.target.value === 'true';
        debouncedUpdatePreview();
    });
    document.getElementById('drive_max_file_size_mb').addEventListener('input', (e) => {
        globalSettings.DRIVE_CONFIG.max_file_size_mb = parseInt(e.target.value);
        debouncedUpdatePreview();
    });
}

// ========================================================================
// Load/Save Configuration
// ========================================================================

async function loadConfiguration() {
    setLoading(true, 'Loading configuration...');

    try {
        const response = await fetch('/api/load-config');
        const data = await response.json();

        if (data.success) {
            // Load clients
            clients = data.config.clients || [];

            // Load global settings
            if (data.config.settings) {
                Object.assign(globalSettings, data.config.settings);
            }

            // Update UI
            renderClients();
            initGlobalSettings();
            updatePreview();

            showMessage('success', `✅ Configuration loaded successfully! Loaded ${clients.length} client(s).`);
        } else {
            showMessage('error', 'Failed to load configuration: ' + data.error);
        }
    } catch (error) {
        showMessage('error', `Failed to load configuration: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

async function saveConfiguration() {
    // Validate clients
    if (clients.length === 0) {
        showMessage('error', 'Please add at least one client before saving.');
        return;
    }

    const errors = validateAllClients();
    if (errors.length > 0) {
        showMessage('error', 'Validation errors:\n' + errors.join('\n'));
        return;
    }

    setLoading(true, 'Saving configuration...');

    try {
        // Prepare client data
        const clientsData = clients.map(c => ({
            id: c.id_generated || sanitizeClientId(c.name),
            name: c.name.trim(),
            folder: c.folder.trim(),
            industry: c.industry.trim(),
            subsegments: c.subsegments.trim()
        }));

        const response = await fetch('/api/save-config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                clients: clientsData,
                settings: globalSettings
            })
        });

        const data = await response.json();

        if (data.success) {
            showMessage('success', `✅ Configuration saved successfully!${data.backup_created ? '\nBackup created: ' + data.backup_created : ''}`);
            return true;
        } else {
            showMessage('error', 'Failed to save configuration: ' + (data.error || 'Unknown error'));
            return false;
        }
    } catch (error) {
        showMessage('error', `Failed to save configuration: ${error.message}`);
        return false;
    } finally {
        setLoading(false);
    }
}

async function saveAndLaunch() {
    // Validate clients
    if (clients.length === 0) {
        showMessage('error', 'Please add at least one client before saving.');
        return;
    }

    const errors = validateAllClients();
    if (errors.length > 0) {
        showMessage('error', 'Validation errors:\n' + errors.join('\n'));
        return;
    }

    setLoading(true, 'Saving configuration and launching workflow...');

    try {
        // Step 1: Save configuration
        const clientsData = clients.map(c => ({
            id: c.id_generated || sanitizeClientId(c.name),
            name: c.name.trim(),
            folder: c.folder.trim(),
            industry: c.industry.trim(),
            subsegments: c.subsegments.trim()
        }));

        const saveResponse = await fetch('/api/save-config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                clients: clientsData,
                settings: globalSettings
            })
        });

        const saveData = await saveResponse.json();

        if (!saveData.success) {
            showMessage('error', 'Failed to save configuration: ' + (saveData.error || 'Unknown error'));
            setLoading(false);
            return;
        }

        // Step 2: Redirect to launch page
        showMessage('success', '✅ Configuration saved! Launching workflow...');

        // Give user a moment to see the success message
        setTimeout(() => {
            window.location.href = '/launch';
        }, 1000);

    } catch (error) {
        showMessage('error', `Failed to save and launch: ${error.message}`);
        setLoading(false);
    }
}

async function downloadConfiguration() {
    const errors = validateAllClients();
    if (errors.length > 0) {
        showMessage('error', 'Validation errors:\n' + errors.join('\n'));
        return;
    }

    setLoading(true, 'Generating configuration...');

    try {
        const clientsData = clients.map(c => ({
            id: c.id_generated || sanitizeClientId(c.name),
            name: c.name.trim(),
            folder: c.folder.trim(),
            industry: c.industry.trim(),
            subsegments: c.subsegments.trim()
        }));

        const response = await fetch('/api/generate-config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                clients: clientsData,
                settings: globalSettings
            })
        });

        const data = await response.json();

        if (data.success) {
            downloadFile(data.content, data.filename);
            showMessage('success', `✅ Configuration generated successfully! File downloaded as ${data.filename}.`);
        } else {
            showMessage('error', 'Generation failed: ' + (data.errors ? data.errors.join('\n') : data.error));
        }
    } catch (error) {
        showMessage('error', `Failed to generate configuration: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

// ========================================================================
// CSV Import/Export
// ========================================================================

function initCsvImport() {
    const fileInput = document.getElementById('csvFile');
    const importBtn = document.getElementById('importCsvBtn');

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            importBtn.disabled = false;
        } else {
            importBtn.disabled = true;
        }
    });

    importBtn.addEventListener('click', importCsv);
    document.getElementById('confirmImportBtn').addEventListener('click', confirmImport);
    document.getElementById('cancelImportBtn').addEventListener('click', cancelImport);
}

async function importCsv() {
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];

    if (!file) {
        showMessage('error', 'Please select a CSV file first.');
        return;
    }

    setLoading(true, 'Importing CSV...');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/import-csv', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            importedClientsPreview = data.clients;
            showImportPreview(data);
        } else {
            showMessage('error', 'Failed to import CSV: ' + data.error);
        }
    } catch (error) {
        showMessage('error', `Failed to import CSV: ${error.message}`);
    } finally {
        setLoading(false);
    }
}

function showImportPreview(data) {
    const preview = document.getElementById('importPreview');
    const content = document.getElementById('importPreviewContent');

    let html = `<p class="form-help">Found ${data.imported} valid client(s)`;
    if (data.failed > 0) {
        html += ` and ${data.failed} error(s)`;
    }
    html += '</p>';

    if (data.errors && data.errors.length > 0) {
        html += '<div class="message message-error visible" style="margin: 20px 0;">';
        html += '<strong>Errors:</strong><ul>';
        data.errors.forEach(err => {
            html += `<li>${err}</li>`;
        });
        html += '</ul></div>';
    }

    if (data.clients && data.clients.length > 0) {
        html += '<table style="width: 100%; margin-top: 20px; border-collapse: collapse;">';
        html += '<thead><tr style="background: rgba(255,255,255,0.05);"><th style="padding: 12px; text-align: left;">Name</th><th style="padding: 12px; text-align: left;">Folder</th><th style="padding: 12px; text-align: left;">Industry</th></tr></thead>';
        html += '<tbody>';
        data.clients.forEach(client => {
            html += `<tr style="border-top: 1px solid rgba(255,255,255,0.1);">
                <td style="padding: 12px;">${client.name}</td>
                <td style="padding: 12px; font-size: 0.85rem; color: #8b949e;">${client.folder.substring(0, 50)}...</td>
                <td style="padding: 12px;">${client.industry || '<em>auto-detect</em>'}</td>
            </tr>`;
        });
        html += '</tbody></table>';
    }

    content.innerHTML = html;
    preview.style.display = 'block';
}

function confirmImport() {
    importedClientsPreview.forEach(client => {
        addClient(client);
    });
    showMessage('success', `✅ Imported ${importedClientsPreview.length} client(s) successfully!`);
    cancelImport();
}

function cancelImport() {
    document.getElementById('importPreview').style.display = 'none';
    document.getElementById('csvFile').value = '';
    document.getElementById('importCsvBtn').disabled = true;
    importedClientsPreview = [];
}

function exportCsv() {
    if (clients.length === 0) {
        showMessage('error', 'No clients to export.');
        return;
    }

    let csv = 'name,folder,industry,subsegments\n';
    clients.forEach(client => {
        const name = client.name.replace(/"/g, '""');
        const folder = client.folder.replace(/"/g, '""');
        const industry = client.industry.replace(/"/g, '""');
        const subsegments = client.subsegments.replace(/"/g, '""');
        csv += `"${name}","${folder}","${industry}","${subsegments}"\n`;
    });

    downloadFile(csv, 'clients.csv');
    showMessage('success', '✅ Exported clients to CSV!');
}

function exportJson() {
    if (clients.length === 0) {
        showMessage('error', 'No clients to export.');
        return;
    }

    const exportData = {
        clients: clients,
        settings: globalSettings
    };

    downloadFile(JSON.stringify(exportData, null, 2), 'config.json');
    showMessage('success', '✅ Exported configuration to JSON!');
}

// ========================================================================
// Live Preview
// ========================================================================

function debouncedUpdatePreview() {
    clearTimeout(previewDebounceTimer);
    previewDebounceTimer = setTimeout(updatePreview, 500);
}

async function updatePreview() {
    const previewContent = document.getElementById('previewContent');

    if (clients.length === 0) {
        previewContent.textContent = '# No clients configured yet.\n# Add clients in the Clients tab to see preview.';
        return;
    }

    try {
        const clientsData = clients.map(c => ({
            id: c.id_generated || sanitizeClientId(c.name),
            name: c.name.trim() || 'Unnamed Client',
            folder: c.folder.trim() || '/path/to/folder',
            industry: c.industry.trim(),
            subsegments: c.subsegments.trim()
        }));

        const response = await fetch('/api/generate-config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                clients: clientsData,
                settings: globalSettings
            })
        });

        const data = await response.json();

        if (data.success) {
            previewContent.textContent = data.content;
        } else {
            previewContent.textContent = `# Error generating preview:\n# ${data.error || 'Unknown error'}`;
        }
    } catch (error) {
        previewContent.textContent = `# Error generating preview:\n# ${error.message}`;
    }
}

function copyPreview() {
    const previewContent = document.getElementById('previewContent');
    const text = previewContent.textContent;

    navigator.clipboard.writeText(text).then(() => {
        showMessage('success', '✅ Copied to clipboard!');
    }).catch(err => {
        showMessage('error', `Failed to copy: ${err.message}`);
    });
}

// ========================================================================
// Validation
// ========================================================================

function validateAllClients() {
    const errors = [];

    if (clients.length === 0) {
        errors.push('At least one client is required');
        return errors;
    }

    clients.forEach((client, index) => {
        if (!client.name || !client.name.trim()) {
            errors.push(`Client ${index + 1}: Name is required`);
        }
        if (!client.folder || !client.folder.trim()) {
            errors.push(`Client ${index + 1}: Folder is required`);
        }
    });

    // Check for duplicate client IDs
    const clientIds = clients.map(c => c.id_generated || sanitizeClientId(c.name));
    const duplicates = clientIds.filter((id, index) => clientIds.indexOf(id) !== index);
    if (duplicates.length > 0) {
        errors.push(`Duplicate client IDs: ${duplicates.join(', ')}`);
    }

    return errors;
}

// ========================================================================
// UI Helpers
// ========================================================================

function showMessage(type, message) {
    const messageEl = document.getElementById(`${type}Message`);
    const allMessages = ['successMessage', 'errorMessage', 'infoMessage'];

    // Hide all messages
    allMessages.forEach(id => {
        document.getElementById(id).classList.remove('visible');
    });

    // Show the message
    messageEl.textContent = message;
    messageEl.classList.add('visible');

    // Auto-hide success/info after 5 seconds
    if (type !== 'error') {
        setTimeout(() => {
            messageEl.classList.remove('visible');
        }, 5000);
    }
}

function setLoading(isLoading, message = 'Processing...') {
    const loading = document.getElementById('loading');
    if (isLoading) {
        loading.querySelector('span').textContent = message;
        loading.classList.add('visible');
    } else {
        loading.classList.remove('visible');
    }
}

function downloadFile(content, filename) {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

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
            logViewer.classList.remove('paused');
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
            const currentValue = selector.value;
            selector.innerHTML = '';

            data.logs.forEach(log => {
                const option = document.createElement('option');
                option.value = log.token;
                option.textContent = log.label;
                selector.appendChild(option);
            });

            // Restore selection if it still exists
            if (currentValue && Array.from(selector.options).some(opt => opt.value === currentValue)) {
                selector.value = currentValue;
            }
        }
    } catch (error) {
        console.error('Failed to load available logs:', error);
        showMessage('error', 'Failed to load available logs: ' + error.message);
    }
}

function switchLogSource(logToken) {
    // Close existing stream
    if (logsEventSource) {
        logsEventSource.close();
    }

    // Clear log content
    document.getElementById('logContent').innerHTML = '';

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
        appendLogLine('─── Log stream disconnected ───', 'error');
    };
}

function appendLogLine(line, type = null) {
    const logContent = document.getElementById('logContent');
    const logViewer = document.getElementById('logViewer');

    // Create line element
    const lineSpan = document.createElement('span');

    // Determine line type if not specified
    if (!type) {
        if (line.includes('ERROR') || line.includes('FAILED') || line.includes('✗')) {
            type = 'error';
        } else if (line.includes('WARNING') || line.includes('WARN') || line.includes('⚠')) {
            type = 'warning';
        } else if (line.includes('SUCCESS') || line.includes('✅') || line.includes('COMPLETE')) {
            type = 'success';
        } else if (line.includes('INFO') || line.includes('ℹ️')) {
            type = 'info';
        }
    }

    // Apply styling
    if (type) {
        lineSpan.className = `log-line-${type}`;
    }

    lineSpan.textContent = line;
    logContent.appendChild(lineSpan);
    logContent.appendChild(document.createTextNode('\n'));

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
        logViewer.classList.remove('auto-scroll');
    } else {
        btn.textContent = '⏸️ Pause';
        btn.classList.remove('btn-success');
        btn.classList.add('btn-secondary');
        logViewer.classList.remove('paused');
        if (logsAutoScroll) {
            logViewer.classList.add('auto-scroll');
        }
    }
}

function clearLogs() {
    if (confirm('Clear current log display?\n\n(This does not delete log files)')) {
        document.getElementById('logContent').innerHTML = '';
        showMessage('info', '🗑️ Log display cleared');
    }
}

function downloadLogs() {
    const logContent = document.getElementById('logContent');
    const logSelector = document.getElementById('logSelector');
    const selectedLog = logSelector.options[logSelector.selectedIndex].text;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('.')[0];
    const filename = `${selectedLog.replace(/[^a-z0-9]/gi, '_')}_${timestamp}.log`;

    downloadFile(logContent.textContent, filename);
    showMessage('success', `✅ Logs downloaded as ${filename}`);
}

// ========================================================================
// Event Listeners
// ========================================================================

window.addEventListener('DOMContentLoaded', () => {
    // Initialize tabs
    initTabs();

    // Initialize settings
    initGlobalSettings();

    // Initialize CSV import
    initCsvImport();

    // Initialize logs tab
    initLogsTab();

    // Add first client by default
    if (clients.length === 0) {
        addClient();
    } else {
        renderClients();
    }

    // Event listeners for main actions
    document.getElementById('loadConfigBtn').addEventListener('click', loadConfiguration);
    document.getElementById('saveConfigBtn').addEventListener('click', saveConfiguration);
    document.getElementById('saveAndLaunchBtn').addEventListener('click', saveAndLaunch);
    document.getElementById('saveAndLaunchPreviewBtn').addEventListener('click', saveAndLaunch);
    document.getElementById('downloadConfigBtn').addEventListener('click', downloadConfiguration);
    document.getElementById('addClientBtn').addEventListener('click', () => addClient());
    document.getElementById('copyPreviewBtn').addEventListener('click', copyPreview);
    document.getElementById('exportCsvBtn').addEventListener('click', exportCsv);
    document.getElementById('exportJsonBtn').addEventListener('click', exportJson);

    // Initial preview
    updatePreview();
});
