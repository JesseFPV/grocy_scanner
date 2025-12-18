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

## Quick Start - Installatie

**Voor volledige installatie-instructies, zie [INSTALLATION.md](INSTALLATION.md)**

Kort overzicht:
1. Installeer systeem packages: `sudo apt-get install python3 python3-pip python3-tk python3-pil git`
2. Clone repository: `git clone https://github.com/JesseFPV/grocy_scanner.git`
3. Installeer dependencies: `pip3 install -r requirements.txt`
4. Start applicatie: `python3 main.py`
5. Configureer auto-start: Zie [INSTALLATION.md](INSTALLATION.md) sectie "Stap 8"

## Raspberry Pi OS Installation

### Recommended: Light Install (Without Desktop)

Voor een Raspberry Pi die alleen deze applicatie draait, is een **Light installatie zonder desktop** aanbevolen. Dit bespaart resources en boott sneller.

**Stap 1: Installeer Raspberry Pi OS Light**
- Download Raspberry Pi OS Lite (zonder desktop) van [raspberrypi.org](https://www.raspberrypi.org/software/)
- Flash naar SD kaart met Raspberry Pi Imager
- Maak SSH aan en configureer WiFi (optioneel)

**Stap 2: Installeer benodigde system packages**

Na eerste boot en login, installeer de benodigde packages voor Tkinter en X11:

```bash
# Update package list
sudo apt-get update

# Installeer X server en Tkinter dependencies
sudo apt-get install -y \
    xserver-xorg \
    xinit \
    python3-tk \
    python3-pil \
    python3-pil.imagetk \
    libxss1 \
    libgconf-2-4

# Voor touchscreen support (meestal al aanwezig, maar voor de zekerheid)
sudo apt-get install -y \
    xinput \
    x11-xserver-utils

# Installeer Python pip als het nog niet geïnstalleerd is
sudo apt-get install -y python3-pip
```

**Stap 3: Configureer auto-start (optioneel)**

Als je de applicatie automatisch wilt starten bij boot, zie de [Systemd Service](#systemd-service) sectie hieronder.

**Belangrijke notities voor Light installatie:**

- Je hebt een **X server** nodig voor Tkinter GUI (dit is geïnstalleerd in stap 2)
- De applicatie moet draaien met `DISPLAY=:0` om de touchscreen te gebruiken
- Voor auto-start bij boot moet je een X server starten (zie systemd service sectie)
- Touchscreen drivers worden meestal automatisch gedetecteerd door Raspberry Pi OS

**Stap 4: Test de installatie**

```bash
# Test of Tkinter werkt
python3 -c "import tkinter; print('Tkinter werkt!')"

# Test X server (start X server)
startx
# Druk Ctrl+Alt+F1 om terug te gaan naar terminal als X start
```

**Stap 5: Start de applicatie**

```bash
# Navigeer naar project directory
cd grocy_scanner

# Installeer Python dependencies
pip3 install -r requirements.txt

# Start de applicatie (met X server)
DISPLAY=:0 python3 main.py
```

### Alternative: Full Install (Met Desktop)

Als je liever een volledige desktop omgeving hebt (bijvoorbeeld voor debugging of andere applicaties):

- Installeer Raspberry Pi OS met Desktop
- Tkinter is meestal al geïnstalleerd
- Volg de normale installatie stappen hieronder

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

## Systemd Service (Auto-start bij boot)

Voor een **Light installatie zonder desktop**, moet je eerst een X server starten. Hier is een complete setup:

**1. Maak een X server startup script:**

```bash
# Maak een script om X server te starten
sudo nano /usr/local/bin/start-x.sh
```

Voeg dit toe:
```bash
#!/bin/bash
# Start X server op display :0
X -nolisten tcp :0 &
sleep 2
# Start de applicatie
export DISPLAY=:0
cd /home/pi/grocy_scanner  # Pas aan naar jouw pad
python3 main.py
```

Maak het uitvoerbaar:
```bash
sudo chmod +x /usr/local/bin/start-x.sh
```

**2. Maak een systemd service:**

```bash
sudo nano /etc/systemd/system/grocy-scanner.service
```

Voeg dit toe (pas paden aan naar jouw situatie):
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

**3. Activeer en start de service:**

```bash
# Herlaad systemd
sudo systemctl daemon-reload

# Activeer service (start bij boot)
sudo systemctl enable grocy-scanner.service

# Start de service nu
sudo systemctl start grocy-scanner.service

# Check status
sudo systemctl status grocy-scanner.service
```

**Voor Full installatie (met desktop):**

Als je een desktop omgeving hebt, gebruik dan het voorbeeld service bestand (`grocy-scanner.service.example`) en pas het pad aan:

```bash
sudo cp grocy-scanner.service.example /etc/systemd/system/grocy-scanner.service
sudo nano /etc/systemd/system/grocy-scanner.service  # Pas paden aan
sudo systemctl daemon-reload
sudo systemctl enable grocy-scanner.service
sudo systemctl start grocy-scanner.service
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
