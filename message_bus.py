"""
core/message_bus.py

A minimal, dependency-free publish/subscribe message bus.
This is the "nervous system" that lets Tracker, Predictor, and
Commander talk to each other without knowing about one another
directly (loose coupling -> easy to test, easy to extend).
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, DefaultDict, List

logger = logging.getLogger("student_agents.bus")


@dataclass
class Message:
    """Envelope for every piece of data that moves between agents."""

    topic: str
    sender: str
    payload: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<Message topic={self.topic!r} from={self.sender!r}>"


Subscriber = Callable[[Message], None]


class MessageBus:
    """
    Simple synchronous pub/sub bus.

    Agents call `subscribe(topic, handler)` to listen, and
    `publish(topic, sender, payload)` to broadcast. Swap this
    class out for Redis/Kafka/RabbitMQ later without touching
    any agent code, since agents only ever talk to the bus.
    """

    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, List[Subscriber]] = defaultdict(list)
        self._history: List[Message] = []

    def subscribe(self, topic: str, handler: Subscriber) -> None:
        logger.debug("Subscribing handler to topic=%s", topic)
        self._subscribers[topic].append(handler)

    def publish(self, topic: str, sender: str, payload: Any) -> Message:
        msg = Message(topic=topic, sender=sender, payload=payload)
        self._history.append(msg)
        logger.info("PUBLISH %-18s <- %s", topic, sender)

        for handler in self._subscribers.get(topic, []):
            handler(msg)

        return msg

    @property
    def history(self) -> List[Message]:
        """Full audit trail of everything said on the bus."""
        return list(self._history)
