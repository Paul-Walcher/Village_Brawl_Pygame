from __future__ import annotations
from typing import Any, Callable


import pygame
from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from constants import color_t, Colors, Fonts, Fontsizes, KeyAlternatives, R_ID
import graphics
from graphics import rendered_surface_position_tuples_t
from clock import Clock
import time

from Frames.choose_playset_frame import ChoosePlaysetFrame

class IntroMenuFrame(Frame):
    """
    Shows the intro Menu.

    The intro menu is structured like this:

        New Game
        Load Save

    Back
    """


    """
    The different states for this frame.
    """
    NOTHING_FOCUSED: int = R_ID()
    MAIN_OPTIONS_FOCUSED: int = R_ID()
    BACK_OPTION_FOCUSED: int = R_ID()


    def __init__(self,
                data: Any = None,
                frame_dim: pygame.Rect = None,
                parent_frame: Frame = None,
                focus_group: str = ""
                ):

        super().__init__(FrameEnums.INTRO_MENU_FRAME, data, frame_dim, parent_frame, focus_group=focus_group)

        self.main_text_frame_width_percentage: float = 0.25
        """
        The width of the frame of the main text options as a percentage of self.width.
        """
        self.main_text_frame_height_percentage: float = 0.5
        """
        The height of the frame of main text options as a percentage of self.height
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
        self.main_text_frame: pygame.Rect = None
        """
        The centered main text rect inside self.frame_dim.
        Contains the main options.
        """
        self.back_text_frame: pygame.Rect = None
        """
        The back text frame at the bottom left.
        """
        self.back_text_selected_frame: pygame.Rect = None
        "The frame for the back text when it is selected."


        self.text_options: list[ tuple[ str, Callable[[], None] ] ] =   [
                                                                            ("New Game", self.new_game_pressed),
                                                                            ("Load Save", self.load_save_pressed)
                                                                        ]
        """
        The text options, as a tuple of
        (name, callback function),
        where callback function is executed when the option is pressed.
        """
        self.option_box_hmargin: float = 0.1
        """
        The margin for a option box inside self.main_text_frame.
        """
        self.option_box_vmargin: float = 0.05
        """
        The margin for a option box inside self.main_text_frame.
        """
        self.option_box_size_increase: float = 0.1
        """
        The size increase for an option box that is selected
        """
        self.option_boxes: list[pygame.Rect] = None
        """
        The inner option boxes, with the margins already applied.
        """
        self.selected_option_boxes: list[pygame.Rect] = None
        """
        Option boxes when an option is selected
        """
        self.options_rendered: list[rendered_surface_position_tuples_t] = None
        """
        The options actually rendered.
        Rendering is done in self.rerender()
        """
        self.selected_options_rendered: list[rendered_surface_position_tuples_t] = None
        """
        The options rendered as selected options.
        Rendering is done in self.rerender().
        """
        self.back_text: str = "Back"
        """
        The text for the back option.
        """
        self.back_text_callback: Callback[[], None] = self.back_pressed
        """
        The callback function for what should happen when self.back is pressed.
        """
        self.back_text_rendered: rendered_surface_position_tuples_t = None
        """
        The back text rendered.
        """
        self.selected_back_text_rendered: rendered_surface_position_tuples_t = None
        """
        Rendered text when the back option is selected.
        """
        self.text_options_index: int = 0
        """
        The index of the currently selected option.
        If no option is selected it is set to 0.
        """
        self.next_frame: Frame = None
        """
        The next frame that is returned from self.tick,
        when self.exit_flag_raised() == True.
        """
        self.state: int = IntroMenuFrame.NOTHING_FOCUSED
        """
        Current state.
        """
        self.option_color: color_t = Colors.STANDARD_TEXT_COLOR
        """
        The standard color for an option when it is not selected
        """
        self.option_selected_color: color_t = Colors.YELLOW
        """
        The color for when an option is selected.
        """
        self.intro_delay_clock: Clock = Clock()
        """
        Clock for intro delay, so that no inputs willbe picked up when reentering
        """
        self.intro_delay: float = 250#ms
        """
        The delay for the intro.
        """
        self.rerender()

    def rerender(self) -> None:
        """
        Calculates the rect positions and prerenders the texts.
        State gets not reset, so a user coming back to this frame can
        see his last selection.
        """

        self.text_options_index = 0

        self.back_text_frame_margin = min(  int(self.width * self.back_text_frame_margin_percentage),
                                            int(self.height * self.back_text_frame_margin_percentage)
                                        )
        #the distance from the corner for the back text

        self.main_text_frame = graphics.get_center_with_rect_as_rect(
                                                                    outer_rect=self.frame_dim,
                                                                    inner_rect=pygame.Rect( 0, 0,
                                                                                            int(self.width * self.main_text_frame_width_percentage),
                                                                                            int(self.height * self.main_text_frame_height_percentage)
                                                                                            )
                                                                    )
        #main frame for the main options
        self.back_text_frame = pygame.Rect(
                                            self.back_text_frame_margin,
                                            self.height - self.back_text_frame_margin - int(self.height * self.back_text_frame_height_percentage),
                                            int(self.width * self.back_text_frame_width_percentage),
                                            int(self.height * self.back_text_frame_height_percentage)
                                            )
        #the frame for the 'back' text
        self.back_text_selected_frame = graphics.apply_margins(
                                                                self.back_text_frame,
                                                                -self.back_text_size_increase_percentage,
                                                                -self.back_text_size_increase_percentage
                                                                )
        #frame for selected back option
        self.option_boxes = list(
                                map(
                                        lambda rect: graphics.apply_margins(
                                                                                rect,
                                                                                self.option_box_hmargin,
                                                                                self.option_box_vmargin
                                                                            ),

                                        graphics.split_rect_vertically(
                                                                            self.main_text_frame,
                                                                            [1.0 / len(self.text_options)] * len(self.text_options)

                                                                        )

                                    )
                                )
        #the inner option boxes
        self.selected_option_boxes = list(
                                        map(
                                                    lambda rect: graphics.apply_margins(
                                                                                            rect,
                                                                                            -self.option_box_size_increase,
                                                                                            -self.option_box_size_increase
                                                                                        ),

                                                    self.option_boxes
                                            )
                                    )
        #the frames for the selected options

        #now rendering the texts
        self.options_rendered = [
                                    graphics.render_page_from_chars(
                                                                        font=Fonts.STANDARD_FONT,
                                                                        page=[self.text_options[i][0]],
                                                                        frame=self.option_boxes[i],
                                                                        text_color=self.option_color,
                                                                        centered=True,
                                                                        vertical_centered=True
                                                                    )
                                    for i in range(len(self.text_options))
                                ]

        self.selected_options_rendered = [
                                                graphics.render_page_from_chars(
                                                                                    font=Fonts.STANDARD_FONT,
                                                                                    page=[self.text_options[i][0]],
                                                                                    frame=self.selected_option_boxes[i],
                                                                                    text_color=self.option_selected_color,
                                                                                    centered=True,
                                                                                    vertical_centered=True
                                                                                )
                                                for i in range(len(self.text_options))
                                            ]

        self.back_text_rendered = graphics.render_page_from_chars(
                                                                    font=Fonts.STANDARD_FONT,
                                                                    page=[self.back_text],
                                                                    frame=self.back_text_frame,
                                                                    text_color=self.option_color,
                                                                    centered=True,
                                                                    vertical_centered=True
                                                                    )
        self.selected_back_text_rendered = graphics.render_page_from_chars(
                                                                            font=Fonts.STANDARD_FONT,
                                                                            page=[self.back_text],
                                                                            frame=self.back_text_selected_frame,
                                                                            text_color=self.option_selected_color,
                                                                            centered=True,
                                                                            vertical_centered=True

                                                                            )
        #changing next_frame
        self.next_frame = None
        #resetting the exit flag
        self.reset_exit_flag()
        #starting the intro delay clock
        self.intro_delay_clock.start()


    def new_game_pressed(self) -> None:
        """
        If new game is pressed, make a new choose playset frame,
        then raise the exit flag.
        """
        self.next_frame = ChoosePlaysetFrame(data=self.data, frame_dim=self.frame_dim.copy(), parent_frame=self, focus_group=self.focus_group)
        self.raise_exit_flag()

    def load_save_pressed(self) -> None:
        """
        Not implemented yet.
        """
        pass

    def back_pressed(self) -> None:
        """
        Back is pressed, means go back to parent frame.
        """
        self.next_frame = self.parent_frame
        self.next_frame.rerender()
        self.raise_exit_flag()


    def bind_events(self) -> None:
        """
        Binding the events.
        """

        if self.is_focused():

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
        Callback
        """

        if self.state == IntroMenuFrame.BACK_OPTION_FOCUSED:
            self.state = IntroMenuFrame.NOTHING_FOCUSED
        elif self.state == IntroMenuFrame.MAIN_OPTIONS_FOCUSED:
            self.state = IntroMenuFrame.BACK_OPTION_FOCUSED

    def right_pressed(self, event, data) -> None:
        """
        Callback
        """

        if self.state == IntroMenuFrame.NOTHING_FOCUSED:
            self.state = IntroMenuFrame.BACK_OPTION_FOCUSED
        elif self.state == IntroMenuFrame.BACK_OPTION_FOCUSED:
            self.state = IntroMenuFrame.MAIN_OPTIONS_FOCUSED

    def up_pressed(self, event, data) -> None:
        """
        Callback
        """

        if self.state == IntroMenuFrame.NOTHING_FOCUSED:
            self.state = IntroMenuFrame.MAIN_OPTIONS_FOCUSED
        elif self.state == IntroMenuFrame.MAIN_OPTIONS_FOCUSED:
            self.text_options_index -= 1
            self.text_options_index %= len(self.text_options)


    def down_pressed(self, event, data) -> None:
        """
        Callback
        """

        if self.state == IntroMenuFrame.NOTHING_FOCUSED:
            self.state = IntroMenuFrame.MAIN_OPTIONS_FOCUSED
        elif self.state == IntroMenuFrame.MAIN_OPTIONS_FOCUSED:
            self.text_options_index += 1
            self.text_options_index %= len(self.text_options)

    def enter_pressed(self, event, data) -> None:
        """
        Callback
        """
        if self.state == IntroMenuFrame.BACK_OPTION_FOCUSED:
            self.back_text_callback()
        elif self.state == IntroMenuFrame.MAIN_OPTIONS_FOCUSED:
            #calling the callback
            self.text_options[self.text_options_index][1]()



    def tick(self) -> None:
        """
        Overwritten from Frame class.
        """
        if self.intro_delay_clock.elapsed() > self.intro_delay:
            self.manage_pygame_events()

        if self.exit_flag_raised():
            self.next_frame.focus()
            return self.next_frame

        return self

    def render(self, screen: pygame.Surface) -> None:
        """
        Overwritten from Frame class.
        """

        screen.fill(Colors.BLACK)

        renderables: list[rendered_surface_position_tuples_t] = []

        if self.state == IntroMenuFrame.BACK_OPTION_FOCUSED:
            renderables.append(self.selected_back_text_rendered)
        else:
            renderables.append(self.back_text_rendered)

        for i in range(len(self.text_options)):

            if self.state == IntroMenuFrame.MAIN_OPTIONS_FOCUSED and i == self.text_options_index:
                renderables.append(self.selected_options_rendered[i])
            else:
                renderables.append(self.options_rendered[i])

        for rspt in renderables:
            for surface, position in rspt:
                screen.blit(surface, position)
