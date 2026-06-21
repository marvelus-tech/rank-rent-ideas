#!/usr/bin/env python3
"""
Consultation Watcher - robust single-instance processor

Responsibilities:
- Monitor per-job signal files under jobs/
- Transcribe audio with Whisper (faster-whisper or WhisperX + optional diarization)
- Generate follow-up email draft
- Update Obsidian note
- Mark signal status done/error with results
"""

import atexit
import fcntl
import json
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime
import inspect
import shutil
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

SIGNAL_ROOT = Path("/Users/oktos/.openclaw/workspace/.consultation-signal")
JOB_SIGNAL_DIR = SIGNAL_ROOT / "jobs"
# OpenClaw (or any tool) reads *.request.json and may write *.reply.json — see README.
EMAIL_HANDOFF_DIR = SIGNAL_ROOT / "email-handoff"
PID_FILE = SIGNAL_ROOT / "watcher.pid"
LOG_FILE = SIGNAL_ROOT / "watcher.log"
POLL_INTERVAL_SECONDS = 0.5
# 30–45 minute calls on CPU can legitimately take a long time to transcribe.
# Treat "stale" as hours, not minutes, to avoid re-queue loops.
STALE_PROCESSING_SECONDS = 3 * 60 * 60

_pid_fd: Optional[int] = None
logger = logging.getLogger("consultation_watcher")


def _native_thread_limit_defaults() -> Dict[str, str]:
    """Cap BLAS/OpenMP thread pools — avoids libiomp5 crashes with ctranslate2 on macOS x86."""
    return {
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1",
    }


def _apply_native_thread_limits_to_environ() -> None:
    """Apply defaults only where unset (override via env if you need more throughput)."""
    for k, v in _native_thread_limit_defaults().items():
        os.environ.setdefault(k, v)


def _looks_like_hub_network_error(exc: BaseException) -> bool:
    """True when Hugging Face Hub likely could not resolve or reach the network."""
    msg = str(exc).lower()
    return any(
        needle in msg
        for needle in (
            "nodename nor servname",
            "name or service not known",
            "errno 8",
            "temporary failure in name resolution",
            "network is unreachable",
            "failed to establish a new connection",
            "connection refused",
            "ssl: certificate_verify_failed",
        )
    )


def setup_logging() -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # --transcribe-child pipes only transcript text on stdout to the parent; logs must use stderr.
    log_stream = sys.stderr if os.environ.get("WATCHER_TRANSCRIBE_CHILD") else sys.stdout
    stream_handler = logging.StreamHandler(log_stream)
    stream_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    file_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)


def acquire_pid_lock() -> None:
    """Ensure only one watcher instance runs using PID file locking."""
    global _pid_fd

    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    _pid_fd = os.open(PID_FILE, os.O_RDWR | os.O_CREAT, 0o644)

    try:
        fcntl.flock(_pid_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        try:
            existing_pid = os.read(_pid_fd, 32).decode().strip()
        except Exception:
            existing_pid = "unknown"
        raise RuntimeError(f"Watcher already running (PID: {existing_pid})")

    os.ftruncate(_pid_fd, 0)
    os.write(_pid_fd, str(os.getpid()).encode())
    os.fsync(_pid_fd)

    def _cleanup() -> None:
        global _pid_fd
        if _pid_fd is not None:
            try:
                os.ftruncate(_pid_fd, 0)
                fcntl.flock(_pid_fd, fcntl.LOCK_UN)
                os.close(_pid_fd)
            except Exception:
                pass
            _pid_fd = None

    atexit.register(_cleanup)


def atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    """Write JSON atomically to avoid partial writes/races."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", dir=str(path.parent), delete=False) as tmp:
        json.dump(data, tmp, indent=2)
        tmp.write("\n")
        tmp_path = tmp.name
    os.replace(tmp_path, path)


def read_signal_at(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None

    for attempt in range(3):
        try:
            with path.open("r") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logger.warning("Signal JSON decode error %s (attempt %s/3): %s", path, attempt + 1, e)
            time.sleep(0.1)
        except Exception as e:
            logger.error("Error reading signal file %s: %s", path, e)
            return None

    return None


def update_signal_at(
    path: Path, mutator: Callable[[Dict[str, Any]], Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Read-modify-write helper with atomic writes."""
    current = read_signal_at(path)
    if current is None:
        return None
    updated = mutator(dict(current))
    atomic_write_json(path, updated)
    return updated


def maybe_recover_stale_processing(
    signal_data: Dict[str, Any], path: Path
) -> Dict[str, Any]:
    """If processing appears stuck for too long, recover to pending."""
    if signal_data.get("status") != "processing":
        return signal_data

    started = signal_data.get("processingStarted")
    if not started:
        return signal_data

    try:
        started_ts = datetime.fromisoformat(started).timestamp()
    except Exception:
        return signal_data

    if (time.time() - started_ts) > STALE_PROCESSING_SECONDS:
        logger.warning(
            "Stale processing %s (> %ss). Resetting to pending.", path, STALE_PROCESSING_SECONDS
        )

        def _mutate(data: Dict[str, Any]) -> Dict[str, Any]:
            data["status"] = "pending"
            data["recoveredAt"] = datetime.now().isoformat()
            return data

        recovered = update_signal_at(path, _mutate)
        return recovered or signal_data

    return signal_data


def mark_processing_at(path: Path) -> Optional[Dict[str, Any]]:
    def _mutate(data: Dict[str, Any]) -> Dict[str, Any]:
        data["status"] = "processing"
        data["processingStarted"] = datetime.now().isoformat()
        data["processingStage"] = "transcribing"
        data["processingStageAt"] = datetime.now().isoformat()
        data.pop("error", None)
        return data

    return update_signal_at(path, _mutate)


def set_processing_stage(path: Path, stage: str) -> None:
    """Update job JSON so /webhook/status can drive live progress in the recorder UI."""

    def _mutate(data: Dict[str, Any]) -> Dict[str, Any]:
        data["processingStage"] = stage
        data["processingStageAt"] = datetime.now().isoformat()
        return data

    update_signal_at(path, _mutate)


def mark_done_at(path: Path, results: Dict[str, Any]) -> None:
    def _mutate(data: Dict[str, Any]) -> Dict[str, Any]:
        data["status"] = "done"
        data["completedAt"] = datetime.now().isoformat()
        data["results"] = results
        data.pop("error", None)
        data.pop("processingStage", None)
        data.pop("processingStageAt", None)
        return data

    update_signal_at(path, _mutate)


def mark_error_at(path: Path, error_message: str) -> None:
    def _mutate(data: Dict[str, Any]) -> Dict[str, Any]:
        data["status"] = "error"
        data["error"] = error_message
        data["completedAt"] = datetime.now().isoformat()
        data.pop("processingStage", None)
        data.pop("processingStageAt", None)
        return data

    update_signal_at(path, _mutate)


def _faster_whisper_transcript(
    model: Any, audio_path: str, *, vad_filter: bool
) -> Tuple[str, Any]:
    """Run faster-whisper once; returns (joined text, info)."""
    segments, info = model.transcribe(audio_path, language="en", vad_filter=vad_filter)
    transcript = " ".join((seg.text or "").strip() for seg in segments).strip()
    return transcript, info


def _faster_whisper_payload(transcript: str) -> Dict[str, Any]:
    return {
        "transcript": transcript,
        "transcriptSegments": None,
        "transcriptionEngine": "faster-whisper",
    }


def _merge_transcript_segments(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    for seg in segments:
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        sp = seg.get("speaker")
        start = seg.get("start")
        end = seg.get("end")
        if merged and merged[-1].get("speaker") == sp:
            merged[-1]["text"] = (merged[-1]["text"] + " " + text).strip()
            if end is not None:
                merged[-1]["end"] = end
        else:
            merged.append({"speaker": sp, "text": text, "start": start, "end": end})
    return merged


def _speaker_roles_in_order(segments: List[Dict[str, Any]]) -> Dict[str, str]:
    """Map pyannote speaker ids to display labels using job names from env (set during transcribe)."""
    order: List[str] = []
    for seg in sorted(segments, key=lambda s: float(s.get("start") or 0.0)):
        sp = seg.get("speaker")
        if sp and sp not in order:
            order.append(sp)

    client_raw = (os.environ.get("CONSULTATION_CLIENT_NAME") or "").strip()
    therapist_raw = (os.environ.get("CONSULTATION_THERAPIST_NAME") or "").strip()
    client_label = client_raw or "Client"
    therapist_label = therapist_raw or "therapist"

    # Default: first detected speaker = therapist (clinician often opens). Override with WHISPERX_FIRST_IS_CLIENT=1.
    first_is_client = os.environ.get("WHISPERX_FIRST_IS_CLIENT", "0").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    mapping: Dict[str, str] = {}
    if len(order) >= 1:
        mapping[order[0]] = client_label if first_is_client else therapist_label
    if len(order) >= 2:
        mapping[order[1]] = therapist_label if first_is_client else client_label
    for idx, sp in enumerate(order[2:], start=3):
        mapping[sp] = f"Speaker {idx}"
    return mapping


def _format_labeled_transcript(merged: List[Dict[str, Any]], role_map: Dict[str, str]) -> str:
    lines: List[str] = []
    for seg in merged:
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        raw_sp = seg.get("speaker")
        label = role_map.get(raw_sp, raw_sp or "Speaker")
        lines.append(f'{label}:\n"{text}"\n')
    return "\n".join(lines).strip()


def _faster_whisper_transcribe_dict(audio_path: str) -> Dict[str, Any]:
    """faster-whisper or openai-whisper CLI; returns structured payload."""
    # Prefer faster-whisper when installed (much faster on CPU, more reliable for long audio).
    try:
        from faster_whisper import WhisperModel  # type: ignore

        model_name = os.environ.get("FASTER_WHISPER_MODEL", "base")
        compute_type = os.environ.get("FASTER_WHISPER_COMPUTE_TYPE", "int8")
        device = os.environ.get("FASTER_WHISPER_DEVICE", "cpu")
        vad_env = os.environ.get("FASTER_WHISPER_VAD_FILTER", "0").strip().lower()
        use_vad = vad_env not in ("0", "false", "no", "off")

        logger.info(
            "Using faster-whisper (model=%s device=%s compute_type=%s vad_filter=%s)",
            model_name,
            device,
            compute_type,
            use_vad,
        )

        model_kw: Dict[str, Any] = {}
        if device.strip().lower() == "cpu":
            model_kw["cpu_threads"] = int(os.environ.get("FASTER_WHISPER_CPU_THREADS", "1"))
            model_kw["num_workers"] = int(os.environ.get("FASTER_WHISPER_NUM_WORKERS", "1"))

        model = WhisperModel(model_name, device=device, compute_type=compute_type, **model_kw)
        transcript, info = _faster_whisper_transcript(model, audio_path, vad_filter=use_vad)

        if not transcript and use_vad:
            dur = getattr(info, "duration", None) or 0.0
            after_vad = getattr(info, "duration_after_vad", None)
            logger.warning(
                "Empty transcript with vad_filter=True (duration=%.2fs, duration_after_vad=%s); retrying without VAD",
                dur,
                after_vad,
            )
            transcript, info = _faster_whisper_transcript(model, audio_path, vad_filter=False)

        if not transcript and shutil.which("ffmpeg"):
            fd, tmp_wav = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            try:
                conv = subprocess.run(
                    [
                        "ffmpeg",
                        "-hide_banner",
                        "-loglevel",
                        "error",
                        "-y",
                        "-i",
                        audio_path,
                        "-ar",
                        "16000",
                        "-ac",
                        "1",
                        "-c:a",
                        "pcm_s16le",
                        tmp_wav,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=600,
                )
                if conv.returncode == 0 and os.path.getsize(tmp_wav) > 1000:
                    logger.warning("Empty transcript on original file; retrying after ffmpeg -> 16kHz mono WAV")
                    transcript, info = _faster_whisper_transcript(model, tmp_wav, vad_filter=False)
            finally:
                try:
                    os.unlink(tmp_wav)
                except OSError:
                    pass

        if not transcript:
            dur = getattr(info, "duration", None) or 0.0
            raise RuntimeError(
                "Transcript is empty (no speech detected or unreadable audio). "
                f"duration={dur:.2f}s — check mic levels / file is not silent or corrupt."
            )
        logger.info("Transcription complete (%s chars, %.1fs audio)", len(transcript), info.duration or 0.0)
        return _faster_whisper_payload(transcript)
    except ImportError as e:
        logger.warning("faster-whisper not installed; falling back to whisper CLI: %s", e)
    except RuntimeError as e:
        if "Transcript is empty" in str(e):
            raise
        logger.warning("faster-whisper failed; falling back to whisper CLI: %s", e)
    except Exception as e:
        logger.warning("faster-whisper unavailable/failed; falling back to whisper CLI: %s", e)

    if shutil.which("whisper") is None:
        raise RuntimeError(
            "Neither faster-whisper nor whisper CLI is available. "
            "Install faster-whisper (recommended) or install openai-whisper to provide the 'whisper' command."
        )

    output_dir = os.path.dirname(audio_path)
    base_name = Path(audio_path).stem
    cli_timeout = int(os.environ.get("WHISPER_CLI_TIMEOUT_SECONDS", str(2 * 60 * 60)))

    result = subprocess.run(
        [
            "whisper",
            audio_path,
            "--model",
            os.environ.get("WHISPER_MODEL", "base"),
            "--language",
            "en",
            "--output_format",
            "txt",
            "--output_dir",
            output_dir,
        ],
        capture_output=True,
        text=True,
        timeout=cli_timeout,
    )

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()
        stdout = (result.stdout or "").strip()
        raise RuntimeError(f"Whisper failed (code {result.returncode}): {stderr or stdout}")

    txt_file = os.path.join(output_dir, f"{base_name}.txt")
    if not os.path.exists(txt_file):
        raise RuntimeError("Whisper completed but transcript .txt file not found")

    with open(txt_file, "r") as f:
        transcript = f.read().strip()

    if not transcript:
        raise RuntimeError("Transcript is empty")

    logger.info("Transcription complete (%s chars)", len(transcript))
    return _faster_whisper_payload(transcript)


def _whisperx_load_model(whisperx: Any, model_name: str, device: str, compute_type: str, language: str) -> Any:
    """WhisperX load_model: newer releases support vad_method=; 3.3.x does not."""
    sig = inspect.signature(whisperx.load_model)
    kwargs: Dict[str, Any] = {
        "compute_type": compute_type,
        "language": language,
    }
    if "vad_method" in sig.parameters:
        kwargs["vad_method"] = (os.environ.get("WHISPERX_VAD_METHOD") or "silero").strip()
    return whisperx.load_model(model_name, device, **kwargs)


def _whisperx_diarization_pipeline(DiarizationPipeline: Any, hf_token: str, device: str) -> Any:
    """DiarizationPipeline: 3.3.x uses use_auth_token=; newer uses token=."""
    sig = inspect.signature(DiarizationPipeline.__init__)
    kw: Dict[str, Any] = {"device": device}
    if "token" in sig.parameters:
        kw["token"] = hf_token
    elif "use_auth_token" in sig.parameters:
        kw["use_auth_token"] = hf_token
    else:
        kw["use_auth_token"] = hf_token
    return DiarizationPipeline(**kw)


def _transcribe_whisperx_impl(audio_path: str) -> Dict[str, Any]:
    """WhisperX: ASR + alignment + optional pyannote diarization; labeled transcript when HF token set."""
    import gc

    import torch
    import whisperx
    from whisperx.diarize import DiarizationPipeline

    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = (os.environ.get("WHISPERX_COMPUTE_TYPE") or "").strip()
    if not compute_type:
        compute_type = "float16" if device == "cuda" else "int8"
    model_name = (
        os.environ.get("WHISPERX_MODEL") or os.environ.get("FASTER_WHISPER_MODEL") or "base"
    ).strip()
    batch_size = int(os.environ.get("WHISPERX_BATCH_SIZE", "8" if device == "cpu" else "16"))
    language = (os.environ.get("WHISPERX_LANGUAGE") or "en").strip()
    vad_note = ""
    if "vad_method" in inspect.signature(whisperx.load_model).parameters:
        vad_note = f" vad={(os.environ.get('WHISPERX_VAD_METHOD') or 'silero').strip()}"

    logger.info(
        "Using WhisperX (model=%s device=%s compute_type=%s%s)",
        model_name,
        device,
        compute_type,
        vad_note,
    )

    audio = whisperx.load_audio(audio_path)
    model = _whisperx_load_model(whisperx, model_name, device, compute_type, language)
    result = model.transcribe(audio, batch_size=batch_size)
    del model
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
    result = whisperx.align(
        result["segments"],
        model_a,
        metadata,
        audio,
        device,
        return_char_alignments=False,
    )
    del model_a
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    hf_token = (os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN") or "").strip()
    if hf_token:
        diarize_model = _whisperx_diarization_pipeline(DiarizationPipeline, hf_token, device)
        d_kw: Dict[str, Any] = {}
        if os.environ.get("WHISPERX_NUM_SPEAKERS"):
            d_kw["num_speakers"] = int(os.environ["WHISPERX_NUM_SPEAKERS"])
        else:
            if os.environ.get("WHISPERX_MIN_SPEAKERS"):
                d_kw["min_speakers"] = int(os.environ["WHISPERX_MIN_SPEAKERS"])
            if os.environ.get("WHISPERX_MAX_SPEAKERS"):
                d_kw["max_speakers"] = int(os.environ["WHISPERX_MAX_SPEAKERS"])
        diarize_df = diarize_model(audio, **d_kw) if d_kw else diarize_model(audio)
        result = whisperx.assign_word_speakers(diarize_df, result)
        del diarize_model
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    else:
        logger.warning(
            "WhisperX: no HF_TOKEN or HUGGINGFACE_HUB_TOKEN — skipping diarization (no speaker labels). "
            "Accept the pyannote diarization model on Hugging Face and set a read token in .env."
        )

    segments = result.get("segments") or []
    out_segments: List[Dict[str, Any]] = []
    for seg in segments:
        text = (seg.get("text") or "").strip()
        if not text:
            continue
        out_segments.append(
            {
                "speaker": seg.get("speaker"),
                "text": text,
                "start": seg.get("start"),
                "end": seg.get("end"),
            }
        )
    merged = _merge_transcript_segments(out_segments)
    has_speakers = any(s.get("speaker") for s in merged)
    if has_speakers:
        role_map = _speaker_roles_in_order(out_segments)
        transcript = _format_labeled_transcript(merged, role_map)
        labeled: List[Dict[str, Any]] = []
        for s in merged:
            raw = s.get("speaker")
            labeled.append(
                {
                    "speaker": role_map.get(raw, raw or "Speaker"),
                    "text": s.get("text", ""),
                    "start": s.get("start"),
                    "end": s.get("end"),
                }
            )
        segments_out: Optional[List[Dict[str, Any]]] = labeled
    else:
        transcript = " ".join((s.get("text") or "").strip() for s in merged).strip()
        segments_out = None

    if not transcript:
        raise RuntimeError("WhisperX returned an empty transcript")

    logger.info(
        "WhisperX transcription complete (%s chars, diarized=%s)",
        len(transcript),
        has_speakers,
    )
    return {
        "transcript": transcript,
        "transcriptSegments": segments_out,
        "transcriptionEngine": "whisperx",
    }


def transcribe_audio_impl(audio_path: str) -> Dict[str, Any]:
    """Run Whisper in-process. Prefer transcribe_audio() subprocess wrapper for timeout isolation."""
    _apply_native_thread_limits_to_environ()
    logger.info("Transcribing audio: %s", audio_path)

    if not audio_path:
        raise ValueError("Missing audioFile path")
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    engine = os.environ.get("TRANSCRIBE_ENGINE", "auto").strip().lower()
    if engine in ("", "auto"):
        try:
            return _transcribe_whisperx_impl(audio_path)
        except Exception as e:
            if _looks_like_hub_network_error(e):
                logger.warning(
                    "WhisperX failed (Hugging Face Hub unreachable — DNS/offline/firewall/VPN; "
                    "WhisperX must download models on first run). Error: %s. "
                    "Fix: ensure huggingface.co resolves, run once online to fill ~/.cache/huggingface, "
                    "check HF_ENDPOINT is unset or correct. Falling back to faster-whisper.",
                    e,
                )
            else:
                logger.warning("WhisperX failed (%s); falling back to faster-whisper", e)
            return _faster_whisper_transcribe_dict(audio_path)
    if engine == "whisperx":
        return _transcribe_whisperx_impl(audio_path)
    if engine == "faster-whisper":
        return _faster_whisper_transcribe_dict(audio_path)
    raise ValueError(
        f"Unknown TRANSCRIBE_ENGINE={engine!r} (use auto, whisperx, or faster-whisper)"
    )


def transcribe_audio(audio_path: str) -> Dict[str, Any]:
    """
    Run transcription in a child process so a hung ASR call can be killed via timeout.
    Returns a dict: transcript, transcriptSegments (optional), transcriptionEngine.
    Set TRANSCRIBE_INPROCESS=1 to call transcribe_audio_impl() in-process (faster, can wedge the watcher).
    """
    if os.environ.get("TRANSCRIBE_INPROCESS", "").strip() in ("1", "true", "yes"):
        return transcribe_audio_impl(audio_path)

    timeout_sec = int(os.environ.get("TRANSCRIBE_TIMEOUT_SECONDS", str(2 * 60 * 60)))
    watcher_script = os.path.abspath(__file__)
    cmd = [sys.executable, watcher_script, "--transcribe-child", audio_path]

    def _run_child(extra_env: Optional[Dict[str, str]] = None) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        # macOS + mixed ML runtimes can double-load OpenMP in child transcribe processes.
        # Keep this scoped to the worker child only.
        env.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
        env.setdefault("TOKENIZERS_PARALLELISM", "false")
        for k, v in _native_thread_limit_defaults().items():
            env.setdefault(k, v)
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            env=env,
        )

    logger.info("Transcribing in subprocess (timeout=%ss): %s", timeout_sec, audio_path)
    try:
        proc = _run_child()
    except subprocess.TimeoutExpired as e:
        raise RuntimeError(
            f"Transcription timed out after {timeout_sec}s (hung worker). "
            f"Increase TRANSCRIBE_TIMEOUT_SECONDS or set TRANSCRIBE_INPROCESS=1 to debug."
        ) from e

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        engine = os.environ.get("TRANSCRIBE_ENGINE", "auto").strip().lower() or "auto"
        # WhisperX can segfault in some local CPU/Python stacks (exit 139). Fall back gracefully.
        if engine in ("auto", "whisperx"):
            logger.warning(
                "Transcription child exited %s; retrying with faster-whisper fallback",
                proc.returncode,
            )
            try:
                proc = _run_child({"TRANSCRIBE_ENGINE": "faster-whisper"})
            except subprocess.TimeoutExpired as e:
                raise RuntimeError(
                    f"Transcription timed out after {timeout_sec}s (hung worker). "
                    f"Increase TRANSCRIBE_TIMEOUT_SECONDS or set TRANSCRIBE_INPROCESS=1 to debug."
                ) from e
            if proc.returncode != 0:
                fallback_err = (proc.stderr or proc.stdout or "").strip()
                raise RuntimeError(
                    f"Transcription subprocess failed (whisperx and faster-whisper): "
                    f"{fallback_err or f'exit {proc.returncode}'}"
                )
        else:
            raise RuntimeError(f"Transcription subprocess failed: {err or f'exit {proc.returncode}'}")

    raw = (proc.stdout or "").strip()
    if not raw:
        raise RuntimeError("Transcript is empty")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"transcript": raw, "transcriptSegments": None, "transcriptionEngine": "legacy"}

    transcript = (data.get("transcript") or "").strip()
    if not transcript:
        raise RuntimeError("Transcript is empty")

    logger.info(
        "Transcription complete (%s chars, engine=%s)",
        len(transcript),
        data.get("transcriptionEngine"),
    )
    return data


def generate_email_draft(client_name: str, transcript: str) -> str:
    return f"""Subject: Thank you for our consultation - {datetime.now().strftime('%B %d, %Y')}

Hi {client_name},

Thank you for taking the time to speak with me today. I appreciate the opportunity to discuss your needs.

Key points from our conversation:
- We covered the main topics you wanted to discuss
- Next steps were outlined during our call

Please let me know if you have any questions or need clarification on anything we discussed.

Best regards,
[Your name]"""


def _write_email_handoff_request(job_path: Path, client_name: str, transcript: str) -> Path:
    EMAIL_HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    stem = job_path.stem
    request_path = EMAIL_HANDOFF_DIR / f"{stem}.request.json"
    payload = {
        "version": 1,
        "kind": "consultation-email-draft",
        "jobFile": str(job_path.resolve()),
        "clientName": client_name,
        "transcript": transcript,
        "requestedAt": datetime.now().isoformat(),
    }
    atomic_write_json(request_path, payload)
    return request_path


def _try_email_draft_hook(request_path: Path) -> Optional[str]:
    """Optional sync hook: EMAIL_DRAFT_HOOK runs with CONSULTATION_EMAIL_REQUEST_JSON set; stdout = email body."""
    hook = os.environ.get("EMAIL_DRAFT_HOOK", "").strip()
    if not hook:
        return None
    timeout = int(os.environ.get("EMAIL_DRAFT_HOOK_TIMEOUT", "120"))
    env = os.environ.copy()
    env["CONSULTATION_EMAIL_REQUEST_JSON"] = str(request_path)
    try:
        proc = subprocess.run(
            hook,
            shell=True,
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(EMAIL_HANDOFF_DIR),
        )
    except subprocess.TimeoutExpired:
        logger.warning("EMAIL_DRAFT_HOOK timed out after %ss", timeout)
        return None
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        logger.warning("EMAIL_DRAFT_HOOK exit %s: %s", proc.returncode, err[:800])
        return None
    out = (proc.stdout or "").strip()
    return out or None


def _wait_for_email_reply_file(stem: str, deadline: float) -> Optional[str]:
    """Poll for {stem}.reply.json written by OpenClaw or another process."""
    reply_path = EMAIL_HANDOFF_DIR / f"{stem}.reply.json"
    if reply_path.exists():
        try:
            reply_path.unlink()
        except OSError:
            pass
    while time.time() < deadline:
        if reply_path.exists():
            for _ in range(5):
                try:
                    raw = reply_path.read_text()
                    data = json.loads(raw)
                    email = (data.get("email") or "").strip()
                    if email:
                        return email
                    break
                except (json.JSONDecodeError, OSError):
                    time.sleep(0.15)
        time.sleep(0.4)
    return None


def draft_email_for_job(job_path: Path, client_name: str, transcript: str, stage_setter: Callable[[Path, str], None]) -> Tuple[str, str]:
    """
    After Whisper: hand off transcript for email drafting, then fall back to template if needed.
    Returns (email_body, source) where source is hook | openclaw | template.
    """
    request_path = _write_email_handoff_request(job_path, client_name, transcript)
    logger.info("Email handoff written: %s", request_path)
    stage_setter(job_path, "drafting")

    hooked = _try_email_draft_hook(request_path)
    if hooked:
        logger.info("Email draft from EMAIL_DRAFT_HOOK (%s chars)", len(hooked))
        return hooked, "hook"

    wait_sec = int(os.environ.get("OPENCLAW_EMAIL_WAIT_SECONDS", "0"))
    if wait_sec > 0:
        stage_setter(job_path, "openclaw_email")
        logger.info(
            "Waiting up to %ss for %s.reply.json (OpenClaw email handoff)",
            wait_sec,
            job_path.stem,
        )
        deadline = time.time() + float(wait_sec)
        reply = _wait_for_email_reply_file(job_path.stem, deadline)
        if reply:
            logger.info("Email draft from handoff reply file (%s chars)", len(reply))
            return reply, "openclaw"
        logger.warning(
            "No .reply.json within %ss; using template email. Set OPENCLAW_EMAIL_WAIT_SECONDS=0 to skip wait.",
            wait_sec,
        )
        stage_setter(job_path, "drafting")

    template = generate_email_draft(client_name, transcript)
    return template, "template"


def update_obsidian_note(note_path: str, transcript: str, email_draft: str) -> bool:
    if not note_path:
        logger.warning("No noteFile provided; skipping Obsidian update")
        return False
    if not os.path.exists(note_path):
        logger.warning("Obsidian note not found: %s", note_path)
        return False

    try:
        with open(note_path, "r") as f:
            content = f.read()

        if "## Transcription\n*Pending...*" in content:
            content = content.replace(
                "## Transcription\n*Pending...*", f"## Transcription\n{transcript}", 1
            )

        if "## Email Draft\n*Pending...*" in content:
            content = content.replace(
                "## Email Draft\n*Pending...*", f"## Email Draft\n{email_draft}", 1
            )

        content = content.replace("🟡 Pending Processing", "✅ Processed", 1)
        content = content.replace("- [ ] Process recording", "- [x] Process recording")
        content = content.replace("- [ ] Generate notes", "- [x] Generate notes")
        content = content.replace("- [ ] Draft follow-up email", "- [x] Draft follow-up email")

        content += f"\n---\n*Processed: {datetime.now().isoformat()}*"

        with open(note_path, "w") as f:
            f.write(content)

        logger.info("Updated Obsidian note: %s", note_path)
        return True
    except Exception as e:
        logger.exception("Error updating Obsidian note: %s", e)
        return False


@contextmanager
def _transcription_persona_env(consultation: Dict[str, Any]) -> Iterator[None]:
    """Expose client/therapist display names to WhisperX speaker mapping (subprocess inherits env)."""
    keys = ("CONSULTATION_CLIENT_NAME", "CONSULTATION_THERAPIST_NAME")
    saved = {k: os.environ.get(k) for k in keys}
    try:
        cn = str(consultation.get("clientName") or "Client").strip() or "Client"
        tn = str(consultation.get("therapistName") or "").strip()
        os.environ["CONSULTATION_CLIENT_NAME"] = cn
        os.environ["CONSULTATION_THERAPIST_NAME"] = tn
        yield
    finally:
        for k in keys:
            v = saved[k]
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def process_consultation(consultation: Dict[str, Any], job_path: Path) -> Dict[str, Any]:
    client_name = consultation.get("clientName", "Client")
    therapist_name = (consultation.get("therapistName") or "").strip()
    audio_file = consultation.get("audioFile")
    note_file = consultation.get("noteFile")

    logger.info("Starting processing for client: %s", client_name)

    # mark_processing_at already set processingStage=transcribing; stages below advance the UI.
    with _transcription_persona_env(consultation):
        tdata = transcribe_audio(audio_file)
    transcript = (tdata.get("transcript") or "").strip()
    email_draft, email_source = draft_email_for_job(
        job_path, client_name, transcript, set_processing_stage
    )
    set_processing_stage(job_path, "saving")
    note_updated = update_obsidian_note(note_file, transcript, email_draft)

    results = {
        "clientName": client_name,
        "therapistName": therapist_name,
        "transcript": transcript,
        "email": email_draft,
        "emailSource": email_source,
        "obsidianUpdated": note_updated,
        "processedAt": datetime.now().isoformat(),
        "transcriptionEngine": tdata.get("transcriptionEngine"),
        "transcriptSegments": tdata.get("transcriptSegments"),
    }
    return results


def signal_handlers(signum, frame):
    logger.info("Received signal %s; shutting down watcher", signum)
    sys.exit(0)


def job_sort_key(path: Path) -> tuple:
    data = read_signal_at(path)
    if not data:
        return ("", path.stat().st_mtime)
    return (data.get("receivedAt") or "", path.stat().st_mtime)


def list_pending_jobs_sorted() -> List[Path]:
    """Oldest receivedAt first (FIFO)."""
    if not JOB_SIGNAL_DIR.exists():
        return []
    paths = list(JOB_SIGNAL_DIR.glob("*.json"))
    paths.sort(key=job_sort_key)
    pending: List[Path] = []
    for path in paths:
        data = read_signal_at(path)
        if not data:
            continue
        data = maybe_recover_stale_processing(data, path)
        if data.get("status") == "pending":
            pending.append(path)
    return pending


def migrate_legacy_signal_if_needed() -> None:
    """Pre-upgrade installs only had new-recording.json; copy active work into jobs/ once."""
    legacy = SIGNAL_ROOT / "new-recording.json"
    if not legacy.exists():
        return
    data = read_signal_at(legacy)
    if not data or data.get("status") not in ("pending", "processing"):
        return
    audio = data.get("audioFile") or ""
    base = os.path.basename(audio)
    if not base.endswith(".webm"):
        return
    stem = Path(base).stem
    job_path = JOB_SIGNAL_DIR / f"{stem}.json"
    if job_path.exists():
        return
    logger.info("Migrating legacy signal to job file: %s", job_path)
    atomic_write_json(job_path, data)


def startup_recover_processing_jobs() -> None:
    """If previous watcher died mid-processing, resume work."""
    if not JOB_SIGNAL_DIR.exists():
        return
    for path in JOB_SIGNAL_DIR.glob("*.json"):
        data = read_signal_at(path)
        if not data or data.get("status") != "processing":
            continue
        logger.warning("Startup: processing -> pending for recovery: %s", path)

        def _recover(d: Dict[str, Any]) -> Dict[str, Any]:
            d["status"] = "pending"
            d["recoveredAt"] = datetime.now().isoformat()
            return d

        update_signal_at(path, _recover)


def main() -> int:
    setup_logging()

    try:
        acquire_pid_lock()
    except RuntimeError as e:
        setup_logging()
        logger.error(str(e))
        return 1

    signal.signal(signal.SIGINT, signal_handlers)
    signal.signal(signal.SIGTERM, signal_handlers)

    logger.info("Consultation watcher started")
    logger.info("Watching job directory: %s", JOB_SIGNAL_DIR)

    JOB_SIGNAL_DIR.mkdir(parents=True, exist_ok=True)
    migrate_legacy_signal_if_needed()
    startup_recover_processing_jobs()

    while True:
        try:
            pending = list_pending_jobs_sorted()
            if pending:
                path = pending[0]
                processing_data = mark_processing_at(path)
                if not processing_data:
                    logger.warning("Could not mark processing for %s; will retry", path)
                    time.sleep(POLL_INTERVAL_SECONDS)
                    continue

                try:
                    results = process_consultation(processing_data, path)
                    mark_done_at(path, results)
                    logger.info(
                        "Processing complete for %s (%s)",
                        results.get("clientName", "Unknown"),
                        path.name,
                    )
                except Exception as e:
                    logger.exception("Processing failed for %s", path)
                    mark_error_at(path, str(e))

            time.sleep(POLL_INTERVAL_SECONDS)

        except Exception:
            logger.exception("Watcher loop error")
            time.sleep(1.0)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "--transcribe-child":
        os.environ["WATCHER_TRANSCRIBE_CHILD"] = "1"
        setup_logging()
        try:
            payload = transcribe_audio_impl(sys.argv[2])
        except Exception as e:
            sys.stderr.write(f"{e}\n")
            raise SystemExit(1)
        sys.stdout.write(json.dumps(payload, ensure_ascii=False))
        raise SystemExit(0)
    raise SystemExit(main())
