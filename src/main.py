import pygame
from gamehandler import Gamehandler
from intro_frame import IntroFrame

pygame.init()

ghandler = Gamehandler()
iframe = IntroFrame(ghandler.width, ghandler.height)

ghandler.run(iframe)

pygame.quit()
