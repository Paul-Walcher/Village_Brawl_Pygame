"""
Gamehandler class, handles the gameloop
"""
import pygame

class Gamehandler:

    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()

        self.running = 1

        self.current_frame = None

    def run(self, start_frame):

        self.current_frame = start_frame

        while self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.current_frame = self.current_frame.tick()

            if self.current_frame is None:
                self.running = False
                break

            self.current_frame.draw(self.screen)
