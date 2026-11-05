from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .raw_markdown import RawItem


POSITIVE_SIGNALS = (
    "面试", "面经", "八股", "求职", "岗位", "算法岗", "校招", "秋招", "手撕",
    "大模型", "agent", "transformer", "自注意力", "attention", "kv cache",
    "rlhf", "深度学习", "layernorm", "batch normalization", "bn",
)

NEGATIVE_SIGNALS = (
    "美剧", "洗碗", "喵喵", "恋爱日记", "无畏契约", "valorant",
    "初恋", "爱情", "相亲", "暗恋",
)


@dataclass(frozen=True)
class FilterDecision:
    aweme_id: str
    decision: str
    confidence: str
    signals: List[str]
    rationale: str
    raw_path: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "aweme_id": self.aweme_id,
            "decision": self.decision,
            "confidence": self.confidence,
            "signals": self.signals,
            "rationale": self.rationale,
            "raw_path": self.raw_path,
        }


def quick_view(item: RawItem) -> Dict[str, object]:
    transcript = item.transcript
    if item.transcript_status == "skipped_image":
        transcript = ""
    return {
        "aweme_id": item.aweme_id,
        "title": item.title,
        "description_prefix": item.description[:200],
        "transcript_prefix": transcript[:450],
        "transcript_status": item.transcript_status,
        "cover_ocr_available": False,
        "source_url": item.source_url,
        "raw_path": item.raw_path,
    }


def heuristic_filter(item: RawItem) -> FilterDecision:
    view = quick_view(item)
    text = "\n".join(
        str(view[key]).lower()
        for key in ("title", "description_prefix", "transcript_prefix")
    )
    positive = [signal for signal in POSITIVE_SIGNALS if signal.lower() in text]
    negative = [signal for signal in NEGATIVE_SIGNALS if signal.lower() in text]

    if negative and not positive:
        decision, confidence = "irrelevant", "high"
        rationale = "命中明显非面试内容信号。"
        signals = negative
    elif len(positive) >= 2:
        decision, confidence = "relevant", "high"
        rationale = "命中多个大模型/算法面试信号。"
        signals = positive
    elif positive:
        decision, confidence = "low_confidence", "low"
        rationale = "仅命中一个弱相关信号，需要 LLM 复核。"
        signals = positive
    else:
        decision, confidence = "irrelevant", "medium"
        rationale = "快速视图中没有大模型算法面试信号。"
        signals = []

    return FilterDecision(
        aweme_id=item.aweme_id,
        decision=decision,
        confidence=confidence,
        signals=signals,
        rationale=rationale,
        raw_path=item.raw_path,
    )
