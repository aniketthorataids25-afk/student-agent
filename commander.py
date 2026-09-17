"""
agents/commander.py

COMMANDER AGENT
---------------
Job: the decision-maker. Subscribes to predictor.prediction, and for
every subject decides what should actually happen -- generate a
study-plan item, and optionally raise an alert for at-risk subjects.
This is the only agent that produces the final, human-facing output.

In a real deployment, `_raise_alert` might message a parent/teacher
via email/SMS/Slack; that's intentionally left as a stub so you can
wire in whatever notification channel you use.
"""

from __future__ import annotations

from typing import List

from agents.base_agent import BaseAgent
from core.message_bus import MessageBus
from core.tools import Prediction, RiskLevel, StudyPlanItem, llm_generate_study_plan

TOPIC_PREDICTION_IN = "predictor.prediction"
TOPIC_PLAN_OUT = "commander.plan_item"
TOPIC_ALERT_OUT = "commander.alert"

_PRIORITY_BY_RISK = {
    RiskLevel.AT_RISK: 1,
    RiskLevel.WATCH: 2,
    RiskLevel.ON_TRACK: 3,
}
_MINUTES_BY_RISK = {
    RiskLevel.AT_RISK: 45,
    RiskLevel.WATCH: 25,
    RiskLevel.ON_TRACK: 15,
}


class CommanderAgent(BaseAgent):
    def __init__(self, bus: MessageBus) -> None:
        super().__init__(name="Commander", bus=bus)
        self.plan: List[StudyPlanItem] = []

        bus.subscribe(TOPIC_PREDICTION_IN, self._on_prediction)

    def _on_prediction(self, msg) -> None:
        prediction: Prediction = msg.payload

        action = llm_generate_study_plan(prediction)
        item = StudyPlanItem(
            subject=prediction.subject,
            action=action,
            minutes_recommended=_MINUTES_BY_RISK[prediction.risk_level],
            priority=_PRIORITY_BY_RISK[prediction.risk_level],
        )
        self.plan.append(item)
        self.publish(TOPIC_PLAN_OUT, item)

        if prediction.risk_level == RiskLevel.AT_RISK:
            self._raise_alert(prediction)

    def _raise_alert(self, prediction: Prediction) -> None:
        alert = (
            f"ALERT: {prediction.subject} is AT RISK "
            f"(predicted next score {prediction.predicted_next_score}%). "
            f"{prediction.reasoning}"
        )
        self.logger.warning(alert)
        self.publish(TOPIC_ALERT_OUT, alert)

    def ordered_plan(self) -> List[StudyPlanItem]:
        """
        Final study plan: one entry per subject (the most recent
        assessment wins, since Commander receives a fresh prediction
        every time new activity comes in), highest priority first.
        """
        latest_by_subject = {item.subject: item for item in self.plan}
        return sorted(latest_by_subject.values(), key=lambda item: item.priority)

    def print_report(self) -> None:
        print("\n" + "=" * 60)
        print("  STUDY PLAN  (Commander's final report)")
        print("=" * 60)
        for item in self.ordered_plan():
            print(f"[P{item.priority}] {item.subject} "
                  f"({item.minutes_recommended} min)")
            print(f"       -> {item.action}")
        print("=" * 60 + "\n")
