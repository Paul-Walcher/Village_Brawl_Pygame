import pygame
from abc import ABC, abstractmethod
from constants import FrameDataID

class Frame(ABC):

    def __init__(self, frame_enum, data=None, frame=None):

        self.frame_enum = frame_enum
        self.data = (data if data is not None else {})
        if self.data is not None:
            self.data[FrameDataID.CURRENT_FRAME] = self
        self.frame = (frame if frame is not None else pygame.Rect(0, 0, 0, 0))
        self.parent_frame = None
        self.input_blocked = False
        self.x = self.frame.x
        self.y = self.frame.y
        self.width = self.frame.width
        self.height = self.frame.height

        self.center = (self.frame.x + self.frame.w // 2,
                        self.frame.y + self.frame.h // 2
                        )
        self.subframes = []# first subframe has the focus, and is drawn above the others

    """
    Use the following functions when changing the frame.
    """

    def set_parent_frame(self, pframe):
        self.parent_frame = pframe

    def block_input(self):
        self.input_blocked = True

    def unblock_input(self):
        self.input_blocked = False

    def set_frame(self, new_frame):

        self.frame = new_frame

        self.x = self.frame.x
        self.y = self.frame.y
        self.width = self.frame.width
        self.height = self.frame.height

    def adjust_frame(self, frame_offsets):

        self.frame.x += frame_offsets.x
        self.frame.y += frame_offsets.y
        self.frame.width += frame_offsets.width
        self.frame.height += frame_offsets.height

        self.x = self.frame.x
        self.y = self.frame.y
        self.width = self.frame.width
        self.height = self.frame.height


    def position(self, pos):

        #pos is a tuple
        x, y = pos

        return (x + self.frame.x, y + self.frame.y)

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
