import pygame
from gamehandler import Gamehandler
from Frames.intro_frame import IntroFrame
from stack import Stack
from constants import FrameDataID

pygame.init()


ghandler = Gamehandler()

data = {FrameDataID.STACK: Stack()}
iframe = IntroFrame(data, pygame.Rect(0, 0, ghandler.width, ghandler.height))

ghandler.run(iframe)

pygame.quit()
