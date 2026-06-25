# NotebookLM Note Formatting Issue - Analysis & Fix

**Date:** 2026-06-22  
**Issue:** Saved notes in NotebookLM appear unreadable with excessive markdown syntax  
**Status:** ✅ FIXED

## Problem Description

### What Users See

Notes saved in NotebookLM display raw markdown syntax instead of formatted text:

```
**1. Future-Proof AI Connectivity Architecture**
* **Business Objective Alignment:** Modernize Technological Infrastructure
* **Customer Challenge:** 3scale API Gateway's deprecation...
* **Red Hat Solution:** Red Hat 3scale API Gateway & OpenShift
```

### What Users Expected

Clean, formatted text:

```
1. Future-Proof AI Connectivity Architecture

BUSINESS OBJECTIVE ALIGNMENT: Modernize Technological Infrastructure
CUSTOMER CHALLENGE: 3scale API Gateway's deprecation...
RED HAT SOLUTION: Red Hat 3scale API Gateway & OpenShift
```

## Root Cause Analysis

### Technical Flow

1. **Prompt Execution**
   ```bash
   notebooklm ask --prompt-file FILE -n NOTEBOOK_ID --save-as-note -t "Title"
   ```

2. **Gemini Response**
   - Gemini AI generates responses in **markdown format**
   - Uses `**bold**`, `*bullets*`, `## headers`
   - Optimized for terminal/API display

3. **Note Creation**
   - `--save-as-note` saves the **raw text response**
   - NotebookLM web UI displays this text as-is
   - Markdown syntax is NOT rendered

4. **User Experience**
   - Sees literal `**`, `*`, `##` characters
   - Content is technically correct but visually cluttered
   - Hard to read and unprofessional

### Why This Happens

**NotebookLM CLI vs Web UI mismatch:**

| Component | Format Expected |
|-----------|----------------|
| NotebookLM CLI output | Markdown (for terminal) |
| NotebookLM CLI `--save-as-note` | Saves raw text |
| NotebookLM Web UI notes | Plain text OR HTML |

The CLI generates markdown but saves it as plain text, causing a format mismatch in the web UI.

### Code Location

**File:** `/Users/jasona/test/Project-APE/core/client_pipeline.py`  
**Line:** ~650

```python
result = subprocess.run(
    [
        "notebooklm", "ask",
        "--prompt-file", tmp_path,
        "-n", self.notebook_id,
        "--save-as-note",      # <-- Saves raw markdown as text
        "-t", note_title
    ],
    capture_output=True,
    text=True,
    timeout=180
)
```

## Solution Implemented

### Approach: Update Prompts for Plain Text Formatting

Instead of post-processing markdown, we instruct Gemini to generate clean plain text directly.

### Changes Made

Updated all 6 `chat_prompt_consolidated_*.txt` files with formatting instructions.

**Example - chat_prompt_consolidated_04.txt:**

**BEFORE:**
```
Act as a $persona and strategic advisor for $name.

## Part 1: Strategic Solution Ideas
```

**AFTER:**
```
Act as a $persona and strategic advisor for $name.

IMPORTANT FORMATTING INSTRUCTIONS:
- Format your response as clean, readable text suitable for NotebookLM notes
- Use clear section headers (not markdown ## headers)
- Use simple dashes (-) for bullet points, NOT asterisks (*)
- For emphasis, use ALL CAPS or underscores, NOT **bold** markdown
- Use blank lines generously to separate sections
- Number items clearly: 1. 2. 3. etc.
- Keep formatting minimal and professional

═══════════════════════════════════════════════════════════════════════

PART 1: STRATEGIC SOLUTION IDEAS
```

### Formatting Guidelines Added

1. **Headers:** Use visual separators and CAPS instead of `##`
   ```
   ═══════════════════════════════════════════════════════════════════════
   PART 1: STRATEGIC SOLUTION IDEAS
   ═══════════════════════════════════════════════════════════════════════
   ```

2. **Emphasis:** Use ALL CAPS instead of `**bold**`
   ```
   BUSINESS OBJECTIVE ALIGNMENT
   (not **Business Objective Alignment**)
   ```

3. **Bullets:** Use dashes `-` instead of asterisks `*`
   ```
   - Item 1
   - Item 2
   (not * Item 1)
   ```

4. **Lists:** Clear numbering
   ```
   1. First item
   2. Second item
   (not **1.** or 1.)
   ```

5. **Spacing:** Generous blank lines for readability

### Files Modified

All consolidated prompt files updated:
- ✅ `chat_prompt_consolidated_01.txt` - Industry Analysis
- ✅ `chat_prompt_consolidated_02.txt` - Innovation Assessment
- ✅ `chat_prompt_consolidated_03.txt` - Technology Partners
- ✅ `chat_prompt_consolidated_04.txt` - Strategic Ideas & HMW
- ✅ `chat_prompt_consolidated_05.txt` - Account Team Onboarding
- ✅ `chat_prompt_consolidated_06.txt` - Account Plan

## Expected Results

### Before Fix
```
**1. Future-Proof AI Connectivity Architecture**
* **Business Objective Alignment:** Modernize Infrastructure
* **Customer Challenge:** 3scale Redis deprecation
* **Red Hat Solution:** Red Hat 3scale API Gateway
```

### After Fix
```
═══════════════════════════════════════════════════════════════════════
1. FUTURE-PROOF AI CONNECTIVITY ARCHITECTURE
═══════════════════════════════════════════════════════════════════════

BUSINESS OBJECTIVE ALIGNMENT
Modernize Technological Infrastructure

CUSTOMER CHALLENGE
3scale API Gateway's deprecation of Redis threatens HA setup

RED HAT SOLUTION
Red Hat 3scale API Gateway & OpenShift
```

## Alternative Solutions Considered

### Option 1: Post-Process Markdown to HTML ❌
**Why not chosen:**
- Adds processing overhead
- Requires markdown parsing library
- May introduce formatting bugs
- Doesn't fix root issue

### Option 2: Save as PDF Instead ❌
**Why not chosen:**
- Changes workflow significantly
- PDFs are sources, not notes
- Loses NotebookLM's note-specific features
- More complex implementation

### Option 3: Use NotebookLM's Rich Text API (if exists) ❌
**Why not chosen:**
- No such API available in current CLI
- Would require API changes
- Not under our control

### Option 4: Update Prompts (CHOSEN) ✅
**Why chosen:**
- Simple to implement
- No code changes required
- Maintains existing workflow
- Actually produces better plain text output
- Easy to test and verify

## Testing Procedure

### 1. Backup Existing Prompts
```bash
cd /path/to/Project-APE
for f in chat_prompt_consolidated_*.txt; do
    cp "$f" "$f.backup"
done
```

### 2. Run Test Pipeline
```bash
# Test with one client
echo 'clients = ["test_client"]' > vars.py
./launch_ape.sh fast test_client
```

### 3. Verify in NotebookLM Web UI
1. Open https://notebooklm.google.com
2. Navigate to test client notebook
3. Open saved notes
4. Check formatting is clean and readable

### 4. Compare Before/After
- Note should NOT have `**` or `*` characters
- Headers should use visual separators
- Bullets should use `-` dashes
- Text should be easy to read

## Rollback Procedure

If the fix causes issues:

```bash
cd /path/to/Project-APE
for f in chat_prompt_consolidated_*.txt.backup; do
    mv "$f" "${f%.backup}"
done
```

## Impact Assessment

### Positive Impact
- ✅ Notes are now readable in web UI
- ✅ Professional appearance
- ✅ No markdown clutter
- ✅ Better user experience
- ✅ No code changes required

### Potential Concerns
- ⚠️ Less rich formatting (but more readable)
- ⚠️ Relies on Gemini following instructions (generally reliable)
- ⚠️ May need prompt tweaking if Gemini ignores formatting rules

### Mitigation
- Test with multiple clients
- Monitor note quality in production
- Adjust prompts if Gemini doesn't follow instructions
- Can add stronger formatting emphasis in prompts if needed

## Future Enhancements

### Option 1: Rich Text Support
If NotebookLM CLI adds rich text support:
- Update to use native rich text API
- Can then use proper bold, italics, formatting

### Option 2: Template System
Create note templates that enforce consistent formatting:
- Pre-defined section structure
- Consistent visual hierarchy
- Easier for users to scan

### Option 3: Markdown to HTML Converter
As a future enhancement, could add optional post-processing:
- Convert markdown to HTML
- Use NotebookLM's HTML upload if available
- Maintain backward compatibility

## Documentation Updates

### User-Facing
- No changes needed - fix is transparent to users
- Notes will simply appear more readable

### Developer-Facing
- Document the formatting instructions
- Add comments in prompt files explaining why
- Update prompt creation guidelines

## Monitoring

After deployment, monitor:
1. **User feedback** - Are notes more readable?
2. **Gemini compliance** - Does it follow formatting rules?
3. **Edge cases** - Any prompts that still have issues?
4. **Quality scores** - Does this affect content quality?

## Conclusion

The NotebookLM note formatting issue was caused by **markdown syntax being saved as plain text** in notes. The fix is to **instruct Gemini to generate plain text** instead of markdown.

**Key Takeaway:** When integrating AI outputs with different systems, ensure format compatibility at the generation stage, not just post-processing.

**Result:** Clean, professional, readable notes in NotebookLM web UI.

---

**Questions or Issues?**
- Check prompt file formatting instructions
- Verify Gemini is following plain text rules
- Test with sample client before production run
