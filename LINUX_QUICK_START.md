<div align="center">
  <img src="dashboard/static/kingkong.png" alt="Project APE - King Kong Logo" width="150"/>
</div>

# Linux Quick Start Guide

## Problem: Double-clicking scripts opens them in a text editor

This is normal Linux behavior. Most file managers (Nautilus, Dolphin, Thunar) default to opening executable scripts in a text editor for security reasons.

## Solution: Install Desktop Launcher

Run this **one-time setup**:

```bash
cd /path/to/project-ape
./install-linux-launcher.sh
```

Choose your preferred option:
- **1** = Desktop icon only
- **2** = Application menu only
- **3** = Both (recommended)

### After Installation

**Option you chose 1 or 3** (Desktop icon):
- Look for "Project APE" icon on your desktop
- Double-click to launch

**If you chose 2 or 3** (App menu):
- Press Super/Windows key
- Type "Project APE"
- Click the icon

## Alternative: Launch from Terminal

If you prefer terminal, no installation needed:

```bash
cd /path/to/project-ape
./launch-project-ape.sh
```

Or use the universal Python launcher:

```bash
cd /path/to/project-ape
python3 launch-project-ape.py
```

## Troubleshooting

### Desktop icon says "Untrusted Application"

Some desktop environments (GNOME) require you to trust the launcher:

1. Right-click the desktop icon
2. Select "Allow Launching" or "Trust and Launch"
3. Icon should now work with double-click

### Icon doesn't appear on desktop

Try these steps:

1. Check if Desktop directory exists:
   ```bash
   ls ~/Desktop/
   ```

2. If it doesn't exist, create it:
   ```bash
   mkdir -p ~/Desktop
   ```

3. Run installer again:
   ```bash
   ./install-linux-launcher.sh
   ```

### Want to configure file manager to run scripts directly?

**GNOME (Nautilus)**:
```
Files → Preferences → Behavior → Executable Text Files → "Run them"
```

**KDE (Dolphin)**:
```
Settings → Configure Dolphin → General → Confirmations
→ Enable "Confirm execution of files"
```

**XFCE (Thunar)**:
```
Edit → Preferences → Advanced
→ Check "Execute shell scripts when they are opened"
```

After this change, you can double-click `.sh` files directly without the desktop launcher.

## What the Installer Does

The installer creates a `.desktop` file (Linux application shortcut) that:
- Points to the Python launcher
- Sets proper execution permissions
- Registers with your desktop environment
- Adds an icon to desktop and/or app menu

This is the standard Linux way to create application shortcuts.

## Manual Installation (Advanced)

If you want to manually create the launcher:

```bash
# Create desktop file
cat > ~/.local/share/applications/project-ape.desktop << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Project APE
Comment=Account Planning Engine
Exec=python3 $(pwd)/launch-project-ape.py
Icon=applications-internet
Terminal=true
Categories=Development;Office;
Path=$(pwd)
EOF

# Make it executable
chmod +x ~/.local/share/applications/project-ape.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications

# Copy to desktop (optional)
cp ~/.local/share/applications/project-ape.desktop ~/Desktop/
chmod +x ~/Desktop/project-ape.desktop
```

## Summary

| Method | Setup Required | Double-Click? | Best For |
|--------|---------------|---------------|----------|
| Desktop Launcher | One-time install | ✅ Yes | GUI users |
| Terminal | None | ❌ No | Terminal users |
| File Manager Config | One-time config | ✅ Yes (for .sh files) | Power users |

**Recommendation**: Use the desktop launcher installer for the best experience.
