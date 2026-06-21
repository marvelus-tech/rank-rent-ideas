#!/usr/bin/env python3
"""Integration tests for email handoff (no Whisper). Run: python3 test_handoff_integration.py"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

# Ensure we import the local watcher
sys.path.insert(0, str(Path(__file__).resolve().parent))

import watcher  # noqa: E402

STEM = "test-e2e-handoff"


def cleanup_handoff_files() -> None:
    for name in (f"{STEM}.request.json", f"{STEM}.reply.json"):
        p = watcher.EMAIL_HANDOFF_DIR / name
        if p.exists():
            p.unlink()


def fake_stage(_p: Path, s: str) -> None:
    pass


def test_template_path() -> None:
    cleanup_handoff_files()
    os.environ.pop("EMAIL_DRAFT_HOOK", None)
    os.environ["OPENCLAW_EMAIL_WAIT_SECONDS"] = "0"
    job_path = watcher.JOB_SIGNAL_DIR / f"{STEM}.json"
    email, src = watcher.draft_email_for_job(
        job_path, "TestClient", "Discussed sleep hygiene and follow-up next week.", fake_stage
    )
    assert src == "template", src
    assert "TestClient" in email
    req = watcher.EMAIL_HANDOFF_DIR / f"{STEM}.request.json"
    assert req.exists(), "request.json should exist"
    data = json.loads(req.read_text())
    assert data["transcript"].startswith("Discussed")
    assert data["clientName"] == "TestClient"
    print("OK: template path + request.json written")


def test_openclaw_reply_path() -> None:
    cleanup_handoff_files()
    os.environ.pop("EMAIL_DRAFT_HOOK", None)
    os.environ["OPENCLAW_EMAIL_WAIT_SECONDS"] = "8"

    job_path = watcher.JOB_SIGNAL_DIR / f"{STEM}.json"

    def write_reply_delayed() -> None:
        time.sleep(0.6)
        rep = watcher.EMAIL_HANDOFF_DIR / f"{STEM}.reply.json"
        tmp = watcher.EMAIL_HANDOFF_DIR / f"{STEM}.reply.json.tmp"
        tmp.write_text(json.dumps({"version": 1, "email": "Subject: E2E\n\nBody from reply file."}))
        tmp.replace(rep)

    th = threading.Thread(target=write_reply_delayed)
    th.start()
    email, src = watcher.draft_email_for_job(job_path, "C", "x", fake_stage)
    th.join()
    assert src == "openclaw", src
    assert "Body from reply file" in email
    print("OK: openclaw reply file path")


def test_hook_path() -> None:
    cleanup_handoff_files()
    os.environ.pop("OPENCLAW_EMAIL_WAIT_SECONDS", None)
    os.environ["OPENCLAW_EMAIL_WAIT_SECONDS"] = "0"
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tf:
        tf.write('print("Subject: HookTest\\n\\nHook body line.")\n')
        hook_path = tf.name
    try:
        os.environ["EMAIL_DRAFT_HOOK"] = f"{sys.executable} {hook_path}"
        job_path = watcher.JOB_SIGNAL_DIR / f"{STEM}.json"
        email, src = watcher.draft_email_for_job(job_path, "C", "x", fake_stage)
        assert src == "hook", src
        assert "Hook body line" in email
        print("OK: EMAIL_DRAFT_HOOK path")
    finally:
        os.unlink(hook_path)
        os.environ.pop("EMAIL_DRAFT_HOOK", None)


def main() -> int:
    watcher.setup_logging()
    try:
        test_template_path()
        test_openclaw_reply_path()
        test_hook_path()
    finally:
        cleanup_handoff_files()
    print("\nAll handoff integration tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
