import pygame
from gamehandler import Gamehandler
from Frames.intro_frame import IntroFrame
from stack import Stack
from context_data import ContextData


if __name__ == "__main__":
    pygame.init()


    ghandler = Gamehandler()

    iframe = IntroFrame(ContextData(), pygame.Rect(0, 0, ghandler.width, ghandler.height))

    ghandler.run(iframe)
    pygame.quit()
