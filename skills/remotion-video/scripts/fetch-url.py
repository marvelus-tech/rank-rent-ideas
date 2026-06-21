#!/usr/bin/env python3
"""
Fetch a website, screenshot it, and extract structured content for video generation.

Usage:
    python3 fetch-url.py https://example.com output.json
    python3 fetch-url.py https://example.com --template announcement --format short --duration short

Outputs a JSON file ready for remotion-video/scripts/generate.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("Error: playwright not installed. Run: pip install playwright", file=sys.stderr)
    sys.exit(1)


def extract_content(page) -> dict:
    """Extract key content from the page."""
    return page.evaluate("""
        () => {
            const data = {
                title: document.title || '',
                description: '',
                headlines: [],
                stats: [],
                ctas: [],
                images: [],
                url: window.location.href,
                domain: window.location.hostname
            };

            // Meta description
            const metaDesc = document.querySelector('meta[name="description"]') ||
                           document.querySelector('meta[property="og:description"]');
            if (metaDesc) data.description = metaDesc.content || '';

            // Headlines (h1, h2)
            document.querySelectorAll('h1, h2').forEach(h => {
                const text = h.innerText.trim();
                if (text && text.length < 100) data.headlines.push(text);
            });

            // Stats/numbers - look for percentages, dollar amounts, counts
            const bodyText = document.body.innerText;
            const statPatterns = [
                /\\b(\\d{1,3}(?:,\\d{3})*(?:\\+?%?))/g,  // 1,000+ or 50%
                /\\b(\\$\\d+(?:\\.\\d{2})?(?:[KMB]?))/gi,  // $1,000 or $5M
                /\\b(\\d+x)\b/gi,  // 10x
            ];
            statPatterns.forEach(pattern => {
                const matches = bodyText.match(pattern);
                if (matches) data.stats.push(...matches.slice(0, 5));
            });
            data.stats = [...new Set(data.stats)].slice(0, 5);

            // CTAs - button/link text
            document.querySelectorAll('a, button').forEach(el => {
                const text = el.innerText.trim();
                if (text && /(?:get|start|try|learn|buy|sign|join|download|watch|see)/i.test(text)) {
                    if (text.length < 50) data.ctas.push(text);
                }
            });
            data.ctas = [...new Set(data.ctas)].slice(0, 5);

            // Images
            document.querySelectorAll('img').forEach(img => {
                const src = img.src;
                if (src && !src.includes('data:') && !src.includes('icon') && !src.includes('logo')) {
                    data.images.push(src);
                }
            });
            data.images = data.images.slice(0, 5);

            return data;
        }
    """)


def build_video_json(content: dict, template: str, format_key: str, duration: str, screenshot_filename: str | None = None) -> dict:
    """Convert extracted content to remotion-video JSON."""

    title = content['title'] or 'Website Overview'
    # Clean up title
    title = re.sub(r'\s*[\|\---]\s*.*$', '', title)  # Remove pipe/dash suffixes

    headlines = content['headlines'][:3]
    stats = content['stats'][:3]
    ctas = content['ctas'][:2]

    # Better description extraction
    description = content['description']
    if not description or len(description) < 20:
        # Try to build from headlines
        description = ' · '.join(headlines[:2]) if headlines else f"Content from {content['domain']}"

    # Smart title selection
    main_title = headlines[0] if headlines else title
    if len(main_title) > 80:
        main_title = main_title[:77] + '...'

    # Clean up domain for kicker
    kicker = content['domain'].upper().replace('WWW.', '').replace('.', ' · ')

    if template == 'announcement':
        benefit = description[:100] if description else f"Discover {content['domain']}"
        cta = ctas[0] if ctas else "Learn More"
        # Clean up CTA
        cta = re.sub(r'\s+', ' ', cta).strip()
        if len(cta) > 30:
            cta = "Learn More"

        props = {
            "kicker": kicker,
            "title": main_title,
            "benefit": benefit,
            "cta": cta,
            "imageUrl": screenshot_filename,
            "durationInSeconds": 15,
            "logoText": content['domain'].upper().replace('WWW.', '').split('.')[0],
        }
    elif template == '3d-promo':
        benefit = description[:100] if description else f"Discover {content['domain']}"
        cta = ctas[0] if ctas else "Learn More"
        cta = re.sub(r'\s+', ' ', cta).strip()
        if len(cta) > 30:
            cta = "Learn More"

        props = {
            "kicker": kicker,
            "title": main_title,
            "benefit": benefit,
            "cta": cta,
            "imageUrl": screenshot_filename,
            "durationInSeconds": 15,
            "logoText": content['domain'].upper().replace('WWW.', '').split('.')[0],
        }
    elif template == 'lead-report':
        # Treat extracted stats as metrics
        metrics = []
        for i, stat in enumerate(stats):
            metrics.append({
                "label": f"Key Metric {i+1}",
                "value": stat,
                "suffix": ""
            })
        if not metrics:
            metrics = [{"label": "Pages", "value": 1}]

        props = {
            "title": title,
            "kicker": content['domain'].upper(),
            "date": content['url'][:50],
            "durationInSeconds": 15,
            "metrics": metrics,
            "leads": [
                {"name": headlines[0][:30] if headlines else "Main Feature",
                 "company": content['domain'],
                 "score": 85,
                 "priority": "High"}
            ],
            "bigNumber": {"value": str(len(headlines)), "label": "Key highlights found"},
            "actions": [{"title": ctas[0] if ctas else "Visit Site",
                        "detail": content['description'][:60] if content['description'] else f"{content['domain']}",
                        "urgency": "High"}]
        }
    elif template == 'data-story':
        points = []
        for i, stat in enumerate(stats):
            points.append({
                "label": headlines[i] if i < len(headlines) else f"Point {i+1}",
                "value": stat,
                "color": ["#0071E3", "#34C759", "#FF9500"][i % 3]
            })
        if not points:
            points = [{"label": "Pages", "value": 1, "color": "#0071E3"}]

        props = {
            "title": title,
            "kicker": content['domain'].upper(),
            "subtitle": content['description'][:60] if content['description'] else "",
            "points": points
        }
    else:
        props = {}

    # Resolve duration
    duration_map = {
        'hook': 5, 'snippet': 7, 'flash': 10, 'short': 15,
        'standard': 30, 'story': 45, 'deep': 60
    }
    duration_sec = duration_map.get(duration, 15) if isinstance(duration, str) else int(duration)

    if template == 'lead-report' and 'durationInSeconds' in props:
        props['durationInSeconds'] = duration_sec

    return {
        "id": f"web-{content['domain'].replace('.', '-')}-{template}",
        "template": template,
        "durationInSeconds": duration,
        "format": format_key,
        "props": props
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Fetch a website and convert to video JSON')
    parser.add_argument('url', help='Website URL to screenshot and analyze')
    parser.add_argument('output', nargs='?', type=Path, help='Output JSON file (default: auto-named)')
    parser.add_argument('--template', default='3d-promo',
                       choices=['announcement', 'lead-report', 'data-story', '3d-promo'],
                       help='Video template to use')
    parser.add_argument('--format', default='short',
                       choices=['short', 'vertical', 'square', 'landscape', 'widescreen'],
                       help='Video format/platform')
    parser.add_argument('--duration', default='short',
                       help='Duration preset (hook/snippet/flash/short/standard/story/deep) or seconds')
    parser.add_argument('--screenshot', type=Path, help='Save screenshot to this path')
    parser.add_argument('--full-page', action='store_true', help='Take full-page screenshot instead of viewport')
    parser.add_argument('--headless', action='store_true', default=True, help='Run browser headless')
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()

        print(f"Fetching: {args.url}")
        try:
            page.goto(args.url, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"Error loading page: {e}", file=sys.stderr)
            browser.close()
            return 1

        # Extract content
        content = extract_content(page)
        print(f"Title: {content['title']}")
        print(f"Headlines: {len(content['headlines'])}")
        print(f"Stats found: {len(content['stats'])}")
        print(f"CTAs found: {len(content['ctas'])}")

        # Screenshot
        if args.screenshot:
            # Default: viewport screenshot (better for 3D cards)
            # Use 1280x800 viewport for ~16:10 aspect ratio that fits card frame
            page.set_viewport_size({'width': 1280, 'height': 800})
            page.screenshot(path=str(args.screenshot), full_page=args.full_page)
            print(f"Screenshot: {args.screenshot} ({'full-page' if args.full_page else 'viewport 1280x800'})")

        # Copy screenshot to remotion public dir for staticFile() access
        screenshot_filename = None
        if args.screenshot:
            screenshot_path = Path(args.screenshot)
            if screenshot_path.exists():
                public_dir = Path('/Users/oktos/.openclaw/workspace/remotion-studio/public')
                public_dir.mkdir(parents=True, exist_ok=True)
                dest = public_dir / screenshot_path.name
                import shutil
                shutil.copy2(screenshot_path, dest)
                screenshot_filename = screenshot_path.name
                print(f"Copied screenshot to public/: {screenshot_filename}")

        browser.close()

    # Build video JSON
    video_json = build_video_json(content, args.template, args.format, args.duration, screenshot_filename)

    # Determine output path
    if args.output:
        output_path = args.output
    else:
        domain = content['domain'].replace('.', '-')
        output_path = Path(f"web-{domain}-{args.template}.json")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(video_json, f, indent=2, ensure_ascii=False)

    print(f"✓ Video JSON: {output_path}")
    print(f"  Template: {args.template}")
    print(f"  Duration: {args.duration}")
    print(f"  Format: {args.format}")
    print(f"\nNext step:")
    print(f"  python3 ~/.openclaw/workspace/skills/remotion-video/scripts/generate.py {output_path}")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
