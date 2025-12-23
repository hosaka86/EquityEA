#!/usr/bin/env python3
"""
Fish Audio TTS Script
=====================

Dieses Skript nutzt die Fish Audio API für Text-to-Speech Generierung
mit Unterstützung für Pausen, Emotionen und Spezialeffekte.

Dokumentation: https://docs.fish.audio/api-reference/endpoint/openapi-v1/text-to-speech
GitHub SDK: https://github.com/fishaudio/fish-audio-python
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess

# Config laden
def load_config():
    """Lädt die Konfiguration aus config.json"""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

try:
    from fishaudio import FishAudio
    from fishaudio.utils import save
    from fishaudio.types import TTSConfig
except ImportError:
    print("ERROR: fish-audio-sdk nicht installiert!")
    print("Bitte installieren mit: pip install fish-audio-sdk")
    sys.exit(1)


class FishAudioTTS:
    """
    Wrapper-Klasse für Fish Audio TTS mit erweiterten Funktionen.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisiert den Fish Audio Client.

        Args:
            api_key: Fish Audio API Key (optional, nutzt FISH_API_KEY env var falls nicht angegeben)
        """
        if api_key:
            os.environ['FISH_API_KEY'] = api_key

        self.client = FishAudio()

    def generate_audio(
        self,
        text: str,
        output_path: str,
        speed: float = 1.0,
        volume: int = 0,
        model: str = "s1",
        format: str = "mp3",
        normalize: bool = False,
        temperature: float = 0.7,
        top_p: float = 0.7,
        repetition_penalty: float = 1.2,
        reference_id: Optional[str] = None
    ) -> Path:
        """
        Generiert Audio aus Text.

        Args:
            text: Text für TTS (kann Control Tags enthalten)
            output_path: Pfad für Output-Datei
            speed: Sprechgeschwindigkeit (0.5 - 2.0, default: 1.0)
            volume: Lautstärke in Dezibel (default: 0)
            model: TTS Model (default: "s1", alternatives: "speech-1.6", "speech-1.5")
            format: Audio-Format ("mp3", "wav", "opus", "pcm")
            normalize: Text-Normalisierung (auf False setzen für Control Tags!)
            temperature: Expressivität (0.0 - 1.0, default: 0.7, lower = more consistent)
            top_p: Nucleus Sampling (0.0 - 1.0, default: 0.7, lower = less diverse)
            repetition_penalty: Penalty für Audio-Pattern-Wiederholungen (default: 1.2, higher = less repetition/hallucinations)
            reference_id: Voice Model ID für Custom Voice

        Returns:
            Path-Objekt zum generierten Audio-File
        """
        print(f"Generiere Audio für: {text[:50]}...")

        # TTSConfig erstellen mit allen Settings (inkl. anti-hallucination parameters)
        config = TTSConfig(
            format=format,
            normalize=normalize,
            temperature=temperature,
            top_p=top_p,
            repetition_penalty=repetition_penalty
        )

        # Audio generieren
        audio = self.client.tts.convert(
            text=text,
            model=model,
            speed=speed,
            config=config,
            reference_id=reference_id
        )

        # Speichern
        output_file = Path(output_path)
        save(audio, str(output_file))

        print(f"Audio gespeichert: {output_file}")
        return output_file

    def add_pauses(self, text: str, pause_duration: str = "short") -> str:
        """
        Fügt Pausen zum Text hinzu.

        Args:
            text: Original-Text
            pause_duration: "short" (1x break), "medium" (2x break), "long" (3x break)

        Returns:
            Text mit Pausen-Tags

        Beispiel:
            >>> add_pauses("Hallo Welt", "medium")
            "Hallo (break)(break) Welt"
        """
        pause_map = {
            "short": "(break)",
            "medium": "(break)(break)",
            "long": "(break)(break)(break)"
        }

        pause_tag = pause_map.get(pause_duration, "(break)")
        return text.replace(" ", f" {pause_tag} ")

    def add_emotion(self, text: str, emotion: str) -> str:
        """
        Fügt Emotions-Tag zum Text hinzu.

        Args:
            text: Text
            emotion: Emotion (z.B. "laugh", "sigh", "cough", "angry", "sad", "excited")

        Returns:
            Text mit Emotions-Tag

        Beispiel:
            >>> add_emotion("Das ist toll", "excited")
            "(excited) Das ist toll"
        """
        return f"({emotion}) {text}"

    def generate_duration_info(self, audio_path: Path) -> Dict[str, Any]:
        """
        Ermittelt die Dauer eines Audio-Files.

        Args:
            audio_path: Pfad zum Audio-File

        Returns:
            Dict mit Dauer-Informationen
        """
        try:
            # ffprobe für Dauer-Ermittlung
            result = subprocess.run(
                [
                    'ffprobe',
                    '-v', 'quiet',
                    '-print_format', 'json',
                    '-show_format',
                    str(audio_path)
                ],
                capture_output=True,
                text=True,
                check=True
            )

            data = json.loads(result.stdout)
            duration = float(data['format']['duration'])

            minutes = int(duration // 60)
            seconds = int(duration % 60)

            return {
                'duration_seconds': duration,
                'duration_formatted': f"{minutes}:{seconds:02d}",
                'file': str(audio_path)
            }
        except Exception as e:
            print(f"WARNUNG: Konnte Dauer nicht ermitteln: {e}")
            print("Tipp: ffmpeg installieren für Dauer-Analyse")
            return {
                'duration_seconds': 0,
                'duration_formatted': "Unknown",
                'file': str(audio_path)
            }


def generate_from_narration_file(
    narration_file: Path,
    output_dir: Path,
    api_key: Optional[str] = None,
    **kwargs
):
    """
    Generiert Audio-Files aus einer strukturierten Narration-Datei.

    Format der Narration-Datei:
        [section_id]
        Text für diesen Abschnitt...

        [next_section]
        Text für nächsten Abschnitt...

    Args:
        narration_file: Pfad zur Narration-Datei
        output_dir: Output-Verzeichnis für Audio-Files
        api_key: Fish Audio API Key
        **kwargs: Zusätzliche Parameter für generate_audio()
    """
    tts = FishAudioTTS(api_key=api_key)

    # Narration-Datei einlesen
    with open(narration_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Abschnitte parsen
    sections = {}
    current_section = None

    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1]
            sections[current_section] = []
        elif current_section and line:
            sections[current_section].append(line)

    # Jeden Abschnitt verarbeiten
    output_dir.mkdir(parents=True, exist_ok=True)
    timing_info = []
    cumulative_time = 0

    print(f"\n{'='*60}")
    print(f"Verarbeite {len(sections)} Abschnitte...")
    print(f"{'='*60}\n")

    for section_id, lines in sections.items():
        text = ' '.join(lines)
        output_file = output_dir / f"{section_id}.mp3"

        print(f"\n[{section_id}]")
        print(f"Text: {text[:100]}...")

        # Audio generieren
        audio_path = tts.generate_audio(
            text=text,
            output_path=str(output_file),
            **kwargs
        )

        # Dauer ermitteln
        duration_info = tts.generate_duration_info(audio_path)

        # Timing berechnen
        start_time = cumulative_time
        end_time = start_time + duration_info['duration_seconds']
        cumulative_time = end_time

        timing_info.append({
            'section_id': section_id,
            'file': str(output_file),
            'duration_seconds': duration_info['duration_seconds'],
            'start': f"{int(start_time//60)}:{int(start_time%60):02d}",
            'end': f"{int(end_time//60)}:{int(end_time%60):02d}",
            'text_preview': text[:100]
        })

    # Timing-Übersicht ausgeben
    print(f"\n{'='*60}")
    print("TIMING-ÜBERSICHT")
    print(f"{'='*60}\n")

    for info in timing_info:
        print(f"[{info['section_id']}]")
        print(f"  File:     {info['file']}")
        print(f"  Duration: {info['duration_seconds']:.1f}s")
        print(f"  Timeline: {info['start']} - {info['end']}")
        print(f"  Text:     {info['text_preview']}...")
        print()

    total_duration = cumulative_time
    print(f"Gesamt-Dauer: {int(total_duration//60)}:{int(total_duration%60):02d}")

    # Timing als JSON speichern
    timing_file = output_dir / "timing.json"
    with open(timing_file, 'w', encoding='utf-8') as f:
        json.dump({
            'sections': timing_info,
            'total_duration_seconds': total_duration,
            'total_duration_formatted': f"{int(total_duration//60)}:{int(total_duration%60):02d}"
        }, f, indent=2, ensure_ascii=False)

    print(f"\nTiming-Daten gespeichert: {timing_file}")


def main():
    """CLI Interface"""
    parser = argparse.ArgumentParser(
        description='Fish Audio TTS Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:

  # Einzelner Text zu Audio:
  python fish_audio_tts.py --text "Hallo Welt" --output hallo.mp3

  # Mit Pausen:
  python fish_audio_tts.py --text "Hallo (break)(break) Welt" --output hallo.mp3 --no-normalize

  # Mit Emotion:
  python fish_audio_tts.py --text "(excited) Das ist großartig!" --output excited.mp3 --no-normalize

  # Aus Narration-Datei:
  python fish_audio_tts.py --narration-file narration.md --output-dir ./audio/

Pause-Tags:
  (break)          - Kurze Pause
  (break)(break)   - Mittlere Pause
  (break)(break)(break) - Lange Pause

Emotion-Tags:
  (laugh), (sigh), (cough), (angry), (sad), (excited), (surprised)

WICHTIG: Bei Verwendung von Control Tags --no-normalize setzen!
        """
    )

    # Input-Optionen
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--text', '-t', help='Text für TTS')
    input_group.add_argument('--narration-file', '-n', type=Path, help='Narration-Datei (Format: [section_id]\\ntext)')

    # Output-Optionen
    parser.add_argument('--output', '-o', help='Output-Datei (für --text)')
    parser.add_argument('--output-dir', '-d', type=Path, help='Output-Verzeichnis (für --narration-file)')

    # TTS-Parameter
    parser.add_argument('--speed', type=float, default=1.0, help='Sprechgeschwindigkeit (0.5-2.0, default: 1.0)')
    parser.add_argument('--volume', type=int, default=0, help='Lautstärke in dB (default: 0)')
    parser.add_argument('--model', default='s1', help='TTS Model (default: s1)')
    parser.add_argument('--format', default='mp3', choices=['mp3', 'wav', 'opus', 'pcm'], help='Audio-Format')
    parser.add_argument('--no-normalize', action='store_true', help='Normalisierung deaktivieren (für Control Tags!)')
    parser.add_argument('--temperature', type=float, default=0.7, help='Expressivität (0.0-1.0, default: 0.7)')
    parser.add_argument('--top-p', type=float, default=0.7, help='Nucleus Sampling (0.0-1.0, default: 0.7)')
    parser.add_argument('--reference-id', help='Custom Voice Reference ID')

    # API Key
    parser.add_argument('--api-key', help='Fish Audio API Key (oder FISH_API_KEY env var)')

    args = parser.parse_args()

    # Config laden
    config = load_config()
    fish_config = config.get('fish_audio', {})
    default_settings = fish_config.get('default_settings', {})

    # API Key (Priorität: CLI arg > config.json > env var)
    api_key = args.api_key or fish_config.get('api_key') or os.getenv('FISH_API_KEY')
    if not api_key:
        print("ERROR: Kein API Key angegeben!")
        print("Bitte setzen in config.json, mit --api-key oder als FISH_API_KEY Environment Variable")
        sys.exit(1)

    # Voice ID (Priorität: CLI arg > config.json)
    reference_id = args.reference_id or fish_config.get('voice_id') or None

    # TTS-Parameter (nutze config.json als Defaults)
    tts_params = {
        'speed': args.speed if args.speed != 1.0 else default_settings.get('speed', 1.0),
        'volume': args.volume if args.volume != 0 else default_settings.get('volume', 0),
        'model': args.model if args.model != 's1' else default_settings.get('model', 's1'),
        'format': args.format if args.format != 'mp3' else default_settings.get('format', 'mp3'),
        'normalize': not args.no_normalize if args.no_normalize else not default_settings.get('normalize', False),
        'temperature': args.temperature if args.temperature != 0.7 else default_settings.get('temperature', 0.7),
        'top_p': args.top_p if args.top_p != 0.7 else default_settings.get('top_p', 0.7),
        'reference_id': reference_id
    }

    # Verarbeitung
    if args.text:
        # Einzelner Text
        if not args.output:
            print("ERROR: --output erforderlich für --text")
            sys.exit(1)

        tts = FishAudioTTS(api_key=api_key)
        tts.generate_audio(
            text=args.text,
            output_path=args.output,
            **tts_params
        )

        # Dauer ausgeben
        duration_info = tts.generate_duration_info(Path(args.output))
        print(f"\nDauer: {duration_info['duration_formatted']}")

    elif args.narration_file:
        # Narration-Datei
        if not args.output_dir:
            print("ERROR: --output-dir erforderlich für --narration-file")
            sys.exit(1)

        generate_from_narration_file(
            narration_file=args.narration_file,
            output_dir=args.output_dir,
            api_key=api_key,
            **tts_params
        )

    print("\nFertig!")


if __name__ == '__main__':
    main()
