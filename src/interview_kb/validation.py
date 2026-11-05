from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, List


REQUIRED_FIELDS = (
    "source", "source_url", "collected_at", "company", "role",
    "interview_round", "topics", "difficulty", "confidence", "has_questions",
)

REQUIRED_HEADINGS = (
    "## 具体问题", "## 参考答案要点", "## 关键细节", "## 原文摘录",
)


def _frontmatter_lines(text: str) -> Dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        return {}
    result: Dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()
    return result


def validate_note(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8")
    meta = _frontmatter_lines(text)
    errors: List[str] = []
    for field in REQUIRED_FIELDS:
        value = meta.get(field, "")
        if not value or value in ('""', "''", "[]"):
            errors.append(f"missing or empty frontmatter field: {field}")
    if meta.get("source") not in ("douyin", "xiaohongshu"):
        errors.append("source must be douyin or xiaohongshu")
    if meta.get("difficulty") not in ("基础", "进阶", "前沿", "unknown"):
        errors.append("difficulty must be 基础/进阶/前沿/unknown")
    if meta.get("confidence") not in ("高", "中", "低"):
        errors.append("confidence must be 高/中/低")
    if meta.get("has_questions") not in ("true", "false"):
        errors.append("has_questions must be true or false")
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            errors.append(f"missing heading: {heading}")
    excerpt = re.search(r"^## 原文摘录\s*$\n(.*?)(?=^## |\Z)", text, re.MULTILINE | re.DOTALL)
    if excerpt and len(excerpt.group(1).strip()) > 500:
        errors.append("原文摘录 exceeds 500 characters")
    return errors


def validate_tree(kb_dir: Path) -> Dict[str, List[str]]:
    failures: Dict[str, List[str]] = {}
    for path in sorted((kb_dir / "by-company").glob("**/*.md")):
        errors = validate_note(path)
        if errors:
            failures[str(path)] = errors
    return failures
