# Container Cleanup Fix
**Date:** June 25, 2026

## Problem

After workflow completion, the Docker/Podman container remains running indefinitely because:
1. The Flask dashboard server runs forever (`app.run()`)
2. The main.py keeps dashboard running with infinite loop: `while True: time.sleep(60)`
3. Container has no auto-shutdown mechanism

This causes:
- Containers pile up and consume resources
- Manual cleanup required (`podman stop`, `podman rm`)
- Poor user experience

## Solution

### 1. Auto-Shutdown After 5 Minutes ✓
**File:** `main.py:352-362`

**Before:**
```python
# Keep dashboard running
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    pass
```

**After:**
```python
# Keep dashboard running for 5 minutes after completion
# This gives users time to review results before container shuts down
try:
    shutdown_delay = 300  # 5 minutes
    logger.info(f"   ⏰ Auto-shutdown in {shutdown_delay//60} minutes...")
    time.sleep(shutdown_delay)
    logger.info("\n⏰ Auto-shutdown timer expired. Stopping container...")
except KeyboardInterrupt:
    logger.info("\n⌨️  Ctrl+C detected. Stopping immediately...")
    pass
```

**Result:**
- Container automatically exits 5 minutes after workflow completes
- Users have time to review results
- No manual cleanup needed
- `--rm` flag in `launch_ape.sh:249` removes container on exit

### 2. API Shutdown Endpoint ✓
**File:** `dashboard/server.py:709-727`

Added `/api/shutdown` endpoint:
```python
@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    """Gracefully shutdown the server and container."""
    def delayed_shutdown():
        time.sleep(2)  # Give response time to send
        os._exit(0)  # Force exit the entire process
    
    threading.Thread(target=delayed_shutdown, daemon=True).start()
    return jsonify({'success': True, 'message': 'Server shutting down...'})
```

**Usage:**
- Dashboard can add a "Shutdown" button for immediate stop
- Future automation scripts can trigger shutdown via API
- Graceful 2-second delay allows response to send

### 3. Browser Caching Issue (Rocket Ship)

**Problem:** Rocket ship still shows in browser despite being removed from `launch.html`

**Cause:** Browser cached old version of HTML file

**Solution:**
1. **Hard refresh browser:** Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
2. **Restart Flask server** to clear any server-side caching
3. **Or add cache-busting header** to Flask app (optional)

### Optional: Add Cache-Busting Header

To prevent future caching issues, add to `dashboard/server.py`:

```python
@app.after_request
def add_header(response):
    """Disable caching for development."""
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
```

## Timeline

### Immediate (on workflow completion):
1. Pipeline completes
2. Summary printed to logs
3. **5-minute countdown starts**
4. Dashboard remains accessible for review

### After 5 minutes:
5. Auto-shutdown message logged
6. Python process exits
7. Container stops (due to exit)
8. Container removed (due to `--rm` flag)

### Manual shutdown anytime:
- Press Ctrl+C in terminal
- Call `/api/shutdown` endpoint
- Both trigger immediate cleanup

## Testing

1. **Start workflow:**
   ```bash
   ./launch_ape.sh fast
   ```

2. **Wait for completion:**
   - Verify summary appears in logs
   - Verify "Auto-shutdown in 5 minutes..." message

3. **Wait 5 minutes:**
   - Verify container exits automatically
   - Check with: `podman ps -a` (should not show project-ape)

4. **OR test immediate shutdown:**
   ```bash
   # Press Ctrl+C
   # OR
   curl -X POST http://localhost:8765/api/shutdown
   ```

## Benefits

✅ No more orphaned containers  
✅ Automatic resource cleanup  
✅ Better user experience  
✅ Container best practices followed  
✅ Graceful shutdown options  
✅ Configurable timeout (easily changed from 300s)

## Future Enhancements

1. Add environment variable for shutdown delay:
   ```python
   shutdown_delay = int(os.getenv('AUTO_SHUTDOWN_DELAY', 300))
   ```

2. Add "Shutdown Now" button in dashboard UI

3. Add container health check that stops when workflow done

4. Send notification before auto-shutdown (browser alert)
