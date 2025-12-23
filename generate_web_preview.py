#!/usr/bin/env python3
"""
Generate Web Preview for TTS Audio Output
==========================================

Creates an interactive HTML page showing:
- Audio players for each section
- Narration texts
- Code blocks (for code tutorials)
- Download links
- Timing information

Usage:
    python generate_web_preview.py <output_dir> [--narration-file <file>] [--code-file <file>]

Example:
    python generate_web_preview.py ./test_audio --narration-file ../EquityEA/codeyoutube.md
"""

import json
import re
import argparse
from pathlib import Path
from html import escape


def extract_narrations_and_code(narration_file):
    """
    Extract narrations and code blocks from markdown file.

    Returns:
        dict: {section_id: {'narration': str, 'code': str, 'title': str}}
    """
    with open(narration_file, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = {}

    # Pattern for code tutorial blocks: ## Block N: Title
    block_pattern = r'## Block (\d+): (.+?)\n\n\*\*Narration:\*\*\n\n"(.+?)"\n\n```(\w+)\n(.*?)\n```'
    blocks = re.findall(block_pattern, content, re.DOTALL)

    for block_num, title, narration, lang, code in blocks:
        section_id = f'block{block_num.zfill(2)}'
        sections[section_id] = {
            'title': title,
            'narration': narration.strip(),
            'code': code.strip(),
            'language': lang
        }

    # If no code blocks found, try simple narration format: [section_id]
    if not sections:
        simple_pattern = r'\[(\w+)\]\n(.+?)(?=\n\[|$)'
        simple_blocks = re.findall(simple_pattern, content, re.DOTALL)

        for section_id, text in simple_blocks:
            sections[section_id] = {
                'title': section_id,
                'narration': text.strip(),
                'code': None,
                'language': None
            }

    return sections


def generate_html(timing_json_path, sections_data, output_path):
    """
    Generate HTML preview page.

    Args:
        timing_json_path: Path to timing.json
        sections_data: Dict of section data from narration file
        output_path: Where to write index.html
    """
    # Load timing data
    with open(timing_json_path, 'r', encoding='utf-8') as f:
        timing = json.load(f)

    # Build HTML
    html_parts = []

    # HTML header
    html_parts.append('''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TTS Audio Preview</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }

        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }

        header p {
            font-size: 1.2em;
            opacity: 0.9;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }

        .stat {
            text-align: center;
        }

        .stat-value {
            font-size: 2em;
            font-weight: 700;
            color: #667eea;
        }

        .stat-label {
            font-size: 0.9em;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .sections {
            padding: 40px;
        }

        .section {
            background: #fff;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .section:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e9ecef;
        }

        .section-title {
            font-size: 1.5em;
            color: #667eea;
            font-weight: 600;
        }

        .section-timing {
            background: #667eea;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
        }

        .narration-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            position: relative;
        }

        .narration-label {
            font-weight: 600;
            color: #495057;
            margin-bottom: 10px;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .narration-text {
            color: #212529;
            line-height: 1.8;
            font-size: 1.05em;
        }

        .code-box {
            margin: 20px 0;
            position: relative;
        }

        .code-label {
            font-weight: 600;
            color: #495057;
            margin-bottom: 10px;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 1px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .copy-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85em;
            font-weight: 600;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }

        .copy-btn:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }

        .copy-btn:active {
            transform: translateY(0);
        }

        .copy-btn.copied {
            background: #28a745;
        }

        pre {
            background: #282c34;
            color: #abb2bf;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Courier New', Courier, monospace;
            font-size: 0.9em;
            line-height: 1.5;
        }

        code {
            font-family: 'Courier New', Courier, monospace;
        }

        .audio-player {
            width: 100%;
            margin: 15px 0;
        }

        audio {
            width: 100%;
            border-radius: 8px;
        }

        .download-link {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.3s;
            margin-top: 10px;
        }

        .download-link:hover {
            background: #5568d3;
        }

        footer {
            background: #f8f9fa;
            padding: 30px 40px;
            text-align: center;
            border-top: 2px solid #e9ecef;
        }

        .download-all {
            display: inline-block;
            background: #764ba2;
            color: white;
            padding: 15px 30px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 700;
            font-size: 1.1em;
            transition: background 0.3s;
        }

        .download-all:hover {
            background: #5f3a82;
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 1.8em;
            }

            .container {
                border-radius: 10px;
            }

            .sections {
                padding: 20px;
            }

            .section {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎙️ TTS Audio Preview</h1>
            <p>Code Tutorial Audio Output</p>
        </header>

        <div class="stats">
            <div class="stat">
                <div class="stat-value">''' + str(len(timing.get('sections', []))) + '''</div>
                <div class="stat-label">Sections</div>
            </div>
            <div class="stat">
                <div class="stat-value">''' + timing.get('total_duration_formatted', '0:00') + '''</div>
                <div class="stat-label">Total Duration</div>
            </div>
            <div class="stat">
                <div class="stat-value">''' + f"{timing.get('total_duration_seconds', 0):.1f}s" + '''</div>
                <div class="stat-label">Seconds</div>
            </div>
        </div>

        <div class="sections">
''')

    # Generate sections
    for section in timing.get('sections', []):
        section_id = section['section_id']
        file_name = Path(section['file']).name
        duration = section.get('duration_seconds', 0)
        start = section.get('start', '0:00')
        end = section.get('end', '0:00')

        # Get narration and code data
        section_data = sections_data.get(section_id, {})
        title = section_data.get('title', section_id)
        narration = section_data.get('narration', '')
        code = section_data.get('code', '')
        language = section_data.get('language', 'mql5')

        html_parts.append(f'''
            <div class="section">
                <div class="section-header">
                    <div class="section-title">
                        {escape(title)}
                    </div>
                    <div class="section-timing">
                        {start} - {end} ({duration:.1f}s)
                    </div>
                </div>

                <div class="audio-player">
                    <audio controls preload="metadata">
                        <source src="{file_name}" type="audio/mpeg">
                        Your browser does not support audio playback.
                    </audio>
                </div>
''')

        # Add narration if available
        if narration:
            # Clean up control tags for display
            display_narration = narration.replace('(break)', ' • ').replace('(excited)', '😄').replace('(laugh)', '😂')
            html_parts.append(f'''
                <div class="narration-box">
                    <div class="narration-label">
                        <span>📝 Narration</span>
                        <button class="copy-btn" onclick="copyToClipboard('narration-{section_id}', this)">📋 Copy</button>
                    </div>
                    <div class="narration-text" id="narration-{section_id}">{escape(display_narration)}</div>
                </div>
''')

        # Add code if available
        if code:
            html_parts.append(f'''
                <div class="code-box">
                    <div class="code-label">
                        <span>💻 Code ({language})</span>
                        <button class="copy-btn" onclick="copyToClipboard('code-{section_id}', this)">📋 Copy</button>
                    </div>
                    <pre><code id="code-{section_id}">{escape(code)}</code></pre>
                </div>
''')

        html_parts.append(f'''
                <a href="{file_name}" download class="download-link">⬇️ Download {file_name}</a>
            </div>
''')

    # Footer
    html_parts.append('''
        </div>

        <footer>
            <a href="timing.json" download class="download-all">📊 Download timing.json</a>
            <p style="margin-top: 20px; color: #6c757d;">
                Generated with Fish Audio TTS • Ready for video production
            </p>
        </footer>
    </div>

    <script>
        function copyToClipboard(elementId, button) {
            const element = document.getElementById(elementId);
            const text = element.textContent || element.innerText;

            // Use modern Clipboard API
            navigator.clipboard.writeText(text).then(() => {
                // Success feedback
                const originalText = button.innerHTML;
                button.innerHTML = '✓ Copied!';
                button.classList.add('copied');

                // Reset after 2 seconds
                setTimeout(() => {
                    button.innerHTML = originalText;
                    button.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                // Fallback for older browsers
                console.error('Copy failed:', err);
                button.innerHTML = '✗ Failed';
                setTimeout(() => {
                    button.innerHTML = '📋 Copy';
                }, 2000);
            });
        }
    </script>
</body>
</html>
''')

    # Write HTML file
    html_content = ''.join(html_parts)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✓ Generated: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Generate web preview for TTS audio output')
    parser.add_argument('output_dir', help='Directory containing audio files and timing.json')
    parser.add_argument('--narration-file', help='Narration markdown file (optional)')

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    timing_json = output_dir / 'timing.json'
    index_html = output_dir / 'index.html'

    # Check if timing.json exists
    if not timing_json.exists():
        print(f"ERROR: timing.json not found in {output_dir}")
        print("Make sure to generate audio files first with fish_audio_tts.py")
        return 1

    # Extract narrations and code if narration file provided
    sections_data = {}
    if args.narration_file:
        narration_file = Path(args.narration_file)
        if narration_file.exists():
            print(f"Extracting narrations and code from {narration_file}...")
            sections_data = extract_narrations_and_code(narration_file)
            print(f"✓ Found {len(sections_data)} sections")
        else:
            print(f"WARNING: Narration file not found: {narration_file}")

    # Generate HTML
    print(f"Generating HTML preview...")
    generate_html(timing_json, sections_data, index_html)

    print(f"\n✓ Done!")
    print(f"\nOpen in browser:")
    print(f"  file://{index_html.absolute()}")
    print(f"\nOr deploy to web server:")
    print(f"  sudo cp -r {output_dir}/* /var/www/html/tts_test/")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
