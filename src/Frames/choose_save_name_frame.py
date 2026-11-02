from __future__ import annotations
from typing import Any, Callable

import os
import pygame

from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, R_ID
import graphics
from graphics import text_t, colored_text_t, page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t
from clock import Clock

from context_data import ContextData

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.load_playset_frame import LoadPlaysetFrame
from Frames.widgets.label import Label
from Frames.widgets.button import Button
from Frames.widgets.text_input import TextInput

class ChooseSaveNameFrame(Frame):
    """
    This frame lets the player choose the name for the savefile.
    """
    #states
    NOTHING_FOCUSED: int = R_ID()
    BACK_OPTION_FOCUSED: int = R_ID()
    TEXTINPUT_FOCUSED: int = R_ID()

    def __init__(self, data: Any = None, frame_dim: pygame.Rect = None, parent_frame: Frame = None, focus_group: str = ""):

        super().__init__(FrameEnums.CHOOSE_SAVE_NAME_FRAME, data=data, frame_dim=frame_dim, parent_frame=parent_frame, focus_group=focus_group)

        self.back_text_frame_width_percentage: float = 0.15
        """
        The width percentage of the back option relative to self.width.
        """
        self.back_text_frame_height_percentage: float = 0.08
        """
        The height percentage of the back option relative to self.height.
        """
        self.back_text_frame_margin_percentage: float = 0.04
        """
        The percentage of the distance from the left bottom corner.
        The margin is taking relative to min(self.width, self.height)
        """
        self.back_text_frame_margin: int = -1
        """
        The distance to the bottom left corner of self.dim for the back etxt frame.
        """
        self.back_text_size_increase_percentage: float = 0.1
        """
        The percentage the framesize increases by when the back option is selected.
        """
        self.back_text_frame: pygame.Rect = None
        """
        The back text frame at the bottom left.
        """
        self.back_button: Button = None
        """
        The back button.
        """
        self.back_color: color_t = Colors.STANDARD_TEXT_COLOR
        """
        Unselected back color.
        """
        self.selected_back_color: color_t = Colors.YELLOW
        """
        Selected back color.
        """

        #textinput
        self.text_input_width_percentage: float = 0.5
        """
        width of the text input relative to self.width.
        """
        self.text_input_height_percentage: float = 0.15
        """
        height of the text input relative to self.height
        """
        self.text_input_frame: pygame.Rect = None
        """
        The frame for the text input
        """
        self.text_input: TextInput = None
        """
        The text input
        """

        self.highlighted_index = -1
        self.is_typing = False

        self.savefile_name = ""
        self.max_name_length = 20

        self.savefile_name_font = None
        self.savefile_name_font_pos = None

        self.enter_text = None
        self.enter_pos = None

        self.headline = None
        self.headline_pos = None


        self.go_back_flag = False
        self.load_playset_flag = False

        #the state
        self.state: int = ChooseSaveNameFrame.NOTHING_FOCUSED
        """
        current state.
        """
        self.intro_delay_clock: Clock = Clock()
        """
        The intro delay clock.
        """
        self.intro_delay: float = 250#ms
        """
        The intro delay.
        """

        self.rerender()

    def rerender(self):
        """
        rerendering.
        """

        self.frame_rect = pygame.Rect(0, 0, self.width, self.height)

        #creating the text input
        text_input_width: int = int(self.text_input_width_percentage * self.width)
        text_input_height: int = int(self.text_input_height_percentage * self.height)

        self.text_input_frame = pygame.Rect(0, 0, text_input_width, text_input_height)
        self.text_input_frame = graphics.get_center_with_rect_as_rect(self.frame_dim, self.text_input_frame)

        self.text_input = TextInput(
                                        frame_dim=self.text_input_frame,
                                        parent_frame=self,
                                        focus_group=self.focus_group,
                                        font=Fonts.STANDARD_FONT,
                                        text_color=Colors.BLACK,
                                        background_color=Colors.WHITE,
                                        cursor_color=Colors.BLACK
                                    )
        #back text
        self.back_text_frame_margin = min(  int(self.width * self.back_text_frame_margin_percentage),
                                            int(self.height * self.back_text_frame_margin_percentage)
                                        )
        #the distance from the corner for the back text
        #main frame for the main options
        self.back_text_frame = pygame.Rect(
                                            self.back_text_frame_margin,
                                            self.height - self.back_text_frame_margin - int(self.height * self.back_text_frame_height_percentage),
                                            int(self.width * self.back_text_frame_width_percentage),
                                            int(self.height * self.back_text_frame_height_percentage)
                                            )
        #rendering the back text
        self.back_button = Button(
                                    frame_dim=self.back_text_frame,
                                    font=Fonts.STANDARD_FONT,
                                    button_page=graphics.str_to_colored_page(text="Back", text_color=self.back_color),
                                    selected_button_page=graphics.str_to_colored_page(text="Back", text_color=self.selected_back_color),
                                    callback_func=self.back_pressed,
                                    background_color=Colors.TRANSPARENT
                                    )

        self.intro_delay_clock.start()





    def bind_events(self):

        if self.is_focused():

            self.add_pygame_key_callback(pygame.K_ESCAPE, None, putback=False, func=self.escape_pressed)

            self.add_pygame_key_callback(pygame.K_LEFT, None, putback=False, func=self.left_pressed)
            self.add_pygame_key_callback(KeyAlternatives.LEFT_ALTERNATIVE, None, putback=False, func=self.left_pressed)

            self.add_pygame_key_callback(pygame.K_RIGHT, None, putback=False, func=self.right_pressed)
            self.add_pygame_key_callback(KeyAlternatives.RIGHT_ALTERNATIVE, None, putback=False, func=self.right_pressed)

            self.add_pygame_key_callback(pygame.K_RETURN, None, putback=False, func=self.enter_pressed)
            self.add_pygame_key_callback(KeyAlternatives.ENTER_ALTERNATIVE, None, putback=False, func=self.enter_pressed)





    def escape_pressed(self, event, data):

        if self.state == ChooseSaveNameFrame.TEXTINPUT_FOCUSED:
            self.focus()
            self.state = ChooseSaveNameFrame.NOTHING_FOCUSED
        else:
            return Frame.EventCallback.EXIT


    def left_pressed(self, event, data):

        if self.state == ChooseSaveNameFrame.BACK_OPTION_FOCUSED:
            self.back_button.unselect()
            self.state = ChooseSaveNameFrame.NOTHING_FOCUSED
        elif self.state == ChooseSaveNameFrame.NOTHING_FOCUSED:
            self.state = ChooseSaveNameFrame.BACK_OPTION_FOCUSED
            self.back_button.select()

    def right_pressed(self, event, data):

        if self.state == ChooseSaveNameFrame.BACK_OPTION_FOCUSED:
            self.back_button.unselect()
            self.text_input.focus()
            self.state = ChooseSaveNameFrame.TEXTINPUT_FOCUSED
        elif self.state == ChooseSaveNameFrame.NOTHING_FOCUSED:

            self.state = ChooseSaveNameFrame.BACK_OPTION_FOCUSED
            self.back_button.select()

    def enter_pressed(self, event, data):
        pass

    def back_pressed(self, data):
        self._next_frame = self.parent_frame
        self.raise_exit_flag()

    def tick(self):

        if self.intro_delay_clock.elapsed() > self.intro_delay:
            self.manage_pygame_events()

        if self.exit_flag_raised():
            if self._next_frame is not None:
                self._next_frame.focus()
                self._next_frame.rerender()
            return self._next_frame

        self.back_button.tick()
        self.text_input.tick()

        #polling events
        for event in self.text_input.poll_events():
            if event.type == TextInput.EventTypes.UNFOCUSED:
                self.focus()
                self.state = ChooseSaveNameFrame.NOTHING_FOCUSED

        return self

    def render(self, screen):

        screen.fill(Colors.BLACK)

        self.back_button.render(screen)
        self.text_input.render(screen)
