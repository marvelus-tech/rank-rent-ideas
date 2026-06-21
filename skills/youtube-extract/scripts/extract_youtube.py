#!/usr/bin/env python3
"""Extract transcript and metadata from a YouTube URL using yt-dlp."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ExtractConfig:
    url: str
    output: Path
    retries: int = 3
    timeout_ms: int = 30000
    language: str = "en"
    # Kept for CLI backward-compatibility with the old Playwright script.
    headful: bool = False
    user_agent: str = ""


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def run_cmd(cmd: List[str], timeout_ms: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        timeout=max(1, timeout_ms // 1000),
    )


def ensure_yt_dlp() -> Optional[str]:
    if shutil.which("yt-dlp"):
        return None
    return (
        "yt-dlp is not installed. Install it with one of:\n"
        "  pipx install yt-dlp\n"
        "  python3 -m pip install -U yt-dlp"
    )


def list_subtitles(url: str, timeout_ms: int) -> Dict[str, Any]:
    proc = run_cmd(["yt-dlp", "--list-subs", url], timeout_ms)
    return {
        "ok": proc.returncode == 0,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "returncode": proc.returncode,
    }


def find_srt_file(workdir: Path, stem: str, language: str) -> Optional[Path]:
    candidates = sorted(workdir.glob(f"{stem}*.{language}*.srt"))
    if not candidates:
        candidates = sorted(workdir.glob(f"{stem}*.srt"))
    return candidates[0] if candidates else None


def parse_timecode_to_seconds(ts: str) -> Optional[float]:
    m = re.match(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", ts.strip())
    if not m:
        return None
    hh, mm, ss, ms = map(int, m.groups())
    return round(hh * 3600 + mm * 60 + ss + ms / 1000.0, 3)


def parse_srt(srt_path: Path) -> List[Dict[str, Any]]:
    content = srt_path.read_text(encoding="utf-8", errors="replace").strip()
    if not content:
        return []

    segments: List[Dict[str, Any]] = []
    blocks = re.split(r"\n\s*\n", content)
    for block in blocks:
        lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue

        time_idx = 1 if re.fullmatch(r"\d+", lines[0]) else 0
        if time_idx >= len(lines) or "-->" not in lines[time_idx]:
            continue

        start_raw = lines[time_idx].split("-->", 1)[0].strip()
        start = parse_timecode_to_seconds(start_raw)
        text_lines = lines[time_idx + 1 :]
        if not text_lines:
            continue

        text = " ".join(text_lines)
        text = re.sub(r"<[^>]+>", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            continue

        segments.append({"start": start, "text": text})

    return segments


def segments_to_text(segments: List[Dict[str, Any]]) -> str:
    return "\n".join(seg.get("text", "") for seg in segments if seg.get("text"))


def get_metadata(url: str, timeout_ms: int) -> Dict[str, Any]:
    proc = run_cmd(["yt-dlp", "--dump-json", "--skip-download", url], timeout_ms)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise RuntimeError((proc.stderr or "yt-dlp metadata extraction failed").strip())

    first_json_line = proc.stdout.strip().splitlines()[0]
    raw = json.loads(first_json_line)

    upload_date = raw.get("upload_date")
    publish_date = None
    if isinstance(upload_date, str) and len(upload_date) == 8:
        publish_date = f"{upload_date[0:4]}-{upload_date[4:6]}-{upload_date[6:8]}"

    return {
        "video_id": raw.get("id"),
        "title": raw.get("title"),
        "channel": raw.get("channel") or raw.get("uploader"),
        "description": raw.get("description"),
        "duration_seconds": raw.get("duration"),
        "publish_date": publish_date,
    }


def extract_once(config: ExtractConfig) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "extracted_at": now_iso(),
        "url": config.url,
        "video_id": None,
        "title": None,
        "channel": None,
        "description": None,
        "duration_seconds": None,
        "publish_date": None,
        "transcript": {
            "method": "none",
            "language": None,
            "text": "",
            "segments": [],
        },
        "status": "error",
        "errors": [],
    }

    missing_err = ensure_yt_dlp()
    if missing_err:
        result["errors"].append(missing_err)
        return result

    if config.headful:
        result["errors"].append("--headful is ignored in yt-dlp mode")
    if config.user_agent:
        result["errors"].append("--user-agent is ignored in yt-dlp mode")

    try:
        metadata = get_metadata(config.url, config.timeout_ms)
        result.update(metadata)
    except Exception as e:
        result["errors"].append(f"Metadata extraction failed: {e}")

    subs_info = list_subtitles(config.url, config.timeout_ms)
    if not subs_info["ok"]:
        err = (subs_info.get("stderr") or "").strip() or f"returncode={subs_info['returncode']}"
        result["errors"].append(f"Subtitle listing failed: {err}")

    with tempfile.TemporaryDirectory(prefix="youtube_extract_") as td:
        tmpdir = Path(td)
        output_stem = "captions"
        template = str(tmpdir / output_stem)

        cmd = [
            "yt-dlp",
            "--write-auto-subs",
            "--skip-download",
            "--sub-langs",
            config.language,
            "--convert-subs",
            "srt",
            "-o",
            template,
            config.url,
        ]
        proc = run_cmd(cmd, config.timeout_ms)
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "subtitle download failed").strip()
            result["errors"].append(f"Subtitle extraction failed: {err}")
        else:
            srt_path = find_srt_file(tmpdir, output_stem, config.language)
            if not srt_path:
                result["errors"].append("yt-dlp completed but no SRT subtitle file was found")
            else:
                segments = parse_srt(srt_path)
                result["transcript"] = {
                    "method": "yt_dlp_auto_subs",
                    "language": config.language,
                    "text": segments_to_text(segments),
                    "segments": segments,
                }

    has_meta = any(result.get(k) for k in ["title", "channel", "description", "video_id"])
    has_text = bool(result.get("transcript", {}).get("text"))

    if has_text:
        result["status"] = "ok"
    elif has_meta:
        result["status"] = "partial"
    else:
        result["status"] = "error"

    return result


def extract_with_retries(config: ExtractConfig) -> Dict[str, Any]:
    last: Dict[str, Any] = {}
    for attempt in range(config.retries + 1):
        if attempt > 0:
            time.sleep(min(10, 2 ** (attempt - 1)))
        last = extract_once(config)
        if last.get("status") == "ok":
            return last
    return last


def parse_args(argv: List[str]) -> ExtractConfig:
    parser = argparse.ArgumentParser(description="Extract YouTube transcript + metadata")
    parser.add_argument("url", help="YouTube video URL")
    parser.add_argument("--output", default="youtube_extract.json", help="Output JSON path")
    parser.add_argument("--retries", type=int, default=3, help="Retry count")
    parser.add_argument("--timeout-ms", type=int, default=30000, help="Command timeout in ms")
    parser.add_argument("--headful", action="store_true", help="Deprecated, ignored in yt-dlp mode")
    parser.add_argument("--user-agent", default="", help="Deprecated, ignored in yt-dlp mode")
    parser.add_argument("--language", default="en", help="Preferred transcript language")

    ns = parser.parse_args(argv)
    return ExtractConfig(
        url=ns.url,
        output=Path(ns.output),
        retries=max(ns.retries, 0),
        timeout_ms=max(ns.timeout_ms, 1000),
        headful=ns.headful,
        user_agent=ns.user_agent,
        language=ns.language,
    )


def main(argv: List[str]) -> int:
    config = parse_args(argv)
    result = extract_with_retries(config)

    config.output.parent.mkdir(parents=True, exist_ok=True)
    config.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Saved output to {config.output}")
    print(f"status={result.get('status')} method={result.get('transcript', {}).get('method')}")

    return 0 if result.get("status") != "error" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
