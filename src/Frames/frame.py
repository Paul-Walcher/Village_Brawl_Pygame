from abc import ABC, abstractmethod

class Frame(ABC):

    def __init__(self, frame_enum, width, height, data=None):

        self.frame_enum = frame_enum
        self.width = width
        self.height = height
        self.data = (data if data is not None else {})

    @abstractmethod
    def tick(self):
        #returns the next frame
        pass

    @abstractmethod
    def draw(self, screen):
        pass
