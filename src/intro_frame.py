import pygame
from frame import Frame
from constants import Colors

class IntroFrame(Frame):

    def __init__(self, width, height):
        super().__init__(width, height)

    def tick(self):

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_ESCAPE]):
            return None

        return self

    def draw(self, screen):

        screen.fill(Colors.BLACK)
        pygame.display.flip()
