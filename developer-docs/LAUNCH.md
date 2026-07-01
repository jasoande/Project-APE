# How to Launch Project APE Workflows

## Quick Start

After configuring your clients in `vars.py`, launch a workflow:

```bash
./run-workflow.sh fast
```

The dashboard at http://localhost:8765 will show real-time progress.

## Launch Methods

### Method 1: Using the Launcher Script (Recommended)

The `run-workflow.sh` script automatically uses the correct Python virtual environment:

```bash
# Fast mode - all clients (15-20 min total)
./run-workflow.sh fast

# Deep mode - all clients (35-40 min total)  
./run-workflow.sh deep

# Specific clients only
./run-workflow.sh fast merck organon

# Force refresh Google Drive cache
./run-workflow.sh fast --refresh
```

### Method 2: Manual with Virtual Environment

```bash
# Activate virtual environment
source ~/.project-ape-venv/bin/activate

# Run main.py
python3 main.py --mode fast

# Deactivate when done
deactivate
```

### Method 3: Docker Container

```bash
# Uses containerized environment
./launch_ape.sh fast
```

## Common Issues

### ❌ "No module named 'dotenv'"

**Problem:** Running `python3 main.py` with system Python instead of virtual environment.

**Solution:** Use `./run-workflow.sh` or activate the virtual environment first:
```bash
source ~/.project-ape-venv/bin/activate
python3 main.py --mode fast
```

### ❌ "No clients defined"

**Problem:** Missing or empty `vars.py` configuration.

**Solution:** Configure clients using web UI or copy template:
```bash
# Option 1: Web UI
python3 dashboard/server.py
# Open http://localhost:8765/configure

# Option 2: Manual
cp example-vars.py vars.py
nano vars.py
```

### ❌ Dashboard shows "0 clients"

**Problem:** Dashboard is running but no workflow has been started.

**Solution:** The dashboard only displays status - launch a workflow with `./run-workflow.sh fast`

## Workflow Modes

| Mode | Duration | Use Case |
|------|----------|----------|
| `fast` | 15-20 min per client | Quick research, initial planning |
| `deep` | 35-40 min per client | Thorough analysis, comprehensive reports |
| `update` | 5-10 min per client | Refresh existing notebooks with new data |

## Monitoring Progress

The dashboard automatically opens at http://localhost:8765 and shows:

- ✅ **Real-time progress** - Current step for each client
- 📊 **Quality scores** - Automated validation (1-10 scale)
- 📝 **Live logs** - Streaming output from each process
- 🔗 **NotebookLM links** - Direct access to generated notebooks

## Next Steps

After launch:
1. Monitor progress in the dashboard
2. Click NotebookLM links when clients complete
3. Review quality scores and artifacts
4. Export or share the research notebooks

For detailed configuration options, see [README.md](README.md)
