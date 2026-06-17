# Project APE Launcher Guide

## Quick Start

The `launch_ape.sh` script makes it easy to run Project APE from anywhere, including the Gemini web interface.

## Usage Examples

### Run all clients in fast mode (default)
```bash
./launch_ape.sh fast
```

### Run all clients in deep mode
```bash
./launch_ape.sh deep
```

### Run specific clients in fast mode
```bash
./launch_ape.sh fast merck_test blue_yonder_test
```

### Run specific clients in deep mode
```bash
./launch_ape.sh deep organon_test
```

### Just use defaults (fast mode, all clients)
```bash
./launch_ape.sh
```

## Using from Gemini Web Interface

When working in the Gemini web console, you can simply say:

**"Run Project APE in fast mode"**
- Gemini will execute: `./launch_ape.sh fast`

**"Run Project APE in deep mode"**
- Gemini will execute: `./launch_ape.sh deep`

**"Run Project APE for Merck only in fast mode"**
- Gemini will execute: `./launch_ape.sh fast merck_test`

## What Happens

1. Script changes to Project APE directory
2. Displays configuration (mode, clients)
3. Launches `python main.py` with your parameters
4. Dashboard opens automatically in browser
5. All 6 clients run in parallel (or just the ones you specified)
6. Monitor progress in real-time dashboard

## Output

- **Dashboard:** http://localhost:8765
- **Logs:** `logs/[client_name].log`
- **Status Files:** `.multi_process_status/[client_name].json`

## Client Names

Use these exact names when specifying clients:
- `merck_test`
- `blue_yonder_test`
- `organon_test`
- `panasonic_avionics_test`
- `hershey_test`
- `lord_abbett_test`

## Modes

- **fast:** Optimized for speed (~15-20 min per client)
- **deep:** Enhanced research with longer timeouts (~35-40 min per client)

## Dashboard

The dashboard will automatically open in your browser showing:
- Real-time progress for each client
- Current step and status
- NotebookLM links (when notebooks are created)
- Quality scores (when complete)
- Completion status

## Stopping Execution

Press `Ctrl+C` in the terminal to stop all clients and shut down the dashboard.

## Next Steps After Completion

After the pipeline completes:
1. Check the dashboard for quality scores and NotebookLM links
2. Review logs for any warnings or issues
3. Open NotebookLM notebooks to see results
4. Each notebook will have:
   - Consolidated PDF source
   - 40+ research sources
   - 6 comprehensive notes
   - Interactive mind map

## Troubleshooting

**Dashboard doesn't open:**
- Manually visit: http://localhost:8765

**Pipeline fails:**
- Check logs in `logs/` directory
- Verify `.env` has GEMINI_API_KEY and GOOGLE_DRIVE_SERVICE_ACCOUNT_KEY
- Ensure NotebookLM CLI is authenticated: `notebooklm list`

**Quality scores show 5.0:**
- Known display bug - actual notebooks are fully populated
- Check NotebookLM web interface for real source counts (40-68 sources)
