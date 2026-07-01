#!/bin/bash
################################################################################
# Project APE - Automated Test Suite
# Executes comprehensive testing across all components
#
# Usage:
#   ./run-tests.sh                  # Run all tests
#   ./run-tests.sh oauth            # Run OAuth tests only
#   ./run-tests.sh container        # Run container tests only
#   ./run-tests.sh integration      # Run integration tests only
#   ./run-tests.sh security         # Run security tests only
#   ./run-tests.sh --parallel       # Run tests in parallel (where safe)
#   ./run-tests.sh --junit          # Generate JUnit XML output
################################################################################

set -e

# Colors
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly MAGENTA='\033[0;35m'
readonly NC='\033[0m'

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Test results array
declare -a TEST_RESULTS=()

# Backup paths
BACKUP_DIR="/tmp/project-ape-test-backup-$(date +%s)"
BACKUP_CREATED=false

# Configuration
PARALLEL_MODE=false
JUNIT_OUTPUT=false
JUNIT_FILE="test-results-$(date +%Y%m%d-%H%M%S).xml"
TEST_CATEGORY="all"

################################################################################
# Utility Functions
################################################################################

log_header() {
    echo
    echo "========================================================================"
    echo -e "${CYAN}$1${NC}"
    echo "========================================================================"
    echo
}

log_section() {
    echo
    echo -e "${BLUE}▶ $1${NC}"
    echo "------------------------------------------------------------------------"
}

log_pass() {
    echo -e "${GREEN}✅ PASS${NC} - $1"
    ((PASSED_TESTS++))
    TEST_RESULTS+=("PASS|$1|${2:-}")
}

log_fail() {
    echo -e "${RED}❌ FAIL${NC} - $1"
    echo -e "${RED}   Error: $2${NC}"
    ((FAILED_TESTS++))
    TEST_RESULTS+=("FAIL|$1|$2")
}

log_skip() {
    echo -e "${YELLOW}⏭️  SKIP${NC} - $1"
    echo -e "${YELLOW}   Reason: $2${NC}"
    ((SKIPPED_TESTS++))
    TEST_RESULTS+=("SKIP|$1|$2")
}

log_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

start_test() {
    ((TOTAL_TESTS++))
    echo -e "${MAGENTA}TEST $TOTAL_TESTS:${NC} $1"
}

################################################################################
# Backup and Restore Functions
################################################################################

backup_state() {
    log_section "Creating backup of current state"

    mkdir -p "$BACKUP_DIR"

    # Backup OAuth credentials
    if [ -d "$HOME/.project-ape" ]; then
        cp -r "$HOME/.project-ape" "$BACKUP_DIR/" 2>/dev/null || true
        log_info "Backed up: ~/.project-ape"
    fi

    # Backup NotebookLM credentials
    if [ -d "$HOME/.notebooklm" ]; then
        cp -r "$HOME/.notebooklm" "$BACKUP_DIR/" 2>/dev/null || true
        log_info "Backed up: ~/.notebooklm"
    fi

    # Backup gcloud config
    if [ -d "$HOME/.config/gcloud" ]; then
        cp -r "$HOME/.config/gcloud" "$BACKUP_DIR/.config-gcloud" 2>/dev/null || true
        log_info "Backed up: ~/.config/gcloud"
    fi

    # Backup container credentials volume
    if podman volume exists project-ape-credentials 2>/dev/null; then
        podman volume export project-ape-credentials > "$BACKUP_DIR/credentials-volume.tar" 2>/dev/null || true
        log_info "Backed up: Podman volume project-ape-credentials"
    fi

    # Backup vars.py if exists
    if [ -f "./vars.py" ]; then
        cp "./vars.py" "$BACKUP_DIR/vars.py" 2>/dev/null || true
        log_info "Backed up: vars.py"
    fi

    BACKUP_CREATED=true
    log_info "Backup created at: $BACKUP_DIR"
}

restore_state() {
    if [ "$BACKUP_CREATED" = false ]; then
        log_warn "No backup to restore"
        return
    fi

    log_section "Restoring original state"

    # Restore OAuth credentials
    if [ -d "$BACKUP_DIR/.project-ape" ]; then
        rm -rf "$HOME/.project-ape"
        cp -r "$BACKUP_DIR/.project-ape" "$HOME/" 2>/dev/null || true
        log_info "Restored: ~/.project-ape"
    fi

    # Restore NotebookLM credentials
    if [ -d "$BACKUP_DIR/.notebooklm" ]; then
        rm -rf "$HOME/.notebooklm"
        cp -r "$BACKUP_DIR/.notebooklm" "$HOME/" 2>/dev/null || true
        log_info "Restored: ~/.notebooklm"
    fi

    # Restore gcloud config
    if [ -d "$BACKUP_DIR/.config-gcloud" ]; then
        rm -rf "$HOME/.config/gcloud"
        mkdir -p "$HOME/.config"
        cp -r "$BACKUP_DIR/.config-gcloud" "$HOME/.config/gcloud" 2>/dev/null || true
        log_info "Restored: ~/.config/gcloud"
    fi

    # Restore container credentials volume
    if [ -f "$BACKUP_DIR/credentials-volume.tar" ]; then
        podman volume rm -f project-ape-credentials 2>/dev/null || true
        podman volume create project-ape-credentials
        cat "$BACKUP_DIR/credentials-volume.tar" | podman volume import project-ape-credentials - 2>/dev/null || true
        log_info "Restored: Podman volume"
    fi

    # Restore vars.py
    if [ -f "$BACKUP_DIR/vars.py" ]; then
        cp "$BACKUP_DIR/vars.py" "./vars.py" 2>/dev/null || true
        log_info "Restored: vars.py"
    fi

    log_info "State restored from: $BACKUP_DIR"
}

cleanup_backup() {
    if [ -d "$BACKUP_DIR" ]; then
        log_info "Cleaning up backup directory: $BACKUP_DIR"
        # Optionally keep backup for debugging
        # rm -rf "$BACKUP_DIR"
    fi
}

################################################################################
# OAuth Setup Tests
################################################################################

test_oauth_fresh_install() {
    start_test "OAuth Fresh Install"

    # Clean state
    rm -rf ~/.project-ape 2>/dev/null || true

    # Check if setup script exists
    if [ ! -f "./setup-oauth-drive.py" ]; then
        log_skip "OAuth Fresh Install" "setup-oauth-drive.py not found"
        return
    fi

    log_info "This test requires manual interaction"
    log_warn "Automated OAuth flow testing not implemented"
    log_skip "OAuth Fresh Install" "Requires browser interaction"
}

test_oauth_rerun_existing() {
    start_test "OAuth Re-run with Existing Credentials"

    if [ ! -f "$HOME/.project-ape/drive_credentials.json" ]; then
        log_skip "OAuth Re-run" "No existing credentials found"
        return
    fi

    # Check credentials file exists and is valid JSON
    if python3 -c "import json; json.load(open('$HOME/.project-ape/drive_credentials.json'))" 2>/dev/null; then
        log_pass "OAuth credentials file is valid JSON"
    else
        log_fail "OAuth credentials file validation" "Invalid JSON format"
        return
    fi

    # Check token file exists
    if [ -f "$HOME/.project-ape/drive_token.json" ]; then
        log_pass "OAuth token file exists"
    else
        log_skip "OAuth Re-run" "No token file found"
    fi
}

test_oauth_billing_error() {
    start_test "OAuth Billing Error Handling"
    log_skip "OAuth Billing Error" "Requires GCP account without billing (manual test)"
}

test_oauth_expired_token() {
    start_test "OAuth Expired Token"

    if [ ! -f "$HOME/.project-ape/drive_token.json" ]; then
        log_skip "OAuth Expired Token" "No token file found"
        return
    fi

    # Check token age
    TOKEN_AGE_DAYS=$(( ($(date +%s) - $(stat -f %m "$HOME/.project-ape/drive_token.json" 2>/dev/null || stat -c %Y "$HOME/.project-ape/drive_token.json" 2>/dev/null)) / 86400 ))

    if [ "$TOKEN_AGE_DAYS" -gt 7 ]; then
        log_info "Token is $TOKEN_AGE_DAYS days old (likely expired)"
        log_skip "OAuth Expired Token" "Token refresh requires browser interaction"
    else
        log_info "Token is $TOKEN_AGE_DAYS days old (still fresh)"
        log_skip "OAuth Expired Token" "Token not expired yet"
    fi
}

test_oauth_wrong_client_type() {
    start_test "OAuth Wrong Client Type Detection"

    if [ ! -f "$HOME/.project-ape/drive_credentials.json" ]; then
        log_skip "OAuth Client Type" "No credentials file found"
        return
    fi

    # Check if credentials have "installed" key (Desktop app)
    if python3 -c "import json; data = json.load(open('$HOME/.project-ape/drive_credentials.json')); exit(0 if 'installed' in data else 1)" 2>/dev/null; then
        log_pass "OAuth client type is Desktop app (correct)"
    else
        log_fail "OAuth client type check" "Credentials missing 'installed' key - may be Web app instead of Desktop app"
    fi
}

################################################################################
# Container Tests
################################################################################

test_container_image_build() {
    start_test "Container Image Builds Successfully"

    # Check if Containerfile exists
    CONTAINERFILE=""
    if [ -f "./Containerfile" ]; then
        CONTAINERFILE="./Containerfile"
    elif [ -f "./developer-docs/Containerfile.debian" ]; then
        CONTAINERFILE="./developer-docs/Containerfile.debian"
    else
        log_skip "Container Build" "No Containerfile found"
        return
    fi

    log_info "Building container from: $CONTAINERFILE"

    # Build container
    if podman build -t project-ape-test:latest -f "$CONTAINERFILE" . > /tmp/build-test.log 2>&1; then
        log_pass "Container image built successfully"
    else
        log_fail "Container build" "Build failed - see /tmp/build-test.log"
        return
    fi

    # Verify image exists
    if podman image exists project-ape-test:latest; then
        log_pass "Container image exists in local registry"
    else
        log_fail "Container image verification" "Image not found after build"
    fi
}

test_container_starts_healthy() {
    start_test "Container Starts and Stays Healthy"

    if ! podman image exists project-ape-test:latest; then
        log_skip "Container Health" "Test image not built (run container build test first)"
        return
    fi

    # Start container with basic health check
    CONTAINER_ID=$(podman run -d \
        --name project-ape-test-health \
        --entrypoint sleep \
        project-ape-test:latest \
        30 2>/dev/null)

    if [ -z "$CONTAINER_ID" ]; then
        log_fail "Container start" "Failed to start container"
        return
    fi

    log_info "Started container: $CONTAINER_ID"

    # Wait for container to be running
    sleep 2

    # Check container status
    if podman ps --filter "id=$CONTAINER_ID" --filter "status=running" | grep -q "$CONTAINER_ID"; then
        log_pass "Container is running"
    else
        log_fail "Container health" "Container not running"
        podman logs "$CONTAINER_ID" 2>&1 | tail -20
        podman rm -f "$CONTAINER_ID" 2>/dev/null || true
        return
    fi

    # Wait a bit longer to ensure stability
    sleep 5

    if podman ps --filter "id=$CONTAINER_ID" --filter "status=running" | grep -q "$CONTAINER_ID"; then
        log_pass "Container remains healthy after 5 seconds"
    else
        log_fail "Container stability" "Container stopped unexpectedly"
    fi

    # Cleanup
    podman rm -f "$CONTAINER_ID" 2>/dev/null || true
}

test_dashboard_accessible() {
    start_test "Dashboard Accessible on Port 8765"

    if ! podman image exists project-ape-test:latest; then
        log_skip "Dashboard Accessibility" "Test image not built"
        return
    fi

    # Start dashboard
    CONTAINER_ID=$(podman run -d \
        --name project-ape-test-dashboard \
        -p 8765:8765 \
        --entrypoint python3 \
        project-ape-test:latest \
        dashboard/server.py 2>/dev/null)

    if [ -z "$CONTAINER_ID" ]; then
        log_fail "Dashboard start" "Failed to start dashboard container"
        return
    fi

    log_info "Started dashboard container: $CONTAINER_ID"

    # Wait for dashboard to start
    sleep 5

    # Test HTTP access
    if curl -s http://localhost:8765/ > /dev/null 2>&1; then
        log_pass "Dashboard accessible on http://localhost:8765"
    else
        log_fail "Dashboard accessibility" "Cannot reach dashboard on port 8765"
        podman logs "$CONTAINER_ID" 2>&1 | tail -20
    fi

    # Cleanup
    podman rm -f "$CONTAINER_ID" 2>/dev/null || true
}

test_no_root_processes() {
    start_test "No Root Processes Running in Container"

    if ! podman image exists project-ape-test:latest; then
        log_skip "Root Process Check" "Test image not built"
        return
    fi

    # Start container
    CONTAINER_ID=$(podman run -d \
        --name project-ape-test-root \
        --entrypoint sleep \
        project-ape-test:latest \
        15 2>/dev/null)

    if [ -z "$CONTAINER_ID" ]; then
        log_fail "Container start for root check" "Failed to start container"
        return
    fi

    sleep 2

    # Check processes running as root (UID 0)
    ROOT_PROCESSES=$(podman exec "$CONTAINER_ID" ps aux 2>/dev/null | grep -c "^root" || echo "0")

    if [ "$ROOT_PROCESSES" -eq 0 ]; then
        log_pass "No root processes detected in container"
    else
        log_fail "Root process check" "Found $ROOT_PROCESSES processes running as root"
        podman exec "$CONTAINER_ID" ps aux 2>/dev/null | grep "^root" || true
    fi

    # Cleanup
    podman rm -f "$CONTAINER_ID" 2>/dev/null || true
}

test_file_permissions() {
    start_test "Container File Permissions Correct"

    if ! podman image exists project-ape-test:latest; then
        log_skip "File Permissions" "Test image not built"
        return
    fi

    # Start container
    CONTAINER_ID=$(podman run -d \
        --name project-ape-test-perms \
        --entrypoint sleep \
        project-ape-test:latest \
        15 2>/dev/null)

    if [ -z "$CONTAINER_ID" ]; then
        log_fail "Container start for permissions check" "Failed to start container"
        return
    fi

    sleep 2

    # Check key file permissions
    ERRORS=0

    # Check /app directory is writable by container user
    if podman exec "$CONTAINER_ID" test -w /app 2>/dev/null; then
        log_info "/app directory is writable"
    else
        log_warn "/app directory is not writable"
        ((ERRORS++))
    fi

    # Check logs directory exists and is writable
    if podman exec "$CONTAINER_ID" test -d /app/logs 2>/dev/null; then
        if podman exec "$CONTAINER_ID" test -w /app/logs 2>/dev/null; then
            log_info "/app/logs is writable"
        else
            log_warn "/app/logs is not writable"
            ((ERRORS++))
        fi
    fi

    if [ "$ERRORS" -eq 0 ]; then
        log_pass "Container file permissions are correct"
    else
        log_fail "File permissions check" "Found $ERRORS permission issues"
    fi

    # Cleanup
    podman rm -f "$CONTAINER_ID" 2>/dev/null || true
}

################################################################################
# Integration Tests
################################################################################

test_setup_sh_end_to_end() {
    start_test "setup.sh Runs End-to-End"

    if [ ! -f "./setup.sh" ]; then
        log_skip "setup.sh Integration" "setup.sh not found"
        return
    fi

    log_skip "setup.sh Integration" "Requires user interaction (manual test)"
}

test_oauth_wizard_completes() {
    start_test "OAuth Wizard Completes Successfully"

    if [ ! -f "./setup-oauth-drive.py" ]; then
        log_skip "OAuth Wizard" "setup-oauth-drive.py not found"
        return
    fi

    log_skip "OAuth Wizard" "Requires browser interaction (manual test)"
}

test_drive_access_verified() {
    start_test "Google Drive Access Verified"

    if [ ! -f "$HOME/.project-ape/drive_token.json" ]; then
        log_skip "Drive Access" "No OAuth token found"
        return
    fi

    # Test Drive API access
    DRIVE_TEST_RESULT=$(python3 << 'EOF'
import sys
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    import os

    token_file = os.path.expanduser("~/.project-ape/drive_token.json")
    creds = Credentials.from_authorized_user_file(token_file)
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(pageSize=5, fields="files(name)").execute()
    files = results.get('files', [])

    print(f"SUCCESS|{len(files)}")
    sys.exit(0)
except Exception as e:
    print(f"ERROR|{str(e)}")
    sys.exit(1)
EOF
)

    if echo "$DRIVE_TEST_RESULT" | grep -q "^SUCCESS"; then
        FILE_COUNT=$(echo "$DRIVE_TEST_RESULT" | cut -d'|' -f2)
        log_pass "Drive API accessible - found $FILE_COUNT files"
    else
        ERROR_MSG=$(echo "$DRIVE_TEST_RESULT" | cut -d'|' -f2)
        log_fail "Drive access test" "$ERROR_MSG"
    fi
}

################################################################################
# Security Tests
################################################################################

test_no_secrets_in_logs() {
    start_test "No Secrets Leaked in Logs"

    # Check for common secret patterns in log files
    SECRETS_FOUND=0

    if [ -d "./logs" ]; then
        # Look for potential secrets (API keys, tokens, credentials)
        PATTERNS=(
            "AIza[0-9A-Za-z-_]{35}"  # Google API keys
            "ya29\.[0-9A-Za-z-_]+"   # Google OAuth tokens
            "client_secret"
            "private_key"
            "-----BEGIN PRIVATE KEY-----"
        )

        for pattern in "${PATTERNS[@]}"; do
            if grep -r -E "$pattern" ./logs/*.log 2>/dev/null | grep -v "client_secret_.*\.json" > /dev/null; then
                log_warn "Found potential secret matching pattern: $pattern"
                ((SECRETS_FOUND++))
            fi
        done
    fi

    if [ "$SECRETS_FOUND" -eq 0 ]; then
        log_pass "No secrets detected in log files"
    else
        log_fail "Secret detection" "Found $SECRETS_FOUND potential secrets in logs"
    fi
}

test_credential_file_permissions() {
    start_test "Credential Files Have Secure Permissions (600/700)"

    PERMISSION_ERRORS=0

    # Check OAuth credentials
    if [ -f "$HOME/.project-ape/drive_credentials.json" ]; then
        PERMS=$(stat -f "%A" "$HOME/.project-ape/drive_credentials.json" 2>/dev/null || stat -c "%a" "$HOME/.project-ape/drive_credentials.json" 2>/dev/null)
        if [ "$PERMS" = "600" ]; then
            log_info "drive_credentials.json has correct permissions (600)"
        else
            log_warn "drive_credentials.json has permissions $PERMS (expected 600)"
            ((PERMISSION_ERRORS++))
        fi
    fi

    # Check OAuth token
    if [ -f "$HOME/.project-ape/drive_token.json" ]; then
        PERMS=$(stat -f "%A" "$HOME/.project-ape/drive_token.json" 2>/dev/null || stat -c "%a" "$HOME/.project-ape/drive_token.json" 2>/dev/null)
        if [ "$PERMS" = "600" ]; then
            log_info "drive_token.json has correct permissions (600)"
        else
            log_warn "drive_token.json has permissions $PERMS (expected 600)"
            ((PERMISSION_ERRORS++))
        fi
    fi

    # Check NotebookLM credentials directory
    if [ -d "$HOME/.notebooklm" ]; then
        PERMS=$(stat -f "%A" "$HOME/.notebooklm" 2>/dev/null || stat -c "%a" "$HOME/.notebooklm" 2>/dev/null)
        if [ "$PERMS" = "700" ]; then
            log_info ".notebooklm directory has correct permissions (700)"
        else
            log_warn ".notebooklm directory has permissions $PERMS (expected 700)"
            ((PERMISSION_ERRORS++))
        fi
    fi

    if [ "$PERMISSION_ERRORS" -eq 0 ]; then
        log_pass "All credential files have secure permissions"
    else
        log_fail "Permission check" "Found $PERMISSION_ERRORS permission issues"
    fi
}

test_container_nonroot_user() {
    start_test "Container Runs as Non-Root User"

    if ! podman image exists project-ape-test:latest; then
        log_skip "Container User Check" "Test image not built"
        return
    fi

    # Start container
    CONTAINER_ID=$(podman run -d \
        --name project-ape-test-user \
        --entrypoint sleep \
        project-ape-test:latest \
        15 2>/dev/null)

    if [ -z "$CONTAINER_ID" ]; then
        log_fail "Container start for user check" "Failed to start container"
        return
    fi

    sleep 2

    # Check default user
    CURRENT_USER=$(podman exec "$CONTAINER_ID" whoami 2>/dev/null)

    if [ "$CURRENT_USER" != "root" ]; then
        log_pass "Container runs as non-root user: $CURRENT_USER"
    else
        log_fail "Container user check" "Container is running as root"
    fi

    # Cleanup
    podman rm -f "$CONTAINER_ID" 2>/dev/null || true
}

test_no_env_mounts() {
    start_test "No .env Files Mounted in Container"

    # Check launch scripts for .env mounts
    ENV_MOUNTS=0

    if [ -f "./launch_ape.sh" ]; then
        if grep -q "\.env" ./launch_ape.sh; then
            log_warn "Found .env reference in launch_ape.sh"
            ((ENV_MOUNTS++))
        fi
    fi

    if [ -f "./ape-run.sh" ]; then
        if grep -q "\.env" ./ape-run.sh; then
            log_warn "Found .env reference in ape-run.sh"
            ((ENV_MOUNTS++))
        fi
    fi

    if [ "$ENV_MOUNTS" -eq 0 ]; then
        log_pass "No .env file mounts detected in launch scripts"
    else
        log_fail ".env mount check" "Found $ENV_MOUNTS references to .env files"
    fi
}

################################################################################
# Test Suite Runners
################################################################################

run_oauth_tests() {
    log_header "OAuth Setup Tests (5 scenarios)"

    test_oauth_fresh_install
    test_oauth_rerun_existing
    test_oauth_billing_error
    test_oauth_expired_token
    test_oauth_wrong_client_type
}

run_container_tests() {
    log_header "Container Tests (5 scenarios)"

    test_container_image_build
    test_container_starts_healthy
    test_dashboard_accessible
    test_no_root_processes
    test_file_permissions
}

run_integration_tests() {
    log_header "Integration Tests (3 scenarios)"

    test_setup_sh_end_to_end
    test_oauth_wizard_completes
    test_drive_access_verified
}

run_security_tests() {
    log_header "Security Tests (4 scenarios)"

    test_no_secrets_in_logs
    test_credential_file_permissions
    test_container_nonroot_user
    test_no_env_mounts
}

run_all_tests() {
    run_oauth_tests
    run_container_tests
    run_integration_tests
    run_security_tests
}

################################################################################
# Parallel Test Execution
################################################################################

run_tests_parallel() {
    log_header "Running Tests in Parallel Mode"

    # Safe to run in parallel (no state conflicts)
    (
        test_oauth_rerun_existing
        test_oauth_expired_token
        test_oauth_wrong_client_type
    ) &
    PID1=$!

    (
        test_credential_file_permissions
        test_no_secrets_in_logs
        test_no_env_mounts
    ) &
    PID2=$!

    (
        test_drive_access_verified
    ) &
    PID3=$!

    # Wait for parallel tests
    wait $PID1
    wait $PID2
    wait $PID3

    # Sequential tests (require container cleanup)
    test_container_image_build
    test_container_starts_healthy
    test_dashboard_accessible
    test_no_root_processes
    test_file_permissions
    test_container_nonroot_user
}

################################################################################
# Results Reporting
################################################################################

print_summary() {
    echo
    log_header "Test Summary"

    echo -e "${CYAN}Total Tests:${NC}   $TOTAL_TESTS"
    echo -e "${GREEN}Passed:${NC}        $PASSED_TESTS"
    echo -e "${RED}Failed:${NC}        $FAILED_TESTS"
    echo -e "${YELLOW}Skipped:${NC}       $SKIPPED_TESTS"
    echo

    # Calculate pass rate
    if [ "$TOTAL_TESTS" -gt 0 ]; then
        PASS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED_TESTS / $TOTAL_TESTS) * 100}")
        echo -e "${CYAN}Pass Rate:${NC}     ${PASS_RATE}%"
        echo
    fi

    # Show failed tests
    if [ "$FAILED_TESTS" -gt 0 ]; then
        echo -e "${RED}Failed Tests:${NC}"
        for result in "${TEST_RESULTS[@]}"; do
            if [[ $result == FAIL* ]]; then
                TEST_NAME=$(echo "$result" | cut -d'|' -f2)
                ERROR_MSG=$(echo "$result" | cut -d'|' -f3)
                echo -e "  ${RED}❌${NC} $TEST_NAME"
                echo -e "     ${RED}→${NC} $ERROR_MSG"
            fi
        done
        echo
    fi

    # Exit code
    if [ "$FAILED_TESTS" -gt 0 ]; then
        exit 1
    else
        exit 0
    fi
}

generate_junit_xml() {
    log_section "Generating JUnit XML Report"

    cat > "$JUNIT_FILE" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Project APE Test Suite" tests="$TOTAL_TESTS" failures="$FAILED_TESTS" skipped="$SKIPPED_TESTS">
  <testsuite name="ProjectAPE" tests="$TOTAL_TESTS" failures="$FAILED_TESTS" skipped="$SKIPPED_TESTS">
EOF

    for result in "${TEST_RESULTS[@]}"; do
        STATUS=$(echo "$result" | cut -d'|' -f1)
        TEST_NAME=$(echo "$result" | cut -d'|' -f2)
        MESSAGE=$(echo "$result" | cut -d'|' -f3)

        case "$STATUS" in
            PASS)
                echo "    <testcase name=\"$TEST_NAME\" />" >> "$JUNIT_FILE"
                ;;
            FAIL)
                cat >> "$JUNIT_FILE" << EOF_FAIL
    <testcase name="$TEST_NAME">
      <failure message="$MESSAGE" />
    </testcase>
EOF_FAIL
                ;;
            SKIP)
                cat >> "$JUNIT_FILE" << EOF_SKIP
    <testcase name="$TEST_NAME">
      <skipped message="$MESSAGE" />
    </testcase>
EOF_SKIP
                ;;
        esac
    done

    cat >> "$JUNIT_FILE" << EOF
  </testsuite>
</testsuites>
EOF

    log_info "JUnit XML report saved to: $JUNIT_FILE"
}

################################################################################
# Main Execution
################################################################################

show_usage() {
    cat << EOF
Usage: ./run-tests.sh [OPTIONS] [CATEGORY]

Test Categories:
  all           Run all tests (default)
  oauth         Run OAuth setup tests only
  container     Run container tests only
  integration   Run integration tests only
  security      Run security tests only

Options:
  --parallel    Run tests in parallel where safe
  --junit       Generate JUnit XML output
  --no-backup   Skip state backup/restore
  -h, --help    Show this help message

Examples:
  ./run-tests.sh                    # Run all tests
  ./run-tests.sh oauth              # Run OAuth tests only
  ./run-tests.sh --parallel         # Run tests in parallel
  ./run-tests.sh --junit security   # Run security tests with JUnit output
EOF
}

main() {
    # Parse arguments
    NO_BACKUP=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --parallel)
                PARALLEL_MODE=true
                shift
                ;;
            --junit)
                JUNIT_OUTPUT=true
                shift
                ;;
            --no-backup)
                NO_BACKUP=true
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            oauth|container|integration|security|all)
                TEST_CATEGORY="$1"
                shift
                ;;
            *)
                echo "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done

    # Show header
    log_header "Project APE - Automated Test Suite"

    echo "Configuration:"
    echo "  Test Category: $TEST_CATEGORY"
    echo "  Parallel Mode: $PARALLEL_MODE"
    echo "  JUnit Output:  $JUNIT_OUTPUT"
    echo "  Backup State:  $([[ $NO_BACKUP == true ]] && echo 'No' || echo 'Yes')"
    echo

    # Backup state (unless disabled)
    if [ "$NO_BACKUP" = false ]; then
        backup_state
        trap 'restore_state; cleanup_backup' EXIT
    fi

    # Run tests
    if [ "$PARALLEL_MODE" = true ]; then
        run_tests_parallel
    else
        case "$TEST_CATEGORY" in
            oauth)
                run_oauth_tests
                ;;
            container)
                run_container_tests
                ;;
            integration)
                run_integration_tests
                ;;
            security)
                run_security_tests
                ;;
            all|*)
                run_all_tests
                ;;
        esac
    fi

    # Generate JUnit XML if requested
    if [ "$JUNIT_OUTPUT" = true ]; then
        generate_junit_xml
    fi

    # Print summary
    print_summary
}

# Run main function
main "$@"
