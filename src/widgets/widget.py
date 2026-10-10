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
        self._frame_dim = frame_dim

    @property
    def frame_dim(self):
        return self._frame_dim
    @frame_dim.setter
    def frame_dim(self, oframe):

        self.x = oframe.x
        self.y = oframe.y
        self.width = oframe.width
        self.height = oframe.height
        self_frame_dim = oframe



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
