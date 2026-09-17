"""
agents/tracker.py

TRACKER AGENT
-------------
Job: be the source of truth for "what actually happened."
It ingests raw study sessions and quiz results, keeps a rolling
history per subject, and whenever new data comes in, publishes a
`SubjectSnapshot` on the "tracker.snapshot" topic for the Predictor
to consume.

Tracker never predicts or decides anything -- single responsibility.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from agents.base_agent import BaseAgent
from core.message_bus import MessageBus
from core.tools import (
    QuizResult,
    StudySession,
    SubjectSnapshot,
    compute_trend,
)

TOPIC_QUIZ_IN = "student.quiz_result"
TOPIC_SESSION_IN = "student.study_session"
TOPIC_SNAPSHOT_OUT = "tracker.snapshot"


class TrackerAgent(BaseAgent):
    def __init__(self, bus: MessageBus) -> None:
        super().__init__(name="Tracker", bus=bus)
        self._scores: Dict[str, List[float]] = defaultdict(list)
        self._sessions: Dict[str, List[StudySession]] = defaultdict(list)

        bus.subscribe(TOPIC_QUIZ_IN, self._on_quiz_result)
        bus.subscribe(TOPIC_SESSION_IN, self._on_study_session)

    # -- public API (also callable directly, e.g. from tests/demo) --

    def record_quiz(self, result: QuizResult) -> None:
        self.publish(TOPIC_QUIZ_IN, result)

    def record_session(self, session: StudySession) -> None:
        self.publish(TOPIC_SESSION_IN, session)

    # -- internal handlers --

    def _on_quiz_result(self, msg) -> None:
        result: QuizResult = msg.payload
        self._scores[result.subject].append(result.score_pct)
        self.logger.info(
            "Recorded quiz: %s -> %.1f%%", result.subject, result.score_pct
        )
        self._emit_snapshot(result.subject)

    def _on_study_session(self, msg) -> None:
        session: StudySession = msg.payload
        self._sessions[session.subject].append(session)
        self.logger.info(
            "Recorded session: %s -> %d min (focus %d/5)",
            session.subject, session.minutes, session.focus_rating,
        )
        self._emit_snapshot(session.subject)

    def _emit_snapshot(self, subject: str) -> None:
        scores = self._scores[subject]
        sessions = self._sessions[subject]

        snapshot = SubjectSnapshot(
            subject=subject,
            avg_score=round(sum(scores) / len(scores), 1) if scores else 0.0,
            total_minutes=sum(s.minutes for s in sessions),
            session_count=len(sessions),
            trend=compute_trend(scores),
        )
        self.publish(TOPIC_SNAPSHOT_OUT, snapshot)
