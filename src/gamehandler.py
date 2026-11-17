"""
Gamehandler class, handles the gameloop
"""
from __future__ import annotations
from typing import Callable

import pygame
from Frames.frame import Frame

import camera

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

        #creating the global camera
        camera.create_global_camera(
                                frame_dim=pygame.Rect(0, 0, self.width, self.height),
                                max_zoom_in_value=camera.Camera.STANDARD_MAX_ZOOM_IN_VALUE,
                                max_zoom_out_value=camera.Camera.STANDARD_MAX_ZOOM_OUT_VALUE
                            )

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

            self.screen.fill((0, 0, 0))
            camera.global_camera.render_surface(
                                            screen=self.screen,
                                            surface=self.current_frame.surface
                                        )

            pygame.display.flip()
