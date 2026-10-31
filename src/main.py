import pygame
import sys
import constants
from gamehandler import Gamehandler
from stack import Stack
from context_data import ContextData
from Frames.frame import Frame
from Frames.intro_frame import IntroFrame

MOUSE_ENABLE_FLAG: str = "-enable-mouse"
MOUSE_DISABLED_FLAG: str = "-disable-mouse"

__MOUSE_ENABLED__: bool = True
#mouse is enabled by default

if __name__ == "__main__":

    pygame.init()

    #checking the arguments
    if MOUSE_ENABLE_FLAG in sys.argv:
        __MOUSE_ENABLED__ = True
    elif MOUSE_DISABLED_FLAG in sys.argv:
        __MOUSE_ENABLED__ = False

    ghandler = Gamehandler()
    iframe = IntroFrame(
                        data=ContextData(
                                            mouse_enabled=__MOUSE_ENABLED__,
                                            current_playset=None,
                                            current_savefile_name=None,
                                            modules=None
                                        ),
                        frame_dim=pygame.Rect(0, 0, ghandler.width, ghandler.height),
                        focus_group=Frame.STANDARD_FOCUS_GROUP
                        )

    ghandler.run(iframe)
    pygame.quit()
