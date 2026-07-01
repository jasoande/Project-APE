# Dependency Cleanup Analysis

## PDF Processing Dependencies

### Current Status
```python
pypdf>=4.0.0      # Status: OPTIONAL
Pillow>=10.0.0    # Status: OPTIONAL
```

## Usage Analysis

### ❌ NOT Used In Standard Mode
The default pipeline (`_execute_standard()`) no longer uses:
- PDF consolidation
- Image to PDF conversion
- `FastPDFConsolidator`

Instead, it adds individual files directly via `UpdateManager`.

### ✅ Still Used In Gemini Agent Mode
The Gemini-orchestrated pipeline (`_execute_with_agent()`) still uses:
- `_prepare_pdf_step()` - Consolidates PDFs
- `_upload_pdf_step()` - Uploads consolidated PDF
- `FastPDFConsolidator` - PDF/Image processing

**However:** Gemini agent mode requires `GEMINI_API_KEY` environment variable, which is currently not set (falls back to standard mode).

## Code Locations

### PDF Consolidation Still Exists In:
1. `core/pdf_consolidator_fast.py` - Full module (226 lines)
2. `core/client_pipeline.py`:
   - Line 24: `from core.pdf_consolidator_fast import FastPDFConsolidator`
   - Line 390-401: `_prepare_pdf_step()` method
   - Line 403-409: `_upload_pdf_step()` method
   - Line 494-533: `_consolidate_pdfs()` method
   - Line 534-557: `_upload_pdf()` method

### Used By:
- Gemini agent workflow (line 318-319 in pipeline steps)

### NOT Used By:
- Standard fast mode ✅
- Standard deep mode ✅
- Update mode ✅

## Options

### Option 1: Keep As Optional (RECOMMENDED)
- Mark as optional in requirements.txt ✅ (DONE)
- Keep code for future Gemini agent use
- Users without `GEMINI_API_KEY` can skip install

### Option 2: Remove Completely
If you NEVER plan to use Gemini agent mode:

1. **Remove from requirements.txt:**
   ```diff
   - pypdf>=4.0.0
   - Pillow>=10.0.0
   ```

2. **Remove code:**
   ```bash
   # Delete PDF consolidator
   rm core/pdf_consolidator_fast.py
   ```

3. **Clean up client_pipeline.py:**
   - Remove `FastPDFConsolidator` import
   - Remove `_prepare_pdf_step()` method
   - Remove `_upload_pdf_step()` method
   - Remove `_consolidate_pdfs()` method
   - Remove `_upload_pdf()` method

4. **Update Gemini agent workflow:**
   - Remove `prepare_pdf` and `upload_pdf` steps
   - Use `UpdateManager` instead

## Recommendation

**Keep as OPTIONAL** because:

1. ✅ Doesn't hurt to have them installed
2. ✅ Allows future Gemini agent usage
3. ✅ Code is already written and working
4. ✅ Small package sizes (pypdf ~1MB, Pillow ~3MB)
5. ✅ Users can skip if needed

**Only remove if:**
- ❌ You're certain you'll NEVER use Gemini agent mode
- ❌ You need to minimize dependencies
- ❌ Installation issues on your platform

## Current Implementation

Updated `requirements.txt` to mark pypdf and Pillow as:
- **Optional**
- **Only needed for Gemini agent mode**
- **Can be removed if never using Gemini orchestration**

## Testing

### Without pypdf/Pillow:
```bash
# Standard mode should work fine
./launch_ape.sh fast merck_test

# Update mode should work fine
./update-sources.sh fast merck_test
```

### With GEMINI_API_KEY set:
```bash
# Gemini agent mode requires pypdf/Pillow
export GEMINI_API_KEY="your-key"
./launch_ape.sh fast merck_test
# Would use PDF consolidation
```

## Summary

- ✅ Dependencies marked as OPTIONAL in requirements.txt
- ✅ Standard mode doesn't need them
- ✅ Update mode doesn't need them
- ✅ Gemini agent mode still uses them (if enabled)
- ✅ Can remove later if Gemini agent is never used

**Status: Dependencies kept as OPTIONAL - can be removed if desired**
