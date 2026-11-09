from __future__ import annotations
from typing import Callable, Any


from abc import ABC, abstractmethod

class Event:
    """
    Generic Event class. Contains a type and the
    data for the event.
    """

    def __init__(self, etype: int, data: Any):

        self.type: int = etype
        """
        Identifier for the event.
        """
        self.data: Any = data
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

    def __init__(self, max_events_queued: int = 25):

        self._event_queue: list[Event] = []
        """
        The event queue. Contains all current events that were not polled.
        """
        self.event_queue_active: bool = True
        """
        If the event queue is active.
        """
        self._max_events_queued: int = max_events_queued
        """
        The maximum amount of events saved in the events queue.
        If a new event is pushed while len(self._event_queue) == self.max_events_queued,
        the oldest event gets removed.
        """

    def max_events_queued(self) -> int:
        """
        Returns the number of events queued.
        """
        return self._max_events_queued

    def set_max_events_queued(self, max_events_queued: int) -> bool:
        """
        Sets the number of events queued.

        Returns None if the number given is invalid.
        """

        if max_events_queued <= 0:
            #invalid input
            return False
        else:
            self._max_events_queued = max_events_queued
            return True

    def push_event(self, event: Event) -> list[Event]:
        """
        Adds an event to the event queue, if the queue is active.

        Returns a list of dropped events if any where dropped at all.
        """

        events_dropped: list[Event] = []

        if self.event_queue_active:
            self._event_queue.append(event)

            while (len(self._event_queue) >= self._max_events_queued):
                dropped_event: Event = self._event_queue.pop(0)
                events_dropped.append(dropped_event)


        return events_dropped

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

    def deactivate_event_queue(self) -> None:
        """
        Deactivates the even queue. clears the event queue,
        then discards all future event pushed until the queue is reactivated.
        """
        self._event_queue = []
        self.event_queue_active = False

    def activate_event_queue(self) -> None:
        """
        Reactivates the event queue.
        """
        self.event_queue_active = True
