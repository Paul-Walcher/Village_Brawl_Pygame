from __future__ import annotations
from typing import Any, Callable

import pygame

from Frames.frame import Frame
from Frames.widgets.label import Label
from Frames.frame_enums import FrameEnums

import graphics
from graphics import text_t, colored_text_t, page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t

from constants import color_t, R_ID, Fonts, Colors
from event_queue_manager import Event
from clock import Clock

class Button(Label):
    """
    Button Widget.

    Used doing button pressed and calling functions.
    """

    PRESSED_ANIMATION_PLAYING = R_ID()

    class ButtonPressFinishedEvent(Event):
        def __init__(self, callback_result: Any):

            Event.__init__(self, Button.EventTypes.BUTTON_PRESS_FINISHED, data=callback_result)

            self.callback_result: Any = callback_result

        def copy(self):
            copy_event: ButtonPressFinishedEvent = ButtonPressFinishedEvent(self.callback_result)
            return copy_event

    class EventTypes:
        BUTTON_PRESS_FINISHED: int = R_ID()

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

                button_page: colored_page_t = None, #the text renderd onto self.frame_dim, as colored text
                selected_button_page: colored_page_t = None, #the text for the page when it is selected

                background_image_path: str = None, #the image used as a background.
                selected_background_image_path: str = None, #the image used as background in the selected state

                callback_func: Callable[[Any], Any] = lambda x: None, #the callback function called when pressed

                background_color: color_t = Colors.TRANSPARENT, #the background color, visible if no image was given.
                selected_background_color: color_t = Colors.TRANSPARENT, #the background color for when the button is selected

                image_scaling_function: Callable[[pygame.Surface, tuple[int, int]], pygame.Surface] \
                                        = pygame.transform.smoothscale, #the function for scaling the image

                press_animation_size_decrease: float= 0.5, #how much the frame descreases in size during the press animation
                press_animation_duration: float = 400#ms


                ):

        Label.__init__(
                        self,
                        frame_dim=frame_dim,
                        hmargin=hmargin,
                        vmargin=vmargin,
                        text_hmargin=text_hmargin,
                        text_vmargin=text_vmargin,
                        text_selected_hmargin=text_selected_hmargin,
                        text_selected_vmargin=text_selected_vmargin,

                        font=font,
                        label_page=button_page,
                        selected_label_page=selected_button_page,
                        background_image_path=background_image_path,
                        selected_background_image_path=selected_background_image_path,
                        background_color=background_color,
                        selected_background_color=selected_background_color,
                        image_scaling_function=image_scaling_function
                        )

        self.frame_enum = FrameEnums.BUTTON_WIDGET
        """
        Setting the frame enum.
        """


        self.callback_func: Callable[[Any], Any] = callback_func
        """
        The function that is called afer press() is finished animating.
        """
        self.callback_argument: Any = None
        """
        The callback argument, callback func is called like: self.callback_func(self.callback_argument).
        When calling press() you can specify a callback argument.
        """
        self.press_animation_size_decrease: float = press_animation_size_decrease
        """
        By how much percentage the press animation decreases the button surface.
        """
        self.press_animation_duration: float = press_animation_duration
        """
        The duration for the press animation.
        """
        self.press_animation_clock: Clock = Clock()
        """
        The clock for keeping track of the press animation.
        """
        self.button_selected_surface_copy: pygame.Rect = None
        """
        Copy for when the button surface gets changed during the pressed animation.
        """
        self._press_queued: bool = False
        """
        If a press input is queued.
        """

        self.rerender()


    def press_animation_playing(self) -> bool:
        """
        Returns whether the press animation is playing or not.
        """
        return (self.state == Button.PRESSED_ANIMATION_PLAYING)

    def selected(self) -> bool:
        """
        Returns whether the button is selected.
        """
        return (self.state == Button.SELECTED) or self.press_animation_playing()

    def press(self, callback_argument: Any = None) -> bool:
        """
        Presses the button and plays the animation.
        Returns True on success, False if a press is already queued, or a press animation is playing.
        """
        if self._press_queued or self.state == Button.PRESSED_ANIMATION_PLAYING:
            return False
        else:
            self._press_queued = True
            self.callback_argument = callback_argument
            return True

    def initialize_pressed_animation(self) -> None:
        """
        Initializes the pressed animation.
        """

        #setting state
        self.state = Button.PRESSED_ANIMATION_PLAYING
        #prerendering
        self.prerender()
        #copying the current surface
        self.button_selected_surface_copy = self.label_selected_surface.copy()
        #starting the timer
        self.press_animation_clock.start()

    def render_pressed_animation(self) -> None:
        """
        Renders the pressed animation.
        """
        percentage: float = self.press_animation_clock.elapsed() / self.press_animation_duration

        if percentage >= 1.0:
            self.finalize_pressed_animation()
        else:

            if percentage <= 0.5:

                P = percentage * 2
                new_size_p: float = 1.0 - (P * self.press_animation_size_decrease)

                self.label_selected_surface = graphics.scale_surface(
                                                                        self.button_selected_surface_copy,
                                                                        scale=new_size_p,
                                                                        scale_function=pygame.transform.smoothscale
                                                                        )
            else:

                P = (percentage - 0.5) * 2
                new_size_p: float = (1.0 - self.press_animation_size_decrease) + (P * self.press_animation_size_decrease)

                self.label_selected_surface = graphics.scale_surface(
                                                                        self.button_selected_surface_copy,
                                                                        scale=new_size_p,
                                                                        scale_function=pygame.transform.smoothscale
                                                                        )

    def finalize_pressed_animation(self) -> None:
        """
        Finalizes the press animation, then executes self.callback_func.
        """

        callback_result: Any = None
        #calling the callback function
        if self.callback_func is not None:
            callback_result = self.callback_func(self.callback_argument)
        #resetting the callback argument
        self.callback_argument = None
        #adding the button press finished event
        self.push_event(Button.ButtonPressFinishedEvent(callback_result=callback_result))
        self.state = Button.SELECTED

        self.label_selected_surface = self.button_selected_surface_copy
        self.label_selected_surface_copy = None
        self.prerender()


    def tick(self) -> Frame:
        """
        Renders the animation if it is playing.
        """

        #checking for queued input
        if self._press_queued:
            self._press_queued = False
            self.initialize_pressed_animation()

        if self.state == Button.PRESSED_ANIMATION_PLAYING:
            self.render_pressed_animation()

        return self

    def render(self, screen) -> None:

        if self.selected():
            #surface offset
            x_off, y_off = (self.width - self.label_selected_surface.get_width()) // 2, (self.height - self.label_selected_surface.get_height()) // 2
            screen.blit(self.label_selected_surface, (self.x + x_off, self.y + y_off))
        else:
            x_off, y_off = (self.width - self.label_not_selected_surface.get_width()) // 2, (self.height - self.label_not_selected_surface.get_height()) // 2
            screen.blit(self.label_not_selected_surface, (self.x + x_off, self.y + y_off))
