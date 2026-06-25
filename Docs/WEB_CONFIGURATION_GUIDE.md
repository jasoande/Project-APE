# Project APE Web Configuration Tool - User Guide

## Quick Start

The web configuration tool provides an easy, form-based interface to create and manage your Project APE client configurations without manually editing Python code.

### Accessing the Tool

1. Start the dashboard server:
   ```bash
   source ~/.project-ape-venv/bin/activate
   python3 dashboard/server.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:8765/configure
   ```

3. Or click the "⚙️ Configure Clients" button from the main dashboard.

## Creating a Configuration

### Step 1: Add Clients

1. Click the **"➕ Add Client"** button to add a new client
2. Multiple clients can be added for batch processing

### Step 2: Fill in Client Details

For each client, provide the following information:

#### Client Name (Required)
- **Description**: The display name for your client
- **Example**: `Merck`, `Blue Yonder`, `Acme Corporation`
- **Auto-Generated**: The system automatically creates a Python-safe client ID from this name
  - `Merck` → `merck`
  - `Blue Yonder` → `blue_yonder`
  - `Acme Corp Test` → `acme_corp_test`

#### Google Drive Folder URL or Local Path (Required)
- **Description**: Location of your client's source documents
- **Google Drive Format**: 
  ```
  https://drive.google.com/drive/folders/FOLDER_ID
  ```
- **Local Path Format**:
  ```
  /Users/yourusername/Documents/ClientFolder
  ```
  or
  ```
  /path/to/client/documents
  ```

**To get a Google Drive folder URL:**
1. Open Google Drive in your web browser
2. Navigate to the client's folder
3. Copy the full URL from your browser's address bar
4. Paste into the form

#### Industry (Optional)
- **Description**: The primary industry or sector
- **Examples**:
  - `pharmaceuticals and life sciences`
  - `supply chain and logistics software`
  - `financial services and asset management`
  - `aerospace and defense`
- **Auto-Detection**: Can be left empty - the system will use AI to detect the industry from document content

#### Subsegments (Optional)
- **Description**: Comma-separated list of specific business areas or focus topics
- **Examples**:
  - `drug discovery, clinical trials, manufacturing operations`
  - `demand planning, warehouse management, transportation optimization`
  - `wealth management, institutional investment, mutual funds`
- **Auto-Detection**: Can be left empty - the system will use AI to detect subsegments from document content

### Step 3: Validate Inputs

The form automatically validates:
- **Required fields**: Name and Folder must be filled
- **Drive URL format**: Checks that Google Drive URLs match the expected format
- **Duplicate names**: Warns if two clients would generate the same client ID

Look for:
- ✅ **Green checkmarks**: Valid input
- ❌ **Red borders**: Invalid input (hover or check error message below field)
- 💡 **Blue helper text**: Guidance about the field

### Step 4: Generate Configuration

1. Click the **"📥 Generate Configuration"** button
2. The system will:
   - Validate all client data
   - Check for duplicate client IDs
   - Generate a complete `vars.py` file
   - Validate the Python syntax
3. If successful:
   - A `vars.py` file will download to your Downloads folder
   - Success message appears at the top of the page

### Step 5: Deploy Configuration

1. **Backup your existing configuration** (recommended):
   ```bash
   cp vars.py vars.py.backup
   ```

2. **Replace the configuration file**:
   ```bash
   cp ~/Downloads/vars.py .
   ```
   or manually copy the downloaded file to your Project APE directory

3. **Validate the new configuration**:
   ```bash
   python -m py_compile vars.py
   ```
   If this succeeds with no output, your configuration is valid.

4. **Run the pipeline**:
   ```bash
   python main.py --mode fast --clients merck_test blue_yonder_test
   ```

## Field Descriptions

### Google Drive URL Format

**Supported Formats:**
```
# Standard format
https://drive.google.com/drive/folders/1zi3Jbvv9eWSg-F3IFZ0aOqsGMT2tqRen

# With user context (also works)
https://drive.google.com/drive/u/0/folders/1zi3Jbvv9eWSg-F3IFZ0aOqsGMT2tqRen

# Drive protocol (advanced)
drive://1zi3Jbvv9eWSg-F3IFZ0aOqsGMT2tqRen

# Local path (no Drive)
/Users/jasona/Documents/MerckDocs
```

**Where to find the folder ID:**
The folder ID is the long alphanumeric string after `/folders/` in the URL.

### Industry Classification

Choose industry categories that best describe your client's primary business:

**Common Industries:**
- Technology and Software
- Pharmaceuticals and Life Sciences
- Financial Services
- Manufacturing and Industrial
- Healthcare and Medical Devices
- Retail and Consumer Goods
- Energy and Utilities
- Aerospace and Defense
- Professional Services
- Education and Research

**Multi-Industry Clients:**
If a client operates in multiple industries, choose the dominant one and mention others in subsegments.

### Subsegments Guidelines

Subsegments help focus the AI's research and analysis. They should be:

**Specific**: `clinical trials` not just `healthcare`  
**Relevant**: Focus on areas where you want strategic insights  
**Comma-separated**: Use commas to separate distinct areas  
**3-5 topics**: More than 5 can dilute focus

**Good Examples:**
```
drug discovery, clinical trials, regulatory compliance
warehouse automation, last-mile delivery, supply chain visibility
cloud migration, API modernization, data analytics
```

**Avoid:**
```
# Too generic
technology, business, innovation

# Too many
research, development, manufacturing, sales, marketing, distribution, customer service, IT

# Too narrow
acetaminophen formulation protocols for tablet compression
```

## Troubleshooting

### Invalid Drive URL Format

**Error**: "Invalid Drive URL format. Expected: https://drive.google.com/drive/folders/FOLDER_ID"

**Solutions:**
1. Copy the URL directly from your browser's address bar while viewing the folder
2. Make sure you copied the entire URL including `https://`
3. Verify the URL contains `/folders/` followed by the folder ID
4. Check for extra characters or spaces at the end

### Download Not Working

**Problem**: Clicking "Generate Configuration" but no file downloads

**Solutions:**
1. **Check browser console** for JavaScript errors (F12 > Console tab)
2. **Try copying content**: On success, the generated content is shown - copy it manually
3. **Check browser pop-up blocker**: Allow downloads from localhost
4. **Use different browser**: Try Chrome, Firefox, or Safari

### Python Syntax Error in Generated File

**Error**: `SyntaxError` when running `python -m py_compile vars.py`

**Solutions:**
1. **Check for special characters** in client names or descriptions (quotes, backslashes)
2. **Re-generate** the configuration using the web tool
3. **Report the issue**: The tool should prevent syntax errors - this indicates a bug

### Pipeline Fails After Using Generated Config

**Error**: Pipeline errors or crashes after deploying new vars.py

**Checklist:**
1. ✅ **Backup exists**: `ls vars.py.backup` should show your backup
2. ✅ **Syntax valid**: `python -m py_compile vars.py` succeeds
3. ✅ **Google Drive access**: Ensure service account has access to folders
4. ✅ **NotebookLM authenticated**: Run `notebooklm status` to check
5. ✅ **Client data exists**: Verify folders contain PDF/document files

**To restore backup:**
```bash
cp vars.py.backup vars.py
```

### Duplicate Client IDs

**Error**: "Duplicate client IDs detected: merck, merck"

**Cause**: Two clients have names that generate the same ID:
- "Merck" and "Merck Test" both → `merck` (if auto-shortened)
- "Blue Yonder" and "BlueYonder" both → `blue_yonder`

**Solution**:
Make names more distinct:
- "Merck Alpha" and "Merck Beta"
- "Blue Yonder US" and "Blue Yonder EU"

## Best Practices

### Before Generating

1. **Plan your client list**: Know which clients you want to process
2. **Verify Drive access**: Ensure all folders are accessible
3. **Prepare industry info**: Have industry/subsegment info ready (optional but recommended)
4. **Backup existing config**: Always keep a backup before replacing vars.py

### During Configuration

1. **Use descriptive names**: "Merck Q2 2024" is better than "Client 1"
2. **Verify URLs immediately**: Use the real-time validation to catch errors early
3. **Be specific with subsegments**: Help the AI focus on relevant topics
4. **Review before generating**: Check all clients before clicking generate

### After Generating

1. **Validate syntax**: Always run `python -m py_compile vars.py`
2. **Test with one client**: `python main.py --mode fast --clients first_client_only`
3. **Monitor dashboard**: Watch http://localhost:8765 for progress
4. **Check quality scores**: Ensure generated plans meet quality thresholds (8.5+)

## Advanced Usage

### Local Folders vs. Google Drive

**Use Local Folders When:**
- Testing with sample data
- Working offline
- Files are already on your machine
- Want faster processing (no download time)

**Use Google Drive When:**
- Collaborating with team members
- Files change frequently
- Client provides Drive access
- Want automatic document updates

### Mixed Configuration

You can mix local and Drive clients in the same configuration:

**Client 1**: Drive folder for live client  
**Client 2**: Local folder for testing  
**Client 3**: Drive folder for production

### Industry Auto-Detection

If you leave industry/subsegments blank:
- **Requires**: ANTHROPIC_API_KEY or GEMINI_API_KEY in .env file
- **Process**: AI analyzes document filenames and content
- **Cost**: Small API fee per auto-detection
- **Accuracy**: Generally good but manual specification is more reliable

**When to use auto-detection:**
- Unknown or diverse industries
- Quick tests or experiments
- Want AI to discover themes

**When to specify manually:**
- Known industries
- Production runs
- Want precise control

## Getting Help

### Web Tool Issues
- Check browser console (F12 > Console)
- Verify dashboard server is running: `lsof -i :8765`
- Review dashboard logs: `/tmp/dashboard_test.log`

### Configuration Issues
- Validate syntax: `python -m py_compile vars.py`
- Compare with example: `diff vars.py example-vars.py`
- Check Python path issues: `python3 -c "import vars; print(vars.clients)"`

### Pipeline Issues
- See main Project APE documentation
- Check logs in `logs/` directory
- Monitor dashboard for specific error messages

### Support
- GitHub Issues: [Report problems](https://github.com/jasoande/Project-APE/issues)
- Documentation: See `developer-docs/` for technical details
- Examples: Check `developer-docs/example-multi-client-vars.py`

## Examples

### Single Client - Pharmaceutical Company

```
Client Name: Merck
Folder: https://drive.google.com/drive/folders/1zi3Jbvv9eWSg-F3IFZ0aOqsGMT2tqRen
Industry: pharmaceuticals and life sciences
Subsegments: drug discovery, clinical trials, manufacturing operations
```

### Multiple Clients - Various Industries

```
Client 1:
  Name: Blue Yonder
  Folder: https://drive.google.com/drive/folders/1GnoQMM8ZK-0PSZElLIWa2z_3fy1TpoBK
  Industry: supply chain and logistics software
  Subsegments: demand planning, warehouse management, transportation optimization

Client 2:
  Name: Lord Abbett
  Folder: https://drive.google.com/drive/folders/1sk7oh0jKkANG1vHuXwWjkZEiqpAeAcRI
  Industry: asset management and investment services
  Subsegments: mutual funds, wealth management, institutional investment strategies
```

### Local Folder - Testing

```
Client Name: Test Client
Folder: /Users/jasona/Documents/TestData
Industry: (leave blank for auto-detection)
Subsegments: (leave blank for auto-detection)
```

---

**Version**: Phase 1 MVP  
**Last Updated**: June 2026  
**Related Docs**: 
- [README.md](../README.md) - Main Project APE documentation
- [GETTING-STARTED.md](../developer-docs/GETTING-STARTED.md) - Setup guide
- [example-vars.py](../example-vars.py) - Configuration template
