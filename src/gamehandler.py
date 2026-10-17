"""
Gamehandler class, handles the gameloop
"""
import pygame

class Gamehandler:

    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        self.running = 1
        self.main_frame = pygame.Rect(0, 0, self.width, self.height)

        self.current_frame = None

    def run(self, start_frame):

        self.current_frame = start_frame

        while self.running:

            frame_back = self.current_frame.tick()

            if frame_back is None:
                self.running = False
                break

            else:

                self.current_frame = frame_back


            self.screen.fill((0, 0, 0))
            self.current_frame.render(self.screen)
            pygame.display.flip()
