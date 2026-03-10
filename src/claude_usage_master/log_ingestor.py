import json
from pathlib import Path
from typing import Any


def _read_checkpoint(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_checkpoint(path: Path, state: dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _extract_date(line: str) -> str | None:
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None
    ts = obj.get("ts")
    if not isinstance(ts, str) or len(ts) < 10:
        return None
    return ts[:10]


def ingest_incremental(log_dir: Path, checkpoint_path: Path) -> dict[str, Any]:
    """Read newly added lines from local jsonl logs.

    Returns newly consumed sample_size and all-time coverage_days in the folder.
    """
    checkpoint = _read_checkpoint(checkpoint_path)
    sample_size = 0
    dates: set[str] = set()

    if not log_dir.exists():
        _write_checkpoint(checkpoint_path, checkpoint)
        return {"sample_size": 0, "coverage_days": 0}

    files = sorted(log_dir.glob("*.jsonl"))
    for file in files:
        key = str(file)
        start = checkpoint.get(key, 0)
        count = 0
        with file.open("r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                day = _extract_date(line)
                if day:
                    dates.add(day)
                if idx > start:
                    count += 1
        sample_size += count
        checkpoint[key] = start + count

    _write_checkpoint(checkpoint_path, checkpoint)
    return {"sample_size": sample_size, "coverage_days": len(dates)}
