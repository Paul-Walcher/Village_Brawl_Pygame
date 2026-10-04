from abc import ABC, abstractmethod

class Frame(ABC):

    def __init__(self, width, height):

        self.width = width
        self.height = height

    @abstractmethod
    def tick(self):
        #returns the next frame
        pass

    @abstractmethod
    def draw(self, screen):
        pass
