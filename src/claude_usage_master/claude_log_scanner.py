"""Scan ~/.claude/projects/**/*.jsonl and emit project-format events.

Claude Code stores conversation logs under ~/.claude/projects/<project-slug>/<session>.jsonl.
Each line is a JSON object. This module reads only newly added lines (incremental via checkpoint),
converts user-message events to project log format, and appends them to data/logs/events.jsonl.

Event mapping:
  type="user", isMeta=false, first time sessionId seen  -> session_start + prompt_submit
  type="user", isMeta=false, sessionId already seen     -> prompt_submit
"""
import json
from pathlib import Path


def _read_checkpoint(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_checkpoint(path: Path, state: dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_events(output_path: Path, events: list[dict[str, str]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")


def scan_claude_logs(
    output_path: Path,
    scan_checkpoint_path: Path,
    claude_projects_dir: Path | None = None,
) -> int:
    """Scan Claude Code project logs and append new events to output_path.

    Reads only lines not yet processed (tracked via scan_checkpoint_path).
    Returns count of new events written.
    """
    if claude_projects_dir is None:
        claude_projects_dir = Path.home() / ".claude" / "projects"

    if not claude_projects_dir.exists():
        return 0

    checkpoint = _read_checkpoint(scan_checkpoint_path)
    new_events: list[dict[str, str]] = []
    # Track which sessionIds have already produced a session_start event,
    # including those seen in previously-processed lines of each file.
    seen_sessions: set[str] = set()

    files = sorted(claude_projects_dir.rglob("*.jsonl"))
    for file in files:
        key = str(file)
        start = checkpoint.get(key, 0)
        new_line_count = 0
        try:
            with file.open("r", encoding="utf-8", errors="replace") as fh:
                for idx, raw in enumerate(fh, start=1):
                    try:
                        entry = json.loads(raw)
                    except Exception:
                        if idx > start:
                            new_line_count += 1
                        continue

                    if idx <= start:
                        # Already processed: only collect session IDs to avoid re-emitting session_start.
                        if entry.get("type") == "user":
                            sid = entry.get("sessionId", "")
                            if sid:
                                seen_sessions.add(sid)
                        continue

                    # New line.
                    new_line_count += 1

                    if entry.get("type") != "user" or entry.get("isMeta", False):
                        continue

                    ts = entry.get("timestamp", "")
                    sid = entry.get("sessionId", "")
                    if not ts:
                        continue

                    if sid and sid not in seen_sessions:
                        seen_sessions.add(sid)
                        new_events.append({"ts": ts, "event": "session_start"})

                    new_events.append({"ts": ts, "event": "prompt_submit"})

        except Exception:
            continue

        checkpoint[key] = start + new_line_count

    if new_events:
        _append_events(output_path, new_events)

    _write_checkpoint(scan_checkpoint_path, checkpoint)
    return len(new_events)
