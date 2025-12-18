# UI Aanpassen / Customization Guide

De UI kan eenvoudig worden aangepast via het `theme.py` bestand. Alle kleuren, lettertypes en afmetingen zijn daar gecentraliseerd.

## Snel Starten

Open `theme.py` en pas de waarden aan naar jouw voorkeur. De wijzigingen worden automatisch toegepast wanneer je de applicatie opnieuw start.

## Beschikbare Instellingen

### Kleuren

```python
# Achtergrond en tekst
BACKGROUND = '#2b2b2b'          # Achtergrondkleur
TEXT_PRIMARY = '#ffffff'         # Primaire tekstkleur (wit)
TEXT_SECONDARY = '#cccccc'       # Secundaire tekstkleur (lichtgrijs)

# Knoppen
BUTTON_ADD = '#4CAF50'           # Groene knop (Toevoegen)
BUTTON_ADD_ACTIVE = '#2e7d32'    # Donkergroen wanneer geselecteerd
BUTTON_ADD_HOVER = '#45a049'     # Hover kleur

BUTTON_DEDUCT = '#f44336'        # Rode knop (Aftrekken)
BUTTON_DEDUCT_ACTIVE = '#c62828' # Donkerrood wanneer geselecteerd
BUTTON_DEDUCT_HOVER = '#da190b'  # Hover kleur

BUTTON_CONFIG = '#555555'        # Config knop kleur
BUTTON_SAVE = '#4CAF50'          # Save knop kleur

# Status kleuren
STATUS_SUCCESS = '#4CAF50'       # Groen (succes)
STATUS_ERROR = '#f44336'         # Rood (fout)
STATUS_WARNING = '#ff9800'       # Oranje (waarschuwing)
STATUS_INFO = '#2196F3'          # Blauw (info)
```

### Lettertypes

```python
FONT_FAMILY = 'Arial'            # Lettertype familie
FONT_TITLE_SIZE = 32             # Titel grootte
FONT_BUTTON_SIZE = 24            # Knop tekst grootte
FONT_STATUS_SIZE = 20            # Status tekst grootte
FONT_INFO_SIZE = 18              # Info tekst grootte
```

### Afmetingen en Spacing

```python
BUTTON_WIDTH = 20                # Knop breedte
BUTTON_HEIGHT = 3                # Knop hoogte
BUTTON_BORDER_WIDTH = 5          # Rand dikte

PADDING_X = 20                   # Horizontale padding
PADDING_Y = 20                   # Verticale padding
TITLE_PADDING_BOTTOM = 30        # Ruimte onder titel
BUTTON_PADDING = 20              # Ruimte tussen knoppen
STATUS_PADDING = 20              # Ruimte rond status

PRODUCT_IMAGE_SIZE = (200, 200)  # Maximale productafbeelding grootte
TEXT_WRAP_LENGTH = 800           # Tekst wrap lengte
```

### Overige Instellingen

```python
FULLSCREEN = True                # Volledig scherm modus
WINDOW_TITLE = "Intake"   # Venster titel
STATUS_RESET_DELAY = 3000        # Delay voor status reset (milliseconden)
```

## Voorbeelden

### Lichte Thema

Maak een nieuw bestand `light_theme.py`:

```python
from theme import Theme

class LightTheme(Theme):
    BACKGROUND = '#f5f5f5'
    TEXT_PRIMARY = '#000000'
    TEXT_SECONDARY = '#333333'
    BUTTON_CONFIG = '#888888'
    STATUS_SUCCESS = '#2e7d32'
    STATUS_ERROR = '#c62828'
```

Gebruik het in `ui.py`:
```python
from light_theme import LightTheme as Theme
```

### Donker Blauw Thema

```python
from theme import Theme

class DarkBlueTheme(Theme):
    BACKGROUND = '#1a1a2e'
    BUTTON_ADD = '#00d4aa'
    BUTTON_DEDUCT = '#ff6b6b'
    TEXT_PRIMARY = '#ffffff'
    STATUS_SUCCESS = '#00d4aa'
    STATUS_ERROR = '#ff6b6b'
```

### Groot Lettertype voor Slecht Zicht

```python
from theme import Theme

class LargeFontTheme(Theme):
    FONT_TITLE_SIZE = 48
    FONT_BUTTON_SIZE = 32
    FONT_STATUS_SIZE = 28
    FONT_INFO_SIZE = 24
    BUTTON_WIDTH = 25
    BUTTON_HEIGHT = 4
```

## Kleur Codes

Gebruik hexadecimale kleurcodes:
- `#RRGGBB` - Standaard formaat
- `#RRGGBBAA` - Met transparantie (indien ondersteund)

Voorbeelden:
- `#ffffff` - Wit
- `#000000` - Zwart
- `#4CAF50` - Groen (Material Design)
- `#f44336` - Rood (Material Design)
- `#2196F3` - Blauw (Material Design)
- `#ff9800` - Oranje (Material Design)

## Lettertypes

Beschikbare lettertypes op Raspberry Pi:
- `Arial` (standaard)
- `Helvetica`
- `DejaVu Sans`
- `Liberation Sans`
- `Sans` (systeem standaard)

Controleer beschikbare lettertypes:
```bash
fc-list : family | sort | uniq
```

## Tips

1. **Test op je Raspberry Pi**: Kleuren kunnen er anders uitzien op verschillende schermen
2. **Contrast**: Zorg voor voldoende contrast tussen tekst en achtergrond
3. **Touch Targets**: Houd knoppen groot genoeg voor touchscreen gebruik (minimaal 44x44 pixels)
4. **Leesbaarheid**: Gebruik grote lettertypes voor betere leesbaarheid op een 7" scherm
5. **Kleurenblindheid**: Overweeg kleuren die ook werken voor kleurenblinden

## Geavanceerde Aanpassingen

Voor meer geavanceerde aanpassingen, bewerk direct `ui.py`:
- Layout wijzigingen: pas de `pack()` en `grid()` calls aan
- Nieuwe componenten: voeg widgets toe in `setup_ui()`
- Animaties: gebruik `root.after()` voor timed updates
- Custom widgets: maak subclasses van tkinter widgets

## Problemen Oplossen

**Kleuren worden niet toegepast:**
- Controleer of je de applicatie opnieuw hebt gestart
- Controleer op syntaxfouten in `theme.py`

**Lettertype werkt niet:**
- Controleer of het lettertype geïnstalleerd is: `fc-list | grep "FontName"`
- Gebruik een fallback lettertype

**UI ziet er niet goed uit:**
- Controleer de resolutie van je scherm
- Pas `TEXT_WRAP_LENGTH` aan voor langere teksten
- Verhoog padding voor meer ruimte

