"""Persist rednote MCP batch results and run local Apple Vision OCR.

The input is a private MCP response, not a cookie file. Public Markdown uses
canonical note URLs; signed access URLs and image payloads remain private.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo


def unpack_batch(path: Path) -> dict:
    envelope = json.loads(path.read_text(encoding="utf-8"))
    if envelope.get("isError"):
        raise ValueError("MCP failed; inspect the private response before retrying")
    for block in envelope.get("content", []):
        if block.get("type") == "text":
            try:
                data = json.loads(block["text"])
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict) and "notes" in data:
                return data
    # get_note_content returns text plus MCP image blocks rather than batch JSON.
    text_blocks = [block["text"] for block in envelope.get("content", []) if block.get("type") == "text"]
    if text_blocks:
        text = text_blocks[0]
        match = re.search(r"\*\*笔记ID\*\*:\s*([A-Za-z0-9]{20,40})", text)
        if match and "**正文**:" in text:
            content = text.split("**正文**:", 1)[1].split("**图片数量**:", 1)[0].strip()
            images = [{"base64": block["data"], "mimeType": block["mimeType"]}
                      for block in envelope.get("content", []) if block.get("type") == "image"]
            scope = re.search(r"\*\*图片范围\*\*:\s*(\S+)", text)
            expected = re.search(r"\*\*预期图片数\*\*:\s*(\d+)", text)
            return {"notes": [{"noteId": match[1], "title": text.splitlines()[0].lstrip("# "),
                               "content": content, "images": images,
                               "imageScope": scope[1] if scope else "unverified",
                               "expectedImageCount": int(expected[1]) if expected else None,
                               "missingImageCount": max(0, int(expected[1]) - len(images)) if expected else None}], "failedCount": 0}
    raise ValueError("MCP response did not contain a batch result")


def extract_batch(response: Path, kb_dir: Path, ocr_binary: Path, folder: str) -> dict:
    batch = unpack_batch(response)
    if len(batch["notes"]) > 20:
        raise ValueError("Batch exceeds the 20-note limit")
    report = {"source": "xiaohongshu", "source_folder": folder,
              "extracted_at": datetime.fromtimestamp(response.stat().st_mtime, ZoneInfo("Asia/Shanghai")).isoformat(),
              "notes": [], "failed_count": batch.get("failedCount", 0)}
    raw_dir = kb_dir / "raw" / "xiaohongshu"
    raw_dir.mkdir(parents=True, exist_ok=True)
    for note in batch["notes"]:
        note_id = note["noteId"]
        if not re.fullmatch(r"[A-Za-z0-9]{20,40}", note_id):
            raise ValueError("Invalid note ID")
        if note.get("images") and note.get("imageScope") != "current_note":
            raise ValueError("Image provenance is unverified; refusing to mix recommendation images into raw notes")
        asset_dir = raw_dir / "images" / note_id
        asset_dir.mkdir(parents=True, exist_ok=True)
        paths = []
        for number, image in enumerate(note.get("images", []), 1):
            mime = image.get("mimeType", "image/jpeg")
            extension = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}.get(mime)
            if not extension:
                raise ValueError(f"Unsupported image type: {mime}")
            encoded = image.get("base64", "")
            if encoded.startswith("data:"):
                encoded = encoded.split(",", 1)[1]
            payload = base64.b64decode(encoded, validate=True)
            if not payload:
                raise ValueError("Empty image payload")
            digest = hashlib.sha256(payload).hexdigest()[:12]
            image_path = asset_dir / f"{number:02d}-{digest}.{extension}"
            if image_path.exists() and image_path.read_bytes() != payload:
                raise ValueError(f"Image changed; refusing to overwrite {image_path}")
            image_path.write_bytes(payload)
            paths.append(image_path)
        ocr = []
        if paths:
            result = subprocess.run([str(ocr_binary.resolve()), *map(str, paths)],
                                    check=True, capture_output=True, text=True, timeout=300)
            ocr = json.loads(result.stdout)
            if len(ocr) != len(paths):
                raise ValueError("OCR returned an incomplete image result set")
        sections = []
        image_report = []
        for number, (image_path, record) in enumerate(zip(paths, ocr), 1):
            text = "\n".join(line["text"] for line in record.get("lines", []))
            error = record.get("error")
            sections.append(f"### 图片 {number}\n\n![]({image_path.relative_to(raw_dir).as_posix()})\n\n"
                            + (f"OCR 失败：{error}" if error else text or "OCR 未识别到文字"))
            image_report.append({"path": str(image_path), "characters": len(text),
                                 "sha256": hashlib.sha256(image_path.read_bytes()).hexdigest(),
                                 "error": error})
        canonical_url = f"https://www.xiaohongshu.com/explore/{note_id}"
        document = (f"# {note.get('title', '')}\n\n"
                    f"source: xiaohongshu\nsource_url: {canonical_url}\n"
                    f"source_folder: {folder}\ncollected_at: unknown\n"
                    f"extracted_at: {report['extracted_at']}\n\n"
                    f"## 正文\n\n{note.get('content', '')}\n\n"
                    "## 图片文字（Apple Vision 本地 OCR）\n\n"
                    "OCR 为机器识别结果，可能有错字；公式、图表须对照原图，不据此补造答案。\n\n"
                    + "\n\n".join(sections) + "\n")
        raw_path = raw_dir / f"{note_id}.md"
        if raw_path.exists() and raw_path.read_text(encoding="utf-8") != document:
            # Keep earlier partial extractions for audit rather than replacing
            # them when a subsequent response contains more images or text.
            digest = hashlib.sha256(document.encode("utf-8")).hexdigest()[:12]
            raw_path = raw_dir / f"{note_id}-{digest}.md"
        raw_path.write_text(document, encoding="utf-8")
        report["notes"].append({"note_id": note_id, "title": note.get("title", ""),
                                "source_url": canonical_url, "raw_path": str(raw_path),
                                "body_prefix": note.get("content", "")[:200],
                                "image_scope": note.get("imageScope", "unverified"),
                                "expected_images": note.get("expectedImageCount"),
                                "missing_images": note.get("missingImageCount"),
                                "images": image_report})
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("response", type=Path)
    parser.add_argument("--kb-dir", type=Path, default=Path("interview-kb"))
    parser.add_argument("--ocr-binary", type=Path, required=True)
    parser.add_argument("--folder", default="knowledge")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = extract_batch(args.response, args.kb_dir, args.ocr_binary, args.folder)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ocr_errors = sum(bool(image["error"]) for note in report["notes"] for image in note["images"])
    missing_images = sum(note["missing_images"] or 0 for note in report["notes"])
    print(json.dumps({"notes": len(report["notes"]), "failed_count": report["failed_count"],
                      "image_count": sum(len(n["images"]) for n in report["notes"]),
                      "ocr_errors": ocr_errors, "missing_images": missing_images}, ensure_ascii=False))
    if not report["notes"] or report["failed_count"] or ocr_errors or missing_images:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
