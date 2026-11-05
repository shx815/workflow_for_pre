from pathlib import Path
import json
import unittest
import hashlib

from interview_kb.filtering import heuristic_filter
from interview_kb.raw_markdown import load_raw_notes
from interview_kb.validation import validate_note, validate_tree


ROOT = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def test_raw_batch_parses(self):
        items = load_raw_notes(ROOT / "interview-kb" / "raw" / "douyin")
        self.assertEqual(len(items), 10)
        self.assertTrue(all(item.source_url.startswith("https://www.douyin.com/") for item in items))
        self.assertTrue(all(item.description for item in items))

    def test_lightweight_filter_counts(self):
        items = load_raw_notes(ROOT / "interview-kb" / "raw" / "douyin")
        decisions = [heuristic_filter(item).decision for item in items]
        self.assertEqual(decisions.count("relevant"), 3)
        self.assertEqual(decisions.count("irrelevant"), 7)

    def test_structured_notes_validate(self):
        failures = validate_tree(ROOT / "interview-kb")
        self.assertEqual(failures, {})

    def test_agent_supplement_is_explicit(self):
        path = ROOT / "interview-kb" / "by-company" / "unknown" / "770311-Transformer为何不用BN.md"
        self.assertEqual(validate_note(path), [])
        self.assertIn("> **Agent 补充：**", path.read_text(encoding="utf-8"))

    def test_processing_ledger_is_complete(self):
        ledger = json.loads((ROOT / "state" / "processing-ledger.json").read_text(encoding="utf-8"))
        items = ledger["items"]
        douyin_items = {key: item for key, item in items.items() if key.startswith("douyin:")}
        self.assertEqual(len(douyin_items), 10)
        statuses = [item["status"] for item in douyin_items.values()]
        self.assertEqual(statuses.count("summarized"), 3)
        self.assertEqual(statuses.count("skipped_irrelevant"), 7)

    def test_xiaohongshu_stage_three_acceptance(self):
        report = json.loads((ROOT / "state/rednote-extraction-report.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(report["notes"]), 5)
        self.assertEqual(report["failed_count"], 0)
        ledger = json.loads((ROOT / "state/processing-ledger.json").read_text(encoding="utf-8"))["items"]
        for note in report["notes"]:
            self.assertEqual(note["image_scope"], "current_note")
            self.assertEqual(note["missing_images"], 0)
            self.assertEqual(len(note["images"]), note["expected_images"])
            self.assertTrue(note["images"])
            self.assertTrue((ROOT / note["raw_path"]).exists())
            entry = ledger["xiaohongshu:" + note["note_id"]]
            self.assertEqual(entry["status"], "summarized")
            self.assertEqual(validate_note(ROOT / entry["output"]), [])
            for image in note["images"]:
                self.assertIsNone(image["error"])
                self.assertGreater(image["characters"], 0)
                self.assertEqual(hashlib.sha256((ROOT / image["path"]).read_bytes()).hexdigest(), image["sha256"])


if __name__ == "__main__":
    unittest.main()
