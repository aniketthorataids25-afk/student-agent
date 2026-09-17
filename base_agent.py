"""
agents/base_agent.py

Common scaffolding every agent shares: a name, a reference to the
bus, and a logger. Subclasses just wire up subscriptions in
`__init__` and implement whatever handler methods they need.
"""

from __future__ import annotations

import logging
from abc import ABC

from core.message_bus import MessageBus


class BaseAgent(ABC):
    def __init__(self, name: str, bus: MessageBus) -> None:
        self.name = name
        self.bus = bus
        self.logger = logging.getLogger(f"student_agents.{name.lower()}")

    def publish(self, topic: str, payload) -> None:
        self.bus.publish(topic=topic, sender=self.name, payload=payload)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<{self.__class__.__name__} name={self.name!r}>"
