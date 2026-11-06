import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame
import sys
import constants
from gamehandler import Gamehandler
from stack import Stack
from context_data import ContextData
from Frames.frame import Frame
from Frames.intro_frame import IntroFrame
from Frames.test_frame import TestFrame

MOUSE_ENABLE_FLAG: str = "-enable-mouse"
MOUSE_DISABLED_FLAG: str = "-disable-mouse"

__MOUSE_ENABLED__: bool = True
#mouse is enabled by default

if __name__ == "__main__":

    cdir = os.getcwd()
    os.chdir(Path(__file__).resolve().parent.parent)

    pygame.init()

    #checking the arguments
    if MOUSE_ENABLE_FLAG in sys.argv:
        __MOUSE_ENABLED__ = True
    elif MOUSE_DISABLED_FLAG in sys.argv:
        __MOUSE_ENABLED__ = False

    ghandler = Gamehandler()

    sframe = TestFrame(data=None, frame_dim=constants.FULLSCREEN)

    ghandler.run(sframe)
    pygame.quit()

    os.chdir(cdir)
