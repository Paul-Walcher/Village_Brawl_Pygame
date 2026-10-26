from __future__ import annotations
from typing import Callable


from abc import ABC, abstractmethod

class Event:
    """
    Generic Event class. Contains a type and the
    data for the event.
    """

    def __init__(self, etype, data):

        self.type: int = etype
        """
        Identifier for the event.
        """
        self.data = data
        """
        Data for the event.
        """

    def copy(self) -> Event:
        """
        Returns a copy of this event.
        Self.data will be passed by reference.
        """
        event: Event = Event(self.type, self.data)
        return event

class EventQueueManager(ABC):
    """
    Parent class for classes that manage internal events.
    """

    def __init__(self):
        self._event_queue: list[Event] = []
        """The event queue. Contains all current events that were not polled."""

    def push_event(self, event: Event) -> None:
        """
        Adds an event to the event queue.
        """
        self._event_queue.append(event)

    def poll_events(self) -> None:
        """
        Returns a list of all current events.
        This also empties the event queue.
        """
        back: list[Event] = self._event_queue
        self._event_queue = []
        return back

    def poll_events_with_putback(self) -> None:
        """
        Returns a copied list of the current events,
        without clearing the queue.
        """
        return [event.copy() for event in self._event_queue]
