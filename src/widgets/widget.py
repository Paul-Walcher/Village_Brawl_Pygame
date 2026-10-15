import pygame
from abc import ABC, abstractmethod
from event_queue_manager import EventQueueManager, Event

class Widget(EventQueueManager):

    def __init__(self, frame_dim):
        super().__init__()

        self.x = frame_dim.x
        self.y = frame_dim.y
        self.width = frame_dim.width
        self.height = frame_dim.height
        self.__frame_dim = frame_dim

        self._has_focus = True

    @property
    def frame_dim(self):
        return self.__frame_dim
    @frame_dim.setter
    def frame_dim(self, oframe):

        self.x = oframe.x
        self.y = oframe.y
        self.width = oframe.width
        self.height = oframe.height
        self.__frame_dim = oframe

    @property
    def has_focus(self):
        return self._has_focus

    @has_focus.setter
    def has_focus(self, x):
        if x != self._has_focus:
            self._has_focus = x
            if self._has_focus:
                self.on_focus_gained()
            else:
                self.on_focus_lost()

    def on_focus_gained(self):
        pass

    def on_focus_lost(self):
        pass

    def move_by(self, x=0, y=0, w=0, h=0):

        nframe = pygame.Rect(self.x + x, self.y, self.width + w, self.height + h)
        self.frame_dim = nframe

    def move_to(self, x=None, y=None, w=None, h=None):

        r = pygame.Rect((x if x is not None else self.x),
                        (y if y is not None else self.y),
                        (w if w is not None else self.width),
                        (h if h is not None else self.height))

        self.frame_dim = r

    def focus(self):
        self._has_focus = True

    def unfocus(self):
        self._has_focus = False

    @abstractmethod
    def rerender(self):
        #rendering fresh from 0
        pass

    @abstractmethod
    def render(self):
        #render the surfaces after an update
        pass

    @abstractmethod
    def tick(self):
        #gets called every frame
        pass

    @abstractmethod
    def get_surfaces(self):
        #returns a list of surfaces to render
        pass

    @abstractmethod
    def get_surfaces_with_position(self):
        #returns a list of [(surface, (x, y))]
        pass

    def get_frame_dim(self):
        return self.frame_dim

    def set_frame_dim(self, frame_dim):
        self.frame_rect = frame_dim
