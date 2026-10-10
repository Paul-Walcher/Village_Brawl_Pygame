import pygame
from abc import ABC, abstractmethod
from event_queue_manager import EventQueueManager, Event

class Widget(EventQueueManager):

    def __init__(self, frame_rect):
        super().__init__()

        self.frame_rect = frame_rect


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

    def get_frame_rect(self):
        return self.frame_rect

    def set_frame_rect(self, frame_rect):
        self.frame_rect = frame_rect
