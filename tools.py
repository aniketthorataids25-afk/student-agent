"""
core/tools.py

Shared data models + a "tool registry" that any agent can call.
Keeping tools here (instead of duplicating logic per-agent) is
what makes agents "share tools" as requested: Tracker, Predictor,
and Commander all import from this one module.

Swap `llm_generate_study_plan`'s body for a real Claude API call
whenever you're ready to move from heuristics to an LLM-authored
plan -- the call site never has to change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from statistics import mean
from typing import Dict, List


# --------------------------------------------------------------------------
# Data models
# --------------------------------------------------------------------------

class RiskLevel(str, Enum):
    ON_TRACK = "on_track"
    WATCH = "watch"
    AT_RISK = "at_risk"


@dataclass
class QuizResult:
    subject: str
    score_pct: float          # 0-100
    taken_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class StudySession:
    subject: str
    minutes: int
    focus_rating: int = 3     # 1 (distracted) - 5 (deep focus)
    taken_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SubjectSnapshot:
    """Rolled-up state for one subject, produced by the Tracker."""

    subject: str
    avg_score: float
    total_minutes: int
    session_count: int
    trend: float  # positive = improving, negative = declining


@dataclass
class Prediction:
    """Forward-looking assessment, produced by the Predictor."""

    subject: str
    risk_level: RiskLevel
    predicted_next_score: float
    reasoning: str


@dataclass
class StudyPlanItem:
    subject: str
    action: str
    minutes_recommended: int
    priority: int  # 1 = highest


# --------------------------------------------------------------------------
# Shared tools (pure functions -> easy to unit test)
# --------------------------------------------------------------------------

def compute_trend(scores: List[float]) -> float:
    """
    Cheap trend estimate: compare the average of the second half
    of recent scores to the first half. No numpy dependency needed.
    """
    if len(scores) < 2:
        return 0.0
    mid = len(scores) // 2
    first_half, second_half = scores[:mid], scores[mid:]
    return round(mean(second_half) - mean(first_half), 2)


def predict_next_score(scores: List[float], trend: float) -> float:
    """Naive linear projection, clamped to [0, 100]."""
    if not scores:
        return 0.0
    projected = scores[-1] + trend
    return round(max(0.0, min(100.0, projected)), 1)


def classify_risk(avg_score: float, trend: float) -> RiskLevel:
    if avg_score < 60 or trend <= -8:
        return RiskLevel.AT_RISK
    if avg_score < 75 or trend < 0:
        return RiskLevel.WATCH
    return RiskLevel.ON_TRACK


def llm_generate_study_plan(prediction: Prediction) -> str:
    """
    Placeholder "LLM tool". Replace this body with a real call to
    the Anthropic API (see README) to get natural-language coaching
    instead of the templated reasoning below. Keeping the signature
    stable means Commander never needs to change.
    """
    templates: Dict[RiskLevel, str] = {
        RiskLevel.AT_RISK: (
            f"{prediction.subject} needs immediate attention. "
            f"Schedule short, frequent review sessions and revisit "
            f"fundamentals before new material."
        ),
        RiskLevel.WATCH: (
            f"{prediction.subject} is slipping slightly. Add one "
            f"extra practice session this week focused on recent topics."
        ),
        RiskLevel.ON_TRACK: (
            f"{prediction.subject} is in good shape. Maintain the "
            f"current pace and consider light enrichment material."
        ),
    }
    return templates[prediction.risk_level]
