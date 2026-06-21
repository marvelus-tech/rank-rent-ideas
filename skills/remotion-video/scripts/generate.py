#!/usr/bin/env python3
"""Generate a Remotion composition file from JSON spec and register it in Root.tsx.

Supports viral duration presets and platform formats.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

WORKSPACE = Path('/Users/oktos/.openclaw/workspace')
STUDIO_DIR = WORKSPACE / 'remotion-studio'
COMPOSITIONS_DIR = STUDIO_DIR / 'src' / 'compositions'
ROOT_FILE = STUDIO_DIR / 'src' / 'Root.tsx'

TEMPLATE_MAP = {
    'lead-report': ('LeadReportVideo', 'LeadReportVideoProps', 'leadReportTotalFrames'),
    'data-story': ('DataStoryVideo', 'DataStoryVideoProps', 'dataStoryDurationInFrames'),
    'announcement': ('AnnouncementVideo', 'AnnouncementVideoProps', 'announcementDurationInFrames'),
    '3d-promo': ('Promo3DVideo', 'Promo3DVideoProps', 'promo3DDurationInFrames'),
    'apple-style': ('AppleStyleVideo', 'AppleStyleVideoProps', 'appleStyleDurationInFrames'),
}

# Platform format presets
FORMATS = {
    'short': (1080, 1920),      # TikTok / Reels / Shorts
    'vertical': (1080, 1920),   # Vertical mobile
    'square': (1080, 1080),     # Instagram Feed / Twitter
    'landscape': (1920, 1080),  # YouTube / LinkedIn
    'widescreen': (1920, 1080), # Widescreen
}

# Viral duration presets (seconds)
DURATION_PRESETS = {
    'hook': 5,          # Ultra-short hook (TikTok/Reels best)
    'snippet': 7,       # Micro-content (highest completion rate)
    'flash': 10,        # Quick story (Twitter/X native)
    'short': 15,        # Short-form sweet spot (TikTok/Reels optimal)
    'standard': 30,     # Standard short-form (YouTube Shorts max)
    'story': 45,        # Narrative story (LinkedIn, Instagram)
    'deep': 60,         # Deep dive (YouTube, LinkedIn long-form)
}

def pascal_case(text: str) -> str:
    return ''.join(part.capitalize() for part in re.split(r'[^a-zA-Z0-9]+', text) if part)


def generate_component_source(component_name: str, template_component: str, props_type: str, props: dict) -> str:
    props_json = json.dumps(props, indent=2, ensure_ascii=False)
    return f'''import React from 'react';
import {{{template_component}, type {props_type}}} from './{template_component}';

const generatedProps: {props_type} = {props_json};

export const {component_name}: React.FC = () => <{template_component} {{...generatedProps}} />;
'''


def update_root(root_text: str, composition_id: str, component_name: str, duration_frames: int, 
                width: int = 1080, height: int = 1920) -> str:
    import_line = f"import {{{component_name}}} from './compositions/{component_name}';"
    if import_line not in root_text:
        anchor = "import {\n  defaultLeadReportProps,\n  LeadReportVideo,\n} from './compositions/LeadReportVideo';"
        root_text = root_text.replace(anchor, anchor + '\n' + import_line)

    comp_block = f'''
        <Composition
          id="{composition_id}"
          component={{{component_name}}}
          durationInFrames={{{duration_frames}}}
          fps={{30}}
          width={{{width}}}
          height={{{height}}}
        />\n'''

    if f'id="{composition_id}"' in root_text:
        return root_text

    marker = '      </Folder>'
    return root_text.replace(marker, comp_block + marker)


def main() -> int:
    parser = argparse.ArgumentParser(description='Generate Remotion composition from JSON data')
    parser.add_argument('input', type=Path, help='Path to JSON input file')
    args = parser.parse_args()

    with args.input.open('r', encoding='utf-8') as f:
        spec = json.load(f)

    composition_id = spec['id']
    template = spec['template']
    
    # Handle duration - support presets or raw seconds
    duration_raw = spec.get('durationInSeconds', 'standard')
    if isinstance(duration_raw, str):
        if duration_raw in DURATION_PRESETS:
            duration_sec = DURATION_PRESETS[duration_raw]
            print(f"Using duration preset: {duration_raw} = {duration_sec}s")
        else:
            print(f"Unknown duration preset '{duration_raw}', using 'standard' (30s)")
            duration_sec = DURATION_PRESETS['standard']
    else:
        duration_sec = int(duration_raw)
    
    # Handle format/platform
    format_key = spec.get('format', 'short')
    if format_key in FORMATS:
        width, height = FORMATS[format_key]
        print(f"Using format: {format_key} ({width}x{height})")
    else:
        width, height = 1080, 1920
        print(f"Unknown format '{format_key}', using default short (1080x1920)")
    
    props = spec['props']
    # Inject duration into props if the component supports it
    if template == 'lead-report':
        props['durationInSeconds'] = duration_sec

    if template not in TEMPLATE_MAP:
        allowed = ', '.join(TEMPLATE_MAP.keys())
        raise ValueError(f'Unsupported template: {template}. Allowed: {allowed}')

    template_component, props_type, _ = TEMPLATE_MAP[template]
    component_name = pascal_case(composition_id)
    output_file = COMPOSITIONS_DIR / f'{component_name}.tsx'

    source = generate_component_source(component_name, template_component, props_type, props)
    output_file.write_text(source, encoding='utf-8')

    duration_frames = max(150, duration_sec * 30)  # minimum 5 seconds
    root_text = ROOT_FILE.read_text(encoding='utf-8')
    updated_root = update_root(root_text, composition_id, component_name, duration_frames, width, height)
    ROOT_FILE.write_text(updated_root, encoding='utf-8')

    print(f"✓ Composition generated: {composition_id}")
    print(f"  Duration: {duration_sec}s ({duration_frames} frames @ 30fps)")
    print(f"  Format: {format_key} ({width}x{height})")
    print(f"  File: {output_file}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
