# Phase 2 Web Configuration Tool - Quick Start Guide

**Last Updated**: June 24, 2026  
**Status**: Ready for Use ✅

---

## 🚀 Getting Started (2 Minutes)

### 1. Start the Dashboard Server

```bash
cd /Users/jasona/test/Project-APE-dev
source ~/.project-ape-venv/bin/activate
python3 dashboard/server.py
```

### 2. Open Your Browser

```
http://localhost:8765/configure
```

### 3. Choose Your Workflow

**Option A: Edit Existing Configuration**
1. Click "📂 Load Existing Configuration"
2. Edit any clients or settings
3. Click "💾 Save Configuration"

**Option B: Create New Configuration**
1. Click "➕ Add Client"
2. Fill in details
3. Click "💾 Save Configuration"

**Option C: Import from CSV**
1. Go to "Import/Export" tab
2. Upload CSV file
3. Review preview
4. Click "Add These Clients"
5. Click "💾 Save Configuration"

---

## 📚 Four Tabs Explained

### 👥 Clients Tab
**What it does**: Manage client configurations

**Key Features**:
- Load existing vars.py
- Add/remove clients
- Edit client details
- Save or download configuration

**When to use**: Adding, editing, or removing clients

---

### ⚙️ Global Settings Tab
**What it does**: Configure advanced settings

**Key Features**:
- Edit AI persona
- Choose fast/deep mode default
- Configure dashboard port
- Adjust timing profiles
- Configure Google Drive settings

**When to use**: Customizing behavior and performance

---

### 📥 Import/Export Tab
**What it does**: Bulk operations

**Key Features**:
- Import clients from CSV
- Export as CSV or JSON
- Preview before importing
- Validation and error reporting

**When to use**: Managing many clients or backing up configuration

---

### 👁️ Preview Tab
**What it does**: See generated vars.py

**Key Features**:
- Live preview (updates as you type)
- Copy to clipboard
- Syntax validation
- Full vars.py file view

**When to use**: Verifying changes before saving

---

## 🎯 Common Tasks

### Task: Load and Edit Existing Configuration

```
1. Click "Clients" tab
2. Click "📂 Load Existing Configuration"
   ✅ Your current vars.py loads
3. Edit any field
4. Click "💾 Save Configuration"
   ✅ Backup created automatically
   ✅ vars.py updated
```

**Time**: 30 seconds  
**Difficulty**: Easy ⭐

---

### Task: Add a New Client

```
1. Click "Clients" tab
2. Click "➕ Add Client"
3. Fill in:
   - Name: "Acme Corporation"
   - Folder: "https://drive.google.com/drive/folders/ABC123"
   - Industry: "technology"
   - Subsegments: "cloud computing, SaaS"
4. Click "💾 Save Configuration"
```

**Time**: 1 minute  
**Difficulty**: Easy ⭐

---

### Task: Change AI Persona

```
1. Click "Global Settings" tab
2. Edit "Persona" field
3. Change from "Red Hat solutions architect"
   to "account executive"
4. Preview tab shows updated code
5. Click "Clients" tab
6. Click "💾 Save Configuration"
```

**Time**: 30 seconds  
**Difficulty**: Easy ⭐

---

### Task: Adjust Timing Profiles

```
1. Click "Global Settings" tab
2. Click "⚡ Fast Mode Timings" to expand
3. Edit any timing value:
   - Example: Change "ask_prompt_delay" from "8.0, 12.0" to "10.0, 15.0"
4. See preview update automatically
5. Click "Clients" tab
6. Click "💾 Save Configuration"
```

**Time**: 1 minute  
**Difficulty**: Medium ⭐⭐

---

### Task: Import Clients from CSV

**1. Prepare CSV file** (clients.csv):
```csv
name,folder,industry,subsegments
Merck,https://drive.google.com/drive/folders/ABC,pharmaceuticals,"drug discovery, clinical trials"
Blue Yonder,https://drive.google.com/drive/folders/XYZ,supply chain software,demand planning
```

**2. Import**:
```
1. Click "Import/Export" tab
2. Click "📄 Choose CSV File"
3. Select your CSV file
4. Click "📥 Import Clients"
   ✅ Preview table appears
5. Review clients and errors
6. Click "✅ Add These Clients"
   ✅ Clients added
7. Click "Clients" tab
8. Click "💾 Save Configuration"
```

**Time**: 2 minutes  
**Difficulty**: Medium ⭐⭐

---

### Task: Export Configuration as Backup

```
1. Click "Import/Export" tab
2. Click "📄 Export as CSV" for clients only
   OR
   Click "📋 Export as JSON" for full config
3. File downloads automatically
```

**Time**: 10 seconds  
**Difficulty**: Easy ⭐

---

### Task: Preview Changes Before Saving

```
1. Make any edits (clients or settings)
2. Click "Preview" tab
   ✅ See generated vars.py code
3. Review the changes
4. Click "📋 Copy to Clipboard" if needed
5. Return to "Clients" tab
6. Click "💾 Save Configuration"
```

**Time**: 1 minute  
**Difficulty**: Easy ⭐

---

## 🔒 Safety Features

### Automatic Backups
Every save creates a backup:
```
vars.py.backup.20260624_163000
```

**Location**: Same directory as vars.py  
**Format**: vars.py.backup.YYYYMMDD_HHMMSS

---

### Syntax Validation
Before saving, the system:
1. Validates Python syntax
2. Checks required fields
3. Verifies no duplicates
4. Tests compilation

**If validation fails**:
- Backup is restored
- Error message shown
- vars.py unchanged

---

### Input Validation
The system validates:
- ✅ Required fields (name, folder)
- ✅ Drive URL format
- ✅ Duplicate client IDs
- ✅ Port numbers (1024-65535)
- ✅ CSV file format
- ✅ Settings data types

---

## 💡 Pro Tips

### Tip 1: Use Live Preview
**Why**: See changes instantly before saving  
**How**: Switch to Preview tab while editing  
**Benefit**: Catch errors early

---

### Tip 2: Export Before Major Changes
**Why**: Extra backup for safety  
**How**: Export as JSON before editing  
**Benefit**: Easy rollback if needed

---

### Tip 3: Import Template CSVs
**Why**: Faster bulk setup  
**How**: Create CSV templates for common client types  
**Benefit**: Consistent formatting

---

### Tip 4: Use Expandable Sections
**Why**: Cleaner interface  
**How**: Click headers to expand/collapse  
**Benefit**: Focus on what you're editing

---

### Tip 5: Test with Download First
**Why**: Safe way to test changes  
**How**: Use "📥 Download vars.py" instead of save  
**Benefit**: No risk to existing config

---

## 🚨 Troubleshooting

### Problem: "Configuration file not found"

**Cause**: No vars.py file exists yet

**Solution**:
1. Create first config using web tool
2. Click "📥 Download vars.py"
3. Move file to project root
4. Now you can use "Load" button

---

### Problem: "Validation errors" when saving

**Cause**: Missing or invalid data

**Solution**:
1. Read error message (shows specific issue)
2. Fix the highlighted problem
3. Common issues:
   - Empty client name
   - Invalid Drive URL format
   - Duplicate client names
4. Try saving again

---

### Problem: Preview not updating

**Cause**: JavaScript error

**Solution**:
1. Press F12 (open browser console)
2. Check for errors
3. Refresh page (Cmd+R or Ctrl+R)
4. Try again

---

### Problem: CSV import shows errors

**Cause**: Invalid CSV format

**Solution**:
1. Check CSV header: `name,folder,industry,subsegments`
2. Ensure name and folder are not empty
3. Quote fields with commas: `"drug discovery, clinical trials"`
4. Check error messages for specific line numbers
5. Fix and re-import

---

## 📖 CSV Format Reference

### Required Columns
```csv
name,folder,industry,subsegments
```

### Example with All Features
```csv
name,folder,industry,subsegments
Merck,https://drive.google.com/drive/folders/ABC123,pharmaceuticals,"drug discovery, clinical trials, manufacturing"
Blue Yonder,/local/path/to/folder,supply chain software,"demand planning, logistics"
Test Client,drive://XYZ789,technology,
```

### Rules
- **name**: Required, unique
- **folder**: Required, Drive URL or local path
- **industry**: Optional (leave empty for auto-detect)
- **subsegments**: Optional, comma-separated (quote if has commas)

---

## 🎓 Learning Path

### Level 1: Basic User (10 minutes)
1. ✅ Load existing configuration
2. ✅ Edit a client name
3. ✅ Save configuration
4. ✅ View preview

**Skills**: Load, edit, save

---

### Level 2: Regular User (20 minutes)
1. ✅ Add new clients
2. ✅ Remove clients
3. ✅ Edit global settings
4. ✅ Export as CSV

**Skills**: CRUD operations, settings

---

### Level 3: Power User (30 minutes)
1. ✅ Import from CSV
2. ✅ Customize timing profiles
3. ✅ Configure Drive settings
4. ✅ Use live preview
5. ✅ Manage backups

**Skills**: Bulk operations, advanced config

---

### Level 4: Expert (45 minutes)
1. ✅ Create configuration templates
2. ✅ Optimize timing profiles
3. ✅ Troubleshoot validation errors
4. ✅ Restore from backups
5. ✅ Export/import workflows

**Skills**: Mastery, troubleshooting

---

## 📊 Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Switch tabs | Click tab buttons |
| Copy preview | Click "Copy to Clipboard" |
| Open file picker | Click file input |
| Save | Click "Save Configuration" |

*Note: No custom keyboard shortcuts yet (Phase 3?)*

---

## 🔗 Related Documentation

- **PHASE2_COMPLETE.md** - Full technical documentation
- **PHASE2_PROGRESS.md** - Backend implementation details
- **WEB_CONFIGURATION_GUIDE.md** - Phase 1 user guide
- **README.md** - Project overview

---

## ❓ FAQ

### Q: Do I need to stop the pipeline before editing?
**A**: No, but it's recommended. The pipeline reads vars.py at startup.

### Q: Can multiple people edit at once?
**A**: No, this is a single-user tool. Last save wins.

### Q: What happens to my old vars.py?
**A**: Automatic backup created: `vars.py.backup.YYYYMMDD_HHMMSS`

### Q: Can I undo a save?
**A**: Manually restore from backup file

### Q: How do I delete a backup?
**A**: Manually delete the `vars.py.backup.*` files

### Q: What if I make a mistake?
**A**: Restore from automatic backup or re-load and start over

### Q: Can I edit the backup files?
**A**: Yes, they're regular vars.py files

### Q: What's the difference between Save and Download?
**A**: 
- **Save**: Writes directly to vars.py (creates backup)
- **Download**: Downloads file to browser (manual install)

---

## 🎉 Quick Wins

**1-Minute Win**: Load existing config → Edit client name → Save  
**5-Minute Win**: Import 5 clients from CSV → Save  
**10-Minute Win**: Customize all settings → Preview → Save

---

## 📞 Getting Help

**Built-in Help**:
- Hover over fields for tooltips
- Read help text below inputs
- Check error messages

**Documentation**:
- This guide (quick reference)
- PHASE2_COMPLETE.md (comprehensive)
- WEB_CONFIGURATION_GUIDE.md (Phase 1 details)

**Support**:
- Check browser console (F12) for errors
- Review error messages
- Check server logs

---

**Ready to use? Start here**: http://localhost:8765/configure

**Status**: ✅ Production Ready  
**Version**: Phase 2  
**Last Updated**: June 24, 2026
