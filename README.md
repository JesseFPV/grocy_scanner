# Intake

A Raspberry Pi-based barcode scanner interface for Grocy inventory management. This application runs on a Raspberry Pi with a USB barcode scanner and a 7" touchscreen display, allowing you to quickly add or deduct stock by scanning barcodes.

## Features

- **Touch-friendly UI**: Large buttons optimized for 7" touchscreen displays
- **Three Actions**: Add to stock, open product, or deduct from stock with a single tap
- **Visual Feedback**: Shows product name, image, and updated stock quantity on success
- **Error Handling**: Clear error messages when barcodes are not found
- **Easy Configuration**: First-run setup dialog for Grocy host and API key
- **USB Barcode Scanner Support**: Works with any USB barcode scanner that emulates keyboard input
- **Customizable UI**: Easy theme customization via `theme.py` - change colors, fonts, and sizes

## Hardware Requirements

- Raspberry Pi (Zero 2W, 3B, 4B, or 5)
- 7" Touchscreen Display (official Raspberry Pi display recommended)
- USB Barcode Scanner (keyboard emulation mode)

## Software Requirements

- Raspberry Pi OS Lite 64-bit (recommended)
- Python 3.7 or higher

## Installation

This guide covers installation on Raspberry Pi OS Lite 64-bit. The application requires an X server to run the GUI, which we'll install and configure.

### Step 1: Install Raspberry Pi OS Lite 64-bit

1. Download **Raspberry Pi OS Lite (64-bit)** from [raspberrypi.org](https://www.raspberrypi.org/software/)
2. Use Raspberry Pi Imager to flash the OS to your SD card
3. During the imaging process, configure:
   - **SSH**: Enable SSH access (recommended)
   - **WiFi**: Configure WiFi credentials (optional but recommended)
   - **User**: Set up your user account (default is `pi`)
4. Insert the SD card into your Raspberry Pi and boot it

### Step 2: Update System and Install X Server

Connect to your Raspberry Pi via SSH or directly, then run:

```bash
# Update package list and upgrade system
sudo apt-get update
sudo apt-get upgrade -y

# Install X server and required dependencies
sudo apt-get install -y \
    xserver-xorg \
    xinit \
    openbox \
    python3 \
    python3-pip \
    python3-venv \
    python3-tk \
    python3-pil \
    python3-pil.imagetk \
    libxss1 \
    libgconf-2-4 \
    xinput \
    x11-xserver-utils \
    x11-xserver-utils \
    git

# Verify X server installation
which X
```

**Note:** The `xinit` package provides the `startx` command, which we'll use to start the X server.

### Step 3: Download Project from GitHub

```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/JesseFPV/grocy_scanner.git

# Navigate into the project directory
cd grocy_scanner
```

**Note:** If you're using a fork or different repository, adjust the URL accordingly.

### Step 4: Create Virtual Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Verify venv was created
ls -la venv/bin/python
```

**Why use a virtual environment?**
- Raspberry Pi OS uses an "externally managed" Python environment
- A virtual environment isolates project dependencies
- Prevents conflicts with system Python packages

### Step 5: Install Required Packages

```bash
# Activate the virtual environment
source venv/bin/activate

# Upgrade pip (recommended)
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

You should see packages like `requests` and `Pillow` installed in the virtual environment.

### Step 6: Test the Installation

Before setting up auto-start, let's test that everything works:

```bash
# Make sure venv is activated
source venv/bin/activate

# Test Tkinter (should work without errors)
python3 -c "import tkinter; print('Tkinter works')"

# Start X server in background
startx &

# Wait a few seconds for X server to initialize
sleep 3

# Set DISPLAY variable and start the application
export DISPLAY=:0
python main.py
```

The application should start and show the configuration dialog. Press `Escape` to exit.

**Troubleshooting:**
- If you get "no display name and no $DISPLAY", make sure you've set `export DISPLAY=:0`
- If `startx` is not found, ensure `xinit` is installed: `sudo apt-get install xinit`
- If the application doesn't start, check logs: `journalctl -u intake.service -n 50` (after setting up the service)

### Step 7: Configure the Application

On first run, the application will prompt you to enter:
- **Grocy Host**: The URL of your Grocy instance (e.g., `https://grocy.example.com`)
- **API Key**: Your Grocy API key (found in Grocy under Settings > API keys)

Configuration is saved to `config.json` in the project directory. This file is automatically ignored by git to protect your API key.

### Step 8: Set Up Auto-Start on Boot

To automatically start Intake when your Raspberry Pi boots, we'll create a systemd service that starts the X server and the application.

#### 8.1: Install Openbox Window Manager

Openbox is a lightweight window manager that we'll use to run the application in kiosk mode:

```bash
sudo apt-get install -y openbox
```

#### 8.2: Create Openbox Autostart Script

Create the Openbox autostart script that will launch Intake:

```bash
# Create Openbox config directory
mkdir -p /home/pi/.config/openbox

# Create autostart script
nano /home/pi/.config/openbox/autostart
```

Add the following content:

```bash
#!/bin/sh

# Disable screen blanking
xset -dpms
xset s off
xset s noblank

# Start Intake app
cd /home/pi/grocy_scanner
source venv/bin/activate
exec python main.py
```

Make it executable:

```bash
chmod +x /home/pi/.config/openbox/autostart
```

#### 8.3: Create Startup Script

Create a script that starts X server with Openbox on tty1:

```bash
# Create the startup script
sudo nano /usr/local/bin/start-intake.sh
```

Add the following content (adjust paths if your username or project location differs):

```bash
#!/usr/bin/env bash
# Intake kiosk startup script
# Starts X on tty1 and launches the Intake Tkinter app

set -e

APP_DIR="/home/pi/grocy_scanner"
VENV_DIR="$APP_DIR/venv"
LOG_FILE="$APP_DIR/intake.log"

# Log helper
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

log "==== Intake startup ===="

# Safety: ensure correct user
if [ "$(id -u)" = "0" ]; then
    log "ERROR: Script must not run as root"
    exit 1
fi

# Ensure app directory exists
if [ ! -d "$APP_DIR" ]; then
    log "ERROR: App directory not found: $APP_DIR"
    exit 1
fi

cd "$APP_DIR"

# Ensure virtual environment exists
if [ ! -f "$VENV_DIR/bin/python" ]; then
    log "ERROR: venv not found at $VENV_DIR"
    exit 1
fi

log "Activating virtual environment"
source "$VENV_DIR/bin/activate"

# Export minimal environment for X / Tkinter
export HOME="/home/pi"
export USER="pi"
export DISPLAY=":0"
export XAUTHORITY="$HOME/.Xauthority"

# Create Xauthority if missing
touch "$XAUTHORITY"
chmod 600 "$XAUTHORITY"

log "Starting X via startx on tty1"

# Start X and keep VT
exec startx /usr/bin/openbox-session -- :0 vt1 -keeptty
```

Make the script executable and set proper ownership:

```bash
sudo chmod +x /usr/local/bin/start-intake.sh
sudo chown pi:pi /usr/local/bin/start-intake.sh
```

#### 8.4: Create Systemd Service

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/intake.service
```

Add the following content (adjust `User=` if your username is different):

```ini
[Unit]
Description=Intake Application (kiosk)
After=getty@tty1.service network.target
Wants=getty@tty1.service

[Service]
User=pi
WorkingDirectory=/home/pi/grocy_scanner
Environment=HOME=/home/pi
Environment=DISPLAY=:0

StandardInput=tty
TTYPath=/dev/tty1
TTYReset=yes
TTYVHangup=yes
TTYVTDisallocate=yes

ExecStart=/usr/local/bin/start-intake.sh
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
```

**Important notes about this service configuration:**
- `TTYPath=/dev/tty1` - Runs on virtual terminal 1 (the physical display)
- `After=getty@tty1.service` - Waits for tty1 to be ready
- `Restart=on-failure` - Only restarts on failure, not on normal exit
- `StandardInput=tty` - Connects to the terminal for proper X server operation

#### 8.5: Enable and Start the Service

```bash
# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable intake.service

# Start the service now (don't wait for reboot)
sudo systemctl start intake.service

# Check the service status
sudo systemctl status intake.service
```

The service should now be running. After rebooting your Raspberry Pi, Intake will start automatically.

#### 8.6: Useful Service Commands

```bash
# View service status
sudo systemctl status intake.service

# View service logs
sudo journalctl -u intake.service -f

# Stop the service
sudo systemctl stop intake.service

# Start the service
sudo systemctl start intake.service

# Restart the service
sudo systemctl restart intake.service

# Disable auto-start (but keep service file)
sudo systemctl disable intake.service
```

## Usage

1. **Start the application** - The UI will appear in fullscreen mode
2. **Select an action** - Tap one of three options:
   - **Add to Stock**: Add a new product to inventory
   - **Open Product**: Mark a product as opened (e.g., opening a bottle of cola)
   - **Deduct from Stock**: Remove/consume a product completely
3. **Scan a barcode** - Use your USB barcode scanner to scan a product barcode
4. **View results** - Success shows product info and new stock level; errors show clear messages

### Keyboard Shortcuts

- `Escape`: Exit fullscreen mode
- `⚙️ Config` button: Access configuration dialog

## USB Barcode Scanner Setup

Most USB barcode scanners work in "keyboard emulation" mode, which means they send scanned data as if typed on a keyboard. The application captures this input automatically.

If your scanner doesn't work automatically, you may need to:
1. Check that the scanner is recognized: `lsusb` or `dmesg | tail`
2. Ensure the scanner is in keyboard emulation mode (check scanner manual)
3. Test scanner input: `cat /dev/input/event*` (may require sudo)

## Troubleshooting

### Service not starting

1. **Check service status:**
   ```bash
   sudo systemctl status intake.service
   ```

2. **View systemd logs for errors:**
   ```bash
   sudo journalctl -u intake.service -n 100 --no-pager
   ```

3. **Check application log file (most important!):**
   ```bash
   # View the log file
   cat /home/pi/grocy_scanner/intake.log
   
   # Or follow it in real-time
   tail -f /home/pi/grocy_scanner/intake.log
   ```
   
   **This log file will show you exactly where the script is failing.**

4. **Verify paths are correct:**
   ```bash
   # Check project directory exists
   ls -la /home/pi/grocy_scanner
   
   # Verify venv exists
   ls -la /home/pi/grocy_scanner/venv/bin/python
   
   # Ensure script is executable
   ls -la /usr/local/bin/start-intake.sh
   ```

5. **Test script manually (as pi user):**
   ```bash
   sudo -u pi /usr/local/bin/start-intake.sh
   ```
   
   **Note:** This will block your terminal. Press Ctrl+C to stop it.

6. **Test X server separately:**
   ```bash
   # As pi user, test X server
   sudo -u pi X -nolisten tcp :0 &
   sleep 3
   sudo -u pi DISPLAY=:0 xdpyinfo
   ```

7. **Common issues and fixes:**
   
   **Issue: Permission denied**
   ```bash
   # Fix script permissions
   sudo chmod +x /usr/local/bin/start-intake.sh
   sudo chown pi:pi /usr/local/bin/start-intake.sh
   ```
   
   **Issue: X server already running**
   ```bash
   # Kill existing X server
   sudo pkill X
   # Then restart service
   sudo systemctl restart intake.service
   ```
   
   **Issue: Virtual environment not found**
   ```bash
   # Recreate venv
   cd /home/pi/grocy_scanner
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   
   **Issue: Tkinter not available**
   ```bash
   # Reinstall python3-tk
   sudo apt-get install --reinstall python3-tk
   ```

### Display issues

**Error: "no display name and no $DISPLAY"**
- **Solution:** The DISPLAY variable must be set. Ensure your startup script includes `export DISPLAY=:0`
- If testing manually, use: `export DISPLAY=:0` before running `python main.py`

**X server not starting**

This is common when running via SSH. The solution is to use `startx` with Openbox on a virtual terminal (tty1).

**Solution: Use startx with Openbox (as documented in installation)**
```bash
# Ensure Openbox is installed
sudo apt-get install openbox

# Ensure autostart script exists and is executable
chmod +x /home/pi/.config/openbox/autostart

# Test manually (will block SSH session)
sudo -u pi startx /usr/bin/openbox-session -- :0 vt1 -keeptty
```

**If you see "Permission denied" for /dev/tty0:**
- This is normal when running via SSH
- The service configuration uses `TTYPath=/dev/tty1` which works correctly
- Make sure the service is configured as shown in Step 8.4

**Verify Openbox autostart:**
```bash
# Check autostart script exists
ls -la /home/pi/.config/openbox/autostart

# View autostart content
cat /home/pi/.config/openbox/autostart
```

### Scanner not working

- Ensure the scanner is in keyboard emulation mode
- Check USB connection: `lsusb`
- Verify scanner is recognized: `dmesg | tail`

### Connection to Grocy fails

- Verify your Grocy host URL is correct (include https://)
- Check that your API key is valid
- Ensure your Raspberry Pi can reach the Grocy server (network connectivity)
- Test connectivity: `ping grocy.example.com` (replace with your Grocy host)

### Virtual environment issues

**Error: "externally-managed-environment"**
- This means you need to use a virtual environment
- Follow Step 4 to create and activate the venv
- Always activate venv before running: `source venv/bin/activate`

**Packages not found**
- Ensure venv is activated: `source venv/bin/activate`
- Reinstall packages: `pip install -r requirements.txt`
- Verify packages: `pip list`

## Updating the Application

To update Intake to the latest version:

```bash
# Stop the service
sudo systemctl stop intake.service

# Navigate to project directory
cd ~/grocy_scanner

# Pull latest changes
git pull

# Activate venv and update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart the service
sudo systemctl start intake.service
```

## UI Customization

The UI can be easily customized by editing `theme.py`. You can change:
- Colors (background, buttons, status messages)
- Fonts (family, sizes, weights)
- Sizes and spacing (button sizes, padding, image sizes)
- Window settings (fullscreen, title)

See `UI_CUSTOMIZATION.md` for detailed instructions and examples.

### Quick Theme Change

To use a different theme, edit `ui.py` and change the import:
```python
# Default theme
from theme import Theme

# Portal/Aperture Science theme (modern, futuristic)
from themes.portal_theme import PortalTheme as Theme

# Or use an example theme
from themes.light_theme import LightTheme as Theme
from themes.large_font_theme import LargeFontTheme as Theme
from themes.dark_blue_theme import DarkBlueTheme as Theme
```

**Note:** The Portal theme is currently active by default and uses the Rajdhani font for a modern, futuristic look.

## Development

The project structure:
- `main.py`: Entry point and application initialization
- `config.py`: Configuration management
- `grocy_api.py`: Grocy API client
- `scanner.py`: USB barcode scanner input handling
- `ui.py`: Touch-friendly GUI interface
- `theme.py`: UI theme configuration (colors, fonts, sizes)
- `themes/`: Example theme files

## License

[Add your license here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
