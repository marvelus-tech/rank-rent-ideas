#!/usr/bin/env python3
"""
Consultation Webhook Server
Receives audio files from the consultation recorder webpage
Saves to Obsidian vault and signals OpenClaw to process
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os
import json
import tempfile
import uuid
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the webpage

# Configuration
OBSIDIAN_VAULT = "/Users/oktos/Obsidian"
CONSULTATIONS_DIR = f"{OBSIDIAN_VAULT}/Consultations/Incoming"
PROCESSED_DIR = f"{OBSIDIAN_VAULT}/Consultations/Processed"
SIGNAL_ROOT = Path("/Users/oktos/.openclaw/workspace/.consultation-signal")
JOB_SIGNAL_DIR = SIGNAL_ROOT / "jobs"
# Temporary resumable uploads land here until finalized.
UPLOAD_TMP_DIR = SIGNAL_ROOT / "uploads"
# Kept for backward compatibility (mirrors latest upload; watcher uses per-job files under jobs/)
LEGACY_SIGNAL_FILE = SIGNAL_ROOT / "new-recording.json"


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=str(path.parent), delete=False) as tmp:
        json.dump(data, tmp, indent=2)
        tmp.write("\n")
        tmp_path = tmp.name
    os.replace(tmp_path, path)


def safe_recording_basename(filename: str) -> str | None:
    """Reject path traversal; require a .webm basename."""
    if not filename or ".." in filename or "/" in filename or "\\" in filename:
        return None
    base = os.path.basename(filename.strip())
    if not base.endswith(".webm"):
        return None
    return base


def job_signal_path_for_basename(base: str) -> Path:
    stem = Path(base).stem
    return JOB_SIGNAL_DIR / f"{stem}.json"

def upload_meta_path(upload_id: str) -> Path:
    return UPLOAD_TMP_DIR / f"{upload_id}.json"

def upload_part_path(upload_id: str) -> Path:
    return UPLOAD_TMP_DIR / f"{upload_id}.part"


# Ensure directories exist
os.makedirs(CONSULTATIONS_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
SIGNAL_ROOT.mkdir(parents=True, exist_ok=True)
JOB_SIGNAL_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_TMP_DIR.mkdir(parents=True, exist_ok=True)


def _new_note_stub(client_name: str, duration: str, filename: str) -> str:
    return f"""# Consultation - {client_name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Metadata
- **Client:** {client_name}
- **Date:** {datetime.now().strftime('%Y-%m-%d')}
- **Time:** {datetime.now().strftime('%H:%M')}
- **Duration:** {duration}
- **Recording:** [[{filename}]]
- **Status:** 🟡 Pending Processing

## Transcription
*Pending...*

## Meeting Notes
*Pending...*

## Action Items
- [ ] Process recording
- [ ] Generate notes
- [ ] Draft follow-up email

## Email Draft
*Pending...*

---
*Received: {datetime.now().isoformat()}*
"""


def _create_job_for_recording(
    *, client_name: str, therapist_name: str = "", duration: str, timestamp: str, filepath: str
) -> dict:
    safe_client = "".join(c for c in client_name if c.isalnum() or c in (" ", "-", "_")).rstrip()
    safe_client = safe_client.replace(" ", "-") or "unknown-client"
    filename = f"{timestamp}-{safe_client}.webm"

    note_filename = f"{timestamp}-{safe_client}.md"
    note_path = os.path.join(CONSULTATIONS_DIR, note_filename)

    with open(note_path, "w") as f:
        f.write(_new_note_stub(client_name, duration, filename))

    signal_data = {
        "type": "new-consultation",
        "jobId": str(uuid.uuid4()),
        "timestamp": timestamp,
        "clientName": client_name,
        "therapistName": therapist_name,
        "duration": duration,
        "audioFile": filepath,
        "noteFile": note_path,
        "status": "pending",
        "receivedAt": datetime.now().isoformat(),
        "recordingFilename": filename,
    }

    job_path = job_signal_path_for_basename(filename)
    atomic_write_json(job_path, signal_data)
    atomic_write_json(LEGACY_SIGNAL_FILE, signal_data)

    return {
        "job_path": job_path,
        "note_filename": note_filename,
        "signal_data": signal_data,
        "filename": filename,
    }


@app.route("/webhook/consultation", methods=["POST"])
def receive_consultation():
    """Receive audio file from consultation recorder"""
    try:
        # Get metadata from form
        client_name = request.form.get("clientName", "Unknown")
        therapist_name = (request.form.get("therapistName") or "").strip()
        duration = request.form.get("duration", "00:00")
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")

        # Check for audio file
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400

        audio_file = request.files["audio"]
        if audio_file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        # Generate filename and final path
        safe_client = "".join(c for c in client_name if c.isalnum() or c in (" ", "-", "_")).rstrip()
        safe_client = safe_client.replace(" ", "-") or "unknown-client"
        filename = f"{timestamp}-{safe_client}.webm"
        filepath = os.path.join(CONSULTATIONS_DIR, filename)

        # Save audio file
        audio_file.save(filepath)
        print(f"✅ Saved: {filepath}")

        created = _create_job_for_recording(
            client_name=client_name,
            therapist_name=therapist_name,
            duration=duration,
            timestamp=timestamp,
            filepath=filepath,
        )
        print(f"✅ Created note: {created['signal_data']['noteFile']}")
        print(f"✅ Job signal: {created['job_path']}")

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Recording received",
                    "filename": created["filename"],
                    "jobId": created["signal_data"]["jobId"],
                    "signalFile": created["job_path"].name,
                    "noteFile": created["note_filename"],
                    "nextStep": "OpenClaw will process this shortly",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/upload/start", methods=["POST"])
def upload_start():
    """
    Start a resumable upload session.
    Client sends metadata (clientName, duration, timestamp optional) and receives uploadId.
    """
    try:
        client_name = request.form.get("clientName", "Unknown")
        therapist_name = (request.form.get("therapistName") or "").strip()
        duration = request.form.get("duration", "00:00")
        # Client may pass an existing timestamp; otherwise server generates.
        timestamp = request.form.get("timestamp") or datetime.now().strftime("%Y-%m-%d-%H%M%S")

        upload_id = str(uuid.uuid4())

        # Precompute the final recording filename/path now so status polling is stable.
        safe_client = "".join(c for c in client_name if c.isalnum() or c in (" ", "-", "_")).rstrip()
        safe_client = safe_client.replace(" ", "-") or "unknown-client"
        filename = f"{timestamp}-{safe_client}.webm"
        final_path = os.path.join(CONSULTATIONS_DIR, filename)

        meta = {
            "uploadId": upload_id,
            "createdAt": datetime.now().isoformat(),
            "clientName": client_name,
            "therapistName": therapist_name,
            "duration": duration,
            "timestamp": timestamp,
            "filename": filename,
            "finalPath": final_path,
            "status": "uploading",
            "receivedBytes": 0,
        }

        atomic_write_json(upload_meta_path(upload_id), meta)
        # Create/empty the part file.
        upload_part_path(upload_id).parent.mkdir(parents=True, exist_ok=True)
        with open(upload_part_path(upload_id), "wb") as f:
            f.write(b"")

        return jsonify({"success": True, "uploadId": upload_id, "filename": filename}), 200
    except Exception as e:
        print(f"❌ upload_start error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/upload/part", methods=["POST"])
def upload_part():
    """
    Append a chunk to the upload session.
    Required query param: uploadId
    Required header: X-Upload-Offset (integer) must match current receivedBytes.
    Body: raw bytes
    """
    try:
        upload_id = (request.args.get("uploadId") or "").strip()
        if not upload_id:
            return jsonify({"error": "Missing uploadId"}), 400

        meta_path = upload_meta_path(upload_id)
        part_path = upload_part_path(upload_id)
        if not meta_path.exists() or not part_path.exists():
            return jsonify({"error": "Unknown uploadId"}), 404

        try:
            expected_offset = int(request.headers.get("X-Upload-Offset", "0"))
        except ValueError:
            return jsonify({"error": "Invalid X-Upload-Offset"}), 400

        with open(meta_path, "r") as f:
            meta = json.load(f)

        current = int(meta.get("receivedBytes", 0))
        if expected_offset != current:
            return (
                jsonify(
                    {
                        "error": "Offset mismatch",
                        "expected": current,
                        "got": expected_offset,
                    }
                ),
                409,
            )

        chunk = request.get_data(cache=False) or b""
        if not chunk:
            return jsonify({"error": "Empty chunk"}), 400

        with open(part_path, "ab") as f:
            f.write(chunk)

        meta["receivedBytes"] = current + len(chunk)
        meta["updatedAt"] = datetime.now().isoformat()
        atomic_write_json(meta_path, meta)

        return jsonify({"success": True, "receivedBytes": meta["receivedBytes"]}), 200
    except Exception as e:
        print(f"❌ upload_part error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/upload/finish", methods=["POST"])
def upload_finish():
    """
    Finalize an upload session:
    - moves the .part file to the final .webm path
    - creates note + job signal
    Returns: { filename, jobId, ... } matching /webhook/consultation response shape.
    """
    try:
        upload_id = (request.form.get("uploadId") or "").strip()
        if not upload_id:
            return jsonify({"error": "Missing uploadId"}), 400

        meta_path = upload_meta_path(upload_id)
        part_path = upload_part_path(upload_id)
        if not meta_path.exists() or not part_path.exists():
            return jsonify({"error": "Unknown uploadId"}), 404

        with open(meta_path, "r") as f:
            meta = json.load(f)

        client_name = meta.get("clientName", "Unknown")
        therapist_name = (meta.get("therapistName") or "").strip()
        duration = meta.get("duration", "00:00")
        timestamp = meta.get("timestamp") or datetime.now().strftime("%Y-%m-%d-%H%M%S")
        filename = meta.get("filename")
        final_path = meta.get("finalPath")
        if not filename or not final_path:
            return jsonify({"error": "Upload metadata missing filename/finalPath"}), 500

        # Move assembled bytes into Incoming/ as the final recording file.
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        os.replace(part_path, final_path)

        created = _create_job_for_recording(
            client_name=client_name,
            therapist_name=therapist_name,
            duration=duration,
            timestamp=timestamp,
            filepath=final_path,
        )

        # Mark upload complete; keep meta around for debugging/resume.
        meta["status"] = "done"
        meta["completedAt"] = datetime.now().isoformat()
        atomic_write_json(meta_path, meta)

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Recording received",
                    "filename": created["filename"],
                    "jobId": created["signal_data"]["jobId"],
                    "signalFile": created["job_path"].name,
                    "noteFile": created["note_filename"],
                    "nextStep": "OpenClaw will process this shortly",
                }
            ),
            200,
        )

    except Exception as e:
        print(f"❌ upload_finish error: {str(e)}")
        return jsonify({"error": str(e)}), 500


def _status_message_for_stage(stage: str) -> str:
    """Human-readable line for the recorder UI (polled via /webhook/status)."""
    return {
        "queued": "Waiting in queue…",
        "transcribing": "Transcribing your audio…",
        "drafting": "Drafting your follow-up email…",
        "openclaw_email": "OpenClaw is drafting your follow-up email from the transcript…",
        "saving": "Saving to your notes…",
    }.get(stage, "Working on it…")


def _status_payload(signal_data: dict, filename: str) -> tuple[dict, int]:
    """Build JSON body for GET /webhook/status from one signal dict."""
    signal_audio_file = signal_data.get("audioFile", "")
    signal_filename = os.path.basename(signal_audio_file) if signal_audio_file else ""
    signal_status = signal_data.get("status", "pending")

    if signal_filename and signal_filename != filename:
        return (
            {
                "status": "pending",
                "filename": filename,
                "stage": "queued",
                "message": f"Signal mismatch (expected {signal_filename})",
            },
            200,
        )

    if signal_status == "done":
        results = signal_data.get("results", {}) or {}
        return (
            {
                "status": "done",
                "filename": filename,
                "results": {
                    "transcript": results.get("transcript", ""),
                    "email": results.get("email", ""),
                    "emailSource": results.get("emailSource", ""),
                    "clientName": results.get("clientName", signal_data.get("clientName", "Unknown")),
                    "therapistName": results.get(
                        "therapistName", signal_data.get("therapistName", "")
                    ),
                    "transcriptionEngine": results.get("transcriptionEngine"),
                    "transcriptSegments": results.get("transcriptSegments"),
                    "processedAt": results.get("processedAt", signal_data.get("completedAt", "")),
                    "files": {
                        "audio": signal_data.get("audioFile", ""),
                        "note": signal_data.get("noteFile", ""),
                    },
                },
            },
            200,
        )

    if signal_status == "error":
        return (
            {
                "status": "error",
                "filename": filename,
                "message": signal_data.get("error", "Processing failed"),
            },
            200,
        )

    if signal_status == "processing":
        stage = (signal_data.get("processingStage") or "transcribing").strip()
        return (
            {
                "status": "processing",
                "filename": filename,
                "stage": stage,
                "message": _status_message_for_stage(stage),
            },
            200,
        )

    return (
        {
            "status": "pending",
            "filename": filename,
            "stage": "queued",
            "message": "Waiting in queue…",
        },
        200,
    )


@app.route("/webhook/status", methods=["GET"])
def get_status():
    """Check consultation status and return results if processed"""
    try:
        raw = request.args.get("file", "").strip()
        print(f"Status check for: {raw!r}")

        base = safe_recording_basename(raw)
        if not base:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Invalid or missing file parameter (expected recording .webm basename)",
                    }
                ),
                400,
            )

        filename = base
        job_path = job_signal_path_for_basename(filename)

        job_data = None
        legacy_data = None

        if job_path.exists():
            with open(job_path, "r") as f:
                job_data = json.load(f)

        if LEGACY_SIGNAL_FILE.exists():
            with open(LEGACY_SIGNAL_FILE, "r") as f:
                legacy_data = json.load(f)

        # Prefer the per-job file, but be resilient during migration:
        # if an older watcher is still writing only the legacy file and it has a terminal
        # status for this filename, honor that even if the job file exists but is still pending.
        signal_data = None
        if job_data is not None:
            signal_data = job_data

        if legacy_data is not None:
            leg_base = os.path.basename(legacy_data.get("audioFile", "") or "")
            if leg_base == filename:
                legacy_status = (legacy_data.get("status") or "pending").lower()
                job_status = ((job_data or {}).get("status") or "pending").lower()
                if legacy_status in ("done", "error") and job_status not in ("done", "error"):
                    signal_data = legacy_data

        if not signal_data:
            return (
                jsonify(
                    {
                        "status": "pending",
                        "filename": filename,
                        "stage": "queued",
                        "message": "No job record found for this recording (upload may not have completed)",
                    }
                ),
                200,
            )

        body, code = _status_payload(signal_data, filename)
        return jsonify(body), code

    except Exception as e:
        print(f"Status check error: {str(e)}")
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/health", methods=["GET"])
def health():
    """Health check"""
    return jsonify({"status": "running", "timestamp": datetime.now().isoformat()})


if __name__ == "__main__":
    print("🎙️  Consultation Webhook Server")
    print(f"📁 Saving to: {CONSULTATIONS_DIR}")
    print(f"📡 Job signals: {JOB_SIGNAL_DIR}")
    print(f"📡 Legacy mirror: {LEGACY_SIGNAL_FILE}")
    print("🚀 Starting server on http://localhost:5678")
    print("\nReady to receive recordings!\n")

    # Run on port 5678 (arbitrary, change if needed)
    app.run(host="0.0.0.0", port=5678, debug=False)
