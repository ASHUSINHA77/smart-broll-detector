from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


MAX_COVERAGE_RATIO = 0.40
MIN_GAP_SECONDS = 3.0

DIRECT_TO_CAMERA_EXCLUSIONS = (
    "welcome back",
    "subscribe",
    "thanks for watching",
    "see you next time",
    "like and subscribe",
)

ABSTRACT_EXCLUSIONS = (
    "feel",
    "feeling",
    "believer",
    "worth it",
    "stress",
    "stressed",
    "realized",
    "thought",
    "honestly",
)

KEYWORD_GROUPS: Dict[str, Dict[str, Any]] = {
    "places/scenes": {
        "weight": 3,
        "words": ("hills", "forest", "forests", "valley", "river", "town", "streets"),
    },
    "objects": {
        "weight": 2,
        "words": ("beans", "mug", "deck", "shops", "stall"),
    },
    "actions": {
        "weight": 2,
        "words": ("drove", "roasting", "grabbed", "sat", "wandered", "picked up"),
    },
}


@dataclass(frozen=True)
class ScoredSegment:
    segment: Dict[str, Any]
    score: int
    hits: Tuple[str, ...]


def detect_broll_placements(
    transcript: Dict[str, Any],
    max_coverage_ratio: float = MAX_COVERAGE_RATIO,
    min_gap_seconds: float = MIN_GAP_SECONDS,
) -> List[Dict[str, Any]]:
    segments = transcript.get("segments", [])
    if not isinstance(segments, list):
        raise ValueError("transcript must include a segments list")

    duration = float(transcript.get("duration") or _duration_from_segments(segments))
    max_coverage = duration * max_coverage_ratio

    candidates = [
        scored
        for segment in segments
        if (scored := _score_segment(segment)) is not None
    ]
    candidates.sort(key=lambda item: (-item.score, item.segment["start"], _segment_duration(item.segment)))

    accepted: List[ScoredSegment] = []
    used_coverage = 0.0

    for candidate in candidates:
        candidate_duration = _segment_duration(candidate.segment)
        if used_coverage + candidate_duration > max_coverage + 1e-9:
            continue
        if any(not _has_min_gap(candidate.segment, kept.segment, min_gap_seconds) for kept in accepted):
            continue

        accepted.append(candidate)
        used_coverage += candidate_duration

    accepted.sort(key=lambda item: item.segment["start"])
    return [_placement_from_scored(item) for item in accepted]


def _score_segment(segment: Dict[str, Any]) -> Optional[ScoredSegment]:
    text = str(segment.get("text", ""))
    normalized = text.lower()

    if _contains_any(normalized, DIRECT_TO_CAMERA_EXCLUSIONS):
        return None

    visual_hits: List[str] = []
    score = 0
    for group_name, group in KEYWORD_GROUPS.items():
        matched_words = [word for word in group["words"] if word in normalized]
        if matched_words:
            score += int(group["weight"]) * len(matched_words)
            visual_hits.extend(f"{group_name}: {word}" for word in matched_words)

    if score == 0:
        return None

    if _contains_any(normalized, ABSTRACT_EXCLUSIONS) and score < 5:
        return None

    return ScoredSegment(segment=segment, score=score, hits=tuple(visual_hits))


def _placement_from_scored(scored: ScoredSegment) -> Dict[str, Any]:
    segment = scored.segment
    return {
        "segment_id": segment["id"],
        "start": segment["start"],
        "end": segment["end"],
        "reason": _build_reason(scored.hits),
        "score": scored.score,
    }


def _build_reason(hits: Sequence[str]) -> str:
    readable_hits = [hit.split(": ", 1)[1] for hit in hits]
    unique_hits = list(dict.fromkeys(readable_hits))
    if len(unique_hits) == 1:
        return f"Concrete visual cue: {unique_hits[0]}."
    return f"Strong visual cues: {', '.join(unique_hits)}."


def _contains_any(text: str, phrases: Iterable[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def _duration_from_segments(segments: Sequence[Dict[str, Any]]) -> float:
    if not segments:
        return 0.0
    return max(float(segment["end"]) for segment in segments)


def _segment_duration(segment: Dict[str, Any]) -> float:
    return float(segment["end"]) - float(segment["start"])


def _has_min_gap(a: Dict[str, Any], b: Dict[str, Any], min_gap_seconds: float) -> bool:
    if float(a["end"]) <= float(b["start"]):
        return float(b["start"]) - float(a["end"]) >= min_gap_seconds
    if float(b["end"]) <= float(a["start"]):
        return float(a["start"]) - float(b["end"]) >= min_gap_seconds
    return False
