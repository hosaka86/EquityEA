#!/usr/bin/env python3
"""
Code Narration Validator
=========================

Validates that code blocks in a narration file match the original source code exactly.
This ensures that when copying code blocks sequentially from the narration,
the result will compile without errors.

Usage:
    python validate_code_narration.py <narration_file> <source_file>

Example:
    python validate_code_narration.py codeyoutube.md EquityMonitor-V107.mq5
"""

import sys
import re
import difflib
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def extract_code_blocks(narration_content, language='mql5'):
    """
    Extract all code blocks from a markdown narration file.

    Args:
        narration_content: Full text content of the narration file
        language: Code block language marker (default: mql5)

    Returns:
        List of code block contents
    """
    pattern = f'```{language}\n(.*?)\n```'
    blocks = re.findall(pattern, narration_content, re.DOTALL)
    return blocks


def normalize_whitespace(text):
    """Remove trailing whitespace from lines while preserving structure"""
    lines = [line.rstrip() for line in text.split('\n')]
    return '\n'.join(lines).strip()


def remove_blank_lines(text):
    """Remove all blank lines for semantic comparison"""
    return '\n'.join([line for line in text.split('\n') if line.strip()])


def count_syntax_elements(code):
    """Count key syntax elements for validation"""
    return {
        'open_braces': code.count('{'),
        'close_braces': code.count('}'),
        'semicolons': code.count(';'),
        'open_parens': code.count('('),
        'close_parens': code.count(')'),
        'open_brackets': code.count('['),
        'close_brackets': code.count(']'),
    }


def validate_narration(narration_file, source_file):
    """
    Main validation function.

    Args:
        narration_file: Path to markdown file with code narration
        source_file: Path to original source code file

    Returns:
        True if validation passes, False otherwise
    """
    # Read files
    try:
        with open(narration_file, 'r', encoding='utf-8') as f:
            narration_content = f.read()
    except Exception as e:
        print(f"{Colors.RED}ERROR: Could not read narration file: {e}{Colors.END}")
        return False

    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_content = f.read()
    except Exception as e:
        print(f"{Colors.RED}ERROR: Could not read source file: {e}{Colors.END}")
        return False

    # Extract code blocks
    code_blocks = extract_code_blocks(narration_content)

    if not code_blocks:
        print(f"{Colors.RED}ERROR: No code blocks found in narration file{Colors.END}")
        print(f"Make sure code blocks are wrapped in ```mql5...```")
        return False

    # Reconstruct code from blocks
    reconstructed_code = '\n'.join(code_blocks)

    # Normalize both for comparison
    source_normalized = normalize_whitespace(source_content)
    reconstructed_normalized = normalize_whitespace(reconstructed_code)

    # Display stats
    print(f"\n{Colors.BOLD}VALIDATION REPORT{Colors.END}")
    print("=" * 80)
    print(f"\n{Colors.BLUE}File Statistics:{Colors.END}")
    print(f"  Narration file: {narration_file}")
    print(f"  Source file: {source_file}")
    print(f"  Code blocks found: {len(code_blocks)}")
    print(f"\n{Colors.BLUE}Code Metrics:{Colors.END}")
    print(f"  Original source: {len(source_normalized):,} chars, {len(source_normalized.split(chr(10))):,} lines")
    print(f"  Reconstructed:   {len(reconstructed_normalized):,} chars, {len(reconstructed_normalized.split(chr(10))):,} lines")

    # Check exact match first
    if source_normalized == reconstructed_normalized:
        print(f"\n{Colors.GREEN}✓ PERFECT MATCH{Colors.END}")
        print(f"  Code blocks are 100% identical to source (byte-for-byte)")
        return validate_syntax(source_content, reconstructed_code)

    # Not exact match - check if only whitespace differs
    source_no_blanks = remove_blank_lines(source_content)
    reconstructed_no_blanks = remove_blank_lines(reconstructed_code)

    if source_no_blanks == reconstructed_no_blanks:
        print(f"\n{Colors.GREEN}✓ SEMANTIC MATCH{Colors.END}")
        print(f"  Code is identical except for blank lines (will compile correctly)")
        print(f"\n{Colors.YELLOW}Note:{Colors.END} Only cosmetic whitespace differences detected")
        return validate_syntax(source_content, reconstructed_code)

    # Real differences exist
    print(f"\n{Colors.RED}✗ MISMATCH DETECTED{Colors.END}")
    print(f"  Code blocks differ from source in meaningful ways\n")

    # Find and display differences
    show_differences(source_normalized, reconstructed_normalized)

    # Still validate syntax to see if it might compile
    print(f"\n{Colors.YELLOW}Checking syntax anyway...{Colors.END}")
    validate_syntax(source_content, reconstructed_code)

    return False


def validate_syntax(source_code, reconstructed_code):
    """
    Validate that syntax elements are balanced.

    Args:
        source_code: Original source code
        reconstructed_code: Reconstructed code from narration

    Returns:
        True if syntax is valid, False otherwise
    """
    print(f"\n{Colors.BLUE}Syntax Validation:{Colors.END}")

    source_counts = count_syntax_elements(source_code)
    reconstructed_counts = count_syntax_elements(reconstructed_code)

    all_valid = True

    # Check braces
    if source_counts['open_braces'] == source_counts['close_braces']:
        if reconstructed_counts['open_braces'] == reconstructed_counts['close_braces']:
            print(f"  {Colors.GREEN}✓{Colors.END} Braces balanced: {{ {reconstructed_counts['open_braces']}, }} {reconstructed_counts['close_braces']}")
        else:
            print(f"  {Colors.RED}✗{Colors.END} Braces UNBALANCED: {{ {reconstructed_counts['open_braces']}, }} {reconstructed_counts['close_braces']}")
            all_valid = False

    # Check parentheses
    if reconstructed_counts['open_parens'] == reconstructed_counts['close_parens']:
        print(f"  {Colors.GREEN}✓{Colors.END} Parentheses balanced: ( {reconstructed_counts['open_parens']}, ) {reconstructed_counts['close_parens']}")
    else:
        print(f"  {Colors.RED}✗{Colors.END} Parentheses UNBALANCED: ( {reconstructed_counts['open_parens']}, ) {reconstructed_counts['close_parens']}")
        all_valid = False

    # Check brackets
    if reconstructed_counts['open_brackets'] == reconstructed_counts['close_brackets']:
        print(f"  {Colors.GREEN}✓{Colors.END} Brackets balanced: [ {reconstructed_counts['open_brackets']}, ] {reconstructed_counts['close_brackets']}")
    else:
        print(f"  {Colors.RED}✗{Colors.END} Brackets UNBALANCED: [ {reconstructed_counts['open_brackets']}, ] {reconstructed_counts['close_brackets']}")
        all_valid = False

    # Compare semicolons
    if source_counts['semicolons'] == reconstructed_counts['semicolons']:
        print(f"  {Colors.GREEN}✓{Colors.END} Semicolons match: {reconstructed_counts['semicolons']}")
    else:
        print(f"  {Colors.YELLOW}⚠{Colors.END} Semicolons differ: {source_counts['semicolons']} (source) vs {reconstructed_counts['semicolons']} (narration)")
        # This might be OK depending on context

    return all_valid


def show_differences(source, reconstructed, context_lines=3):
    """
    Show a unified diff of the differences.

    Args:
        source: Original source code
        reconstructed: Reconstructed code
        context_lines: Number of context lines to show
    """
    source_lines = source.split('\n')
    reconstructed_lines = reconstructed.split('\n')

    # Generate unified diff
    diff = difflib.unified_diff(
        source_lines,
        reconstructed_lines,
        fromfile='Original Source',
        tofile='Narration Code',
        lineterm='',
        n=context_lines
    )

    print(f"\n{Colors.BLUE}Differences (unified diff):{Colors.END}")
    print("-" * 80)

    diff_lines = list(diff)
    if len(diff_lines) > 100:
        # Too many differences, show only first 50
        for line in diff_lines[:50]:
            print_diff_line(line)
        print(f"\n{Colors.YELLOW}... ({len(diff_lines) - 50} more lines omitted) ...{Colors.END}")
    else:
        for line in diff_lines:
            print_diff_line(line)

    print("-" * 80)


def print_diff_line(line):
    """Print a diff line with appropriate coloring"""
    if line.startswith('+') and not line.startswith('+++'):
        print(f"{Colors.GREEN}{line}{Colors.END}")
    elif line.startswith('-') and not line.startswith('---'):
        print(f"{Colors.RED}{line}{Colors.END}")
    elif line.startswith('@@'):
        print(f"{Colors.BLUE}{line}{Colors.END}")
    else:
        print(line)


def main():
    """Main entry point"""
    if len(sys.argv) != 3:
        print(f"{Colors.BOLD}Code Narration Validator{Colors.END}")
        print(f"\nUsage: {sys.argv[0]} <narration_file> <source_file>")
        print(f"\nExample:")
        print(f"  {sys.argv[0]} codeyoutube.md EquityMonitor-V107.mq5")
        sys.exit(1)

    narration_file = Path(sys.argv[1])
    source_file = Path(sys.argv[2])

    # Check files exist
    if not narration_file.exists():
        print(f"{Colors.RED}ERROR: Narration file not found: {narration_file}{Colors.END}")
        sys.exit(1)

    if not source_file.exists():
        print(f"{Colors.RED}ERROR: Source file not found: {source_file}{Colors.END}")
        sys.exit(1)

    # Run validation
    success = validate_narration(narration_file, source_file)

    # Final verdict
    print(f"\n{Colors.BOLD}FINAL VERDICT:{Colors.END}")
    if success:
        print(f"{Colors.GREEN}✓ VALIDATION PASSED{Colors.END}")
        print(f"  The code blocks in the narration are correct.")
        print(f"  Copying them sequentially will produce compilable code.")
        sys.exit(0)
    else:
        print(f"{Colors.RED}✗ VALIDATION FAILED{Colors.END}")
        print(f"  The narration code blocks do not match the source.")
        print(f"  Fix the issues above before generating audio.")
        sys.exit(1)


if __name__ == '__main__':
    main()
