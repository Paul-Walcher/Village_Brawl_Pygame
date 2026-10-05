"""
Gamehandler class, handles the gameloop
"""
import pygame
from Frames.frame_mappings import frame_mappings

class Gamehandler:

    def __init__(self):
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()
        self.running = 1
        self.main_frame = pygame.Rect(0, 0, self.width, self.height)

        self.current_frame = None
        self.frame_enum = None

    def run(self, start_frame):

        self.current_frame = start_frame
        self.frame_enum = start_frame.frame_enum

        while self.running:

            frame_enum, data = self.current_frame.tick()

            if frame_enum is None:
                self.running = False
                break

            if frame_enum != self.frame_enum:

                self.current_frame = frame_mappings[frame_enum](data, self.main_frame)
                self.frame_enum = frame_enum


            self.current_frame.draw(self.screen)
