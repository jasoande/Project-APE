# Service Account Removal Plan - Project APE

**Objective**: Remove all service account authentication code and documentation, make OAuth-only

Date: June 26, 2026  
Status: 🔄 In Progress

---

## Executive Summary

Project APE currently supports both OAuth and service account authentication for Google Drive access. Per requirements, we must remove ALL service account functionality and make the system **OAuth-only**.

### Scope

- **64 lines of code/documentation** reference service accounts
- **7 files** need code changes
- **5 files** need documentation updates
- **5 files** need complete removal
- **1 configuration default** needs changing

---

## Files Requiring Changes

### Category 1: Python Code (Authentication Logic)

#### 1. core/drive_manager.py ⚠️ **CRITICAL**
**Lines**: 34, 124-125, 193, 199-200, 254-275

**Changes Needed**:
- ❌ Remove `from google.oauth2 import service_account` (line 34)
- ❌ Remove `self.service_account_key = self.config.get('service_account_key')` (line 125)
- ❌ Remove `if self.auth_method == 'service_account':` branch (lines 199-200)
- ❌ Remove entire `_service_account_authenticate()` method (lines 254-275)
- ✅ Update docstrings to remove service account mentions
- ✅ Default auth_method to 'oauth' only
- ✅ Remove service_account from DRIVE_CONFIG schema

**Impact**: Core authentication - must test thoroughly

#### 2. dashboard/config_generator.py
**Lines**: 240-241, 399-400

**Changes Needed**:
- ❌ Remove `'auth_method': 'service_account'` defaults
- ✅ Change to `'auth_method': 'oauth'`
- ❌ Remove `'service_account_key': None` config option
- ✅ Update generated vars.py template

**Impact**: Configuration generation - affects new setups

### Category 2: Shell Scripts (Setup & Automation)

#### 3. setup.sh ⚠️ **HIGH PRIORITY**
**Lines**: 236-281, 339-342, 383-438, 492

**Changes Needed**:
- ❌ Remove entire service account setup section (lines 236-281)
- ❌ Remove service account instructions from summary (lines 339-342)
- ❌ Remove service account detection logic (lines 383-438)
- ❌ Remove service account JSON structure (line 492)
- ✅ Add OAuth-only instructions
- ✅ Simplify authentication setup to OAuth only

**Impact**: Initial setup experience - critical user path

#### 4. setup-environment.sh
**Lines**: 506, 921-923

**Changes Needed**:
- ❌ Remove service account warning (line 506)
- ❌ Remove service account creation instructions (lines 921-923)
- ✅ Replace with OAuth setup instructions
- ✅ Add link to OAuth wizard

**Impact**: Environment setup - user guidance

#### 5. launch_ape.sh
**Lines**: 260

**Changes Needed**:
- ❌ Remove `-v $(pwd)/service-account-key.json:/app/service-account.json:ro,z \` volume mount
- ✅ Add OAuth token volume mount if needed

**Impact**: Container launcher - runtime behavior

### Category 3: Documentation

#### 6. README.md
**Lines**: 499, 502, 734

**Changes Needed**:
- ❌ Remove `./create-service-account.sh` reference
- ❌ Remove "share folders with service account" instructions
- ❌ Remove service account key from file structure
- ✅ Emphasize OAuth-only approach
- ✅ Link to OAuth setup guide

**Impact**: Main documentation - user facing

#### 7. API_REFERENCE.md
**Lines**: 713, 737, 868

**Changes Needed**:
- ❌ Remove `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- ❌ Remove service-account-key.json from file structure
- ❌ Remove "OAuth and service account" from features
- ✅ Document OAuth-only authentication

**Impact**: Technical documentation

#### 8. Docs/WEB_CONFIGURATION_GUIDE.md
**Lines**: 234

**Changes Needed**:
- ❌ Remove service account access checklist item
- ✅ Replace with OAuth completion check

**Impact**: Web UI documentation

#### 9. setup-oauth-drive.py
**Lines**: 7, 33

**Changes Needed**:
- ✅ Update messaging - remove "alternative to service account"
- ✅ Say "OAuth authentication (the only supported method)"

**Impact**: OAuth setup messaging

### Category 4: Files to DELETE

#### 10. developer-docs/create-service-account.sh ❌ **DELETE**
**Purpose**: Creates service accounts - no longer needed

#### 11. developer-docs/test-service-account-quick.sh ❌ **DELETE**
**Purpose**: Tests service account auth - obsolete

#### 12. service-account-key.json ❌ **DELETE**
**Purpose**: Service account credentials - empty file, remove

#### 13. developer-docs/save/service-account-key.json ❌ **DELETE**
**Purpose**: Backup of service account key - remove

#### 14. developer-docs/save/service-account.json ❌ **DELETE**
**Purpose**: Service account backup - remove

---

## Implementation Plan

### Phase 1: Code Changes (High Risk)

1. ✅ **core/drive_manager.py** - Remove service account authentication
   - Remove import
   - Remove method
   - Remove config options
   - Update docstrings
   - **TEST**: Verify OAuth still works

2. ✅ **dashboard/config_generator.py** - Change defaults
   - Set auth_method='oauth' as only option
   - Remove service_account_key from config
   - **TEST**: Generate new vars.py and verify

### Phase 2: Setup Scripts (Medium Risk)

3. ✅ **setup.sh** - Remove service account setup
   - Remove entire service account section
   - Update summary instructions
   - **TEST**: Run setup.sh and verify OAuth path

4. ✅ **setup-environment.sh** - Update instructions
   - Remove service account references
   - Add OAuth instructions
   - **TEST**: Run and verify output

5. ✅ **launch_ape.sh** - Remove volume mount
   - Remove service account key mount
   - **TEST**: Launch container and verify auth

### Phase 3: Documentation (Low Risk)

6. ✅ **README.md** - Update main docs
7. ✅ **API_REFERENCE.md** - Update API docs
8. ✅ **Docs/WEB_CONFIGURATION_GUIDE.md** - Update web guide
9. ✅ **setup-oauth-drive.py** - Update messaging

### Phase 4: File Cleanup (Low Risk)

10. ✅ Delete service account scripts and keys
11. ✅ Update .gitignore to prevent accidental commits

### Phase 5: Testing & Validation

12. ✅ Test OAuth authentication end-to-end
13. ✅ Verify no service account code remains
14. ✅ Test fresh installation
15. ✅ Test existing OAuth setups still work

---

## Testing Strategy

### Unit Tests
```bash
# Test drive_manager OAuth only
python3 -c "
from core.drive_manager import DriveManager
import inspect
source = inspect.getsource(DriveManager)
assert 'service_account' not in source.lower()
print('✅ No service account code in drive_manager')
"
```

### Integration Tests
```bash
# Test OAuth flow
python3 setup-oauth-drive.py  # Should complete without errors

# Test main.py with OAuth
python3 main.py --help  # Should not mention service accounts

# Test config generation
python3 dashboard/config_generator.py  # Should generate OAuth-only config
```

### Manual Tests
1. Fresh install on clean system
2. OAuth setup via web UI
3. Complete workflow with OAuth
4. Verify no service account prompts

---

## Risks & Mitigation

### Risk 1: Breaking Existing Deployments
**Impact**: High  
**Probability**: Medium  

**Mitigation**:
- Add migration guide for users with service accounts
- Provide clear error message if service account detected
- Document how to transition to OAuth

### Risk 2: Code Dependencies
**Impact**: Medium  
**Probability**: Low  

**Mitigation**:
- Comprehensive grep for all references
- Test imports after removal
- Verify no broken imports

### Risk 3: Documentation Gaps
**Impact**: Low  
**Probability**: Low  

**Mitigation**:
- Review all docs after changes
- Add OAuth troubleshooting section
- Create migration FAQ

---

## Rollback Plan

If issues arise:

1. Git revert all changes
2. Restore from backup
3. Tag working OAuth-only version
4. Document issues found

**Git Commands**:
```bash
# Create backup branch before changes
git checkout -b backup-before-service-account-removal

# Make changes on feature branch
git checkout -b remove-service-accounts

# If rollback needed
git checkout backup-before-service-account-removal
```

---

## Success Criteria

✅ **Code**:
- No references to 'service_account' in Python code
- No service account imports
- OAuth works for all operations

✅ **Scripts**:
- No service account setup in any script
- All scripts reference OAuth only

✅ **Documentation**:
- No service account mentioned
- OAuth clearly documented as the only method
- Migration guide provided

✅ **Files**:
- All service account scripts deleted
- No service account keys in repo
- .gitignore updated

✅ **Testing**:
- Fresh install works with OAuth
- Existing OAuth setups still work
- No errors or warnings about service accounts

---

## Timeline

- **Phase 1 (Code)**: 30 minutes
- **Phase 2 (Scripts)**: 30 minutes
- **Phase 3 (Docs)**: 20 minutes
- **Phase 4 (Cleanup)**: 10 minutes
- **Phase 5 (Testing)**: 30 minutes

**Total Estimated Time**: 2 hours

---

## Sign-off

**Reviewed by**: Principal Software Engineer  
**Approved for**: OAuth-only authentication  
**Start Date**: June 26, 2026  
**Target Completion**: June 26, 2026

---

## Next Steps

1. Review this plan
2. Create backup branch
3. Execute Phase 1 (Code Changes)
4. Test after each phase
5. Complete all phases
6. Final validation
7. Update version number
8. Create pull request

**Ready to proceed? ✅**
