import base64
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from interview_kb.rednote import extract_batch, unpack_batch


class RednoteExtractionTests(unittest.TestCase):
    def test_mcp_failure_is_not_treated_as_empty_success(self):
        with tempfile.TemporaryDirectory() as directory:
            response = Path(directory) / "response.json"
            response.write_text(json.dumps({"isError": True, "content": []}))
            with self.assertRaisesRegex(ValueError, "MCP failed"):
                unpack_batch(response)

    def test_ocr_and_source_images_are_preserved_without_signed_url(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            note_id = "68abecda000000001d01a881"
            batch = {"notes": [{"noteId": note_id, "title": "面试问题", "content": "DAPO 改进了什么？", "imageScope": "current_note",
                                 "url": "https://www.xiaohongshu.com/explore/example?xsec_token=test-token",
                                 "images": [{"mimeType": "image/png", "base64": base64.b64encode(b"fixture-image").decode()}]}],
                     "failedCount": 0}
            response = root / "batch.json"
            response.write_text(json.dumps({"content": [{"type": "text", "text": json.dumps(batch)}]}))
            recognized = [{"lines": [{"text": "Clip-Higher", "confidence": 0.9}]}]
            completed = subprocess.CompletedProcess([], 0, json.dumps(recognized), "")
            with patch("interview_kb.rednote.subprocess.run", return_value=completed):
                report = extract_batch(response, root / "kb", Path("/unused/ocr"), "knowledge")
            raw = Path(report["notes"][0]["raw_path"]).read_text()
            self.assertIn("DAPO 改进了什么？", raw)
            self.assertIn("Clip-Higher", raw)
            self.assertNotIn("test-token", raw)
            self.assertIn("collected_at: unknown", raw)
            self.assertEqual(report["notes"][0]["images"][0]["characters"], 11)
            self.assertEqual(Path(report["notes"][0]["images"][0]["path"]).read_bytes(), b"fixture-image")

    def test_unscoped_images_are_rejected_before_writing_raw(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            response = root / "batch.json"
            data = {"notes": [{"noteId": "68abecda000000001d01a881", "images": [{"base64": "eA=="}]}]}
            response.write_text(json.dumps({"content": [{"type": "text", "text": json.dumps(data)}]}))
            with self.assertRaisesRegex(ValueError, "Image provenance"):
                extract_batch(response, root / "kb", Path("/unused/ocr"), "knowledge")
            self.assertEqual(list((root / "kb").rglob("*.md")), [])

    def test_untrusted_note_id_cannot_escape_raw_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            response = root / "batch.json"
            data = {"notes": [{"noteId": "../../outside", "images": []}]}
            response.write_text(json.dumps({"content": [{"type": "text", "text": json.dumps(data)}]}))
            with self.assertRaisesRegex(ValueError, "Invalid note ID"):
                extract_batch(response, root / "kb", Path("/unused/ocr"), "knowledge")


if __name__ == "__main__":
    unittest.main()
