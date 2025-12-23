# Selektive Audio-Regenerierung - Einzelne Blöcke neu generieren

Anleitung zum Neu-Generieren einzelner Audio-Blöcke bei Fehlern oder Hallucinations.

---

## 🎯 Wann einzelne Blöcke neu generieren?

**Häufige Gründe:**
- ❌ Hallucinations (zusätzliche Wörter am Ende)
- ❌ Falsche Aussprache (OnInit statt "On Init")
- ❌ Audio-Artefakte oder Störgeräusche
- ❌ Falsche Betonung oder Pausen
- ❌ Zu schnell/langsam gesprochen

**Vorteil:** Nur 1 Block neu generieren statt alle 23!

---

## 📝 Schritt-für-Schritt: Einzelnen Block neu generieren

### Beispiel: Block 3 (Input Parameters) hat Fehler

**Schritt 1: Temporäre Narration erstellen**

```bash
cd ../EquityEA

# Erstelle temporäre Datei nur für Block 3
cat > temp_block03.txt << 'EOF'
[block03]
Now let's set up the input parameters. (break) These are the settings users can adjust without modifying the code. (long-break) We organize them into four logical sections. (break) General settings include the magic number filter and drawdown calculation mode. (break) Display settings control the visual dashboard, (break) like position, colors, and font size. (break) File management settings handle the auto-save feature, (break) so your statistics persist even after restarting MetaTrader. (long-break) And finally, (break) the killswitch protection settings. (break) Set a maximum drawdown threshold, (break) choose the trigger type, (break) and decide if you want aggressive mode, (break) which continuously closes any new positions that appear. (long-break)
EOF
```

**Schritt 2: Audio für diesen Block generieren**

```bash
cd ../template
source venv/bin/activate

./venv/bin/python fish_audio_tts.py \
  --narration-file ../EquityEA/temp_block03.txt \
  --output-dir ../EquityEA/audio/
```

**Schritt 3: Überprüfen**

```bash
# Audio anhören
mpg123 ../EquityEA/audio/block03.mp3

# Oder im Browser
firefox ../EquityEA/audio/block03.mp3
```

**Schritt 4: Cleanup**

```bash
cd ../EquityEA
rm temp_block03.txt
```

**Schritt 5: Web-Preview aktualisieren**

```bash
cd ../template
python3 generate_web_preview.py ../EquityEA/audio/ --narration-file ../EquityEA/codeyoutube.md

# Deploy zu Web-Server
sudo cp ../EquityEA/audio/block03.mp3 /var/www/html/tts_test/
sudo cp ../EquityEA/audio/index.html /var/www/html/tts_test/
```

---

## 🔧 Alternative: Direkt aus narrations_combined.txt extrahieren

**Methode 1: Mit grep und sed**

```bash
cd ../EquityEA

# Extrahiere Block 3 aus der kombinierten Datei
sed -n '/^\[block03\]/,/^\[block04\]/p' narrations_combined.txt | \
  head -n -1 > temp_block03.txt

# Generiere Audio
cd ../template
source venv/bin/activate
./venv/bin/python fish_audio_tts.py \
  --narration-file ../EquityEA/temp_block03.txt \
  --output-dir ../EquityEA/audio/

# Cleanup
rm ../EquityEA/temp_block03.txt
```

**Methode 2: Mit Python-Script (empfohlen)**

Erstelle `regenerate_single.py`:

```python
#!/usr/bin/env python3
"""
Regeneriere einzelnen Audio-Block.

Usage:
    python3 regenerate_single.py block03
    python3 regenerate_single.py interlude_section2
"""

import sys
import subprocess
from pathlib import Path

def extract_section(section_id, input_file='narrations_combined.txt'):
    """Extrahiere einzelne Sektion aus kombinierter Datei"""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Finde Start und Ende
    start_marker = f'[{section_id}]'
    sections = content.split('[')

    for i, section in enumerate(sections):
        if section.startswith(section_id + ']'):
            # Finde Text bis zur nächsten Sektion
            text = section.split(']', 1)[1].strip()
            if i + 1 < len(sections):
                # Entferne nächste Sektion
                next_section_start = text.find('\n\n[')
                if next_section_start > 0:
                    text = text[:next_section_start]

            return f'[{section_id}]\n{text}\n'

    return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 regenerate_single.py <section_id>")
        print("Example: python3 regenerate_single.py block03")
        sys.exit(1)

    section_id = sys.argv[1]

    # Extrahiere Sektion
    print(f"Extracting {section_id}...")
    text = extract_section(section_id)

    if not text:
        print(f"ERROR: Section {section_id} not found!")
        sys.exit(1)

    # Schreibe temporäre Datei
    temp_file = Path(f'temp_{section_id}.txt')
    temp_file.write_text(text, encoding='utf-8')
    print(f"✓ Created {temp_file}")

    # Generiere Audio
    print(f"\nGenerating audio for {section_id}...")
    result = subprocess.run([
        '../template/venv/bin/python',
        '../template/fish_audio_tts.py',
        '--narration-file', str(temp_file),
        '--output-dir', './audio/'
    ])

    if result.returncode == 0:
        print(f"\n✓ Successfully regenerated audio/{section_id}.mp3")

        # Cleanup
        temp_file.unlink()
        print(f"✓ Cleaned up {temp_file}")

        print(f"\nNext steps:")
        print(f"1. Listen to audio/{section_id}.mp3")
        print(f"2. If good, update web preview:")
        print(f"   cd ../template")
        print(f"   python3 generate_web_preview.py ../EquityEA/audio/ --narration-file ../EquityEA/codeyoutube.md")
        print(f"3. Deploy to web server:")
        print(f"   sudo cp ../EquityEA/audio/{section_id}.mp3 /var/www/html/tts_test/")
    else:
        print(f"\n✗ Audio generation failed!")
        temp_file.unlink()
        sys.exit(1)

if __name__ == '__main__':
    main()
```

**Verwendung:**

```bash
cd ../EquityEA
chmod +x regenerate_single.py

# Regeneriere Block 3
./regenerate_single.py block03

# Oder Interlude
./regenerate_single.py interlude_section2
```

---

## 🎛️ Config-Tuning für problematische Blöcke

Falls ein Block konstant Hallucinations hat, temporär strengere Settings verwenden:

### Erstelle `config_strict.json`:

```json
{
  "fish_audio": {
    "api_key": "c51d1ae1ee32480297e4f5ef98c12ede",
    "voice_id": "b7204d4e40ef4a548c7c8547b7f73492",
    "default_settings": {
      "speed": 1.0,
      "volume": 0,
      "model": "s1",
      "format": "mp3",
      "normalize": false,
      "temperature": 0.3,
      "top_p": 0.3,
      "repetition_penalty": 2.0
    }
  }
}
```

**Dann:**

```bash
cd ../template

# Backup original config
cp config.json config_original.json

# Use strict config
cp config_strict.json config.json

# Regenerate problematic block
./venv/bin/python fish_audio_tts.py \
  --narration-file ../EquityEA/temp_block03.txt \
  --output-dir ../EquityEA/audio/

# Restore original
mv config_original.json config.json
```

---

## 🔄 Multiple Blöcke gleichzeitig neu generieren

### Beispiel: Blocks 3, 5, 7 haben Fehler

```bash
cd ../EquityEA

# Erstelle temporäre Datei mit nur diesen Blöcken
cat > temp_multiple.txt << 'EOF'
[block03]
(Text von Block 3...)

[block05]
(Text von Block 5...)

[block07]
(Text von Block 7...)
EOF

# Generiere
cd ../template
source venv/bin/activate
./venv/bin/python fish_audio_tts.py \
  --narration-file ../EquityEA/temp_multiple.txt \
  --output-dir ../EquityEA/audio/

# Cleanup
rm ../EquityEA/temp_multiple.txt
```

---

## 📊 Timing neu berechnen nach Änderungen

**Problem:** Wenn du einzelne Blöcke neu generierst, stimmt `timing.json` nicht mehr.

**Lösung:** Komplettes timing.json neu generieren:

```bash
cd ../template
source venv/bin/activate

# Regeneriere timing.json aus allen vorhandenen MP3s
./venv/bin/python fish_audio_tts.py \
  --narration-file ../EquityEA/narrations_combined.txt \
  --output-dir ../EquityEA/audio/ \
  --skip-existing

# (Wenn --skip-existing nicht existiert, manuell)
```

**Oder manuell updaten:**

```python
#!/usr/bin/env python3
"""Update timing.json nach selektiver Regenerierung"""

import json
import subprocess
from pathlib import Path

def get_duration(mp3_path):
    """Hole Dauer mit ffprobe"""
    result = subprocess.run([
        'ffprobe', '-v', 'quiet',
        '-print_format', 'json',
        '-show_format', str(mp3_path)
    ], capture_output=True, text=True)

    data = json.loads(result.stdout)
    return float(data['format']['duration'])

def update_timing_json(audio_dir='../EquityEA/audio'):
    """Update timing.json"""
    audio_dir = Path(audio_dir)
    timing_file = audio_dir / 'timing.json'

    # Lade existierende timing.json
    with open(timing_file, 'r') as f:
        timing = json.load(f)

    # Update Dauern
    cumulative = 0
    for section in timing['sections']:
        mp3_path = Path(section['file'])
        if mp3_path.exists():
            duration = get_duration(mp3_path)

            # Update section
            section['duration_seconds'] = duration

            # Update timeline
            start_min = int(cumulative // 60)
            start_sec = int(cumulative % 60)
            section['start'] = f"{start_min}:{start_sec:02d}"

            cumulative += duration

            end_min = int(cumulative // 60)
            end_sec = int(cumulative % 60)
            section['end'] = f"{end_min}:{end_sec:02d}"

    # Update total
    timing['total_duration_seconds'] = cumulative
    total_min = int(cumulative // 60)
    total_sec = int(cumulative % 60)
    timing['total_duration_formatted'] = f"{total_min}:{total_sec:02d}"

    # Speichern
    with open(timing_file, 'w') as f:
        json.dump(timing, f, indent=2)

    print(f"✓ Updated {timing_file}")
    print(f"  Total duration: {timing['total_duration_formatted']}")

if __name__ == '__main__':
    update_timing_json()
```

**Verwendung:**

```bash
cd ../EquityEA
python3 update_timing.py
```

---

## 🔍 Debugging: Welcher Block ist problematisch?

### Quick-Check Script:

```bash
#!/bin/bash
# check_blocks.sh - Überprüfe alle Blöcke

cd ../EquityEA/audio

echo "Checking all audio blocks..."
echo "=============================="

for file in block*.mp3 interlude*.mp3; do
    if [ -f "$file" ]; then
        # Hole Dauer
        duration=$(ffprobe -v quiet -print_format json -show_format "$file" | \
                   grep -o '"duration":"[^"]*"' | cut -d'"' -f4)

        # Check für Hallucinations (zu lang?)
        expected=50  # Erwartete max Sekunden
        if (( $(echo "$duration > $expected" | bc -l) )); then
            echo "⚠️  $file: ${duration}s (UNUSUALLY LONG - check for hallucinations)"
        else
            echo "✓  $file: ${duration}s"
        fi
    fi
done
```

---

## ✅ Checklist nach selektiver Regenerierung

Nach dem Neu-Generieren einzelner Blöcke:

- [ ] Audio anhören und Qualität prüfen
- [ ] `timing.json` aktualisieren (falls nötig)
- [ ] Web-Preview neu generieren
- [ ] Zu Web-Server deployen
- [ ] Im Browser testen (http://localhost/tts_test/)
- [ ] Ursprungs-Datei (narrations_combined.txt) anpassen falls Textänderung
- [ ] Git commit der Änderungen

---

## 📝 Beispiel-Workflow: Kompletter Fix für Block 3

```bash
# 1. Problem identifiziert: Block 3 hat Hallucinations

# 2. Text in codeyoutube.md überprüfen/anpassen falls nötig
cd ../EquityEA
nano codeyoutube.md  # Fix "OnInit" → "On Init" etc.

# 3. Narrations neu extrahieren
python3 extract_narrations.py

# 4. Einzelnen Block regenerieren
./regenerate_single.py block03

# 5. Audio testen
mpg123 audio/block03.mp3

# 6. Web-Preview aktualisieren
cd ../template
python3 generate_web_preview.py ../EquityEA/audio/ --narration-file ../EquityEA/codeyoutube.md

# 7. Deploy
sudo cp ../EquityEA/audio/block03.mp3 /var/www/html/tts_test/
sudo cp ../EquityEA/audio/index.html /var/www/html/tts_test/

# 8. Im Browser prüfen
firefox http://localhost/tts_test/

# 9. Git commit
cd ../EquityEA
git add codeyoutube.md audio/block03.mp3 audio/index.html
git commit -m "Fix block03 narration and regenerate audio"
git push
```

---

## 🎯 Pro-Tips

**1. Batch-Testing:**
Nach Vollständiger Generierung alle Blöcke durchhören und markieren:
```bash
# Erstelle Checkliste
for i in {01..18}; do
    echo "[ ] block${i}.mp3 - Duration: $(ffprobe -v quiet -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 audio/block${i}.mp3)s"
done > audio_review_checklist.md
```

**2. A/B Testing:**
Wenn ein Block mehrfach Probleme hat, generiere 2-3 Versionen:
```bash
# Version A (current config)
./regenerate_single.py block03
mv audio/block03.mp3 audio/block03_v1.mp3

# Version B (strict config)
# (use config_strict.json)
./regenerate_single.py block03
mv audio/block03.mp3 audio/block03_v2.mp3

# Höre beide an, wähle beste
```

**3. Keep Originals:**
Vor Regenerierung:
```bash
cp audio/block03.mp3 audio/block03_original.mp3
```

Falls neue Version schlechter → Rollback möglich!

---

## 🆘 Troubleshooting

### Problem: "Section not found"

**Ursache:** Falsche section_id

**Lösung:**
```bash
# Liste alle verfügbaren sections
grep '^\[' narrations_combined.txt

# Ausgabe:
# [interlude_section1]
# [interlude_section2]
# [block01]
# [block02]
# ...
```

### Problem: Audio klingt robotisch nach Regenerierung

**Ursache:** Zu strikte Config (temperature zu niedrig)

**Lösung:** Erhöhe temperature auf 0.5-0.7 temporär

### Problem: Timing.json zeigt falsche Werte

**Ursache:** Nicht aktualisiert nach Regenerierung

**Lösung:** Nutze `update_timing.py` Script oben

---

## 📚 Zusammenfassung

**Für einzelne Block-Regenerierung:**
1. Extrahiere Sektion aus `narrations_combined.txt`
2. Erstelle temp-Datei mit nur diesem Block
3. Generiere Audio mit `fish_audio_tts.py`
4. Update Web-Preview
5. Deploy zu Web-Server
6. Cleanup temp-Datei

**Oder nutze `regenerate_single.py` für Ein-Zeilen-Command!**

**Zeitersparnis:** ~10 Minuten statt 15+ Minuten für komplette Neu-Generierung!
