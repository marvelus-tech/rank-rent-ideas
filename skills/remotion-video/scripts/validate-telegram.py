#!/usr/bin/env python3
"""
Validate a video file for Telegram compatibility.

Usage:
    python3 validate-telegram.py video.mp4

Checks:
    - H.264 video codec
    - yuv420p pixel format (NOT yuvj420p)
    - Baseline profile
    - AAC audio
    - File size < 50MB (Telegram limit for non-premium)
    - Duration < 60s (recommended for viral)
    - Dimensions (9:16, 1:1, or 16:9)

Exit codes:
    0 = Compatible
    1 = Incompatible (details printed)
"""

import json
import subprocess
import sys
from pathlib import Path


def ffprobe(video_path: str) -> dict:
    """Run ffprobe and return stream info."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=codec_name,pix_fmt,profile,level,width,height',
        '-show_entries', 'format=duration,size',
        '-of', 'json',
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ ffprobe failed: {result.stderr}")
        sys.exit(1)
    return json.loads(result.stdout)


def check_audio(video_path: str) -> str:
    """Get audio codec."""
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'a:0',
        '-show_entries', 'stream=codec_name',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def validate(video_path: str) -> bool:
    """Validate video and return True if compatible."""
    path = Path(video_path)
    if not path.exists():
        print(f"❌ File not found: {video_path}")
        return False

    print(f"🔍 Validating: {video_path}")
    print(f"   Size: {path.stat().st_size / 1024 / 1024:.1f} MB")

    info = ffprobe(video_path)
    stream = info.get('streams', [{}])[0]
    fmt = info.get('format', {})

    issues = []

    # Video codec
    codec = stream.get('codec_name', 'unknown')
    if codec != 'h264':
        issues.append(f"Codec: {codec} (needs h264)")
    else:
        print(f"   ✅ Codec: {codec}")

    # Pixel format
    pix_fmt = stream.get('pix_fmt', 'unknown')
    if pix_fmt not in ('yuv420p', 'yuvj420p'):
        issues.append(f"Pixel format: {pix_fmt} (needs yuv420p)")
    elif pix_fmt == 'yuvj420p':
        issues.append(f"Pixel format: {pix_fmt} (yuvj420p may fail on some devices, use yuv420p)")
    else:
        print(f"   ✅ Pixel format: {pix_fmt}")

    # Profile
    profile = stream.get('profile', 'unknown')
    if 'Baseline' not in profile and 'Constrained' not in profile:
        issues.append(f"Profile: {profile} (recommend Baseline for max compatibility)")
    else:
        print(f"   ✅ Profile: {profile}")

    # Audio
    audio = check_audio(video_path)
    if audio and audio != 'aac':
        issues.append(f"Audio: {audio} (recommend aac)")
    elif audio:
        print(f"   ✅ Audio: {audio}")
    else:
        print(f"   ⚠️  No audio stream")

    # Dimensions
    width = stream.get('width', 0)
    height = stream.get('height', 0)
    if width and height:
        ratio = width / height
        if ratio in (9/16, 16/9, 1.0):
            print(f"   ✅ Dimensions: {width}x{height} ({ratio:.2f})")
        else:
            print(f"   ⚠️  Dimensions: {width}x{height} (unusual ratio {ratio:.2f})")
    else:
        issues.append("Could not detect dimensions")

    # Duration
    duration = float(fmt.get('duration', 0))
    if duration > 60:
        issues.append(f"Duration: {duration:.1f}s (recommend <60s for viral)")
    else:
        print(f"   ✅ Duration: {duration:.1f}s")

    # File size
    size_mb = path.stat().st_size / 1024 / 1024
    if size_mb > 50:
        issues.append(f"Size: {size_mb:.1f}MB (Telegram limit for non-premium: 50MB)")
    elif size_mb > 20:
        print(f"   ⚠️  Size: {size_mb:.1f}MB (large but under 50MB limit)")
    else:
        print(f"   ✅ Size: {size_mb:.1f}MB")

    if issues:
        print(f"\n❌ INCOMPATIBLE — {len(issues)} issue(s):")
        for issue in issues:
            print(f"   • {issue}")
        print(f"\n🔧 Fix: ~/.openclaw/workspace/skills/remotion-video/scripts/telegram-fix.sh {video_path}")
        return False
    else:
        print(f"\n✅ Telegram compatible!")
        return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    ok = validate(sys.argv[1])
    sys.exit(0 if ok else 1)
