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
    // Initialize drag-and-drop zone
    initCSVDropZone();

    // Initialize import button
    const importBtn = document.getElementById('btn-import-csv');
    if (importBtn) {
        importBtn.addEventListener('click', importCsv);
    }

    // Initialize preview buttons
    document.getElementById('confirmImportBtn').addEventListener('click', confirmImport);
    document.getElementById('cancelImportBtn').addEventListener('click', cancelImport);
}

// Initialize CSV drag-and-drop
function initCSVDropZone() {
    const dropZone = document.getElementById('csv-drop-zone');
    const fileInput = document.getElementById('csv-file-input');

    if (!dropZone || !fileInput) return;

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    // Highlight drop zone on drag over
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        }, false);
    });

    // Handle dropped files
    dropZone.addEventListener('drop', handleCSVDrop, false);

    // Handle click to browse
    dropZone.addEventListener('click', (e) => {
        // Don't trigger if clicking the browse button itself
        if (e.target.classList.contains('btn-browse')) return;
        fileInput.click();
    });

    // Handle file input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleCSVFile(e.target.files[0]);
        }
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

function handleCSVDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;

    if (files.length === 0) return;

    const file = files[0];

    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
        showMessage('error', 'Please upload a CSV file (.csv)');
        return;
    }

    handleCSVFile(file);
}

function handleCSVFile(file) {
    // Validate file
    const validation = validateCSVFile(file);
    if (!validation.valid) {
        showMessage('error', 'File validation failed:\n' + validation.errors.join('\n'));
        return;
    }

    // Display selected file
    document.getElementById('csv-drop-zone').style.display = 'none';
    document.getElementById('csv-file-selected').style.display = 'flex';
    document.getElementById('csv-file-name').textContent = file.name;
    document.getElementById('csv-file-size').textContent = formatFileSize(file.size);

    // Store file for later upload
    window.selectedCSVFile = file;

    // Enable import button
    const importBtn = document.getElementById('btn-import-csv');
    if (importBtn) {
        importBtn.disabled = false;
    }
}

function removeCSVFile() {
    document.getElementById('csv-drop-zone').style.display = 'block';
    document.getElementById('csv-file-selected').style.display = 'none';
    document.getElementById('csv-file-input').value = '';
    window.selectedCSVFile = null;
    const importBtn = document.getElementById('btn-import-csv');
    if (importBtn) {
        importBtn.disabled = true;
    }
}

function validateCSVFile(file) {
    const errors = [];

    // Check file extension
    if (!file.name.toLowerCase().endsWith('.csv')) {
        errors.push('File must be a CSV (.csv)');
    }

    // Check file size
    if (file.size === 0) {
        errors.push('File is empty');
    }

    if (file.size > 10 * 1024 * 1024) {
        errors.push('File too large (max 10MB)');
    }

    return {
        valid: errors.length === 0,
        errors: errors
    };
}

async function importCsv() {
    // Use the file stored by drag-drop handler
    const file = window.selectedCSVFile;

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
            showMessage('success', `✅ CSV parsed successfully! Found ${data.imported} client(s).`);
        } else {
            showMessage('error', 'Failed to import CSV: ' + data.error);
        }
    } catch (error) {
        showMessage('error', `Failed to import CSV: ${error.message}`);
    } finally {
        setLoading(false);
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
// Setup Environment Button
// ========================================================================

let setupEventSource = null;
let setupRunning = false;

function runSetupEnvironment() {
    if (setupRunning) {
        showMessage('warning', '⚠️ Setup is already running');
        return;
    }

    // Confirm with user
    const confirmMsg = 'Run environment setup?\n\n' +
                      'This will:\n' +
                      '• Install Podman (container runtime)\n' +
                      '• Install Google Cloud SDK\n' +
                      '• Install Python 3.14+\n' +
                      '• Create virtual environment\n' +
                      '• Install NotebookLM CLI\n\n' +
                      'This may take 2-5 minutes.';

    if (!confirm(confirmMsg)) {
        return;
    }

    // Update UI state
    setupRunning = true;
    const setupBtn = document.getElementById('setupEnvBtn');
    const setupPanel = document.getElementById('setupOutputPanel');
    const setupOutput = document.getElementById('setupOutput');
    const setupStatus = document.getElementById('setupStatus');

    // Show panel and reset state
    setupPanel.style.display = 'block';
    setupOutput.textContent = '';
    setupStatus.style.display = 'none';

    // Update button state
    setupBtn.disabled = true;
    setupBtn.innerHTML = '<div class="spinner" style="width: 16px; height: 16px; margin-right: 8px;"></div> Running Setup...';

    // Show initial message
    showMessage('info', '🔧 Starting environment setup...');

    // Connect to SSE endpoint
    setupEventSource = new EventSource('/api/run-setup');

    setupEventSource.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);

            // Append output
            if (data.message) {
                const timestamp = new Date().toLocaleTimeString();
                const prefix = `[${timestamp}] `;

                // Add line with appropriate styling
                const line = document.createElement('div');
                line.textContent = prefix + data.message;

                // Color code based on type
                if (data.type === 'success') {
                    line.style.color = '#00d084';
                } else if (data.type === 'error') {
                    line.style.color = '#ff6b6b';
                } else if (data.type === 'warning') {
                    line.style.color = '#ffb900';
                } else if (data.type === 'info') {
                    line.style.color = '#93c5fd';
                }

                setupOutput.appendChild(line);

                // Auto-scroll
                setupOutput.parentElement.scrollTop = setupOutput.parentElement.scrollHeight;
            }

            // Handle completion
            if (data.type === 'complete') {
                setupEventSource.close();
                setupRunning = false;

                // Update button
                setupBtn.disabled = false;
                setupBtn.innerHTML = '🔧 Setup Environment';

                // Show final status
                setupStatus.style.display = 'block';
                if (data.success) {
                    setupStatus.style.background = 'rgba(34,197,94,0.2)';
                    setupStatus.style.border = '1px solid #22c55e';
                    setupStatus.style.color = '#86efac';
                    setupStatus.textContent = '✅ Environment setup completed successfully!';
                    showMessage('success', '✅ Environment setup complete!');
                } else {
                    setupStatus.style.background = 'rgba(220,38,38,0.2)';
                    setupStatus.style.border = '1px solid #dc2626';
                    setupStatus.style.color = '#fca5a5';
                    setupStatus.textContent = '❌ Setup failed. See logs above for details.';
                    showMessage('error', '❌ Setup failed. Check output above.');
                }
            }
        } catch (err) {
            console.error('Error parsing setup output:', err);
        }
    };

    setupEventSource.onerror = function(error) {
        console.error('Setup stream error:', error);
        setupEventSource.close();
        setupRunning = false;

        // Update button
        setupBtn.disabled = false;
        setupBtn.innerHTML = '🔧 Setup Environment';

        // Show error
        setupStatus.style.display = 'block';
        setupStatus.style.background = 'rgba(220,38,38,0.2)';
        setupStatus.style.border = '1px solid #dc2626';
        setupStatus.style.color = '#fca5a5';
        setupStatus.textContent = '❌ Connection error. Check server logs.';
        showMessage('error', '❌ Setup failed due to connection error');
    };
}

function clearSetupOutput() {
    document.getElementById('setupOutput').textContent = '';
    document.getElementById('setupStatus').style.display = 'none';
    showMessage('info', '🗑️ Setup output cleared');
}

// ========================================================================
// NotebookLM Authentication
// ========================================================================

let authCheckInterval = null;
let lastAuthCheck = null;

async function checkAuthStatus() {
    try {
        const response = await fetch('/api/check-auth-status');
        const data = await response.json();

        if (data.success) {
            updateAuthUI(data.authenticated, data.profile, data.checked_at);
            lastAuthCheck = Date.now();
        } else {
            console.error('Auth check failed:', data.error);
            updateAuthUI(false, 'default', Date.now() / 1000);
        }
    } catch (error) {
        console.error('Failed to check auth status:', error);
        updateAuthUI(false, 'default', Date.now() / 1000);
    }
}

function updateAuthUI(authenticated, profile, checkedAt) {
    const badge = document.getElementById('authStatusBadge');
    const profileEl = document.getElementById('authProfile');
    const lastCheckedEl = document.getElementById('authLastChecked');
    const logoutBtn = document.getElementById('logoutNotebookLMBtn');

    // Update badge
    if (authenticated) {
        badge.style.background = 'rgba(34,197,94,0.1)';
        badge.style.borderColor = '#22c55e';
        badge.innerHTML = `
            <span style="font-size: 1.2rem;">✅</span>
            <span style="font-weight: 600; color: #86efac;">Authenticated</span>
        `;
        logoutBtn.style.display = 'inline-flex';
    } else {
        badge.style.background = 'rgba(220,38,38,0.1)';
        badge.style.borderColor = '#dc2626';
        badge.innerHTML = `
            <span style="font-size: 1.2rem;">❌</span>
            <span style="font-weight: 600; color: #fca5a5;">Not Authenticated</span>
        `;
        logoutBtn.style.display = 'none';
    }

    // Update profile
    profileEl.textContent = profile || 'default';

    // Update last checked time
    const now = Date.now();
    const elapsed = Math.floor((now - (checkedAt * 1000)) / 1000);
    let timeStr;
    if (elapsed < 5) {
        timeStr = 'Just now';
    } else if (elapsed < 60) {
        timeStr = `${elapsed} seconds ago`;
    } else if (elapsed < 3600) {
        timeStr = `${Math.floor(elapsed / 60)} minutes ago`;
    } else {
        timeStr = new Date(checkedAt * 1000).toLocaleTimeString();
    }
    lastCheckedEl.textContent = timeStr;
}

async function loginNotebookLM() {
    const loginBtn = document.getElementById('loginNotebookLMBtn');
    const instructionsPanel = document.getElementById('loginInstructions');
    const instructionsContent = document.getElementById('loginInstructionsContent');

    loginBtn.disabled = true;
    loginBtn.textContent = '⏳ Initiating login...';

    try {
        const response = await fetch('/api/notebooklm-login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            showMessage('info', '🔐 ' + data.message);

            // Show instructions
            if (data.instructions && data.instructions.length > 0) {
                instructionsContent.textContent = data.instructions.join('\n');
                instructionsPanel.style.display = 'block';
            }

            // Start polling for auth status every 5 seconds
            if (authCheckInterval) {
                clearInterval(authCheckInterval);
            }
            authCheckInterval = setInterval(checkAuthStatus, 5000);

            // Check immediately after a delay
            setTimeout(checkAuthStatus, 2000);

        } else {
            showMessage('error', 'Login failed: ' + data.error);

            // Show fallback instructions
            if (data.fallback_instructions && data.fallback_instructions.length > 0) {
                instructionsContent.textContent = data.fallback_instructions.join('\n');
                instructionsPanel.style.display = 'block';
            }
        }
    } catch (error) {
        showMessage('error', `Failed to initiate login: ${error.message}`);
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = '🔐 Login to NotebookLM';
    }
}

async function logoutNotebookLM() {
    if (!confirm('Are you sure you want to logout from NotebookLM?\n\nYou will need to re-authenticate before running workflows.')) {
        return;
    }

    const logoutBtn = document.getElementById('logoutNotebookLMBtn');
    logoutBtn.disabled = true;
    logoutBtn.textContent = '⏳ Logging out...';

    try {
        const response = await fetch('/api/notebooklm-logout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            showMessage('success', '✅ ' + data.message);
            await checkAuthStatus();

            // Hide instructions panel
            document.getElementById('loginInstructions').style.display = 'none';
        } else {
            showMessage('error', 'Logout failed: ' + data.error);
        }
    } catch (error) {
        showMessage('error', `Failed to logout: ${error.message}`);
    } finally {
        logoutBtn.disabled = false;
        logoutBtn.textContent = '🚪 Logout';
    }
}

function initAuthStatusPolling() {
    // Check auth status on page load
    checkAuthStatus();

    // Poll every 30 seconds
    if (authCheckInterval) {
        clearInterval(authCheckInterval);
    }
    authCheckInterval = setInterval(checkAuthStatus, 30000);

    // Update "last checked" display every 5 seconds
    setInterval(() => {
        if (lastAuthCheck) {
            const lastCheckedEl = document.getElementById('authLastChecked');
            const elapsed = Math.floor((Date.now() - lastAuthCheck) / 1000);
            let timeStr;
            if (elapsed < 5) {
                timeStr = 'Just now';
            } else if (elapsed < 60) {
                timeStr = `${elapsed} seconds ago`;
            } else if (elapsed < 3600) {
                timeStr = `${Math.floor(elapsed / 60)} minutes ago`;
            } else {
                const date = new Date(lastAuthCheck);
                timeStr = date.toLocaleTimeString();
            }
            lastCheckedEl.textContent = timeStr;
        }
    }, 5000);
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

    // Setup environment button
    document.getElementById('setupEnvBtn').addEventListener('click', runSetupEnvironment);
    document.getElementById('clearSetupOutputBtn').addEventListener('click', clearSetupOutput);

    // NotebookLM authentication buttons
    document.getElementById('loginNotebookLMBtn').addEventListener('click', loginNotebookLM);
    document.getElementById('refreshAuthStatusBtn').addEventListener('click', checkAuthStatus);
    document.getElementById('logoutNotebookLMBtn').addEventListener('click', logoutNotebookLM);

    // Initialize auth status polling
    initAuthStatusPolling();

    // Drive sources buttons
    document.getElementById('refreshSourcesBtn').addEventListener('click', showRefreshOptionsModal);
    document.getElementById('viewCacheStatsBtn').addEventListener('click', showCacheStats);
    document.getElementById('clearCacheBtn').addEventListener('click', clearCache);

    // Modal close buttons
    document.getElementById('closeCacheStatsBtn').addEventListener('click', () => {
        document.getElementById('cacheStatsModal').style.display = 'none';
    });
    document.getElementById('closeRefreshOptionsBtn').addEventListener('click', () => {
        document.getElementById('refreshOptionsModal').style.display = 'none';
    });
    document.getElementById('cancelRefreshBtn').addEventListener('click', () => {
        document.getElementById('refreshOptionsModal').style.display = 'none';
    });
    document.getElementById('startRefreshBtn').addEventListener('click', startRefreshSources);

    // Initialize cache stats
    loadCacheStats();

    // Initial preview
    updatePreview();
});

// ========================================================================
// Google Drive Sources Management
// ========================================================================

async function loadCacheStats() {
    try {
        const response = await fetch('/api/cache-stats');
        const data = await response.json();

        if (data.success) {
            // Update summary badge
            const cacheStatusBadge = document.getElementById('cacheStatusBadge');
            const totalCacheSize = document.getElementById('totalCacheSize');
            const totalCacheFiles = document.getElementById('totalCacheFiles');

            if (data.total_files > 0) {
                cacheStatusBadge.innerHTML = `
                    <span style="font-size: 1.2rem;">✅</span>
                    <span style="font-weight: 600; color: #86efac;">${data.stats.filter(s => s.cached).length} Cached</span>
                `;
                cacheStatusBadge.style.background = 'rgba(34,197,94,0.1)';
                cacheStatusBadge.style.borderColor = '#22c55e';
            } else {
                cacheStatusBadge.innerHTML = `
                    <span style="font-size: 1.2rem;">💾</span>
                    <span style="font-weight: 600; color: #c0c8d0;">No Cache</span>
                `;
            }

            totalCacheSize.textContent = `${data.total_size_mb} MB`;
            totalCacheFiles.textContent = data.total_files;

            // Store stats for use in modals
            window.cacheStats = data.stats;
        }
    } catch (error) {
        console.error('Failed to load cache stats:', error);
    }
}

async function showCacheStats() {
    try {
        const response = await fetch('/api/cache-stats');
        const data = await response.json();

        if (data.success) {
            const modal = document.getElementById('cacheStatsModal');
            const content = document.getElementById('cacheStatsContent');

            // Build stats table
            let html = `
                <div style="margin-bottom: 20px; padding: 16px; background: rgba(59,130,246,0.05); border: 1px solid #3b82f6; border-radius: 8px;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                        <div>
                            <div style="color: #8b949e; font-size: 0.85rem; margin-bottom: 4px;">Total Cache Size</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #fff;">${data.total_size_mb} MB</div>
                        </div>
                        <div>
                            <div style="color: #8b949e; font-size: 0.85rem; margin-bottom: 4px;">Total Files</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #fff;">${data.total_files}</div>
                        </div>
                        <div>
                            <div style="color: #8b949e; font-size: 0.85rem; margin-bottom: 4px;">Cached Clients</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #fff;">${data.stats.filter(s => s.cached).length}</div>
                        </div>
                    </div>
                </div>
            `;

            if (data.stats.length === 0) {
                html += `<div style="text-align: center; padding: 40px; color: #8b949e;">No clients configured</div>`;
            } else {
                data.stats.forEach(stat => {
                    const bgColor = stat.cached ? 'rgba(34,197,94,0.05)' : 'rgba(139,148,158,0.05)';
                    const borderColor = stat.cached ? '#22c55e' : '#8b949e';
                    const statusIcon = stat.type === 'local' ? '📁' : (stat.cached ? '✅' : '❌');
                    const statusText = stat.type === 'local' ? 'Local Folder' : (stat.cached ? 'Cached' : 'Not Cached');

                    html += `
                        <div style="margin-bottom: 12px; padding: 16px; background: ${bgColor}; border: 1px solid ${borderColor}; border-radius: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                                <div>
                                    <div style="font-weight: 600; font-size: 1.1rem; color: #fff; margin-bottom: 4px;">${stat.client_name}</div>
                                    <div style="font-size: 0.85rem; color: #8b949e;">${stat.client_id}</div>
                                </div>
                                <div style="padding: 4px 12px; background: rgba(0,0,0,0.2); border-radius: 6px; border: 1px solid ${borderColor};">
                                    <span style="margin-right: 6px;">${statusIcon}</span>
                                    <span style="font-weight: 600; font-size: 0.85rem;">${statusText}</span>
                                </div>
                            </div>
                    `;

                    if (stat.cached && stat.type === 'drive') {
                        html += `
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 12px;">
                                <div>
                                    <div style="color: #8b949e; font-size: 0.8rem;">Cache Size</div>
                                    <div style="font-weight: 600; color: #e6edf3;">${stat.size_mb} MB</div>
                                </div>
                                <div>
                                    <div style="color: #8b949e; font-size: 0.8rem;">Files</div>
                                    <div style="font-weight: 600; color: #e6edf3;">${stat.file_count}</div>
                                </div>
                                <div>
                                    <div style="color: #8b949e; font-size: 0.8rem;">Last Refresh</div>
                                    <div style="font-weight: 600; color: #e6edf3;">${stat.age}</div>
                                </div>
                            </div>
                            <button
                                class="btn btn-secondary"
                                style="padding: 6px 12px; font-size: 0.85rem; width: 100%;"
                                onclick="toggleFileList('${stat.client_id}')">
                                📄 View Files
                            </button>
                            <div id="files-${stat.client_id}" style="display: none; margin-top: 12px; max-height: 300px; overflow-y: auto; background: rgba(0,0,0,0.3); border-radius: 6px; padding: 12px;">
                                <!-- File list will be loaded here -->
                            </div>
                        `;
                    } else if (stat.error) {
                        html += `<div style="color: #fca5a5; font-size: 0.85rem;">Error: ${stat.error}</div>`;
                    }

                    html += `</div>`;
                });
            }

            content.innerHTML = html;
            modal.style.display = 'block';
        }
    } catch (error) {
        showMessage('error', `Failed to load cache stats: ${error.message}`);
    }
}

async function showRefreshOptionsModal() {
    const modal = document.getElementById('refreshOptionsModal');
    const clientList = document.getElementById('clientSelectionList');

    // Get list of clients with Drive folders
    const driveClients = clients.filter(c =>
        c.folder && (c.folder.includes('drive.google.com') || c.folder.startsWith('drive://'))
    );

    if (driveClients.length === 0) {
        showMessage('warning', 'No clients with Google Drive folders configured');
        return;
    }

    // Build client selection checkboxes
    let html = `
        <div style="margin-bottom: 12px; padding: 12px; background: rgba(59,130,246,0.05); border: 1px solid #3b82f6; border-radius: 6px;">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                <input type="checkbox" id="selectAllClients" style="width: 18px; height: 18px; cursor: pointer;" checked />
                <span style="font-weight: 600; color: #93c5fd;">Select All Clients</span>
            </label>
        </div>
    `;

    driveClients.forEach(client => {
        html += `
            <label style="display: flex; align-items: center; gap: 8px; padding: 10px; border-radius: 6px; cursor: pointer; transition: background 0.2s;"
                   onmouseover="this.style.background='rgba(255,255,255,0.05)'"
                   onmouseout="this.style.background='transparent'">
                <input type="checkbox" class="client-checkbox" data-client-id="${client.id}" style="width: 18px; height: 18px; cursor: pointer;" checked />
                <span style="flex: 1; font-weight: 600; color: #e6edf3;">${client.name}</span>
                <span style="color: #8b949e; font-size: 0.85rem;">${client.id}</span>
            </label>
        `;
    });

    clientList.innerHTML = html;

    // Add select all functionality
    document.getElementById('selectAllClients').addEventListener('change', (e) => {
        document.querySelectorAll('.client-checkbox').forEach(cb => {
            cb.checked = e.target.checked;
        });
    });

    modal.style.display = 'block';
}

async function startRefreshSources() {
    const selectedClients = Array.from(document.querySelectorAll('.client-checkbox:checked'))
        .map(cb => cb.dataset.clientId);

    if (selectedClients.length === 0) {
        showMessage('warning', 'Please select at least one client to refresh');
        return;
    }

    // Close modal
    document.getElementById('refreshOptionsModal').style.display = 'none';

    // Show progress panel
    const progressPanel = document.getElementById('refreshProgressPanel');
    const progressContent = document.getElementById('refreshProgressContent');
    progressPanel.style.display = 'block';
    progressContent.textContent = '';

    // Disable refresh button during operation
    const refreshBtn = document.getElementById('refreshSourcesBtn');
    const originalBtnText = refreshBtn.textContent;
    refreshBtn.disabled = true;
    refreshBtn.textContent = '🔄 Refreshing...';

    try {
        const response = await fetch('/api/refresh-sources', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ clients: selectedClients })
        });

        // Stream progress updates
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.substring(6));

                        // Format message with colors
                        let colorClass = '';
                        let icon = '';
                        if (data.type === 'error') {
                            colorClass = 'color: #fca5a5';
                            icon = '❌';
                        } else if (data.type === 'success') {
                            colorClass = 'color: #86efac';
                            icon = '✅';
                        } else if (data.type === 'warning') {
                            colorClass = 'color: #fdba74';
                            icon = '⚠️';
                        } else if (data.type === 'info') {
                            colorClass = 'color: #93c5fd';
                            icon = 'ℹ️';
                        }

                        if (data.message) {
                            progressContent.textContent += `${data.message}\n`;
                        }

                        // Scroll to bottom
                        progressContent.scrollTop = progressContent.scrollHeight;

                        // Handle completion
                        if (data.type === 'complete') {
                            if (data.success) {
                                showMessage('success', `✅ Refresh complete! Updated ${data.total_files} files across ${data.successful} client(s)`);
                            } else {
                                showMessage('warning', `⚠️ Refresh completed with ${data.failed} error(s)`);
                            }

                            // Reload cache stats
                            await loadCacheStats();
                        }
                    } catch (e) {
                        // Skip invalid JSON
                    }
                }
            }
        }
    } catch (error) {
        showMessage('error', `Refresh failed: ${error.message}`);
        progressContent.textContent += `\n❌ Error: ${error.message}\n`;
    } finally {
        refreshBtn.disabled = false;
        refreshBtn.textContent = originalBtnText;
    }
}

async function clearCache() {
    if (!confirm('Are you sure you want to clear ALL cached Drive files?\n\nThis will delete all downloaded files from the cache. They will be re-downloaded on the next workflow run.')) {
        return;
    }

    const clearBtn = document.getElementById('clearCacheBtn');
    const originalText = clearBtn.textContent;
    clearBtn.disabled = true;
    clearBtn.textContent = '🗑️ Clearing...';

    try {
        const response = await fetch('/api/clear-cache', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}) // Clear all clients
        });

        const data = await response.json();

        if (data.success) {
            showMessage('success', `✅ ${data.message} (${data.cleared_size_mb} MB freed)`);
            await loadCacheStats();
        } else {
            showMessage('error', `Failed to clear cache: ${data.error}`);
        }
    } catch (error) {
        showMessage('error', `Failed to clear cache: ${error.message}`);
    } finally {
        clearBtn.disabled = false;
        clearBtn.textContent = originalText;
    }
}

// ========================================================================
// System Status Functions
// ========================================================================

async function loadSystemStatus() {
    try {
        const response = await fetch('/api/system-status');
        const data = await response.json();

        const panel = document.getElementById('systemStatusPanel');

        // Create status cards
        panel.innerHTML = `
            <div style="background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 12px;">
                <div style="font-size: 0.75rem; color: #8b949e; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Python Version</div>
                <div style="font-size: 1.1rem; color: #e6edf3; font-weight: 600;">${data.python_version}</div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 12px;">
                <div style="font-size: 0.75rem; color: #8b949e; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Virtual Environment</div>
                <div style="font-size: 1.1rem; color: ${data.venv_active ? '#86efac' : '#fca5a5'}; font-weight: 600;">
                    ${data.venv_active ? '✅ Active' : '❌ Not Active'}
                </div>
                ${data.venv_path ? `<div style="font-size: 0.7rem; color: #8b949e; margin-top: 4px; word-break: break-all;">${data.venv_path}</div>` : ''}
            </div>
            <div style="background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 12px;">
                <div style="font-size: 0.75rem; color: #8b949e; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Disk Space</div>
                <div style="font-size: 1.1rem; color: ${data.disk_percent > 90 ? '#fca5a5' : data.disk_percent > 75 ? '#fdba74' : '#86efac'}; font-weight: 600;">
                    ${data.disk_free_gb} GB Free
                </div>
                <div style="font-size: 0.7rem; color: #8b949e; margin-top: 4px;">
                    ${data.disk_percent}% used of ${data.disk_total_gb} GB
                </div>
            </div>
            <div style="background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 12px;">
                <div style="font-size: 0.75rem; color: #8b949e; margin-bottom: 4px; text-transform: uppercase; letter-spacing: 0.5px;">Environment</div>
                <div style="font-size: 1.1rem; color: #e6edf3; font-weight: 600;">
                    ${data.container_mode ? '🐳 Container' : '💻 Local'}
                </div>
            </div>
        `;
    } catch (error) {
        const panel = document.getElementById('systemStatusPanel');
        panel.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #fca5a5; grid-column: 1 / -1;">
                ❌ Failed to load system status: ${error.message}
            </div>
        `;
    }
}

// ========================================================================
// Cache File Browser Functions
// ========================================================================

async function toggleFileList(clientId) {
    const fileListDiv = document.getElementById(`files-${clientId}`);

    if (fileListDiv.style.display === 'none') {
        // Show and load files
        fileListDiv.style.display = 'block';
        await loadCacheFiles(clientId);
    } else {
        // Hide
        fileListDiv.style.display = 'none';
    }
}

async function loadCacheFiles(clientId) {
    const fileListDiv = document.getElementById(`files-${clientId}`);

    try {
        fileListDiv.innerHTML = '<div style="text-align: center; padding: 20px; color: #8b949e;">Loading files...</div>';

        const response = await fetch(`/api/cache-files/${clientId}`);
        const data = await response.json();

        if (data.success && data.files.length > 0) {
            // Create table with file details
            let html = `
                <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
                    <thead>
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.1);">
                            <th style="text-align: left; padding: 8px; color: #8b949e; font-weight: 600;">File Name</th>
                            <th style="text-align: right; padding: 8px; color: #8b949e; font-weight: 600;">Size</th>
                            <th style="text-align: right; padding: 8px; color: #8b949e; font-weight: 600;">Cached</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            data.files.forEach(file => {
                const cachedDate = new Date(file.cached_at * 1000);
                const cachedStr = cachedDate.toLocaleDateString() + ' ' + cachedDate.toLocaleTimeString();

                html += `
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 8px; color: #e6edf3; word-break: break-word;">${file.name}</td>
                        <td style="padding: 8px; color: #8b949e; text-align: right; white-space: nowrap;">${file.size_mb} MB</td>
                        <td style="padding: 8px; color: #8b949e; text-align: right; white-space: nowrap; font-size: 0.75rem;">${cachedStr}</td>
                    </tr>
                `;
            });

            html += `
                    </tbody>
                </table>
                <div style="margin-top: 12px; padding: 8px; background: rgba(59,130,246,0.05); border: 1px solid #3b82f6; border-radius: 4px; font-size: 0.8rem; color: #93c5fd;">
                    📊 Total: ${data.total_count} files
                </div>
            `;

            fileListDiv.innerHTML = html;
        } else if (data.files.length === 0) {
            fileListDiv.innerHTML = '<div style="text-align: center; padding: 20px; color: #8b949e;">No files found in cache</div>';
        } else {
            fileListDiv.innerHTML = `<div style="text-align: center; padding: 20px; color: #fca5a5;">Error: ${data.error}</div>`;
        }
    } catch (error) {
        fileListDiv.innerHTML = `<div style="text-align: center; padding: 20px; color: #fca5a5;">Failed to load files: ${error.message}</div>`;
    }
}

// ========================================================================
// Theme Toggle Functions
// ========================================================================

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    const themeIcon = document.getElementById('themeIcon');

    if (savedTheme === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        if (themeIcon) themeIcon.textContent = '☀️';
    } else {
        document.documentElement.removeAttribute('data-theme');
        if (themeIcon) themeIcon.textContent = '🌙';
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const themeIcon = document.getElementById('themeIcon');

    if (currentTheme === 'light') {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'dark');
        if (themeIcon) themeIcon.textContent = '🌙';
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        if (themeIcon) themeIcon.textContent = '☀️';
    }
}

// Load system status on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize theme
    initTheme();

    // Load system status
    loadSystemStatus();

    // Add event listener for refresh button
    const refreshSystemStatusBtn = document.getElementById('refreshSystemStatusBtn');
    if (refreshSystemStatusBtn) {
        refreshSystemStatusBtn.addEventListener('click', loadSystemStatus);
    }

    // Add event listener for theme toggle button
    const themeToggleBtn = document.getElementById('themeToggle');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
});
