"""
Gamehandler class, handles the gameloop
"""
from __future__ import annotations
from typing import Callable

import pygame
from Frames.frame import Frame

class Gamehandler:
    """
    This class handles the gameloop in run().
    """

    def __init__(self):

        self.screen: pygame.Surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        """
        The screen everything will be rendered onto. Is set to fullscreen.
        """
        self.width, self.height = self.screen.get_size()
        """
        Size of the screen.
        """
        self.running: bool = True
        """
        If the gameloop is running.
        """
        self.current_frame: Frame = None
        """
        References the current frame. Each frame returns its next frame (or itself)
        via Frame.tick()
        """

    def run(self, starting_frame: Frame) -> None:
        """
        This is the main gameloop.
        """
        if starting_frame is None:
            raise RuntimeError("Starting Frame can't be None.")

        self.current_frame = starting_frame

        while self.running:

            frame_back: Frame = self.current_frame.tick()

            if frame_back is None:
                self.running = False
                break

            else:

                self.current_frame = frame_back

            self.current_frame.clear_pygame_events()


            self.screen.fill((0, 0, 0))
            self.current_frame.render(self.screen)
            pygame.display.flip()
