from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Dict, List


@dataclass(frozen=True)
class RawItem:
    aweme_id: str
    title: str
    author: str
    source_url: str
    observed_at: str
    transcript_status: str
    description: str
    transcript: str
    raw_path: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


def _frontmatter(text: str) -> Dict[str, str]:
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    values: Dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1].replace('\\"', '"')
        values[key.strip()] = value
    return values


def _section(text: str, start: str, end: str) -> str:
    pattern = re.compile(
        rf"^{re.escape(start)}\s*$\n(.*?)(?=^{re.escape(end)}\s*$)",
        flags=re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def parse_raw_note(path: Path) -> RawItem:
    text = path.read_text(encoding="utf-8")
    meta = _frontmatter(text)
    required = ("aweme_id", "title", "author", "source_url", "observed_at", "transcript_status")
    missing = [key for key in required if not meta.get(key)]
    if missing:
        raise ValueError(f"{path}: missing fields: {', '.join(missing)}")
    return RawItem(
        aweme_id=meta["aweme_id"],
        title=meta["title"],
        author=meta["author"],
        source_url=meta["source_url"],
        observed_at=meta["observed_at"],
        transcript_status=meta["transcript_status"],
        description=_section(text, "### 原始描述", "### 转录"),
        transcript=_section(text, "### 转录", "## Source"),
        raw_path=str(path.resolve()),
    )


def load_raw_notes(raw_dir: Path) -> List[RawItem]:
    return [parse_raw_note(path) for path in sorted(raw_dir.glob("*.md"))]
