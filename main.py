"""
main.py

Wires the three agents onto one MessageBus and runs a simulated
week of student activity end-to-end:

    raw activity -> Tracker -> Predictor -> Commander -> study plan

Run it with:
    python main.py
"""

from __future__ import annotations

import logging

from agents.commander import CommanderAgent
from agents.predictor import PredictorAgent
from agents.tracker import TrackerAgent
from core.message_bus import MessageBus
from core.tools import QuizResult, StudySession


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)-24s | %(message)s",
        datefmt="%H:%M:%S",
    )


def simulate_week(tracker: TrackerAgent) -> None:
    """Feed Tracker a week's worth of realistic, messy student data."""

    # Math: declining -- should end up AT_RISK
    for score in (82, 74, 65, 58):
        tracker.record_quiz(QuizResult(subject="Math", score_pct=score))
    tracker.record_session(StudySession(subject="Math", minutes=30, focus_rating=2))

    # Physics: stable, healthy -- should end up ON_TRACK
    for score in (88, 90, 87, 91):
        tracker.record_quiz(QuizResult(subject="Physics", score_pct=score))
    tracker.record_session(StudySession(subject="Physics", minutes=40, focus_rating=4))

    # History: mild dip -- should end up WATCH
    for score in (80, 78, 74, 73):
        tracker.record_quiz(QuizResult(subject="History", score_pct=score))
    tracker.record_session(StudySession(subject="History", minutes=20, focus_rating=3))


def main() -> None:
    configure_logging()

    bus = MessageBus()
    tracker = TrackerAgent(bus)
    PredictorAgent(bus)                  # subscribes itself to the bus
    commander = CommanderAgent(bus)      # subscribes itself to the bus

    simulate_week(tracker)

    commander.print_report()
    print(f"Total messages exchanged on the bus: {len(bus.history)}")


if __name__ == "__main__":
    main()
