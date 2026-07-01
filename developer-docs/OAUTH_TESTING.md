# OAuth Setup Testing Guide
## Ensuring Error-Free Setup Every Time

This document outlines test scenarios and validation procedures to ensure `setup-oauth-drive-improved.py` works reliably across all user scenarios.

---

## Test Matrix

| Scenario | Description | Expected Outcome | Test Status |
|----------|-------------|------------------|-------------|
| **Fresh Install** | New user, never used GCP | Creates project, completes setup | ⬜ TODO |
| **Existing Project** | User has GCP projects already | Uses existing project | ⬜ TODO |
| **No Billing** | User without billing enabled | Gracefully falls back to existing project | ⬜ TODO |
| **Re-run** | Running script second time | Detects existing credentials, re-auths only | ⬜ TODO |
| **Expired Token** | Token is 7+ days old | Re-authenticates successfully | ⬜ TODO |
| **Wrong Client Type** | User creates Web app instead of Desktop | Detects and guides to fix | ⬜ TODO |
| **Org Restrictions** | Workspace with project creation disabled | Offers existing project selection | ⬜ TODO |
| **Linux Headless** | Server without browser | Provides manual URL copy option | ⬜ TODO |

---

## Pre-Test Setup

### Test Environment Requirements

**Option A: Clean macOS Environment**
```bash
# Backup existing credentials
mv ~/.project-ape ~/.project-ape.backup
mv ~/.config/gcloud ~/.config/gcloud.backup

# Fresh test
python3 setup-oauth-drive-improved.py
```

**Option B: Docker Test Container**
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl gnupg
RUN curl https://sdk.cloud.google.com | bash
ENV PATH="/root/google-cloud-sdk/bin:${PATH}"
WORKDIR /app
COPY setup-oauth-drive-improved.py .
CMD ["python3", "setup-oauth-drive-improved.py"]
```

**Option C: VM/Cloud Shell**
```bash
# Use Google Cloud Shell (guaranteed fresh environment)
git clone <your-repo>
cd Project-APE-dev
python3 setup-oauth-drive-improved.py
```

---

## Test Scenarios

### Scenario 1: Fresh Install (Most Common)

**User Profile**:
- Never used Google Cloud before
- Has Gmail account
- Running on personal laptop

**Test Steps**:

1. **Clean state**:
   ```bash
   rm -rf ~/.project-ape
   gcloud auth revoke --all
   ```

2. **Run script**:
   ```bash
   python3 setup-oauth-drive-improved.py
   ```

3. **Expected Flow**:
   - ✅ Detects gcloud installed
   - ✅ Prompts for gcloud authentication
   - ✅ Opens browser for sign-in
   - ✅ Creates new project "Project APE Drive Access"
   - ✅ Enables Drive API
   - ✅ Opens browser to create OAuth credentials
   - ✅ Guides through step-by-step instructions
   - ✅ Auto-detects downloaded JSON file
   - ✅ Moves to ~/.project-ape/drive_credentials.json
   - ✅ Opens browser for OAuth flow
   - ✅ Handles "App not verified" warning
   - ✅ Saves token to ~/.project-ape/drive_token.json
   - ✅ Sets chmod 600 on both files

4. **Validation**:
   ```bash
   # Check files exist
   ls -lh ~/.project-ape/
   # Should show:
   # -rw------- drive_credentials.json
   # -rw------- drive_token.json

   # Check permissions
   stat -f "%A %N" ~/.project-ape/*.json | grep "^600"

   # Test Drive access
   python3 -c "
   from google.oauth2.credentials import Credentials
   from googleapiclient.discovery import build
   creds = Credentials.from_authorized_user_file('$HOME/.project-ape/drive_token.json')
   service = build('drive', 'v3', credentials=creds)
   results = service.files().list(pageSize=5).execute()
   print('✅ Successfully accessed Drive!')
   print(f'Found {len(results.get(\"files\", []))} files')
   "
   ```

5. **Success Criteria**:
   - [ ] No errors during execution
   - [ ] Both files created with correct permissions
   - [ ] Drive API accessible
   - [ ] Total time < 10 minutes

---

### Scenario 2: Billing Account Required

**User Profile**:
- New GCP user
- No billing account configured
- Wants to create new project

**Test Steps**:

1. **Simulate billing restriction**:
   - Use account without billing
   - Or revoke billing permissions temporarily

2. **Run script**:
   ```bash
   python3 setup-oauth-drive-improved.py
   ```

3. **Expected Flow**:
   - ✅ Authenticates with gcloud
   - ✅ Attempts to create project
   - ⚠️  Project creation fails with billing error
   - ✅ Script detects error
   - ✅ Offers to use existing project
   - ✅ Lists user's existing projects
   - ✅ User selects existing project
   - ✅ Continues with OAuth setup
   - ✅ Completes successfully

4. **Validation**:
   ```bash
   # Verify script used existing project
   gcloud config get-value project
   # Should show selected project, not new one

   # Rest of validation same as Scenario 1
   ```

5. **Success Criteria**:
   - [ ] Script doesn't crash on billing error
   - [ ] Clearly explains the issue
   - [ ] Provides fallback option
   - [ ] Completes setup successfully

---

### Scenario 3: Re-run After Successful Setup

**User Profile**:
- Previously completed OAuth setup
- Wants to re-authenticate or verify setup

**Test Steps**:

1. **Existing state**:
   ```bash
   ls ~/.project-ape/
   # drive_credentials.json exists
   # drive_token.json exists
   ```

2. **Run script**:
   ```bash
   python3 setup-oauth-drive-improved.py
   ```

3. **Expected Flow**:
   - ✅ Detects gcloud already authenticated
   - ✅ Detects active project
   - ✅ Asks: Use current project? (yes)
   - ✅ Detects Drive API already enabled
   - ✅ Detects existing credentials file
   - ✅ Asks: Use existing credentials? (yes)
   - ✅ Skips to OAuth authentication
   - ✅ Completes in < 2 minutes

4. **Success Criteria**:
   - [ ] Doesn't duplicate setup steps
   - [ ] Offers to use existing resources
   - [ ] Fast re-auth (< 2 min)

---

### Scenario 4: Expired Token (7+ Days Old)

**User Profile**:
- Completed setup 2 weeks ago
- Hasn't used Project APE since
- Token expired

**Test Steps**:

1. **Simulate expired token**:
   ```bash
   # Make token file old
   touch -t 202606010000 ~/.project-ape/drive_token.json
   ```

2. **Test Drive access**:
   ```bash
   python3 verify-drive-access.py
   # Should fail with "Token expired"
   ```

3. **Run script**:
   ```bash
   python3 setup-oauth-drive-improved.py
   ```

4. **Expected Flow**:
   - ✅ Detects existing setup
   - ✅ Skips to re-authentication
   - ✅ Opens browser for OAuth
   - ✅ Generates fresh token
   - ✅ Overwrites old token
   - ✅ Completes in < 1 minute

5. **Validation**:
   ```bash
   # Verify token is fresh
   stat -f "%Sm" ~/.project-ape/drive_token.json

   # Test Drive access
   python3 verify-drive-access.py
   # Should succeed
   ```

---

### Scenario 5: User Creates Wrong OAuth Client Type

**User Profile**:
- Follows wizard instructions
- Accidentally selects "Web application" instead of "Desktop app"
- OAuth flow fails

**Test Steps**:

1. **Manually create wrong type**:
   - Go to Cloud Console
   - Create OAuth client with "Web application"
   - Download credentials

2. **Run script with wrong credentials**:
   ```bash
   mv ~/Downloads/client_secret_*.json ~/.project-ape/drive_credentials.json
   python3 setup-oauth-drive-improved.py
   ```

3. **Expected Behavior**:
   - ⚠️  OAuth flow starts
   - ❌ Fails with `redirect_uri_mismatch` error
   - ✅ Script detects the error
   - ✅ Explains the issue clearly
   - ✅ Provides fix instructions:
     - Delete wrong client
     - Create new "Desktop app" client
     - Re-download
   - ✅ Offers to retry

4. **Success Criteria**:
   - [ ] Clear error message
   - [ ] Explains root cause
   - [ ] Provides actionable fix
   - [ ] Doesn't corrupt existing state

---

### Scenario 6: Organization Restrictions

**User Profile**:
- Google Workspace user
- Organization blocks project creation
- Needs to use existing project

**Test Steps**:

1. **Use Workspace account with restrictions**
   - Sign in with org account
   - Run script

2. **Expected Flow**:
   - ✅ Authenticates successfully
   - ✅ Attempts to create project
   - ⚠️  Fails with permission error
   - ✅ Detects org restrictions
   - ✅ Explains the limitation
   - ✅ Lists existing projects in org
   - ✅ User selects existing project
   - ✅ Continues setup

3. **Success Criteria**:
   - [ ] Handles permission errors gracefully
   - [ ] Offers alternative path
   - [ ] Completes successfully

---

### Scenario 7: Linux Headless Server (SSH)

**User Profile**:
- RHEL/Ubuntu server
- Connected via SSH
- No X11 forwarding
- Browser on different machine

**Test Steps**:

1. **SSH without X11**:
   ```bash
   ssh user@server  # No -X flag
   cd Project-APE-dev
   python3 setup-oauth-drive-improved.py
   ```

2. **Expected Flow**:
   - ✅ gcloud auth detects no browser
   - ✅ Prints URL for manual copy
   - ✅ User copies URL to local browser
   - ✅ Completes auth
   - ✅ Pastes verification code back
   - ✅ OAuth flow provides URL fallback
   - ✅ User completes auth on local machine
   - ✅ Token saved on server

3. **Validation**:
   ```bash
   # Token should exist on server
   ls -lh ~/.project-ape/drive_token.json

   # Test from server
   python3 verify-drive-access.py
   ```

4. **Success Criteria**:
   - [ ] Works without browser on server
   - [ ] Provides clear manual instructions
   - [ ] Completes successfully

---

## Automated Test Script

Create `test-oauth-setup.sh`:

```bash
#!/bin/bash
# Automated OAuth Setup Testing Suite

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BACKUP_DIR="/tmp/project-ape-backup-$(date +%s)"
TEST_RESULTS=()

backup_state() {
    echo "Backing up existing state to $BACKUP_DIR..."
    mkdir -p "$BACKUP_DIR"
    
    if [ -d "$HOME/.project-ape" ]; then
        cp -r "$HOME/.project-ape" "$BACKUP_DIR/"
    fi
    
    if [ -d "$HOME/.config/gcloud" ]; then
        cp -r "$HOME/.config/gcloud" "$BACKUP_DIR/"
    fi
}

restore_state() {
    echo "Restoring original state..."
    rm -rf "$HOME/.project-ape"
    
    if [ -d "$BACKUP_DIR/.project-ape" ]; then
        cp -r "$BACKUP_DIR/.project-ape" "$HOME/"
    fi
    
    if [ -d "$BACKUP_DIR/gcloud" ]; then
        cp -r "$BACKUP_DIR/gcloud" "$HOME/.config/"
    fi
}

test_fresh_install() {
    echo -e "${YELLOW}TEST: Fresh Install${NC}"
    
    # Clean state
    rm -rf ~/.project-ape
    
    # This requires manual interaction
    echo "⚠️  This test requires manual steps:"
    echo "  1. Run: python3 setup-oauth-drive-improved.py"
    echo "  2. Follow all prompts"
    echo "  3. Verify success message"
    echo ""
    read -p "Run test manually and press Enter when complete..."
    
    # Validation
    if [ -f "$HOME/.project-ape/drive_credentials.json" ] && \
       [ -f "$HOME/.project-ape/drive_token.json" ]; then
        echo -e "${GREEN}✅ PASS: Files created${NC}"
        TEST_RESULTS+=("Fresh Install: PASS")
    else
        echo -e "${RED}❌ FAIL: Missing files${NC}"
        TEST_RESULTS+=("Fresh Install: FAIL")
    fi
}

test_permissions() {
    echo -e "${YELLOW}TEST: File Permissions${NC}"
    
    if [ -f "$HOME/.project-ape/drive_credentials.json" ]; then
        PERMS=$(stat -f "%A" "$HOME/.project-ape/drive_credentials.json" 2>/dev/null || stat -c "%a" "$HOME/.project-ape/drive_credentials.json" 2>/dev/null)
        
        if [ "$PERMS" = "600" ]; then
            echo -e "${GREEN}✅ PASS: Credentials have chmod 600${NC}"
            TEST_RESULTS+=("Permissions: PASS")
        else
            echo -e "${RED}❌ FAIL: Credentials have chmod $PERMS (expected 600)${NC}"
            TEST_RESULTS+=("Permissions: FAIL")
        fi
    else
        echo -e "${YELLOW}⚠️  SKIP: No credentials file${NC}"
        TEST_RESULTS+=("Permissions: SKIP")
    fi
}

test_drive_access() {
    echo -e "${YELLOW}TEST: Drive API Access${NC}"
    
    python3 <<EOF
import sys
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    
    creds = Credentials.from_authorized_user_file('$HOME/.project-ape/drive_token.json')
    service = build('drive', 'v3', credentials=creds)
    results = service.files().list(pageSize=1).execute()
    
    print("${GREEN}✅ PASS: Drive API accessible${NC}")
    sys.exit(0)
except Exception as e:
    print(f"${RED}❌ FAIL: {e}${NC}")
    sys.exit(1)
EOF

    if [ $? -eq 0 ]; then
        TEST_RESULTS+=("Drive Access: PASS")
    else
        TEST_RESULTS+=("Drive Access: FAIL")
    fi
}

print_results() {
    echo ""
    echo "========================================================================"
    echo "TEST RESULTS"
    echo "========================================================================"
    echo ""
    
    for result in "${TEST_RESULTS[@]}"; do
        if [[ $result == *"PASS"* ]]; then
            echo -e "${GREEN}✅ $result${NC}"
        elif [[ $result == *"FAIL"* ]]; then
            echo -e "${RED}❌ $result${NC}"
        else
            echo -e "${YELLOW}⚠️  $result${NC}"
        fi
    done
    
    echo ""
}

main() {
    echo "========================================================================"
    echo "OAuth Setup Testing Suite"
    echo "========================================================================"
    echo ""
    
    backup_state
    
    trap restore_state EXIT
    
    test_fresh_install
    test_permissions
    test_drive_access
    
    print_results
}

main
```

Make it executable:
```bash
chmod +x test-oauth-setup.sh
```

---

## Manual Testing Checklist

For each release, manually verify:

### Before Release

- [ ] Test on fresh macOS installation
- [ ] Test on fresh Linux installation (RHEL/Ubuntu)
- [ ] Test with brand new Google account
- [ ] Test with existing Google Cloud user
- [ ] Test without billing account
- [ ] Test with organization restrictions
- [ ] Test re-running script after successful setup
- [ ] Test with expired token
- [ ] Verify all error messages are clear and actionable

### After Release

- [ ] Monitor user feedback for first 5 users
- [ ] Check for common failure patterns
- [ ] Update documentation based on real issues
- [ ] Add FAQ entries for common questions

---

## Success Metrics

**Target Goals**:

| Metric | Target | Current |
|--------|--------|---------|
| First-time success rate | > 95% | TBD |
| Average setup time | < 10 min | TBD |
| Support tickets per 100 users | < 5 | TBD |
| Steps requiring user manual intervention | < 3 | TBD |

**Track via**:
- GitHub issues labeled `oauth-setup`
- User survey responses
- Support ticket analysis

---

## Regression Testing

Before each release:

```bash
# Run full test suite
./test-oauth-setup.sh

# Manual verification
python3 setup-oauth-drive-improved.py
# Follow all prompts
# Verify success

# Test integration with Project APE
./launch_ape.sh fast
# Verify Drive access works end-to-end
```

---

## Continuous Improvement

**Feedback Loop**:

1. User reports issue → GitHub issue
2. Reproduce scenario → Add to test matrix
3. Fix bug → Update script
4. Add test case → Update this doc
5. Release → Monitor new users

**Review Quarterly**:
- Analyze common failure modes
- Update script to handle edge cases
- Improve error messages
- Update documentation

---

**Version**: 1.0.0  
**Last Updated**: June 30, 2026  
**Next Review**: September 30, 2026
