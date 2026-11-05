from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .filtering import heuristic_filter, quick_view
from .raw_markdown import load_raw_notes
from .validation import validate_tree


def _prepare(raw_dir: Path, output: Path) -> int:
    items = load_raw_notes(raw_dir)
    records = []
    for item in items:
        records.append({
            "quick_view": quick_view(item),
            "heuristic": heuristic_filter(item).to_dict(),
        })
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts = {key: 0 for key in ("relevant", "low_confidence", "irrelevant")}
    for record in records:
        counts[record["heuristic"]["decision"]] += 1
    print(json.dumps({"items": len(records), "counts": counts, "output": str(output)}, ensure_ascii=False))
    return 0


def _validate(kb_dir: Path) -> int:
    failures = validate_tree(kb_dir)
    note_count = len(list((kb_dir / "by-company").glob("**/*.md")))
    print(json.dumps({"notes": note_count, "failures": failures}, ensure_ascii=False, indent=2))
    return 1 if failures else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interview knowledge-base workflow")
    sub = parser.add_subparsers(dest="command", required=True)
    prepare = sub.add_parser("prepare-filter", help="Build lightweight filter packets")
    prepare.add_argument("--raw-dir", type=Path, required=True)
    prepare.add_argument("--output", type=Path, required=True)
    validate = sub.add_parser("validate", help="Validate structured interview notes")
    validate.add_argument("--kb-dir", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "prepare-filter":
        return _prepare(args.raw_dir, args.output)
    if args.command == "validate":
        return _validate(args.kb_dir)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
