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
from modules import Modules

from Frames.frame import Frame
from Frames.intro_frame import IntroFrame
from Frames.widgets.renderable_card_listviewer import RenderableCardListviewer
from Frames.show_explorer_starting_cards_frame import ShowExplorerStartingCardsFrame

from playsets.example_playset.enums import ExplorerEnums

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

    explorer_enum = ExplorerEnums.BASIC_EXPLORER

    cdata = ContextData()
    cdata.mouse_enabled = __MOUSE_ENABLED__
    cdata.current_playset = "example_playset"
    cdata.modules = Modules.load_playset(cdata.current_playset)

    sframe = ShowExplorerStartingCardsFrame(
                                                explorer_enum=explorer_enum,
                                                data=cdata,
                                                frame_dim=constants.FULLSCREEN
                                            )

    ghandler.run(sframe)
    pygame.quit()

    os.chdir(cdir)
