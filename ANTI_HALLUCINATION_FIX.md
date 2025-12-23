# Fish Audio TTS Hallucination Fix

## Problem

Fish Audio TTS fügt manchmal am Ende von Narrations zusätzliche Wörter oder Textfragmente hinzu, die nicht im Original-Text stehen (~5% Chance).

**Quellen:**
- [Fish Speech Hallucination Issues (HuggingFace)](https://huggingface.co/spaces/fishaudio/fish-speech-1/discussions/3)
- [TTS Hallucinations General](https://github.com/k2-fsa/sherpa-onnx/issues/1695)
- [Fish Audio API Documentation](https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech)

---

## Lösungen implementiert

### ✅ 1. Script-Update: `fish_audio_tts.py`

**Neu hinzugefügt:**
- `repetition_penalty` Parameter (default: 1.2)
  - Reduziert Audio-Pattern-Wiederholungen
  - Höhere Werte (1.5-2.0) = weniger Hallucinations

**Code-Änderung:**
```python
config = TTSConfig(
    format=format,
    normalize=normalize,
    temperature=temperature,
    top_p=top_p,
    repetition_penalty=repetition_penalty  # NEU!
)
```

### ✅ 2. Config-Update: `config.json`

**Optimierte Anti-Hallucination-Werte:**

```json
{
  "temperature": 0.5,        // Vorher: 0.7 → Mehr Konsistenz
  "top_p": 0.5,              // Vorher: 0.7 → Weniger Diversität
  "repetition_penalty": 1.5  // NEU! → Reduziert Wiederholungen
}
```

**Parameter-Erklärung:**
- **temperature** (0.5 statt 0.7):
  - Niedrigere Werte = konsistenter, vorhersagbarer
  - Reduziert "kreative" Ergänzungen am Ende

- **top_p** (0.5 statt 0.7):
  - Nucleus Sampling - niedrigere Werte = weniger Variation
  - Verhindert unerwartete Wort-Auswahl

- **repetition_penalty** (1.5):
  - Bestraft wiederholende Audio-Patterns
  - Empfohlen: 1.2-2.0 für beste Resultate

---

## 🔄 Audio neu generieren

Um die Fixes anzuwenden, Audio neu generieren:

```bash
cd ../template
source venv/bin/activate

# Mit optimierten Einstellungen
./venv/bin/python fish_audio_tts.py \
  --narration-file ../EquityEA/narrations_combined.txt \
  --output-dir ../EquityEA/audio/
```

Die neuen Parameter werden automatisch aus `config.json` geladen.

---

## 📊 Erwartete Verbesserungen

**Vorher (alte Settings):**
- ~5% Hallucination-Rate
- Gelegentlich zusätzliche Wörter am Ende
- Textfragmente aus vorherigen Generationen

**Nachher (neue Settings):**
- Deutlich reduzierte Hallucination-Rate
- Konsistentere Ausgabe
- Weniger Wiederholungen und unerwarteter Text

---

## 🛠️ Fine-Tuning (falls nötig)

Falls noch Probleme auftreten:

### Aggressivere Settings:
```json
{
  "temperature": 0.3,
  "top_p": 0.3,
  "repetition_penalty": 2.0
}
```
⚠️ **Trade-off:** Weniger natürlich klingend, aber stabiler

### Balanced Settings (aktuell):
```json
{
  "temperature": 0.5,
  "top_p": 0.5,
  "repetition_penalty": 1.5
}
```
✅ **Empfohlen:** Gute Balance zwischen Qualität und Stabilität

### Original Settings:
```json
{
  "temperature": 0.7,
  "top_p": 0.7,
  "repetition_penalty": 1.2
}
```
❌ **Problem:** Mehr Hallucinations, instabiler

---

## 🔍 Weitere Optimierungen

Laut Fish Audio Team können auch helfen:

1. **Reference Audio Qualität:**
   - 20-40 Sekunden klar, ohne Hintergrundgeräusche
   - Nicht zu kurz (<20s), nicht zu lang (>40s)

2. **Retry-Strategie:**
   - Bei schlechten Resultaten: Einfach neu generieren
   - Auto-regressive Models haben inherente Variabilität

3. **Chunk-Kontrolle** (für sehr lange Texte):
   - `chunk_length` Parameter nutzen
   - Verhindert zu lange Kontext-Fenster

---

## 📝 Quellen

- [HuggingFace Fish Speech Discussions](https://huggingface.co/spaces/fishaudio/fish-speech-1/discussions/3)
- [Fish Audio TTS API Reference](https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech)
- [ReadSpeaker: How to Prevent TTS Hallucinations](https://www.readspeaker.com/blog/text-to-speech-hallucinating/)

---

**Status:** ✅ Implementiert und bereit für Re-Generierung
**Nächster Schritt:** Audio neu generieren und testen
