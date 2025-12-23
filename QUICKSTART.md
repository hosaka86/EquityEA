# EquityMonitor Video Tutorial - Quick Start

Schnellanleitung für die Erstellung des Video-Tutorials.

---

## Workflow

**Vollständige Dokumentation:** Siehe `CODE_TUTORIAL_WORKFLOW.md` im Projekt-Root

### Schritt 1: Code validieren (KRITISCH!)

```bash
python validate_code_narration.py codeyoutube.md EquityMonitor-V107.mq5
```

**Muss** `✓ VALIDATION PASSED` zeigen, bevor du weiter machst!

### Schritt 2: Narrations extrahieren

```bash
python3 extract_narrations.py
```

**Erstellt:**
- `narrations/code/blockXX.txt` - Einzelne Narration-Texte
- `narrations/interlude/interlude_sectionX.txt` - Interlude-Texte
- **`narrations_combined.txt`** - ⚡ Direkt für TTS verwendbar!

### Schritt 3: Audio generieren

```bash
source venv/bin/activate
./venv/bin/python fish_audio_tts.py \
  --narration-file narrations_combined.txt \
  --output-dir ./audio/
```

**Hinweis:** Config nutzt Anti-Hallucination-Settings:
- `temperature: 0.5` (lower = konsistenter)
- `top_p: 0.5` (lower = weniger divers)
- `repetition_penalty: 1.5` (higher = weniger Wiederholungen)

Siehe `ANTI_HALLUCINATION_FIX.md` für Details.

### Schritt 4: Web-Preview erstellen

```bash
python3 generate_web_preview.py ./audio/ --narration-file codeyoutube.md
```

**Optional: Deploy zu Web-Server**
```bash
sudo mkdir -p /var/www/html/tts_test
sudo cp audio/*.mp3 audio/timing.json audio/index.html /var/www/html/tts_test/
sudo chmod -R 755 /var/www/html/tts_test
# → http://localhost/tts_test/
```

Öffne `audio/index.html` im Browser!

### Schritt 5: Video produzieren

Shot-Liste aus `audio/timing.json` erstellen und loslegen!

---

## Dateien

**Input:**
- `EquityMonitor-V107.mq5` - Original Code
- `codeyoutube.md` - Tutorial mit Narrations + Code-Blöcken
- `interlude_value_proposition.md` - Interlude Narrations

**Scripts:**
- `validate_code_narration.py` - Code-Validierung
- `extract_narrations.py` - Narrations extrahieren
- `generate_web_preview.py` - Web-Preview erstellen

**Output:**
- `narrations/` - Extrahierte Texte (einzelne .txt Files)
- `narrations_combined.txt` - Kombinierte Datei für TTS (Fish Audio Format)
- `audio/` - MP3s + timing.json + index.html (Preview)

---

## Wichtige Hinweise

⚠️ **NIEMALS** Audio generieren ohne Code-Validierung!

✅ Nutze Web-Preview zum Reviewen vor Video-Aufnahme

📊 `timing.json` ist deine Shot-Liste-Grundlage

**Komplette Details:** Siehe `CODE_TUTORIAL_WORKFLOW.md` im Projekt-Root
