import pygame
from gamehandler import Gamehandler
from Frames.intro_frame import IntroFrame
from stack import Stack
from context_data import ContextData
from Frames.frame import Frame


if __name__ == "__main__":
    pygame.init()


    ghandler = Gamehandler()

    iframe = IntroFrame(
                        data=ContextData(),
                        frame_dim=pygame.Rect(0, 0, ghandler.width, ghandler.height),
                        focus_group=Frame.STANDARD_FOCUS_GROUP
                        )

    ghandler.run(iframe)
    pygame.quit()
