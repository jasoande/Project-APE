/**
 * Project APE - Environment Setup Wizard
 * Polished graphical UI with auto-detection, theme support, and live feedback
 */

// ---------------------------------------------------------------------------
// Theme
// ---------------------------------------------------------------------------
function initTheme() {
    const saved = localStorage.getItem('theme') || 'dark';
    const icon = document.getElementById('themeIcon');
    if (saved === 'light') {
        document.documentElement.setAttribute('data-theme', 'light');
        if (icon) icon.textContent = '☀️';
    } else {
        document.documentElement.removeAttribute('data-theme');
        if (icon) icon.textContent = '🌙';
    }
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const icon = document.getElementById('themeIcon');
    if (current === 'light') {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'dark');
        if (icon) icon.textContent = '🌙';
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        if (icon) icon.textContent = '☀️';
    }
}

// ---------------------------------------------------------------------------
// CSRF
// ---------------------------------------------------------------------------
function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

// ---------------------------------------------------------------------------
// API helper
// ---------------------------------------------------------------------------
async function api(endpoint, method, data) {
    method = method || 'GET';
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (method === 'POST') {
        opts.headers['X-CSRFToken'] = getCSRFToken();
        if (data) opts.body = JSON.stringify(data);
    }
    const res = await fetch(endpoint, opts);
    if (!res.ok) {
        const err = await res.json().catch(function() { return {}; });
        throw new Error(err.error || 'Request failed (' + res.status + ')');
    }
    return res.json();
}

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------
const state = {
    currentStep: 0,
    total: 7,
    completed: 0,
    running: false,
    systemInfo: null
};

const STEP_ICONS = {
    pending:   ['&#x1F5A5;','&#x1F4E6;','&#x1F4E4;','&#x2601;','&#x1F40D;','&#x1F4C1;','&#x1F4D3;'],
    completed: '&#x2705;',
    error:     '&#x274C;',
    skipped:   '&#x23ED;'
};

// ---------------------------------------------------------------------------
// UI helpers
// ---------------------------------------------------------------------------
function $(id) { return document.getElementById(id); }

function toggleStep(n) {
    var body = $('step-' + n + '-body');
    if (body) body.classList.toggle('open');
}

function openStep(n) {
    var body = $('step-' + n + '-body');
    if (body) body.classList.add('open');
}

function updateProgress() {
    var pct = (state.completed / state.total) * 100;
    var bar = $('progress-bar');
    var text = $('progress-text');
    var status = $('overall-status');
    bar.style.width = pct + '%';
    if (state.completed === state.total) {
        bar.classList.add('complete');
        status.textContent = 'All checks passed';
    } else if (state.running) {
        status.textContent = 'Checking dependencies...';
    } else {
        status.textContent = 'Ready';
    }
    text.textContent = state.completed + ' of ' + state.total + ' checks completed';
}

function setBadge(n, type, label) {
    var badge = $('step-' + n + '-badge');
    badge.className = 'step-badge ' + type;
    badge.textContent = label;
}

function setStepState(n, cssState) {
    var step = $('step-' + n);
    step.className = 'setup-step' + (cssState ? ' ' + cssState : '');
}

function setIcon(n, html) {
    $('step-' + n + '-icon').innerHTML = html;
}

function setDetails(n, html) {
    $('step-' + n + '-details').innerHTML = html;
}

function setActions(n, html) {
    $('step-' + n + '-actions').innerHTML = html;
}

function detailCard(rows) {
    var html = '<div class="detail-card">';
    rows.forEach(function(r) {
        var cls = r[2] ? ' ' + r[2] : '';
        html += '<div class="detail-row"><span class="detail-label">' + r[0] + '</span><span class="detail-value' + cls + '">' + r[1] + '</span></div>';
    });
    return html + '</div>';
}

function addLog(n, msg, type) {
    var el = $('step-' + n + '-log');
    if (!el) {
        var container = $('step-' + n + '-details');
        container.innerHTML += '<div class="live-log" id="step-' + n + '-log"></div>';
        el = $('step-' + n + '-log');
    }
    var cls = type ? ' log-' + type : '';
    el.innerHTML += '<div class="log-line' + cls + '">' + escHtml(msg) + '</div>';
    el.scrollTop = el.scrollHeight;
}

function escHtml(s) {
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
}

function delay(ms) { return new Promise(function(r) { setTimeout(r, ms); }); }

// ---------------------------------------------------------------------------
// Step runners
// ---------------------------------------------------------------------------
async function checkStep1() {
    setStepState(1, 'active');
    setBadge(1, 'checking', 'Detecting...');
    openStep(1);

    try {
        var r = await api('/api/setup/system-info');
        state.systemInfo = r;
        setDetails(1, detailCard([
            ['Operating System', r.os, 'success'],
            ['Architecture', r.arch],
            ['Platform', r.platform],
            ['Python', r.python_version]
        ]));
        markComplete(1);
        return true;
    } catch (e) {
        markError(1, 'Detection failed: ' + e.message);
        return false;
    }
}

async function checkStep2() {
    if (state.systemInfo && state.systemInfo.os !== 'macOS') {
        markSkipped(2, 'Not required on ' + (state.systemInfo.os || 'Linux'));
        return true;
    }
    setStepState(2, 'active');
    setBadge(2, 'checking', 'Checking...');
    openStep(2);

    try {
        var r = await api('/api/setup/check-homebrew');
        if (r.installed) {
            setDetails(2, detailCard([
                ['Version', r.version, 'success'],
                ['Location', r.path]
            ]));
            markComplete(2);
            return true;
        }
        setBadge(2, 'missing', 'Not Installed');
        setDetails(2, '<p class="step-description">Homebrew is not installed. It\'s needed to install Podman and Python on macOS.</p>');
        setActions(2,
            '<button class="btn btn-primary" onclick="installStep2()"><span class="spinner" id="spin-2" style="display:none"></span> Install Homebrew</button>' +
            '<button class="btn btn-secondary" onclick="skipStep(2)">Skip</button>'
        );
        return false;
    } catch (e) {
        markError(2, e.message);
        return false;
    }
}

async function installStep2() {
    setBadge(2, 'installing', 'Installing...');
    $('spin-2').style.display = 'inline-block';
    addLog(2, 'Installing Homebrew... This may take several minutes.', 'info');
    try {
        var r = await api('/api/setup/install-homebrew', 'POST');
        if (r.success) {
            addLog(2, 'Homebrew installed: ' + r.version, 'success');
            setDetails(2, detailCard([['Version', r.version, 'success'], ['Location', r.path]]));
            markComplete(2);
            continueSetup();
        } else {
            throw new Error(r.error || 'Installation failed');
        }
    } catch (e) {
        markError(2, e.message);
        addLog(2, 'Error: ' + e.message, 'error');
    }
}

async function checkStep3() {
    setStepState(3, 'active');
    setBadge(3, 'checking', 'Checking...');
    openStep(3);

    try {
        var r = await api('/api/setup/check-podman');
        if (r.installed) {
            var rows = [['Version', r.version, 'success']];
            if (state.systemInfo && state.systemInfo.os === 'macOS') {
                rows.push(['Machine Status', r.machine_running ? 'Running' : 'Stopped', r.machine_running ? 'success' : 'warning']);
            }
            setDetails(3, detailCard(rows));
            markComplete(3);
            return true;
        }
        setBadge(3, 'missing', 'Not Installed');
        setDetails(3, '');
        setActions(3,
            '<button class="btn btn-primary" onclick="installStep3()"><span class="spinner" id="spin-3" style="display:none"></span> Install Podman</button>' +
            '<button class="btn btn-secondary" onclick="skipStep(3)">Skip</button>'
        );
        return false;
    } catch (e) {
        markError(3, e.message);
        return false;
    }
}

async function installStep3() {
    setBadge(3, 'installing', 'Installing...');
    $('spin-3').style.display = 'inline-block';
    addLog(3, 'Installing Podman...', 'info');
    try {
        var r = await api('/api/setup/install-podman', 'POST');
        if (r.success) {
            addLog(3, 'Podman installed: ' + r.version, 'success');
            setDetails(3, detailCard([['Version', r.version, 'success']]));
            markComplete(3);
            continueSetup();
        } else { throw new Error(r.error || 'Failed'); }
    } catch (e) {
        markError(3, e.message);
        addLog(3, 'Error: ' + e.message, 'error');
    }
}

async function checkStep4() {
    setStepState(4, 'active');
    setBadge(4, 'checking', 'Checking...');
    openStep(4);

    try {
        var r = await api('/api/setup/check-gcloud');
        if (r.installed) {
            var rows = [['Version', r.version, 'success']];
            if (r.authenticated) rows.push(['Account', r.account, 'success']);
            else rows.push(['Authenticated', 'No', 'warning']);
            setDetails(4, detailCard(rows));
            markComplete(4);
            return true;
        }
        setBadge(4, 'missing', 'Not Installed');
        setDetails(4, '');
        setActions(4,
            '<button class="btn btn-primary" onclick="installStep4()"><span class="spinner" id="spin-4" style="display:none"></span> Install gcloud</button>' +
            '<button class="btn btn-secondary" onclick="skipStep(4)">Skip</button>'
        );
        return false;
    } catch (e) {
        markError(4, e.message);
        return false;
    }
}

async function installStep4() {
    setBadge(4, 'installing', 'Installing...');
    $('spin-4').style.display = 'inline-block';
    addLog(4, 'Installing Google Cloud SDK...', 'info');
    try {
        var r = await api('/api/setup/install-gcloud', 'POST');
        if (r.success) {
            addLog(4, 'gcloud installed: ' + r.version, 'success');
            setDetails(4, detailCard([['Version', r.version, 'success']]));
            markComplete(4);
            continueSetup();
        } else { throw new Error(r.error || 'Failed'); }
    } catch (e) {
        markError(4, e.message);
        addLog(4, 'Error: ' + e.message, 'error');
    }
}

async function checkStep5() {
    setStepState(5, 'active');
    setBadge(5, 'checking', 'Checking...');
    openStep(5);

    try {
        var r = await api('/api/setup/check-python');
        if (r.compatible) {
            setDetails(5, detailCard([
                ['Version', r.version, 'success'],
                ['Location', r.path]
            ]));
            markComplete(5);
            return true;
        }
        var msg = r.installed ? 'Python ' + r.version + ' found but 3.10+ is required.' : 'Python 3.10+ is not installed.';
        setBadge(5, 'missing', r.installed ? 'Upgrade Needed' : 'Not Installed');
        setDetails(5, '<p class="step-description">' + msg + '</p>');
        setActions(5,
            '<button class="btn btn-primary" onclick="installStep5()"><span class="spinner" id="spin-5" style="display:none"></span> Install Python 3.14</button>' +
            '<button class="btn btn-secondary" onclick="skipStep(5)">Skip</button>'
        );
        return false;
    } catch (e) {
        markError(5, e.message);
        return false;
    }
}

async function installStep5() {
    setBadge(5, 'installing', 'Installing...');
    $('spin-5').style.display = 'inline-block';
    addLog(5, 'Installing Python 3.14...', 'info');
    try {
        var r = await api('/api/setup/install-python', 'POST');
        if (r.success) {
            addLog(5, 'Python installed: ' + r.version, 'success');
            setDetails(5, detailCard([['Version', r.version, 'success'], ['Location', r.path]]));
            markComplete(5);
            continueSetup();
        } else { throw new Error(r.error || 'Failed'); }
    } catch (e) {
        markError(5, e.message);
        addLog(5, 'Error: ' + e.message, 'error');
    }
}

async function checkStep6() {
    setStepState(6, 'active');
    setBadge(6, 'checking', 'Checking...');
    openStep(6);

    try {
        var r = await api('/api/setup/check-venv');
        if (r.exists && r.compatible) {
            setDetails(6, detailCard([
                ['Location', r.path, 'success'],
                ['Python', r.version]
            ]));
            markComplete(6);
            return true;
        }
        var msg = r.exists ? 'Virtual environment exists but uses Python ' + r.version + ' (needs 3.10+).' : 'Virtual environment not found.';
        setBadge(6, 'missing', r.exists ? 'Outdated' : 'Not Created');
        setDetails(6, '<p class="step-description">' + msg + '</p>');
        setActions(6,
            '<button class="btn btn-primary" onclick="installStep6()"><span class="spinner" id="spin-6" style="display:none"></span> Create Virtual Environment</button>'
        );
        return false;
    } catch (e) {
        markError(6, e.message);
        return false;
    }
}

async function installStep6() {
    setBadge(6, 'installing', 'Creating...');
    $('spin-6').style.display = 'inline-block';
    addLog(6, 'Creating virtual environment at ~/.project-ape-venv ...', 'info');
    try {
        var r = await api('/api/setup/create-venv', 'POST');
        if (r.success) {
            addLog(6, 'Virtual environment created: ' + r.path, 'success');
            setDetails(6, detailCard([['Location', r.path, 'success'], ['Python', r.version]]));
            markComplete(6);
            continueSetup();
        } else { throw new Error(r.error || 'Failed'); }
    } catch (e) {
        markError(6, e.message);
        addLog(6, 'Error: ' + e.message, 'error');
    }
}

async function checkStep7() {
    setStepState(7, 'active');
    setBadge(7, 'checking', 'Checking...');
    openStep(7);

    try {
        var r = await api('/api/setup/check-notebooklm');
        if (r.installed) {
            var rows = [['NotebookLM CLI', r.version, 'success']];
            if (r.flask_version) rows.push(['Flask', r.flask_version, 'success']);
            rows.push(['All Dependencies', 'Installed', 'success']);
            setDetails(7, detailCard(rows));
            markComplete(7);
            return true;
        }
        setBadge(7, 'missing', 'Not Installed');
        setDetails(7, '');
        setActions(7,
            '<button class="btn btn-primary" onclick="installStep7()"><span class="spinner" id="spin-7" style="display:none"></span> Install Dependencies</button>'
        );
        return false;
    } catch (e) {
        markError(7, e.message);
        return false;
    }
}

async function installStep7() {
    setBadge(7, 'installing', 'Installing...');
    $('spin-7').style.display = 'inline-block';
    addLog(7, 'Installing NotebookLM CLI and dependencies...', 'info');
    addLog(7, 'This may take 3-5 minutes.', 'info');
    try {
        var r = await api('/api/setup/install-notebooklm', 'POST');
        if (r.success) {
            addLog(7, 'NotebookLM CLI: ' + r.version, 'success');
            if (r.flask_version) addLog(7, 'Flask: ' + r.flask_version, 'success');
            addLog(7, 'All dependencies installed.', 'success');
            var rows = [['NotebookLM CLI', r.version, 'success']];
            if (r.flask_version) rows.push(['Flask', r.flask_version, 'success']);
            setDetails(7, detailCard(rows));
            markComplete(7);
            continueSetup();
        } else { throw new Error(r.error || 'Failed'); }
    } catch (e) {
        markError(7, e.message);
        addLog(7, 'Error: ' + e.message, 'error');
    }
}

// ---------------------------------------------------------------------------
// State transitions
// ---------------------------------------------------------------------------
function markComplete(n) {
    setStepState(n, 'completed');
    setBadge(n, 'installed', 'Installed');
    setIcon(n, STEP_ICONS.completed);
    setActions(n, '');
    state.completed++;
    updateProgress();
}

function markSkipped(n, reason) {
    setStepState(n, 'skipped');
    setBadge(n, 'skipped', 'Skipped');
    setIcon(n, STEP_ICONS.skipped);
    setDetails(n, '<p class="step-description">' + escHtml(reason || 'Skipped') + '</p>');
    setActions(n, '');
    state.completed++;
    updateProgress();
}

function markError(n, msg) {
    setStepState(n, 'error');
    setBadge(n, 'error', 'Error');
    setIcon(n, STEP_ICONS.error);
    openStep(n);
    var existing = $('step-' + n + '-details').innerHTML;
    if (!existing.includes('detail-card')) {
        setDetails(n, '<p class="step-description" style="color:var(--error-red)">' + escHtml(msg) + '</p>');
    }
    setActions(n,
        '<button class="btn btn-primary" onclick="retryStep(' + n + ')">Retry</button>' +
        '<button class="btn btn-secondary" onclick="skipStep(' + n + ')">Skip</button>'
    );
}

function skipStep(n) {
    markSkipped(n, 'Skipped by user — install manually later');
    continueSetup();
}

function retryStep(n) {
    setStepState(n, '');
    setIcon(n, STEP_ICONS.pending[n - 1]);
    setDetails(n, '');
    setActions(n, '');
    state.currentStep = n - 1;
    state.running = true;
    continueSetup();
}

// ---------------------------------------------------------------------------
// Orchestration
// ---------------------------------------------------------------------------
var stepFns = [null, checkStep1, checkStep2, checkStep3, checkStep4, checkStep5, checkStep6, checkStep7];

async function continueSetup() {
    if (!state.running) return;

    for (var i = state.currentStep + 1; i <= state.total; i++) {
        state.currentStep = i;
        await delay(300);
        var ok = await stepFns[i]();
        if (!ok) {
            state.running = false;
            return;
        }
    }

    state.running = false;
    if (state.completed >= state.total) {
        showComplete();
    }
}

function showComplete() {
    $('completion-card').classList.add('visible');
    $('footer-actions').style.display = 'none';
    $('btn-start').style.display = 'none';
    $('btn-restart').style.display = 'inline-flex';
}

async function startSetup() {
    state.running = true;
    state.currentStep = 0;
    state.completed = 0;
    updateProgress();

    var btn = $('btn-start');
    btn.disabled = true;
    $('btn-spinner').style.display = 'inline-block';
    $('btn-label').textContent = 'Checking...';

    await continueSetup();

    btn.disabled = false;
    $('btn-spinner').style.display = 'none';
    $('btn-label').textContent = 'Start Setup';
}

function restartSetup() {
    for (var i = 1; i <= state.total; i++) {
        setStepState(i, '');
        setIcon(i, STEP_ICONS.pending[i - 1]);
        setBadge(i, 'pending', 'Pending');
        setDetails(i, '');
        setActions(i, '');
        var body = $('step-' + i + '-body');
        if (body) body.classList.remove('open');
    }
    state.currentStep = 0;
    state.completed = 0;
    state.running = false;
    var bar = $('progress-bar');
    bar.classList.remove('complete');
    updateProgress();
    $('completion-card').classList.remove('visible');
    $('footer-actions').style.display = 'flex';
    $('btn-start').style.display = 'inline-flex';
    $('btn-restart').style.display = 'none';
    startSetup();
}

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
window.addEventListener('DOMContentLoaded', function() {
    initTheme();
    setTimeout(startSetup, 400);
});
