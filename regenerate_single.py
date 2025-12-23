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
        print("\nExamples:")
        print("  python3 regenerate_single.py block03")
        print("  python3 regenerate_single.py interlude_section2")
        print("\nAvailable sections:")
        print("  Run: grep '^\\[' narrations_combined.txt")
        sys.exit(1)

    section_id = sys.argv[1]

    # Extrahiere Sektion
    print(f"Extracting {section_id}...")
    text = extract_section(section_id)

    if not text:
        print(f"ERROR: Section {section_id} not found!")
        print("\nAvailable sections:")
        subprocess.run(['grep', '^\\[', 'narrations_combined.txt'])
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
        print(f"1. Listen to audio/{section_id}.mp3:")
        print(f"   mpg123 audio/{section_id}.mp3")
        print(f"\n2. If good, update web preview:")
        print(f"   cd ../template")
        print(f"   python3 generate_web_preview.py ../EquityEA/audio/ --narration-file ../EquityEA/codeyoutube.md")
        print(f"\n3. Deploy to web server:")
        print(f"   sudo cp ../EquityEA/audio/{section_id}.mp3 /var/www/html/tts_test/")
        print(f"   sudo cp ../EquityEA/audio/index.html /var/www/html/tts_test/")
    else:
        print(f"\n✗ Audio generation failed!")
        temp_file.unlink()
        sys.exit(1)

if __name__ == '__main__':
    main()
