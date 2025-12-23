# TTS Best Practices für Code-Tutorials

Best Practices für Text-to-Speech Generierung in Code-Tutorial-Projekten.

---

## 🎯 MQL5/Code-Spezifische Narration

### Funktionsnamen richtig schreiben

**Problem:** TTS spricht zusammengeschriebene Funktionsnamen falsch aus.

**Lösung:** Spaces zwischen Wörtern einfügen in der Narration (nicht im Code!):

| ❌ Falsch (klingt falsch) | ✅ Richtig (TTS-freundlich) |
|---------------------------|----------------------------|
| "OnInit function"         | "On Init function"         |
| "OnDeinit function"       | "On Deinit function"       |
| "OnTick function"         | "On Tick function"         |
| "OnTimer function"        | "On Timer function"        |
| "OnChartEvent"            | "On Chart Event"           |
| "CalculateHistoricalStats" | "Calculate Historical Stats" |
| "UpdateTradingStatistics" | "Update Trading Statistics" |

### CamelCase-Namen

**Regel:** Alle CamelCase-Funktionen/Variablen mit Leerzeichen trennen in Narration:

```
Code:              Narration:
----------------------------------------
UpdateDashboard    → "Update Dashboard"
GetFillingMode     → "Get Filling Mode"
CloseAllPositions  → "Close All Positions"
ShouldAutoSave     → "Should Auto Save"
```

### Akronyme und Abkürzungen

**Option 1 - Buchstabieren:**
- EA → "E A"
- MQL5 → "M Q L 5"
- TTS → "T T S"
- API → "A P I"

**Option 2 - Ausschreiben:**
- EA → "Expert Advisor"
- MQL5 → "MetaQuotes Language 5"
- TTS → "Text to Speech"
- API → "Application Programming Interface"

**Empfohlung:** Beim ersten Erwähnen ausschreiben, danach buchstabieren.

---

## ⚙️ Fish Audio TTS Config

### Anti-Hallucination Settings

**Standard-Config für Code-Tutorials:**

```json
{
  "temperature": 0.5,
  "top_p": 0.5,
  "repetition_penalty": 1.5,
  "normalize": false
}
```

**Parameter-Erklärung:**

| Parameter | Wert | Zweck |
|-----------|------|-------|
| `temperature` | 0.5 | Konsistenz (lower = vorhersagbarer) |
| `top_p` | 0.5 | Diversität (lower = weniger Variation) |
| `repetition_penalty` | 1.5 | Verhindert Wiederholungen am Ende |
| `normalize` | false | Erhält Control Tags (break, excited, etc.) |

### Wann Config anpassen?

**Aggressivere Settings (weniger Hallucinations, weniger natürlich):**
```json
{
  "temperature": 0.3,
  "top_p": 0.3,
  "repetition_penalty": 2.0
}
```

**Standard Settings (mehr Ausdrucksstärke, mehr Risiko):**
```json
{
  "temperature": 0.7,
  "top_p": 0.7,
  "repetition_penalty": 1.2
}
```

---

## 📝 Narration-Struktur

### Control Tags

**Pausen:**
- `(break)` - Kurze Pause (~0.5s)
- `(break)(break)` - Mittlere Pause (~1s) - **Empfohlen zwischen Sätzen**
- `(break)(break)(break)` - Lange Pause (~2s) - **Empfohlen zwischen Abschnitten**

**Emotionen:**
- `(excited)` - Begeistert
- `(laugh)` - Lachen
- `(sad)` - Traurig
- `(angry)` - Verärgert

**Best Practice:**
```
"Let's implement the On Init function. (break)(break)
This runs once when the EA starts. (break)
First, we print a header. (long-break)
Then we initialize variables."
```

### Text-Länge pro Block

**Empfohlen:**
- **Tutorial-Blöcke:** 20-40 Sekunden Audio
- **Interlude-Sektionen:** 30-45 Sekunden Audio
- **Gesamtes Tutorial:** 10-20 Minuten

**Warum begrenzen?**
- Längere Texte → mehr Hallucination-Risiko
- Kürzere Blöcke → einfacher zu bearbeiten
- Bessere Video-Segmentierung

---

## ✅ Pre-Generation Checklist

Vor Audio-Generierung prüfen:

- [ ] **Funktionsnamen mit Spaces** (OnInit → On Init)
- [ ] **CamelCase getrennt** (UpdateDashboard → Update Dashboard)
- [ ] **Akronyme klar** (EA → "E A" oder ausschreiben)
- [ ] **Control Tags eingefügt** (Pausen, Emotionen)
- [ ] **Config überprüft** (Anti-Hallucination-Settings aktiv)
- [ ] **Code validiert** (validate_code_narration.py PASSED)
- [ ] **Narrations extrahiert** (narrations_combined.txt vorhanden)

---

## 🔧 Troubleshooting

### Problem: Hallucinations (zusätzliche Wörter am Ende)

**Lösung 1:** Config verschärfen
```json
{
  "temperature": 0.3,
  "repetition_penalty": 2.0
}
```

**Lösung 2:** Neu generieren
- Fish Audio hat ~5% inherente Variabilität
- Manchmal hilft einfach ein Retry

**Lösung 3:** Text kürzen
- Längere Texte → mehr Risiko
- In kleinere Abschnitte aufteilen

### Problem: Falsche Aussprache von Funktionsnamen

**Lösung:** Narration anpassen (nicht Code!):
```
❌ "Next is the OnInit function"
✅ "Next is the On Init function"
```

Dann neu extrahieren und Audio regenerieren.

### Problem: Unnatürlich klingende Ausgabe

**Lösung:** Config lockern
```json
{
  "temperature": 0.7,
  "top_p": 0.7
}
```

**Trade-off:** Mehr Natürlichkeit = mehr Hallucination-Risiko

---

## 📚 Workflow Integration

### In neuen Projekten:

1. **Narration schreiben:**
   - Funktionsnamen mit Spaces
   - Control Tags einfügen
   - CamelCase trennen

2. **Config vorbereiten:**
   - `config.json` mit Anti-Hallucination-Settings
   - API Key und Voice ID eintragen

3. **Vor Audio-Generierung:**
   - Code-Validierung durchführen
   - Narrations extrahieren
   - Checklist durchgehen

4. **Nach Audio-Generierung:**
   - Audio anhören und prüfen
   - Bei Problemen Config anpassen und neu generieren

---

## 🎯 Zusammenfassung

**Wichtigste Regeln:**

1. ✅ **Funktionsnamen mit Spaces** in Narration
2. ✅ **Anti-Hallucination-Config** verwenden
3. ✅ **Control Tags** für natürliche Pausen
4. ✅ **Text-Länge begrenzen** (20-40s pro Block)
5. ✅ **Vor Generierung validieren**

**Diese Practices anwenden = weniger manuelle Nachbearbeitung!**

---

Siehe auch:
- `CODE_TUTORIAL_WORKFLOW.md` - Kompletter Workflow
- `ANTI_HALLUCINATION_FIX.md` - Technische Details zu Hallucinations
- `QUICKSTART.md` - Schnelleinstieg
