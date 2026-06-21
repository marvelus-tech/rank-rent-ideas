#!/usr/bin/env python3
"""
Peekaboo Agent Core — Vision-driven autonomous UI automation framework.

Provides the "Manus-style" agent loop for Peekaboo:
  OBSERVE → ANALYZE → PLAN → ACT → VERIFY → (RECOVER if needed)

Features:
  - Vision-first: every action is preceded by screenshot + analysis
  - Self-correcting: verifies outcomes, retries with alternate strategies
  - Stateful: persists progress to JSON, can resume after interruption
  - Multi-strategy: tries primary approach, falls back to alternates
  - Debug-rich: saves every screenshot and decision to disk

Usage:
    from peekaboo_agent import PeekabooAgent, AgentState
    agent = PeekabooAgent("maps_scrape", state_file="data/agent_state.json")
    agent.run_phase("init", lambda ctx: launch_browser())
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
UTC = timezone.utc
from pathlib import Path
from typing import Any, Callable, Literal


# ------------------------------------------------------------------
# Exceptions
# ------------------------------------------------------------------

class AgentError(Exception):
    """Agent failed to complete a phase after all retries."""
    pass


class PhaseError(Exception):
    """A single phase attempt failed."""
    pass


# ------------------------------------------------------------------
# Agent State
# ------------------------------------------------------------------

@dataclass
class AgentState:
    """Persistent task state — survives crashes and resumes."""
    task_name: str = ""
    task_id: str = ""
    phase: str = "idle"
    step: int = 0
    started_at: str = ""
    last_action: str = ""
    last_action_success: bool = False
    leads_extracted: int = 0
    total_attempts: int = 0
    screenshots: list[str] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    phase_history: list[str] = field(default_factory=list)
    strategy_log: list[dict] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    _file_path: Path | None = None

    @classmethod
    def load(cls, path: str | Path) -> "AgentState":
        p = Path(path)
        if p.exists():
            raw = json.loads(p.read_text(encoding="utf-8"))
            # Ignore unknown fields for forward compatibility
            known = {f.name for f in cls.__dataclass_fields__.values() if f.name != "_file_path"}
            raw = {k: v for k, v in raw.items() if k in known}
            inst = cls(**raw)
            inst._file_path = p
            return inst
        return cls(_file_path=p)

    def save(self) -> None:
        if self._file_path:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {k: v for k, v in asdict(self).items() if not k.startswith("_")}
            self._file_path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")

    def start_task(self, task_name: str, **meta) -> None:
        self.task_name = task_name
        self.task_id = f"{task_name}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}"
        self.started_at = datetime.now(UTC).isoformat()
        self.phase = "init"
        self.step = 0
        self.phase_history = []
        self.errors = []
        self.strategy_log = []
        self.data = meta
        self.save()

    def set_phase(self, phase: str) -> None:
        self.phase = phase
        self.phase_history.append(phase)
        self.step = 0
        self.save()

    def advance_step(self, action: str, success: bool = True) -> None:
        self.step += 1
        self.last_action = action
        self.last_action_success = success
        self.total_attempts += 1
        self.save()

    def log_screenshot(self, path: str) -> None:
        self.screenshots.append(path)
        self.save()

    def log_error(self, phase: str, error: str, context: dict | None = None) -> None:
        self.errors.append({
            "timestamp": datetime.now(UTC).isoformat(),
            "phase": phase,
            "error": error,
            "context": context or {},
        })
        self.save()

    def log_strategy(self, phase: str, strategy: str, reason: str) -> None:
        self.strategy_log.append({
            "timestamp": datetime.now(UTC).isoformat(),
            "phase": phase,
            "strategy": strategy,
            "reason": reason,
        })
        self.save()

    def set_data(self, key: str, value: Any) -> None:
        self.data[key] = value
        self.save()

    def get_data(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def is_resumable(self, expected_phase: str) -> bool:
        """Check if we can resume from a previous run."""
        if not self.started_at:
            return False
        # Only resume if we're in the same task family and not too old
        age_hours = (datetime.now(UTC) - datetime.fromisoformat(self.started_at.replace("Z", "+00:00"))).total_seconds() / 3600
        return age_hours < 2 and self.phase == expected_phase


# ------------------------------------------------------------------
# Screenshot Analysis Result
# ------------------------------------------------------------------

@dataclass
class ScreenshotAnalysis:
    """Result of analyzing a screenshot."""
    screenshot_path: str
    raw_text: str = ""
    element_map: dict[str, str] = field(default_factory=dict)
    detected_ui: list[str] = field(default_factory=list)
    detected_businesses: list[dict] = field(default_factory=list)
    current_url: str | None = None
    page_title: str | None = None
    error_flags: list[str] = field(default_factory=list)
    confidence: float = 0.0


# ------------------------------------------------------------------
# Peekaboo Agent Core
# ------------------------------------------------------------------

class PeekabooAgent:
    """
    Vision-driven agent framework for Peekaboo macOS automation.

    Implements the core loop:
        OBSERVE → ANALYZE → PLAN → ACT → VERIFY → RECOVER
    """

    def __init__(
        self,
        task_name: str,
        browser_app: str = "Brave Browser",
        max_retries: int = 3,
        state_file: str | Path | None = None,
        debug_dir: str = "data/debug/agent",
        mode: Literal["interactive", "autonomous"] = "autonomous",
        delay_base: float = 3.0,
    ):
        self.task_name = task_name
        self.browser_app = browser_app
        self.max_retries = max_retries
        self.mode = mode
        self.delay_base = delay_base

        # State
        if state_file:
            self.state = AgentState.load(state_file)
        else:
            self.state = AgentState()

        # Debug
        self.debug_dir = Path(debug_dir)
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_counter = 0

    # ------------------------------------------------------------------
    # Low-level Peekaboo wrappers
    # ------------------------------------------------------------------

    def _peek(self, *args: str, capture: bool = True, timeout: int = 300) -> str:
        """Run a Peekaboo CLI command."""
        cmd = ["peekaboo"] + list(args)
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture,
                text=True,
                timeout=timeout,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            err = f"[peekaboo error] {' '.join(args)}: {e.stderr}"
            print(err, file=sys.stderr)
            return ""
        except subprocess.TimeoutExpired:
            err = f"[peekaboo timeout] {' '.join(args)}"
            print(err, file=sys.stderr)
            return ""

    def _pbpaste(self) -> str:
        """Read macOS clipboard."""
        try:
            result = subprocess.run(
                ["pbpaste"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        return ""

    def sleep(self, seconds: float | None = None) -> None:
        """Pause execution."""
        time.sleep(seconds or self.delay_base)

    # ------------------------------------------------------------------
    # Vision system
    # ------------------------------------------------------------------

    def observe(self, label: str = "") -> str:
        """
        Capture and save an annotated screenshot.
        Returns the path to the screenshot.
        """
        self.screenshot_counter += 1
        name = f"agent_step_{self.screenshot_counter:03d}"
        if label:
            name += f"_{label}"
        path = self.debug_dir / f"{name}.png"

        # Capture annotated screenshot
        self._peek(
            "see",
            "--app", self.browser_app,
            "--annotate",
            "--path", str(path),
            
        )
        self.state.log_screenshot(str(path))
        return str(path)

    def analyze_screenshot(self, screenshot_path: str, prompt: str | None = None) -> ScreenshotAnalysis:
        """
        Analyze a screenshot using Peekaboo's built-in vision.
        Falls back to heuristics if vision analysis fails.
        """
        result = ScreenshotAnalysis(screenshot_path=screenshot_path)

        # Try Peekaboo's built-in analysis
        default_prompt = (
            "Analyze this Google Maps screenshot. "
            "List visible UI elements, business listings, search results, "
            "detail panels, loading states, and any error messages. "
            "Identify element IDs if visible (B1, B2, etc.)."
        )
        analysis_prompt = prompt or default_prompt

        analysis_output = self._peek(
            "image",
            "--path", screenshot_path,
            "--analyze", analysis_prompt,
            timeout=60,
        )

        if analysis_output:
            result.raw_text = analysis_output
            result.confidence = 0.8
            # Parse element IDs from analysis
            result.element_map = self._parse_element_map(analysis_output)
            result.detected_ui = self._parse_ui_elements(analysis_output)
            result.detected_businesses = self._parse_businesses(analysis_output)
            result.error_flags = self._parse_error_flags(analysis_output)
        else:
            # Fallback: no analysis available
            result.confidence = 0.3
            result.error_flags.append("vision_analysis_unavailable")

        return result

    def quick_observe(self, label: str = "") -> ScreenshotAnalysis:
        """One-liner: screenshot + analyze."""
        path = self.observe(label)
        return self.analyze_screenshot(path)

    # ------------------------------------------------------------------
    # Analysis parsers (heuristics)
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_element_map(text: str) -> dict[str, str]:
        """Extract element ID → description mapping from analysis text."""
        elements = {}
        # Match patterns like "B1 - search box" or "Element B2: result listing"
        patterns = [
            r"([A-Z]\d+)\s*[-:]\s*(.+?)(?:\n|$)",
            r"Element\s+([A-Z]\d+)[\s:-]+(.+?)(?:\n|$)",
            r"([A-Z]\d+)\s+\((.+?)\)",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                eid = match.group(1).upper()
                desc = match.group(2).strip()
                if desc and len(desc) > 2:
                    elements[eid] = desc
        return elements

    @staticmethod
    def _parse_ui_elements(text: str) -> list[str]:
        """Identify UI components from analysis."""
        ui_keywords = [
            "search box", "search bar", "search field",
            "result", "listing", "business card",
            "detail panel", "info panel", "sidebar",
            "map", "zoom", "directions",
            "menu", "filter", "sort",
            "loading", "spinner", "progress",
            "error", "offline", "retry",
            "website link", "phone button", "call button",
            "reviews", "rating", "stars",
            "hours", "open now", "closed",
            "address", "location",
        ]
        found = []
        text_lower = text.lower()
        for keyword in ui_keywords:
            if keyword in text_lower:
                found.append(keyword)
        return found

    @staticmethod
    def _parse_businesses(text: str) -> list[dict]:
        """Extract business mentions from analysis."""
        businesses = []
        # Look for business name patterns
        name_patterns = [
            r'"([^"]{3,50})"',  # Quoted names
            r"business[\s:]+([A-Z][A-Za-z\s&']{2,40})",
            r"listing[\s:]+([A-Z][A-Za-z\s&']{2,40})",
            r"([A-Z][A-Za-z\s&']{3,40})\s*[-–—]\s*(?:rating|reviews|address)",
        ]
        seen = set()
        for pattern in name_patterns:
            for match in re.finditer(pattern, text):
                name = match.group(1).strip()
                if name and name not in seen and len(name) > 3:
                    seen.add(name)
                    businesses.append({"name": name, "source": "analysis_text"})
        return businesses

    @staticmethod
    def _parse_error_flags(text: str) -> list[str]:
        """Detect error conditions in analysis."""
        flags = []
        text_lower = text.lower()
        error_indicators = {
            "no results": "no_results",
            "no listings": "no_listings",
            "empty": "empty_results",
            "loading": "still_loading",
            "spinner": "still_loading",
            "error": "page_error",
            "offline": "offline",
            "sign in": "auth_required",
            "captcha": "captcha",
            "verify": "verification_required",
            "not found": "page_not_found",
            "404": "page_not_found",
        }
        for indicator, flag in error_indicators.items():
            if indicator in text_lower:
                flags.append(flag)
        return flags

    # ------------------------------------------------------------------
    # Browser lifecycle
    # ------------------------------------------------------------------

    def ensure_browser(self, url: str | None = None) -> None:
        """Ensure browser is running and focused."""
        # Check if running
        apps = self._peek("list", "apps", "--json")
        is_running = self.browser_app.lower() in apps.lower()

        if not is_running:
            print(f"[agent] Launching {self.browser_app}...")
            self._peek("app", "launch", self.browser_app)
            self.sleep(5)

        # Focus
        self._peek("window", "focus", "--app", self.browser_app)
        self.sleep(1)

        # Navigate if URL provided
        if url:
            self._peek("hotkey", "--keys", "cmd,l", "--app", self.browser_app)
            self.sleep(0.5)
            self._peek("type", url, "--app", self.browser_app, "--clear")
            self.sleep(0.5)
            self._peek("press", "return", "--app", self.browser_app)
            self.sleep(5)

    def quit_browser(self) -> None:
        """Gracefully quit browser."""
        try:
            self._peek("app", "quit", "--app", self.browser_app)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Core agent loop
    # ------------------------------------------------------------------

    def run_phase(
        self,
        phase_name: str,
        phase_fn: Callable[[ScreenshotAnalysis], Any],
        verify_fn: Callable[[Any, ScreenshotAnalysis], bool] | None = None,
        alternate_strategies: list[Callable[[ScreenshotAnalysis], Any]] | None = None,
    ) -> Any:
        """
        Execute a task phase with full vision loop.

        Args:
            phase_name: Name of the phase (for logging and state)
            phase_fn: Primary strategy function
            verify_fn: Optional custom verification function
            alternate_strategies: Fallback functions to try if primary fails

        Returns:
            Result from the successful strategy
        """
        self.state.set_phase(phase_name)
        strategies = [phase_fn] + (alternate_strategies or [])

        for strategy_idx, strategy in enumerate(strategies):
            strategy_name = f"strategy_{strategy_idx}"
            if strategy_idx == 0:
                strategy_name = "primary"

            self.state.log_strategy(phase_name, strategy_name, f"Attempting {strategy_name} for {phase_name}")
            print(f"\n[agent] Phase '{phase_name}' — {strategy_name} (attempt 1/{self.max_retries})")

            for attempt in range(self.max_retries):
                try:
                    # 1. OBSERVE
                    print(f"  [observe] Taking screenshot...")
                    pre_analysis = self.quick_observe(f"{phase_name}_pre_{attempt}")

                    # 2. PLAN & ACT
                    print(f"  [act] Executing {strategy_name}...")
                    result = strategy(pre_analysis)

                    # 3. VERIFY
                    print(f"  [verify] Checking outcome...")
                    self.sleep(1)
                    post_analysis = self.quick_observe(f"{phase_name}_post_{attempt}")

                    verified = self._verify_result(
                        phase_name, result, pre_analysis, post_analysis, verify_fn
                    )

                    if verified:
                        print(f"  ✅ {phase_name} succeeded with {strategy_name}")
                        self.state.advance_step(f"{phase_name}:{strategy_name}", success=True)
                        return result

                    # Verification failed — log and retry
                    print(f"  ⚠️ Verification failed, retrying...")
                    self.state.log_error(
                        phase_name,
                        f"Verification failed (attempt {attempt + 1})",
                        {"strategy": strategy_name, "pre": pre_analysis.raw_text[:200], "post": post_analysis.raw_text[:200]},
                    )

                    # Exponential backoff
                    wait = self.delay_base * (2 ** attempt)
                    print(f"  [backoff] Waiting {wait}s...")
                    self.sleep(wait)

                except Exception as e:
                    err_msg = f"{type(e).__name__}: {str(e)}"
                    print(f"  ❌ Error: {err_msg}")
                    self.state.log_error(phase_name, err_msg, {"strategy": strategy_name})
                    if attempt < self.max_retries - 1:
                        wait = self.delay_base * (2 ** attempt)
                        print(f"  [backoff] Waiting {wait}s before retry...")
                        self.sleep(wait)
                    else:
                        # All retries exhausted for this strategy
                        break

            # Strategy exhausted — try next alternate
            if strategy_idx < len(strategies) - 1:
                print(f"  [fallback] Switching to alternate strategy...")
                self.sleep(2)
            else:
                # All strategies failed
                break

        # Catastrophic failure — all strategies exhausted
        error_summary = f"Phase '{phase_name}' failed after {self.max_retries} retries × {len(strategies)} strategies"
        print(f"\n[agent] 🔥 {error_summary}")
        self.state.log_error(phase_name, error_summary)

        if self.mode == "interactive":
            # In interactive mode, pause and let user fix
            print("\n[agent] Interactive mode — pausing for manual intervention.")
            print(f"  Last screenshot: {self.state.screenshots[-1] if self.state.screenshots else 'N/A'}")
            print("  Fix the issue and press Enter to retry, or type 'skip' to abort phase...")
            user_input = input("  > ").strip().lower()
            if user_input == "skip":
                raise AgentError(error_summary)
            # User wants to retry — recurse with same parameters
            return self.run_phase(phase_name, phase_fn, verify_fn, alternate_strategies)
        else:
            raise AgentError(error_summary)

    def _verify_result(
        self,
        phase_name: str,
        result: Any,
        pre: ScreenshotAnalysis,
        post: ScreenshotAnalysis,
        custom_verify: Callable[[Any, ScreenshotAnalysis], bool] | None = None,
    ) -> bool:
        """Verify that a phase produced the expected outcome."""
        # Custom verification takes priority
        if custom_verify:
            try:
                return custom_verify(result, post)
            except Exception as e:
                print(f"  [verify] Custom verifier failed: {e}")
                return False

        # Default verifications by phase type
        if phase_name == "init":
            # Browser should be showing a web page
            return "error" not in post.error_flags and ("search" in post.detected_ui or "map" in post.detected_ui)

        elif phase_name == "search":
            # Results should have appeared
            has_results = (
                "result" in post.detected_ui
                or "listing" in post.detected_ui
                or len(post.detected_businesses) > 0
                or "business card" in post.detected_ui
            )
            not_loading = "still_loading" not in post.error_flags
            return has_results and not_loading

        elif phase_name == "extract":
            # Should have extracted some data
            if isinstance(result, list):
                return len(result) > 0
            elif isinstance(result, dict):
                return bool(result.get("name"))
            return result is not None

        elif phase_name == "scroll":
            # New content should have loaded
            return "still_loading" not in post.error_flags

        elif phase_name == "detail_open":
            # Detail panel should be visible
            return "detail panel" in post.detected_ui or "info panel" in post.detected_ui

        elif phase_name == "detail_close":
            # Should be back to list view
            return "result" in post.detected_ui or "listing" in post.detected_ui

        # Generic: no obvious errors
        return len(post.error_flags) == 0

    # ------------------------------------------------------------------
    # Interactive helpers
    # ------------------------------------------------------------------

    def click_element(self, element_id: str | None = None, coords: tuple[int, int] | None = None, label: str = "") -> bool:
        """Click an element by ID or coordinates."""
        if element_id:
            print(f"  [click] Element {element_id} ({label})")
            self._peek("click", "--on", element_id, "--app", self.browser_app)
        elif coords:
            print(f"  [click] Coordinates {coords} ({label})")
            x, y = coords
            self._peek("click", "--coords", f"{x},{y}", "--app", self.browser_app)
        else:
            return False
        self.sleep(0.5)
        return True

    def type_text(self, text: str, clear: bool = False, submit: bool = False) -> None:
        """Type text into the focused field."""
        args = ["type", text, "--app", self.browser_app]
        if clear:
            args.append("--clear")
        self._peek(*args)
        if submit:
            self.sleep(0.3)
            self._peek("press", "return", "--app", self.browser_app)
        self.sleep(0.5)

    def press_key(self, key: str, count: int = 1) -> None:
        """Press a special key."""
        for _ in range(count):
            self._peek("press", key, "--app", self.browser_app)
            self.sleep(0.2)

    def scroll_page(self, direction: str = "down", amount: int = 3) -> None:
        """Scroll the page."""
        self._peek(
            "scroll",
            "--direction", direction,
            "--amount", str(amount),
            "--app", self.browser_app,
            
        )
        self.sleep(1)

    def hotkey(self, keys: str) -> None:
        """Send a hotkey combo."""
        self._peek("hotkey", "--keys", keys, "--app", self.browser_app)
        self.sleep(0.5)

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def generate_report(self) -> dict[str, Any]:
        """Generate a full agent run report."""
        return {
            "task_id": self.state.task_id,
            "task_name": self.state.task_name,
            "status": "completed" if not self.state.errors else "completed_with_errors",
            "duration_seconds": None,  # Could track start/end
            "phases_completed": self.state.phase_history,
            "total_steps": self.state.step,
            "total_attempts": self.state.total_attempts,
            "errors_count": len(self.state.errors),
            "errors": self.state.errors[-5:],  # Last 5 errors
            "screenshots_taken": len(self.state.screenshots),
            "screenshot_paths": self.state.screenshots[-10:],  # Last 10
            "strategies_used": self.state.strategy_log,
            "data": self.state.data,
        }

    def print_report(self) -> None:
        """Print a human-readable report."""
        report = self.generate_report()
        print(f"\n{'='*60}")
        print(f"AGENT REPORT: {report['task_name']}")
        print(f"{'='*60}")
        print(f"Task ID:    {report['task_id']}")
        print(f"Status:     {report['status']}")
        print(f"Phases:     {', '.join(report['phases_completed'])}")
        print(f"Steps:      {report['total_steps']}")
        print(f"Attempts:   {report['total_attempts']}")
        print(f"Errors:     {report['errors_count']}")
        print(f"Screenshots: {report['screenshots_taken']}")
        if report['errors']:
            print(f"\nRecent errors:")
            for err in report['errors']:
                print(f"  - [{err['phase']}] {err['error'][:80]}")
        print(f"{'='*60}\n")


# ------------------------------------------------------------------
# Utility
# ------------------------------------------------------------------

def extract_json_from_text(text: str) -> dict | None:
    """Try to extract a JSON object from messy text."""
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON in text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Try multiple JSON objects
    for match in re.finditer(r'\{[^{}]*\}', text):
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            continue

    return None
