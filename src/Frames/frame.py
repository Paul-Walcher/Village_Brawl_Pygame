import pygame
from abc import ABC, abstractmethod
from constants import FrameDataID

class Frame(ABC):

    def __init__(self, frame_enum, data=None, frame_dim=None):

        self.frame_enum = frame_enum
        self.data = (data if data is not None else {})
        if self.data is not None:
            self.data[FrameDataID.CURRENT_FRAME] = self
        self.frame_dim = (frame_dim if frame_dim is not None else pygame.Rect(0, 0, 0, 0))
        self.parent_frame = None
        self.input_blocked = False

        self.x, self.y, self.width, self.height = 0, 0, 0, 0
        self.recalculate_dimensions()

        self.center = (self.frame_dim.x + self.frame_dim.w // 2,
                        self.frame_dim.y + self.frame_dim.h // 2
                        )
        self.subframes = []# first subframe has the focus, and is drawn above the others

    """
    Use the following functions when changing the frame.
    """

    def recalculate_dimensions(self):

        self.x = self.frame_dim.x
        self.y = self.frame_dim.y
        self.width = self.frame_dim.width
        self.height = self.frame_dim.height


    def set_parent_frame(self, pframe):
        self.parent_frame = pframe

    def block_input(self):
        self.input_blocked = True

    def unblock_input(self):
        self.input_blocked = False

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

        self.subframes.insert(0, subframe)


    @abstractmethod
    def tick(self):
        #returns the next frame
        pass

    @abstractmethod
    def draw(self, screen):
        pass
