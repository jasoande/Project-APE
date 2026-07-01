# Phase 2 Testing Instructions

## Test Scenario
1. Create a new test document in Merck's Google Drive folder
2. Run update-sources.sh to detect and add the new file
3. Verify the new file is added to the existing notebook
4. Verify no duplicates are created

## Commands to Run

```bash
# First, manually add a test file to the Merck Google Drive folder
# File name: "Phase2_Test_Document.pdf" or similar

# Then run the update script
./update-sources.sh fast merck_test

# Verify the log shows:
# - Force refresh enabled
# - Downloading from Drive
# - New files detected: 1
# - Added X new sources
# - No duplicates (or minimal duplicates removed)
```

## Expected Results
- ✅ New file detected
- ✅ New file added to notebook  
- ✅ No duplicate sources created
- ✅ Research prompts run successfully
- ✅ Notes updated
- ✅ Mind map regenerated
- ✅ Quality score calculated
