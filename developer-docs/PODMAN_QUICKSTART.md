# Project APE - Podman Quick Start

**Get running in 5 minutes!**

---

## Step 1: Install Podman (2 minutes)

```bash
./podman-install.sh
```

**Or manually:**

```bash
# macOS
brew install podman
podman machine init
podman machine start

# RHEL/Fedora
sudo dnf install podman
```

---

## Step 2: Build Container (2 minutes)

```bash
./build-container.sh
```

This creates a container with:
- ✅ Python 3.13
- ✅ LibreOffice (PDF conversion)
- ✅ Node.js + NotebookLM CLI
- ✅ All Python dependencies

---

## Step 3: Configure (30 seconds)

Make sure you have:
- ✅ `vars.py` configured with your clients
- ✅ Client data in `Venella_2026/` directory
- ✅ NotebookLM authenticated: `notebooklm login`

---

## Step 4: Run! (30 seconds)

```bash
# Fast mode - all clients
./run-container.sh --mode fast

# Deep mode - single client
./run-container.sh --mode deep --clients merck_test
```

---

## Step 5: Monitor

**Dashboard:** http://localhost:8765

**Logs:**
```bash
podman logs -f project-ape
```

---

## Common Commands

```bash
# Build container
./build-container.sh

# Run fast mode
./run-container.sh --mode fast

# Run deep mode
./run-container.sh --mode deep --clients merck_test

# View logs
podman logs -f project-ape

# Stop container
podman stop project-ape

# Remove container
podman rm project-ape

# List containers
podman ps -a

# Enter container (debug)
podman exec -it project-ape /bin/bash
```

---

## Using Podman Compose

```bash
# Start services
podman-compose up

# Start in background
podman-compose up -d

# View logs
podman-compose logs -f

# Stop services
podman-compose down
```

---

## Troubleshooting

### "Podman not found"
```bash
./podman-install.sh
```

### "Image not found"
```bash
./build-container.sh
```

### "Port 8765 already in use"
```bash
lsof -i :8765
# Kill the process or use different port:
podman run -p 9000:8765 ...
```

### "Permission denied"
```bash
chmod +x *.sh
```

### "NotebookLM authentication failed"
```bash
# Login on host first
notebooklm login

# Verify credentials mounted
podman exec -it project-ape ls -la /home/apeuser/.notebooklm
```

---

## What's Different in Container?

| Aspect | Host | Container |
|--------|------|-----------|
| Dependencies | Manual install | Pre-installed |
| LibreOffice | System install | Included |
| Python version | Host version | 3.13 |
| Isolation | None | Complete |
| Cleanup | Manual | Auto (--rm) |

---

## Full Documentation

See `CONTAINER_GUIDE.md` for complete documentation including:
- Production deployment
- Systemd integration
- Security best practices
- Performance tuning
- CI/CD integration

---

**Questions?** See `CONTAINER_GUIDE.md` or run:
```bash
./run-container.sh --help
```

---

**You're ready to go!** 🚀
