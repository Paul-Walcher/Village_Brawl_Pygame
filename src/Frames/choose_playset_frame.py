from __future__ import annotations
from typing import Any, Callable

import os
import pygame

from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, color_t, R_ID
import graphics
from graphics import page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t
from clock import Clock
from Frames.choose_save_name_frame import ChooseSaveNameFrame
from context_data import ContextData

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.text_slider import TextSlider
from Frames.widgets.label import Label
from Frames.widgets.button import Button

class ChoosePlaysetFrame(Frame):
    """
    This frame lets the player choose the playset.
    """

    #states
    NOTHING_FOCUSED: int = R_ID()
    BACK_OPTION_FOCUSED: int = R_ID()
    PLAYSET_OPTIONS_FOCUSED: int = R_ID()

    def __init__(   self,
                    data: Any = None,
                    frame_dim: pygame.Rect = None,
                    parent_frame: Frame = None,
                    focus_group: str = ""
                    ):

        super().__init__(FrameEnums.CHOOSE_PLAYSET_FRAME, data=data, frame_dim=frame_dim, parent_frame=parent_frame, focus_group=focus_group)

        self.playset_pages: list[page_t] = [[x] for x in os.listdir(PLAYSETS_FOLDER) if os.path.isdir(os.path.join(PLAYSETS_FOLDER, x))]
        """
        Playsets are loaded and put into a list.
        The playsets are loaded via getting the names of all folders at constants.PLAYSETS_FOLDER
        """
        self.playsets_span: int = 1
        """
        The span of the playlists.


        This means there are self.playsets_span rendered on top,
        then the main playset,
        then self.playsets_span again.
        """
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
        #the frames for the headline
        self.headline_frame_width_percentage: float = 1.0
        """
        The width of the headline frame in relation to self.width.
        """
        self.headline_frame_height_percentage: float = 0.4
        """
        The height of the headline frame in relation to self.height.
        """
        self.headline_frame_hmargin: float = 0.2
        """
        The horizontal margin for the headline frame
        """
        self.headline_frame_vmargin: float = 0.1
        """
        The vertical margin for the headline frame.
        """
        self.headline_frame: pygame.Rect = None
        """
        The frame the headline will be rendered into.
        """
        self.headline_text: page_t = ["Choose your", "Playset"]
        """
        The text as a page that will be rendered as the headline.
        """
        self.rendered_headline: rendered_surface_position_tuples_t = None
        """
        The rendered headline.
        """
        self.headline_color: color_t = Colors.CYAN
        """
        The color the headline will be rendered in.
        """
        self.playset_options_frame_width_margin: float = 0.5
        """
        The width of the playset options frame relative to self.width
        """
        self.playset_options_frame_height_margin: float = 0.7
        """
        The height of the playset options frame relative to (self.height - self.headline_frame.height - self.headline_frame.y)
        """
        self.playset_options_frame: pygame.Rect = None
        """
        The frame for the playset options.
        """
        self.text_slider: TextSlider = None
        """
        The text slider showing the playset options.
        """
        self.option_color: color_t = Colors.STANDARD_TEXT_COLOR
        """
        Color for the options
        """
        self.option_selected_color: color_t = Colors.YELLOW
        """
        Color for selected options
        """
        self.state: int = ChoosePlaysetFrame.NOTHING_FOCUSED
        """
        The current state.
        """
        self.intro_delay_clock: Clock = Clock()
        """
        Clock for the intro delay
        """
        self.intro_delay: float = 250#ms
        """
        Delay after the frame is made the main frame.
        """
        self.rerender()

    def rerender(self):


        headline_rect: pygame.Rect = pygame.Rect(
                                                    0,
                                                    0,
                                                    int(self.width * self.headline_frame_width_percentage),
                                                    int(self.height * self.headline_frame_height_percentage)
                                                )

        self.headline_frame = graphics.apply_margins(headline_rect, self.headline_frame_hmargin, self.headline_frame_vmargin)

        self.rendered_headline = graphics.render_page_from_chars(
                                                                    font=Fonts.STANDARD_FONT,
                                                                    page=self.headline_text,
                                                                    frame=self.headline_frame,
                                                                    text_color=self.headline_color,
                                                                    centered=True,
                                                                    vertical_centered=True
                                                                )
        #the text slider
        options_rect: pygame.Rect = self.frame_dim.copy()
        options_rect.y = self.headline_frame.y + self.headline_frame.height
        options_rect.height = self.height - options_rect.y

        self.playset_options_frame = graphics.get_center_with_rect_as_rect(
                                                                                outer_rect=options_rect,
                                                                                inner_rect=pygame.Rect(
                                                                                                            0, 0,
                                                                                                            int(self.playset_options_frame_width_margin * options_rect.width),
                                                                                                            int(self.playset_options_frame_height_margin * options_rect.height)
                                                                                                        )
                                                                            )
        self.text_slider = TextSlider(
                                            text=self.playset_pages,
                                            frame_dim=self.playset_options_frame,
                                            font=Fonts.STANDARD_FONT,
                                            horizontal=False,
                                            cutoff=True,
                                            max_slides=1,
                                            text_span=self.playsets_span,
                                            text_color=self.option_color
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

                                    )
        #changing next_frame
        self._next_frame = None
        #resetting the exit flag
        self.reset_exit_flag()
        #starting the intro delay clock
        self.intro_delay_clock.start()

    def bind_events(self):

        if self.is_focused():
            #adding generic escape callback
            self.add_default_escape_callback()

            self.add_pygame_key_callback(pygame.K_LEFT, None, putback=False, func=self.left_pressed)
            self.add_pygame_key_callback(KeyAlternatives.LEFT_ALTERNATIVE, None, putback=False, func=self.left_pressed)

            self.add_pygame_key_callback(pygame.K_RIGHT, None, putback=False, func=self.right_pressed)
            self.add_pygame_key_callback(KeyAlternatives.RIGHT_ALTERNATIVE, None, putback=False, func=self.right_pressed)

            self.add_pygame_key_callback(pygame.K_UP, None, putback=False, func=self.up_pressed)
            self.add_pygame_key_callback(KeyAlternatives.UP_ALTERNATIVE, None, putback=False, func=self.up_pressed)

            self.add_pygame_key_callback(pygame.K_DOWN, None, putback=False, func=self.down_pressed)
            self.add_pygame_key_callback(KeyAlternatives.DOWN_ALTERNATIVE, None, putback=False, func=self.down_pressed)

            self.add_pygame_key_callback(pygame.K_RETURN, None, putback=False, func=self.enter_pressed)
            self.add_pygame_key_callback(KeyAlternatives.ENTER_ALTERNATIVE, None, putback=False, func=self.enter_pressed)


    def left_pressed(self, event, data) -> None:
        """
        Callback function.
        """
        if self.state == ChoosePlaysetFrame.BACK_OPTION_FOCUSED:
            self.state = ChoosePlaysetFrame.NOTHING_FOCUSED
        elif self.state == ChoosePlaysetFrame.PLAYSET_OPTIONS_FOCUSED:
            self.state = ChoosePlaysetFrame.BACK_OPTION_FOCUSED

    def right_pressed(self, event, data) -> None:
        """
        Callback function.
        """
        if self.state == ChoosePlaysetFrame.NOTHING_FOCUSED:
            self.state = ChoosePlaysetFrame.BACK_OPTION_FOCUSED
        elif self.state == ChoosePlaysetFrame.BACK_OPTION_FOCUSED:
            self.state = ChoosePlaysetFrame.PLAYSET_OPTIONS_FOCUSED

    def up_pressed(self, event, data):
        """
        Callback function
        """
        if self.state == ChoosePlaysetFrame.NOTHING_FOCUSED:
            self.state = ChoosePlaysetFrame.PLAYSET_OPTIONS_FOCUSED
        elif self.state == ChoosePlaysetFrame.PLAYSET_OPTIONS_FOCUSED:
            #sliding
            self.text_slider.slide_down()

    def down_pressed(self, event, data):
        """
        Callback function
        """
        if self.state == ChoosePlaysetFrame.NOTHING_FOCUSED:
            self.state = ChoosePlaysetFrame.PLAYSET_OPTIONS_FOCUSED
        elif self.state == ChoosePlaysetFrame.PLAYSET_OPTIONS_FOCUSED:
            #sliding
            self.text_slider.slide_up()

    def enter_pressed(self, event, data):
        """
        Callback function.
        """
        if self.state == ChoosePlaysetFrame.BACK_OPTION_FOCUSED:
            self._next_frame = self.parent_frame
            self.parent_frame.focus()
            self.parent_frame.rerender()
            self.raise_exit_flag()
        elif self.state == ChoosePlaysetFrame.PLAYSET_OPTIONS_FOCUSED:
            self.text_slider.play_select_animation()

    def tick(self):

        self.manage_pygame_events()

        if self.exit_flag_raised():
            if self._next_frame is not None:
                self._next_frame.focus()
            return self._next_frame

        self.text_slider.tick()

        #getting all events
        for event in self.text_slider.poll_events():
            if event.type == TextSlider.EventTypes.SELECT_ANIMATION_ENDED:

                if type(self.data) == ContextData:
                    self.data.current_playset = self.playset_pages[self.text_slider.get_selected_index()][0]

                    self._next_frame = ChooseSaveNameFrame(data=self.data, frame_dim=self.frame_dim.copy(), parent_frame=self, focus_group=self.focus_group)
                    self.raise_exit_flag()

        return self

    def render(self, screen):

        screen.fill(Colors.BLACK)

        for surface, pos in self.rendered_headline:
            screen.blit(surface, pos)

        if self.state == ChoosePlaysetFrame.BACK_OPTION_FOCUSED:
            for surface, pos in self.selected_back_text_rendered:
                screen.blit(surface, pos)
        else:
            for surface, pos in self.back_text_rendered:
                screen.blit(surface, pos)

        if self.state == ChoosePlaysetFrame.PLAYSET_OPTIONS_FOCUSED:
            pygame.draw.rect(screen, self.option_color, self.playset_options_frame, width=4)

        self.text_slider.render(screen)
