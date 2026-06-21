#!/usr/bin/env python3
"""
One-stop pipeline: URL → fetch → screenshot → generate composition → render MP4.

Usage:
    python3 web-to-video.py https://example.com
    python3 web-to-video.py https://example.com --template announcement --duration short --format short
    python3 web-to-video.py https://example.com --no-render  # stop after generating composition

This script chains:
  1. fetch-url.py  → screenshot + extract content + build JSON
  2. generate.py   → create Remotion composition
  3. render.sh     → render MP4 (optional)
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path('/Users/oktos/.openclaw/workspace/skills/remotion-video/scripts')
STUDIO_DIR = Path('/Users/oktos/.openclaw/workspace/remotion-studio')


def run_fetch_url(url: str, template: str, format_key: str, duration: str, screenshot: Path) -> Path:
    """Run fetch-url.py and return the generated JSON path."""
    cmd = [
        sys.executable, str(SKILL_DIR / 'fetch-url.py'),
        url,
        '--template', template,
        '--format', format_key,
        '--duration', duration,
        '--screenshot', str(screenshot),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"fetch-url.py failed with code {result.returncode}")
    
    # Parse output to find JSON path
    for line in result.stdout.split('\n'):
        if line.startswith('✓ Video JSON:'):
            return Path(line.replace('✓ Video JSON:', '').strip())
    
    # Fallback: guess the filename
    return Path('web-video.json')


def run_generate(json_path: Path) -> str:
    """Run generate.py and return the composition ID."""
    cmd = [sys.executable, str(SKILL_DIR / 'generate.py'), str(json_path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"generate.py failed with code {result.returncode}")
    
    # Parse composition ID from output
    for line in result.stdout.split('\n'):
        if line.startswith('✓ Composition generated:'):
            return line.replace('✓ Composition generated:', '').strip()
    
    # Fallback
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data['id']


def run_render(composition_id: str, output_name: str) -> Path:
    """Run render.sh and return the output MP4 path."""
    cmd = [str(SKILL_DIR / 'render.sh'), composition_id, output_name]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"render.sh failed with code {result.returncode}")
    
    # Find output path
    output_dir = STUDIO_DIR / 'output'
    output_file = output_dir / output_name
    return output_file


def main() -> int:
    parser = argparse.ArgumentParser(
        description='URL → screenshot → video pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick 15s TikTok/Reels promo from any website
  python3 web-to-video.py https://yourproduct.com

  # 7s Twitter/X flash announcement
  python3 web-to-video.py https://yourproduct.com --duration snippet --format square

  # 60s YouTube deep dive
  python3 web-to-video.py https://yourproduct.com --duration deep --format landscape

  # Generate only, don't render (for manual preview in Remotion Studio)
  python3 web-to-video.py https://yourproduct.com --no-render
        """
    )
    parser.add_argument('url', help='Website URL to turn into a video')
    parser.add_argument('--template', default='3d-promo',
                       choices=['announcement', 'lead-report', 'data-story', '3d-promo'],
                       help='Video template style')
    parser.add_argument('--format', default='short',
                       choices=['short', 'vertical', 'square', 'landscape', 'widescreen'],
                       help='Video format/platform')
    parser.add_argument('--duration', default='short',
                       help='Duration preset or seconds')
    parser.add_argument('--output', default=None,
                       help='Custom output MP4 filename')
    parser.add_argument('--no-render', action='store_true',
                       help='Stop after generating composition (skip MP4 render)')
    parser.add_argument('--screenshot-dir', type=Path,
                       default=STUDIO_DIR / 'output' / 'screenshots',
                       help='Directory for screenshots')
    args = parser.parse_args()
    
    # Create screenshot directory
    args.screenshot_dir.mkdir(parents=True, exist_ok=True)
    domain = args.url.replace('https://', '').replace('http://', '').split('/')[0].replace('.', '-')
    screenshot = args.screenshot_dir / f"{domain}.png"
    
    print(f"{'='*60}")
    print(f"WEB → VIDEO PIPELINE")
    print(f"{'='*60}")
    print(f"URL:      {args.url}")
    print(f"Template: {args.template}")
    print(f"Duration: {args.duration}")
    print(f"Format:   {args.format}")
    print()
    
    # Step 1: Fetch URL
    print(f"[1/3] Fetching website and extracting content...")
    json_path = run_fetch_url(args.url, args.template, args.format, args.duration, screenshot)
    print(f"      JSON: {json_path}")
    print(f"      Screenshot: {screenshot}")
    print()
    
    # Step 2: Generate composition
    print(f"[2/3] Generating Remotion composition...")
    composition_id = run_generate(json_path)
    print(f"      Composition ID: {composition_id}")
    print()
    
    if args.no_render:
        print("✓ Pipeline complete (composition only)")
        print(f"\nTo render manually:")
        print(f"  npx remotion studio  # preview in browser")
        print(f"  {SKILL_DIR / 'render.sh'} {composition_id}")
        return 0
    
    # Step 3: Render
    print(f"[3/3] Rendering MP4...")
    output_name = args.output or f"{composition_id}.mp4"
    output_path = run_render(composition_id, output_name)
    
    print(f"\n{'='*60}")
    print(f"✓ VIDEO COMPLETE")
    print(f"{'='*60}")
    print(f"MP4:    {output_path}")
    print(f"Size:   {output_path.stat().st_size / 1024 / 1024:.1f} MB")
    print(f"\nPreview:")
    print(f"  open {output_path}")
    print(f"\nUpload to:")
    if args.format in ('short', 'vertical'):
        print(f"  • TikTok / Instagram Reels / YouTube Shorts")
    elif args.format == 'square':
        print(f"  • Instagram Feed / Twitter(X) / LinkedIn")
    elif args.format in ('landscape', 'widescreen'):
        print(f"  • YouTube main / LinkedIn / Twitter(X)")
    
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
