# Troubleshooting Guide

## macOS: tkinter ModuleNotFoundError

Als je de fout krijgt: `ModuleNotFoundError: No module named '_tkinter'`, betekent dit dat tkinter niet beschikbaar is in je Python installatie.

### Oplossing 1: Installeer Tcl/Tk via Homebrew (Aanbevolen)

```bash
# Installeer Tcl/Tk
brew install python-tk

# Herstart je terminal of activeer je virtual environment opnieuw
deactivate
source .venv/bin/activate
```

### Oplossing 2: Gebruik Python.org Installer

Als Homebrew Python geen tkinter support heeft:

1. Download Python van [python.org](https://www.python.org/downloads/)
2. Installeer Python (dit bevat tkinter standaard)
3. Gebruik deze Python versie voor het project:

```bash
# Vind de Python.org installatie
/usr/local/bin/python3 --version  # of
/Library/Frameworks/Python.framework/Versions/3.x/bin/python3 --version

# Maak een nieuw virtual environment met deze Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Oplossing 3: Gebruik pyenv met tkinter support

```bash
# Installeer pyenv als je dat nog niet hebt
brew install pyenv

# Installeer Tcl/Tk
brew install tcl-tk

# Installeer Python met tkinter support
env PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$(brew --prefix tcl-tk)/include' --with-tcltk-libs='-L$(brew --prefix tcl-tk)/lib'" pyenv install 3.11.0

# Gebruik deze versie
pyenv local 3.11.0
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Verificatie

Test of tkinter werkt:

```bash
python3 -c "import tkinter; print('tkinter werkt!')"
```

Als dit geen fout geeft, werkt tkinter correct.

## Raspberry Pi: tkinter installatie

Op Raspberry Pi OS is tkinter meestal al geïnstalleerd. Als het ontbreekt:

```bash
sudo apt-get update
sudo apt-get install python3-tk
```

## Andere problemen

### Scanner werkt niet
- Controleer of de scanner in keyboard emulation mode staat
- Test met: `cat /dev/input/event*` (mogelijk sudo nodig)
- Zorg dat de applicatie focus heeft voor keyboard input

### Display problemen
- Controleer resolutie: `xrandr`
- Test fullscreen: druk op Escape om fullscreen te verlaten
- Controleer touchscreen drivers: `lsusb` en `dmesg | grep -i touch`

### Grocy API verbinding
- Controleer URL format: moet beginnen met `http://` of `https://`
- Test API key in browser: `https://jouw-grocy-url/api/system/info?GROCY-API-KEY=jouw-key`
- Controleer firewall/network instellingen

