import os
import pygame
import threading

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import (
    PLAYSETS_FOLDER,
    Colors,
    Fonts,
    Fontsizes,
    KeyAlternatives,
    FrameDataID
)
import graphics
from clock import Clock
from modules import Modules
import constants

from event_queue_manager import EventQueueManager, Event
from widgets.widget import Widget

class Cardlist(Widget):

    def __init__(self, frame_dim):
        super().__init__(frame_dim)

    def tick(self):
        pass

    def get_surfaces(self):
        pass

    def get_surfaces_with_positions(self):
        pass

    def rerender(self):
        pass

    def render(self):
        pass
