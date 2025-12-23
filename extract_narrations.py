#!/usr/bin/env python3
"""
Extract narration texts from interlude and code tutorial files.
Creates separate text files for each narration section for audio generation.
"""

import re
from pathlib import Path


def extract_interlude_narrations(interlude_file):
    """Extract narrations from interlude_value_proposition.md"""
    with open(interlude_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to find narration sections
    # Looking for: **Narration:**\n\n"text..."
    pattern = r'### Section \d+: (.+?)\n\n\*\*Narration:\*\*\n\n"(.+?)"'
    matches = re.findall(pattern, content, re.DOTALL)

    narrations = []
    for i, (title, text) in enumerate(matches, 1):
        narrations.append({
            'id': f'interlude_section{i}',
            'title': title,
            'text': text.strip()
        })

    return narrations


def extract_code_narrations(code_file):
    """Extract narrations from codeyoutube.md"""
    with open(code_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to find narration sections in code blocks
    # Looking for: ## Block N: Title\n\n**Narration:**\n\n"text..."
    pattern = r'## Block (\d+): (.+?)\n\n\*\*Narration:\*\*\n\n"(.+?)"'
    matches = re.findall(pattern, content, re.DOTALL)

    narrations = []
    for block_num, title, text in matches:
        narrations.append({
            'id': f'block{block_num.zfill(2)}',
            'title': title,
            'text': text.strip()
        })

    return narrations


def save_narrations(narrations, output_dir):
    """Save narrations to individual text files"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = []

    for narration in narrations:
        filename = f"{narration['id']}.txt"
        filepath = output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(narration['text'])

        manifest.append({
            'id': narration['id'],
            'title': narration['title'],
            'file': filename
        })

        print(f"✓ Created: {filename}")

    return manifest


def create_manifest(manifest, output_file):
    """Create a manifest file listing all narrations"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Narration Manifest\n\n")
        f.write(f"Total sections: {len(manifest)}\n\n")

        for item in manifest:
            f.write(f"- **{item['id']}**: {item['title']}\n")
            f.write(f"  File: `{item['file']}`\n\n")

    print(f"✓ Created manifest: {output_file}")


def create_combined_narration(narrations, output_file):
    """
    Create combined narration file in Fish Audio TTS format.

    Format:
        [section_id]
        Narration text...

        [next_section_id]
        Next narration text...
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for narration in narrations:
            f.write(f"[{narration['id']}]\n")
            f.write(narration['text'])
            f.write("\n\n")

    print(f"✓ Created combined file: {output_file}")
    print(f"  Format: Fish Audio TTS ready ([section_id] format)")


def main():
    print("Extracting narrations...\n")

    # Extract interlude narrations
    print("=== Interlude Sections ===")
    interlude_narrations = extract_interlude_narrations('interlude_value_proposition.md')
    interlude_manifest = save_narrations(interlude_narrations, 'narrations/interlude')

    print(f"\n=== Code Tutorial Blocks ===")
    code_narrations = extract_code_narrations('codeyoutube.md')
    code_manifest = save_narrations(code_narrations, 'narrations/code')

    # Create combined manifest
    print(f"\n=== Manifest ===")
    all_manifest = interlude_manifest + code_manifest
    create_manifest(all_manifest, 'narrations/manifest.md')

    # Create combined narration file for Fish Audio TTS
    print(f"\n=== Combined TTS File ===")
    all_narrations = interlude_narrations + code_narrations
    create_combined_narration(all_narrations, 'narrations_combined.txt')

    print(f"\n✓ Done! Extracted {len(interlude_narrations)} interlude sections and {len(code_narrations)} code blocks")
    print(f"  Total narrations: {len(all_manifest)}")
    print(f"\n📝 Use 'narrations_combined.txt' directly with fish_audio_tts.py")


if __name__ == '__main__':
    main()
