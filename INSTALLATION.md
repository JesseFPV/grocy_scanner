# Installatie Instructies voor Raspberry Pi

Deze gids helpt je om Intake te installeren op een Raspberry Pi en automatisch bij boot te laten starten.

## Vereisten

- Raspberry Pi (Zero 2W, 3B, 4B, of 5)
- Raspberry Pi OS (Desktop of Lite)
- 7" Touchscreen Display (optioneel, maar aanbevolen)
- USB Barcode Scanner
- Internetverbinding voor installatie

## Stap 1: Raspberry Pi OS Installeren

1. Download Raspberry Pi OS van [raspberrypi.org](https://www.raspberrypi.org/software/)
2. Gebruik Raspberry Pi Imager om het OS naar je SD kaart te flashen
3. Configureer WiFi en SSH tijdens het flash proces (optioneel maar handig)
4. Start je Raspberry Pi op

## Stap 2: Systeem Updates

Log in op je Raspberry Pi (via SSH of direct) en voer uit:

```bash
# Update systeem packages
sudo apt-get update
sudo apt-get upgrade -y
```

## Stap 3: Installeer Benodigde Systeem Packages

### Voor Raspberry Pi OS met Desktop:

```bash
# Installeer Python en benodigde packages
sudo apt-get install -y python3 python3-pip python3-venv python3-tk python3-pil python3-pil.imagetk git
```

### Voor Raspberry Pi OS Lite (zonder Desktop):

```bash
# Installeer X server en GUI dependencies
sudo apt-get install -y \
    xserver-xorg \
    xinit \
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
    git
```

## Stap 4: Clone het Project

```bash
# Navigeer naar je home directory
cd ~

# Clone het repository (vervang met jouw repository URL)
git clone https://github.com/JesseFPV/grocy_scanner.git

# Of als je het lokaal hebt, kopieer het naar ~/grocy_scanner
# cd grocy_scanner
```

**Let op:** Pas de repository URL aan naar jouw eigen repository als je een fork hebt gemaakt.

## Stap 5: Maak Virtual Environment en Installeer Dependencies

**Belangrijk:** Nieuwere versies van Raspberry Pi OS gebruiken een "externally managed" Python omgeving. We moeten daarom een virtual environment gebruiken.

```bash
# Navigeer naar project directory
cd ~/grocy_scanner

# Maak een virtual environment
python3 -m venv venv

# Activeer de virtual environment
source venv/bin/activate

# Installeer Python packages in de venv
pip install -r requirements.txt
```

**Let op:** Elke keer dat je de applicatie handmatig start, moet je eerst de venv activeren:
```bash
source venv/bin/activate
python main.py
```

## Stap 6: Test de Installatie

### Voor Desktop versie:

```bash
# Test of alles werkt
cd ~/grocy_scanner

# Activeer virtual environment
source venv/bin/activate

# Start de applicatie
python main.py
```

De applicatie zou moeten starten. Druk `Escape` om te sluiten.

### Voor Lite versie:

```bash
# Start X server eerst
startx &

# Wacht een paar seconden, dan start de applicatie
sleep 3
cd ~/grocy_scanner

# Activeer virtual environment
source venv/bin/activate

# Start de applicatie (met X server)
DISPLAY=:0 python main.py
```

## Stap 7: Configureer de Applicatie

Bij de eerste start wordt je gevraagd om:
- **Grocy Host URL**: Bijvoorbeeld `https://grocy.example.com`
- **API Key**: Je Grocy API key (te vinden in Grocy onder Settings > API keys)

Deze configuratie wordt opgeslagen in `config.json` in de project directory.

## Stap 8: Automatisch Starten bij Boot

### Optie A: Met Desktop Omgeving (Aanbevolen voor beginners)

1. **Maak een systemd service:**

```bash
# Kopieer het voorbeeld service bestand
sudo cp ~/grocy_scanner/grocy-scanner.service.example /etc/systemd/system/intake.service

# Bewerk het service bestand
sudo nano /etc/systemd/system/intake.service
```

2. **Pas het service bestand aan:**

Zorg dat de volgende regels correct zijn (pas paden aan indien nodig):

```ini
[Unit]
Description=Intake Application
After=network.target graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/grocy_scanner
Environment=DISPLAY=:0
ExecStart=/home/pi/grocy_scanner/venv/bin/python /home/pi/grocy_scanner/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
```

**Belangrijk:** Zorg dat `ExecStart` verwijst naar de Python executable in de venv (`venv/bin/python`), niet naar de systeem Python.

**Belangrijk:** 
- Vervang `pi` met jouw gebruikersnaam als die anders is
- Vervang `/home/pi/grocy_scanner` met het juiste pad naar je project

3. **Activeer en start de service:**

```bash
# Herlaad systemd configuratie
sudo systemctl daemon-reload

# Activeer service (start automatisch bij boot)
sudo systemctl enable intake.service

# Start de service nu
sudo systemctl start intake.service

# Controleer de status
sudo systemctl status intake.service
```

### Optie B: Zonder Desktop (Lite versie)

1. **Maak een startup script:**

```bash
# Maak het script
sudo nano /usr/local/bin/start-intake.sh
```

Voeg dit toe (pas paden aan):

```bash
#!/bin/bash
# Start X server op display :0
X -nolisten tcp :0 &
sleep 3

# Wacht tot X server klaar is
export DISPLAY=:0

# Navigeer naar project directory
cd /home/pi/grocy_scanner  # Pas aan naar jouw pad

# Activeer virtual environment en start de applicatie
source venv/bin/activate
python main.py
```

Maak het script uitvoerbaar:

```bash
sudo chmod +x /usr/local/bin/start-intake.sh
```

2. **Maak een systemd service:**

```bash
sudo nano /etc/systemd/system/intake.service
```

Voeg dit toe:

```ini
[Unit]
Description=Intake Application
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/start-intake.sh
Restart=always
RestartSec=10
Environment=DISPLAY=:0

[Install]
WantedBy=multi-user.target
```

3. **Activeer en start de service:**

```bash
# Herlaad systemd
sudo systemctl daemon-reload

# Activeer service
sudo systemctl enable intake.service

# Start de service
sudo systemctl start intake.service

# Controleer status
sudo systemctl status intake.service
```

## Stap 9: Verificatie

Na het opnieuw opstarten van je Raspberry Pi zou de applicatie automatisch moeten starten:

```bash
# Herstart de Raspberry Pi
sudo reboot
```

Na het opstarten zou je de Intake interface moeten zien op je scherm.

## Handige Commando's

```bash
# Bekijk service status
sudo systemctl status intake.service

# Stop de service
sudo systemctl stop intake.service

# Start de service handmatig
sudo systemctl start intake.service

# Herstart de service
sudo systemctl restart intake.service

# Bekijk logs
sudo journalctl -u intake.service -f

# Deactiveer auto-start (maar stop niet)
sudo systemctl disable intake.service
```

## Troubleshooting

### De applicatie start niet automatisch

1. **Controleer service status:**
   ```bash
   sudo systemctl status intake.service
   ```

2. **Bekijk logs voor fouten:**
   ```bash
   sudo journalctl -u intake.service -n 50
   ```

3. **Controleer of paden correct zijn:**
   - Zorg dat het pad naar `main.py` klopt
   - Zorg dat de gebruiker (`User=pi`) correct is
   - Zorg dat `WorkingDirectory` correct is

### X server start niet (Lite versie)

1. **Test X server handmatig:**
   ```bash
   X -nolisten tcp :0 &
   ```

2. **Controleer of X server draait:**
   ```bash
   ps aux | grep X
   ```

### Touchscreen werkt niet

1. **Controleer touchscreen drivers:**
   ```bash
   xinput list
   ```

2. **Test touchscreen:**
   ```bash
   DISPLAY=:0 xinput test <device-id>
   ```

### Barcode scanner werkt niet

1. **Controleer of scanner wordt herkend:**
   ```bash
   lsusb
   dmesg | tail
   ```

2. **Test scanner input:**
   ```bash
   cat /dev/input/event0  # Vervang event0 met jouw device
   ```

### Applicatie crasht bij start

1. **Test handmatig:**
   ```bash
   cd ~/grocy_scanner
   python3 main.py
   ```

2. **Controleer Python dependencies:**
   ```bash
   pip3 list | grep -E "requests|Pillow"
   ```

3. **Herinstalleer dependencies:**
   ```bash
   pip3 install -r requirements.txt --force-reinstall
   ```

## Veelvoorkomende Problemen

### Probleem: "Permission denied" bij service start

**Oplossing:** 
1. Zorg dat het script uitvoerbaar is:
   ```bash
   sudo chmod +x /usr/local/bin/start-intake.sh
   ```
2. Controleer of venv bestaat en toegankelijk is:
   ```bash
   ls -la ~/grocy_scanner/venv/bin/python
   ```

### Probleem: "externally-managed-environment" error bij pip install

**Oplossing:** Dit betekent dat je een virtual environment moet gebruiken. Volg Stap 5 opnieuw:
```bash
cd ~/grocy_scanner
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Probleem: Service start maar applicatie verschijnt niet

**Oplossing:** 
1. Controleer of DISPLAY correct is ingesteld:
   - Voor Desktop: `Environment=DISPLAY=:0`
   - Voor Lite: Zorg dat X server draait voordat applicatie start
2. Controleer of het venv pad correct is in ExecStart:
   - Moet zijn: `/home/pi/grocy_scanner/venv/bin/python`
   - Niet: `/usr/bin/python3`

### Probleem: Service crasht direct na start

**Oplossing:** 
1. Bekijk logs: `sudo journalctl -u intake.service -n 50`
2. Test handmatig: 
   ```bash
   cd ~/grocy_scanner
   source venv/bin/activate
   python main.py
   ```
3. Controleer of venv bestaat: `ls -la ~/grocy_scanner/venv/bin/python`
4. Controleer of alle dependencies geïnstalleerd zijn in de venv:
   ```bash
   source venv/bin/activate
   pip list
   ```

## Aanpassen van Configuratie

Als je de applicatie configuratie wilt aanpassen:

1. **Handmatig bewerken:**
   ```bash
   nano ~/grocy_scanner/config.json
   ```

2. **Of via de applicatie:**
   - Start de applicatie
   - Klik op het ⚙️ configuratie icoon
   - Voer nieuwe gegevens in

## Updates Installeren

Om de applicatie bij te werken:

```bash
cd ~/grocy_scanner

# Stop de service eerst
sudo systemctl stop intake.service

# Pull nieuwe wijzigingen
git pull

# Installeer nieuwe dependencies (indien nodig)
pip3 install -r requirements.txt

# Start de service opnieuw
sudo systemctl start intake.service
```

## Veiligheid

- De `config.json` bevat je API key - deel dit bestand nooit
- Zorg dat je firewall correct is geconfigureerd
- Overweeg om SSH alleen via key-based authenticatie toe te staan

## Ondersteuning

Als je problemen ondervindt:
1. Controleer de logs: `sudo journalctl -u intake.service`
2. Test handmatig: `cd ~/grocy_scanner && python3 main.py`
3. Controleer de README.md voor meer informatie

