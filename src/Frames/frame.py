import pygame
from abc import ABC, abstractmethod

class Frame(ABC):

    def __init__(self, frame_enum, width, height, data=None, frame=None):

        self.frame_enum = frame_enum
        self.width = width
        self.height = height
        self.data = (data if data is not None else {})
        self.frame = (frame if frame is not None else pygame.Rect(0, 0, width, height))

        self.center = (self.frame.x + self.frame.w // 2,
                        self.frame.y + self.frame.h // 2
                        )

    @abstractmethod
    def tick(self):
        #returns the next frame
        pass

    @abstractmethod
    def draw(self, screen):
        pass
