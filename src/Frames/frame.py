import pygame
from abc import ABC, abstractmethod
from constants import FrameDataID
from event_queue_manager import EventQueueManager, Event
from widgets.widget import Widget

class Frame(EventQueueManager):

    class EventTypes:
        #event types
        EXIT_FRAME = 0 #signal to exit the current frame
        EXIT_PARENT_FRAME = 1

    def __init__(self, frame_enum, data=None, frame_dim=None):

        self.frame_enum = frame_enum
        self.data = (data if data is not None else {})
        if self.data is not None:
            self.data[FrameDataID.CURRENT_FRAME] = self
        self._frame_dim = (frame_dim if frame_dim is not None else pygame.Rect(0, 0, 0, 0))
        self.x = self.frame_dim.x
        self.y = self.frame_dim.y
        self.width = self.frame_dim.width
        self.height = self.frame_dim.height
        self.parent_frame = None
        self.input_blocked = False
        self.shown = True
        self.event_queue = []
        self.subframes_tick_data = {}

        self.center = (self.frame_dim.x + self.frame_dim.w // 2,
                        self.frame_dim.y + self.frame_dim.h // 2
                        )
        self.subframes = []# first subframe has the focus, and is drawn above the others
        self.widgets = [] #own widgets

    @property
    def frame_dim(self):
        return self._frame_dim

    @frame_dim.setter
    def frame_dim(self, oframe):

        self.x = oframe.x
        self.y = oframe.y
        self.width = oframe.width
        self.height = oframe.height
        self.center = (self.x + self.width // 2,
                        self.y + self.height // 2
                        )
        self._frame_dim = oframe

    """
    Use the following functions when changing the frame.
    """

    #event adding functions
    def push_exit_event(self):

        exit_event = Event(
                                    Frame.EventTypes.EXIT_FRAME,
                                    self
                                )
        self.event_queue.append(exit_event)

    def push_parent_exit_event(self):

        exit_event = Event(
                                    Frame.EventTypes.EXIT_PARENT_FRAME,
                                    self
                                )
        self.event_queue.append(exit_event)

    def poll_events_subframes(self):
        return {sframe: sframe.poll_events() for sframe in self.subframes}

    def poll_events_subframes_with_putback(self):
        return {sframe: sframe.poll_events_with_putback() for sframe in self.subframes}

    def poll_events_widgets(self):
        return {w: w.poll_events() for w in self.widgets}

    def poll_events_widgets_with_putback(self):
        return {w: w.poll_events_with_putback() for w in self.widgets}

    def hide(self):
        self.shown = False

    def show(self):
        self.shown = True

    def set_parent_frame(self, pframe):
        self.parent_frame = pframe

    def block_input(self):
        self.input_blocked = True

    def unblock_input(self):
        self.input_blocked = False

    def block_input_all_frames(self, exceptions=None):

        if exceptions is None:
            exceptions = []

        if self not in exceptions:
            self.block_input()

        for sframe in self.subframes:
            if sframe not in exceptions:
                sframe.block_input()

    def unblock_input_all_frames(self, exceptions=None):

        if exceptions is None:
            exceptions = []

        if self not in exceptions:
            self.unblock_input()

        for sframe in self.subframes:
            if sframe not in exceptions:
                sframe.unblock_input()

    def set_frame(self, new_frame_dim):

        self.frame_dim = new_frame_dim

        self.x = self.frame_dim.x
        self.y = self.frame_dim.y
        self.width = self.frame_dim.width
        self.height = self.frame_dim.height

    def adjust_frame(self, frame_offsets):

        self.frame_dim.x += frame_offsets.x
        self.frame_dim.y += frame_offsets.y
        self.frame_dim.width += frame_offsets.width
        self.frame_dim.height += frame_offsets.height

        self.x = self.frame_dim.x
        self.y = self.frame_dim.y
        self.width = self.frame_dim.width
        self.height = self.frame_dim.height


    def position(self, pos):

        #pos is a tuple
        x, y = pos

        return (x + self.frame_dim.x, y + self.frame_dim.y)

    def focus(self, subframe):

        idx = self.subframes.index(subframe)
        sframe = self.subframes.pop(idx)
        self.subframes.insert(0, sframe)

    def remove_subframe(self, subframe):

        idx = self.subframes.index(subframe)
        sframe = self.subframes.pop(idx)

        return sframe

    def add_subframe(self, subframe):

        subframe.set_parent_frame(self)
        self.subframes.insert(0, subframe)


    def subframes_tick(self):
        frames_to_delete = []
        return_data = {}
        for subframe in self.subframes:

            fenum, data = subframe.tick()
            return_data[subframe] = data
            if (fenum is None):
                frames_to_delete.append(subframe)

        for subframe in frames_to_delete:

            self.remove_subframe(subframe)

        return return_data

    def widgets_tick(self):
        for w in self.widgets:
            w.tick()

    def render_subframes(self, screen):
        for subframe in self.subframes[::-1]:
            if subframe.shown:
                subframe.draw(screen)

    def render_widgets(self, screen):
        for widget in self.widgets:
            for w, pos in widget.get_surfaces_with_position():
                screen.blit(w, pos)


    def tick(self):
        #returns the next frame
        self.widgets_tick()
        self.subframes_tick_data = self.subframes_tick()

    def draw(self, screen):
        self.render_widgets(screen)
        self.render_subframes(screen)
