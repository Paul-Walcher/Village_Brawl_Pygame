"""
This provides a camera class,
with functions to zoom or move the
shown frame.
"""
from __future__ import annotations
from typing import Type, Any, Callable, override

import pygame

from constants import (
                        fequal,
                        EPSILON,
                        point_t
                        )

import calculations


class Camera:
    """
    This class provides functionality to move around
    the viewport, zoom in and out,
    and get the altered mouse coordinates.
    """

    ABSOLUTE_MAX_ZOOM_IN_VALUE: float = 5.0
    ABSOLUTE_MAX_ZOOM_OUT_VALUE: float = 0.05

    STANDARD_MAX_ZOOM_IN_VALUE: float = 3.0
    STANDARD_MAX_ZOOM_OUT_VALUE: float = 0.2

    def __init__(
                    self,
                    frame_dim: pygame.Rect,
                    max_zoom_in_value: float = 3.0,
                    max_zoom_out_value: float = 0.2
                ):

        #general intialization
        self.frame_dim: pygame.Rect = frame_dim.copy()
        """
        The original frame dimension that this camera manages.
        """
        self._x_offset: float = 0.0
        """
        The x offset for the camera.
        The given surface will be rendered at
        self.frame_dim.x + self._x_offset
        """
        self._y_offset: float = 0.0
        """
        The y offset for the camera.
        The given surface will be rendered at
        self.frame_dim.y + self._y_offset
        """

        #===================================
        # ZOOM
        #===================================

        self._current_zoom: float = 1.0
        """
        The current zoom value.

        The zoom value is the scale by which the final surface will scaled.
        """
        self._max_zoom_in_value: float = max_zoom_in_value
        """
        The maximum amount that can be zoomed in.
        """
        self._max_zoom_out_value: float = max_zoom_out_value
        """
        The maximum amount that can be zoomed out.
        """

        #adjusting the zoom values if they are invalid
        self._check_max_zoom_values()

    def _check_max_zoom_values(self) -> bool:
        """
        Returns True if everything is alright,
        False if any value was invalid and had to be changed.
        """

        valid: bool = True

        if  self._max_zoom_in_value > Camera.ABSOLUTE_MAX_ZOOM_IN_VALUE - EPSILON\
            or self._max_zoom_in_value < 1.0 + EPSILON:
            #invalid
            self._max_zoom_in_value = Camera.STANDARD_MAX_ZOOM_IN_VALUE - 2 * EPSILON
            valid = False

        if  self._max_zoom_out_value < Camera.ABSOLUTE_MAX_ZOOM_OUT_VALUE + EPSILON\
            or self._max_zoom_out_value > 1.0 - EPSILON:
            #invalid
            self._max_zoom_out_value = Camera.STANDARD_MAX_ZOOM_OUT_VALUE + 2 * EPSILON
            valid = False

        return valid

    def _check_current_zoom_value(self) -> bool:
        """
        Returns True if everything is alright,
        False if any value was invalid and had to be changed.
        """

        valid: bool = True

        if self._current_zoom > (self._max_zoom_in_value - EPSILON):

            self._current_zoom = (self._max_zoom_in_value - 2 * EPSILON) #not setting directly to max
            valid = False

        if self._current_zoom < (self._max_zoom_out_value + EPSILON):

            self._current_zoom = (self._max_zoom_out_value + 2 * EPSILON) #not setting directly to max
            valid = False

        return valid


    #===================================
    # GETTER FUNCTIONS
    #===================================

    def get_camera_offsets(self) -> tuple[float, float]:
        """
        Returns the camera offsets
        as (x_offset, y_offset).
        """
        return (self._x_offset, self.y_offset)

    def get_camera_zoom(self) -> float:
        """
        Returns the current zoom value of the camera.
        """
        return self._current_zoom

    def get_camera_max_zoom_in_value(self) -> float:
        """
        Gets the maximum amount that can be zoomed in.
        """
        return self._max_zoom_in_value

    #===================================
    # GENERAL FUNCTIONS
    #===================================

    def reset(self) -> None:
        """
        Resets the camera.
        """
        self._x_offset = 0.0
        self._y_offset = 0.0

        self._current_zoom = 1.0

    def move_to(self, x_offset: float = None, y_offset: float = None) -> None:
        """
        Sets the camera offsets directly to the values.
        If any value is None, this value will stay the same.
        """

        if x_offset is not None:
            self._x_offset = x_offset

        if y_offset is not None:
            self._y_offset = y_offset

    def move_camera(self, x_offset: float = None, y_offset: float = None) -> None:
        """
        Moves the camera by the given offsets.
        """

        if x_offset is not None:
            self._x_offset += x_offset
        if y_offset is not None:
            self._y_offset += y_offset

    def set_zoom(self, zoom_value: float) -> bool:
        """
        Returns if the zoom in operation was successful or not,
        meaning the zoom value was inside the bounds.
        """

        self._current_zoom = zoom_value
        success: bool = self._check_current_zoom_value()

        return success

    def zoom_in(self, value: float) -> bool:
        """
        Zooms in by the absolute value given.
        Returns true on success, False on failure.
        """

        value = abs(value)
        self._current_zoom -= value

        success: bool = self._check_current_zoom_value()

        return success

    def zoom_out(self, value: float) -> bool:
        """
        Zooms out by the absolute value given.
        Returns true on success, False on failure.
        """

        value = abs(value)
        self._current_zoom += value

        success: bool = self._check_current_zoom_value()

        return success

    def zoom_by(self, value: float) -> bool:
        """
        Zooms in/out by the value given.
        """

        self._current_zoom += value

        success: bool = self._check_current_zoom_value()

        return success

    def set_max_zoom_in(self, value: float) -> bool:
        """
        Sets the maximum zoom in value to the given value.
        Returns True on success and False on failure.
        """

        self._max_zoom_in_value = value

        success: bool = self._check_max_zoom_values()

        return success

    def set_max_zoom_out(self, value: float) -> bool:
        """
        Sets the maximum zoom out value to the given value.
        Returns True on success and False on failure.
        """

        self._max_zoom_out_value = value

        success: bool = self._check_max_zoom_values()

        return success

    def render_surface(
                        self,
                        screen: pygame.Surface,
                        surface: pygame.Surface
                        ) -> None:
        """
        Applies all changes, and renders the surface onto the screen.
        """

        x: int = None
        y: int = None
        #x and y starting positions
        x, y = self.frame_dim.x, self.frame_dim.y

        #applying offsets
        x += int(self._x_offset)
        y += int(self._y_offset)

        #scaling the given surface
        if not fequal(self._current_zoom, 1.0):
            #getting sizes
            swidth: int = surface.get_width()
            sheight: int = surface.get_height()

            new_width: int = int(swidth * self._current_zoom)
            new_height: int = int(sheight * self._current_zoom)

            extra_width: int = (new_width - swidth)
            extra_height: int = (new_height - sheight)

            x -= extra_width // 2
            y -= extra_height // 2

            surface = pygame.transform.smoothscale(surface=surface, size=(new_width, new_height))

        screen.blit(surface, (x, y))

    def transform_point(self, point: point_t) -> point_t:
        """
        Transforms the given point from the usual
        screen space into the camera space.
        """

        x: float = None
        y: float = None

        x, y = point

        #positioning x and y relative to the own x and y
        x -= self.frame_dim.x
        y -= self.frame_dim.y

        #now applying the offsets
        x -= self._x_offset
        y -= self._y_offset

        #applying the zoom
        swidth: int = self.frame_dim.width
        sheight: int = self.frame_dim.height

        new_width: float = swidth * self._current_zoom
        new_height: float = sheight * self._current_zoom

        extra_width: float = (new_width - swidth)
        extra_height: float = (new_height - sheight)

        x += extra_width / 2
        y += extra_height / 2

        x /= self._current_zoom
        y /= self._current_zoom


        return (int(x), int(y))

    def get_mouse_position(self) -> point_t:
        """
        Gets the actual mouse position in camera space,
        using the zoom and offset.
        """

        return (self.transform_point(pygame.mouse.get_pos()))

    def viewport(self) -> pygame.Rect:
        """
        Returns the viewport, i.e.
        the rectangle of what is currently rendered.
        """
        x: int = 0
        y: int = 0

        x, y = self.transform_point((self.frame_dim.x, self.frame_dim.y))
        #getting width and height
        width: int = int(self.frame_dim.width / self._current_zoom)
        height: int = int(self.frame_dim.height / self._current_zoom)

        return pygame.Rect(x, y, width, height)

    def point_visible(self, point: point_t) -> bool:
        """
        Checks if a point is inside the viewport.
        """
        return calculations.point_collides(point=point, rect=self.viewport())

    def rect_visible(self, rect: pygame.Rect) -> bool:
        """
        Checks if a rectangle intersects with the viewport.
        """
        return calculations.rect_collides(rect1=rect, rect2=self.viewport())



#creating a usable camera
global_camera: Camera = None

def create_global_camera(
                            frame_dim: pygame.Rect,
                            max_zoom_in_value: float,
                            max_zoom_out_value: float
                            ) -> None:
    """
    Creates the global camera with the arguments give.
    """
    global global_camera

    global_camera = Camera(
                            frame_dim=frame_dim,
                            max_zoom_in_value=max_zoom_in_value,
                            max_zoom_out_value=max_zoom_out_value
                            )
