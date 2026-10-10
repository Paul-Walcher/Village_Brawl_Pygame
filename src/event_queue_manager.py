from abc import ABC, abstractmethod

class Event:

    def __init__(self, type, data):

        self.type = type
        self.data = data

    def copy(self):
        event = Event(self.type, self.data)
        return event

class EventQueueManager(ABC):

    def __init__(self):
        self.event_queue = []

    def push_event(self, event):
        self.event_queue.append(event)

    def poll_events(self):
        back = self.event_queue
        self.event_queue = []
        return back

    def poll_events_with_putback(self):
        return [event.copy() for event in self.event_queue]
