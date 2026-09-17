"""
agents/predictor.py

PREDICTOR AGENT
---------------
Job: turn "what happened" (Tracker's snapshots) into "what's likely
to happen next." Subscribes to tracker.snapshot, runs a lightweight
forecast + risk classification, and publishes a `Prediction` on
"predictor.prediction" for the Commander to act on.

Swap `classify_risk` / `predict_next_score` in core/tools.py for a
real ML model later -- Predictor's job here (orchestration) doesn't
have to change, only the tool implementation does.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from agents.base_agent import BaseAgent
from core.message_bus import MessageBus
from core.tools import Prediction, classify_risk, predict_next_score

TOPIC_SNAPSHOT_IN = "tracker.snapshot"
TOPIC_PREDICTION_OUT = "predictor.prediction"


class PredictorAgent(BaseAgent):
    def __init__(self, bus: MessageBus) -> None:
        super().__init__(name="Predictor", bus=bus)
        self._score_history: Dict[str, List[float]] = defaultdict(list)

        bus.subscribe(TOPIC_SNAPSHOT_IN, self._on_snapshot)

    def _on_snapshot(self, msg) -> None:
        snapshot = msg.payload
        self._score_history[snapshot.subject].append(snapshot.avg_score)

        next_score = predict_next_score(
            self._score_history[snapshot.subject], snapshot.trend
        )
        risk = classify_risk(snapshot.avg_score, snapshot.trend)

        prediction = Prediction(
            subject=snapshot.subject,
            risk_level=risk,
            predicted_next_score=next_score,
            reasoning=(
                f"avg={snapshot.avg_score}%, trend={snapshot.trend:+.1f}, "
                f"sessions={snapshot.session_count}"
            ),
        )
        self.logger.info(
            "Prediction: %s -> %s (next~%.1f%%)",
            prediction.subject, prediction.risk_level.value, next_score,
        )
        self.publish(TOPIC_PREDICTION_OUT, prediction)
