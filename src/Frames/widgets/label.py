from __future__ import annotations
from typing import Any, Callable

import pygame

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums

import graphics
from graphics import text_t, colored_text_t, page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t

from constants import color_t, R_ID, Fonts, Colors
from event_queue_manager import Event
from clock import Clock

class Label(Frame):
    """
    Button Widget.

    Used doing button pressed and calling functions.
    """

    #states
    NOT_SELECTED: int = R_ID()
    SELECTED: int = R_ID()

    def __init__(
                self,
                frame_dim: pygame.Rect, #the frame dimension

                hmargin: float = 0.0, #the horizontal margin
                vmargin: float = 0.0, #the vertical margin
                text_hmargin: float = 0.2, #the horizontal margin for the text inside the button
                text_vmargin: float = 0.1, #the vertical margin for the text inside the button.
                text_selected_hmargin: float = 0.1, #margin for when the text is selected
                text_selected_vmargin: float = 0.05, #margin for when the text is selected.


                font: pygame.font.Font = Fonts.STANDARD_FONT, #used for the text

                label_page: colored_page_t = None, #the text renderd onto self.frame_dim, as colored text
                selected_label_page: colored_page_t = None, #the text for the page when it is selected

                background_image_path: str = None, #the image used as a background.
                selected_background_image_path: str = None, #the image used as background in the selected state

                background_color: color_t = Colors.TRANSPARENT, #the background color, visible if no image was given.
                selected_background_color: color_t = Colors.TRANSPARENT, #the background color for when the button is selected

                image_scaling_function: Callable[[pygame.Surface, tuple[int, int]], pygame.Surface] \
                                        = pygame.transform.smoothscale #the function for scaling the image
                ):

        Frame.__init__(
                        self,
                        frame_enum=FrameEnums.LABEL_WIDGET,
                        data=None,
                        frame_dim=frame_dim,
                        focus_group=None
                        )

        self.hmargin: float = hmargin
        """
        The horizontal margin applied when rendering the label.
        """
        self.vmargin: float = vmargin
        """
        The vertical margin applied when rendering the label.
        """
        self.text_hmargin: float = text_hmargin
        """
        The horizontal margin for placing text inside self.inner_frame_dim.
        """
        self.text_vmargin: float = text_vmargin
        """
        The vertical margin for placing text inside self.inner_frame_dim.
        """
        self.text_selected_hmargin: float = text_hmargin
        """
        The horizontal margin for placing text inside self.inner_frame_dim when self.state == Label.SELECTED or Label.PRESSED_ANIMATION_PLAYING.
        """
        self.text_selected_vmargin: float = text_vmargin
        """
        The vertical margin for placing text inside self.inner_frame_dim when self.state == Label.SELECTED or Label.PRESSED_ANIMATION_PLAYING.
        """
        self.inner_frame_dim: pygame.Rect = None
        """
        The frame dimension after applying hmargin and vmargin.
        """
        self.inner_text_frame_dim: pygame.Rect = None
        """
        The inner rect after applying self.text_hmargin and self.text_vmargin to self.inner_frame_dim.
        """
        self.relative_inner_text_frame_dim: pygame.Rect = None
        """
        The inner text frame dim relative to self.inner_frame_dim.
        """
        self.inner_selected_text_frame_dim: pygame.Rect = None
        """
        The inner rect after applying self.text_hmargin and self.text_vmargin to self.inner_frame_dim when selected.
        """
        self.relative_inner_selected_text_frame_dim: pygame.Rect = None
        """
        The inner text frame dim relative to self.inner_frame_dim when selected.
        """
        self.font = font
        """
        The font used for the text.
        """
        self.label_page: colored_page_t = label_page
        """
        The text as calculated pages
        """
        self.label_page_rendered: rendered_surface_position_tuples_t = None
        """
        The label page rendered.
        """
        self.selected_label_page: colored_page_t = selected_label_page
        """
        The colored text for when the label is selected.
        """
        self.selected_label_page_rendered: rendered_surface_position_tuples_t = None
        """
        The rendered text for when the label is selected.
        """
        self.background_image_path: str = background_image_path
        """
        path to the background image, shown when the label is in not selected state
        """
        self.background_image_rendered: pygame.Surface = None
        """
        The rendered background image. Is stretched to self.frame_dim witn image_scaling_function.
        """
        self.selected_background_image_path: str = selected_background_image_path
        """
        The path to the background for the selected background image.
        """
        self.selected_background_image_rendered: pygame.Surface = None
        """
        The rendered background image for when the label is selected.
        """
        self.background_color: color_t = background_color
        """
        The background color for when no image is shown and the label is not selected.
        """
        self.selected_background_color: color_t = (selected_background_color if selected_background_color is not None else background_color)
        """
        background color for when the label is selected.
        """
        self.image_scaling_function: Callable[[pygame.Surface, tuple[int, int]], pygame.Surface]\
                                     = image_scaling_function
        """
        The function used for scaling the background image.
        """
        self.label_not_selected_surface: pygame.Surface = None
        """
        Surface for when the label is not selected.
        """
        self.label_selected_surface: pygame.Surface = None
        """
        The surface for when the label is selected
        """
        self.state: int = Label.NOT_SELECTED
        """
        The state of the label.
        """

        self.rerender()

    def rerender(self) -> None:
        """
        Rerendering.
        """

        #dimension calculations
        self.inner_frame_dim = graphics.apply_margins(self.frame_dim, self.hmargin, self.vmargin)
        self.inner_text_frame_dim = graphics.apply_margins(self.inner_frame_dim, self.text_hmargin, self.text_vmargin)
        self.inner_selected_text_frame_dim = graphics.apply_margins(self.inner_frame_dim, self.text_selected_hmargin, self.text_selected_vmargin)
        #relative text frame dim to the inner frame
        self.relative_inner_text_frame_dim = self.inner_text_frame_dim.copy()
        self.relative_inner_text_frame_dim.x -= self.inner_frame_dim.x
        self.relative_inner_text_frame_dim.y -= self.inner_frame_dim.y

        self.relative_inner_selected_text_frame_dim = self.inner_selected_text_frame_dim.copy()
        self.relative_inner_selected_text_frame_dim.x -= self.inner_frame_dim.x
        self.relative_inner_selected_text_frame_dim.y -= self.inner_frame_dim.y
        #creating the surfaces
        self.label_not_selected_surface = pygame.Surface(
                                                            (self.inner_frame_dim.width, self.inner_frame_dim.height),
                                                            pygame.SRCALPHA
                                                            )

        self.label_selected_surface = pygame.Surface(
                                                        (self.inner_frame_dim.width, self.inner_frame_dim.height),
                                                        pygame.SRCALPHA
                                                        )

        #creating the image surfaces
        if self.background_image_path is not None:
            self.background_image_rendered = graphics.render_image(
                                                                    img_path=self.background_image_path,
                                                                    dimensions=(self.inner_frame_dim.width, self.inner_frame_dim.height),
                                                                    scaling_function=self.image_scaling_function
                                                                    )
            #copying for selected background
            self.selected_background_image_rendered = self.background_image_rendered.copy()

        if self.selected_background_image_path is not None:
            self.selected_background_image_rendered = graphics.render_image(
                                                                    img_path=self.selected_background_image_path,
                                                                    dimensions=(self.inner_frame_dim.width, self.inner_frame_dim.height),
                                                                    scaling_function=self.image_scaling_function
                                                                    )

        #rendering the text
        if self.label_page is not None:
            self.label_page_rendered = graphics.render_page_from_chars_color(  font=self.font,
                                                                                page=self.label_page,
                                                                                frame=self.relative_inner_text_frame_dim,
                                                                                text_color=Colors.STANDARD_TEXT_COLOR,
                                                                                centered=True,
                                                                                vertical_centered=True,
                                                                                line_margin_as_percentage=0.02
                                                                                )

            self.selected_label_page_rendered = graphics.copy_rendered_surface_position_tuples(self.label_page_rendered)

        if self.selected_label_page is not None:
            self.selected_label_page_rendered = graphics.render_page_from_chars_color( font=self.font,
                                                                                        page=self.selected_label_page,
                                                                                        frame=self.relative_inner_selected_text_frame_dim,
                                                                                        text_color=Colors.STANDARD_TEXT_COLOR,
                                                                                        centered=True,
                                                                                        vertical_centered=True,
                                                                                        line_margin_as_percentage=0.02
                                                                                        )

        #prerendering
        self.prerender()

    def prerender(self) -> None:
        """
        Rendering without recalculating every position.
        """
        fill_color: color_t = (self.selected_background_color if self.selected() else self.background_color)

        self.label_not_selected_surface.fill(fill_color)
        self.label_selected_surface.fill(fill_color)

        if self.background_image_rendered is not None:
            self.label_not_selected_surface.blit(self.background_image_rendered, (0, 0))
        if self.label_page_rendered is not None:
            for surface, position in self.label_page_rendered:
                self.label_not_selected_surface.blit(surface, position)

        if self.selected_background_image_rendered is not None:
            self.label_selected_surface.blit(self.selected_background_image_rendered, (0, 0))
        if self.selected_label_page_rendered is not None:
            for surface, position in self.selected_label_page_rendered:
                self.label_selected_surface.blit(surface, position)

    def select(self) -> None:
        """
        Makes this labels state selected if it was not before.
        """
        if self.state == Label.NOT_SELECTED:
            self.state = Label.SELECTED
            self.prerender()

    def unselect(self) -> None:
        """
        Makes this lebels state unselected if is currently unselected.
        if the press animation is playing this does nothing.
        """
        if self.state == Label.SELECTED:
            self.state = Label.NOT_SELECTED
            self.prerender()

    def selected(self) -> bool:
        """
        Returns whether the label is selected.
        """
        return (self.state == Label.SELECTED)


    def tick(self) -> Frame:
        """
        Does nothing.
        """
        return self

    def render(self, screen) -> None:

        if self.selected():
            screen.blit(self.label_selected_surface, (self.x, self.y))
        else:
            screen.blit(self.label_not_selected_surface, (self.x, self.y))
