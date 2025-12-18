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

- Raspberry Pi OS (latest version recommended)
- Python 3.7 or higher

## Quick Start - Installation

**For complete installation instructions, see [INSTALLATION.md](INSTALLATION.md)**

Quick overview:
1. Install system packages: `sudo apt-get install python3 python3-pip python3-tk python3-pil git`
2. Clone repository: `git clone https://github.com/JesseFPV/grocy_scanner.git`
3. Install dependencies: `pip3 install -r requirements.txt`
4. Start application: `python3 main.py`
5. Configure auto-start: See [INSTALLATION.md](INSTALLATION.md) section "Step 8"

## Raspberry Pi OS Installation

### Recommended: Light Install (Without Desktop)

For a Raspberry Pi that only runs this application, a **Light installation without desktop** is recommended. This saves resources and boots faster.

**Step 1: Install Raspberry Pi OS Light**
- Download Raspberry Pi OS Lite (without desktop) from [raspberrypi.org](https://www.raspberrypi.org/software/)
- Flash to SD card using Raspberry Pi Imager
- Enable SSH and configure WiFi (optional)

**Step 2: Install required system packages**

After first boot and login, install the required packages for Tkinter and X11:

```bash
# Update package list
sudo apt-get update

# Install X server and Tkinter dependencies
sudo apt-get install -y \
    xserver-xorg \
    xinit \
    python3-tk \
    python3-pil \
    python3-pil.imagetk \
    libxss1 \
    libgconf-2-4

# For touchscreen support (usually already present, but to be sure)
sudo apt-get install -y \
    xinput \
    x11-xserver-utils

# Install Python pip if not already installed
sudo apt-get install -y python3-pip
```

**Step 3: Configure auto-start (optional)**

If you want the application to start automatically on boot, see the [Systemd Service](#systemd-service) section below.

**Important notes for Light installation:**

- You need an **X server** for Tkinter GUI (this is installed in step 2)
- The application must run with `DISPLAY=:0` to use the touchscreen
- For auto-start on boot, you need to start an X server (see systemd service section)
- Touchscreen drivers are usually automatically detected by Raspberry Pi OS

**Step 4: Test the installation**

```bash
# Test if Tkinter works
python3 -c "import tkinter; print('Tkinter works!')"

# Test X server (start X server)
startx
# Press Ctrl+Alt+F1 to return to terminal when X starts
```

**Step 5: Start the application**

```bash
# Navigate to project directory
cd grocy_scanner

# Install Python dependencies
pip3 install -r requirements.txt

# Start the application (with X server)
DISPLAY=:0 python3 main.py
```

### Alternative: Full Install (With Desktop)

If you prefer a full desktop environment (for example, for debugging or other applications):

- Install Raspberry Pi OS with Desktop
- Tkinter is usually already installed
- Follow the normal installation steps below

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/JesseFPV/grocy_scanner.git
   cd grocy_scanner
   ```

2. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Make main.py executable:**
   ```bash
   chmod +x main.py
   ```

4. **Run the application:**
   ```bash
   python3 main.py
   ```

   Or if you want to run it from stdin (for barcode scanner input):
   ```bash
   python3 main.py < /dev/ttyUSB0
   ```
   
   Note: The exact device path for your USB scanner may vary. Check `/dev/input/` or use `dmesg` after plugging in the scanner.

## Configuration

On first run, the application will prompt you to enter:
- **Grocy Host**: The URL of your Grocy instance (e.g., `https://grocy.example.com`)
- **API Key**: Your Grocy API key (found in Grocy under Settings > API keys)

Configuration is saved to `config.json` in the project directory. This file is automatically ignored by git to protect your API key.

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

### Scanner not working
- Ensure the scanner is in keyboard emulation mode
- Check USB connection
- Try running with explicit input redirection: `python3 main.py < /dev/ttyUSB0`

### Connection to Grocy fails
- Verify your Grocy host URL is correct (include https://)
- Check that your API key is valid
- Ensure your Raspberry Pi can reach the Grocy server (network connectivity)

### Display issues
- If the UI doesn't fit properly, you can exit fullscreen with `Escape` and resize
- For better touch response, ensure your touchscreen drivers are properly installed

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

## Systemd Service (Auto-start on boot)

For a **Light installation without desktop**, you need to start an X server first. Here is a complete setup:

**1. Create an X server startup script:**

```bash
# Create a script to start X server
sudo nano /usr/local/bin/start-x.sh
```

Add this content:
```bash
#!/bin/bash
# Start X server on display :0
X -nolisten tcp :0 &
sleep 2
# Start the application
export DISPLAY=:0
cd /home/pi/grocy_scanner  # Adjust to your path
python3 main.py
```

Make it executable:
```bash
sudo chmod +x /usr/local/bin/start-x.sh
```

**2. Create a systemd service:**

```bash
sudo nano /etc/systemd/system/intake.service
```

Add this content (adjust paths to your situation):
```ini
[Unit]
Description=Intake Application
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/grocy_scanner
ExecStart=/usr/local/bin/start-x.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**3. Enable and start the service:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable intake.service

# Start the service now
sudo systemctl start intake.service

# Check status
sudo systemctl status intake.service
```

**For Full installation (with desktop):**

If you have a desktop environment, use the example service file (`grocy-scanner.service.example`) and adjust the path:

```bash
sudo cp grocy-scanner.service.example /etc/systemd/system/intake.service
sudo nano /etc/systemd/system/intake.service  # Adjust paths
sudo systemctl daemon-reload
sudo systemctl enable intake.service
sudo systemctl start intake.service
```

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
