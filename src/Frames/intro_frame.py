from __future__ import annotations
from typing import Callable, Any

import pygame
from constants import Colors
from constants import Fonts, Fontsizes, KeyAlternatives
from constants import SIMAGE, CIMAGE, INTRO_IMAGES
import graphics
from graphics import rendered_surface_position_tuples_t, colored_page_t
from clock import Clock
import random

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.widgets.label import Label
from Frames.intro_menu_frame import IntroMenuFrame


class IntroFrame(Frame):
    """
    This frame shows the intro screen.
    """

    def __init__(self, data: Any = None, frame_dim: pygame.Rect = None, parent_frame: Frame = None, focus_group=""):

        super().__init__(frame_enum=FrameEnums.INTRO_FRAME, data=data,
                            frame_dim=frame_dim, parent_frame=parent_frame, focus_group=focus_group)

        #dividing the frame dimension into the top frame for the headline, and the bottom for the shown image.
        self.headline_height_percentage: float = 0.3
        """
        The percentage of the height the headline occupies.

        --------------
        |            | -> Headline frame
        --------------
        |            | -> Image frame
        |            |
        --------------
        """
        self.image_height_percentage: float = (1.0 - self.headline_height_percentage)
        """
        The remaining height goes to the image.
        """
        self.headline_area: pygame.Rect = None
        """
        The area that belongs to the headline.
        """
        self.headline_frame_hmargin: float = 0.4
        """
        The horizontal margins to apply to the headline frame,
        such that the text is not right at the edges.
        """
        self.headline_frame_vmargin: float = 0.2
        """
        Vertical margins, same purpose as self.headline_frame_hmargin
        """
        self.image_area: pygame.Rect = None
        """
        The area that belongs to the image.
        """
        self.image_frame_hmargin: float = 0.4
        """
        The horizontal margin for the image frame.
        """
        self.image_frame_vmargin: float = 0.1
        """
        The vertical margin for the image frame.
        """
        self.headline_frame: pygame.Rect = None
        """
        The rectangle the headline will be rendered into.
        """
        self.image_frame: pygame.Rect = None
        """
        The rectangle the various images will be rendered into.
        """

        self.headline_increase_percentage: float = 0.25
        """
        At its biggest, the the headline will be rendered into a frame
        that is (1 + self.headline_height_percentage) times the original frame.
        """
        self.headline_clock: Clock = Clock()
        """
        The clock used for changing the headlines size.
        """
        self.headline_animation_duration: float = 2000#ms
        """
        The duration for the headline to expand to full size,
        and go back to normal size.
        """
        self.headline_text: colored_page_t = [[("Village Brawl", Colors.WHITE)]]
        """
        The text that will be shown. Is a page in colored text form.
        """
        self.headline_label: Label = None
        """
        The rendered headline.
        """
        self.press_text_frame: pygame.Rect = None
        """
        The frame for the press text.
        """
        self.press_text_label: Label = None
        """
        Press text label.
        """
        self.image_animation_clock: Clock = Clock()
        """
        The clock for the image animation
        """
        self.image_animation_duration: float = 2000#ms
        """
        Duration for the image animation.
        The image will increase or decrease in alpha.
        """
        self.alpha_increasing: bool = False
        """
        If this is True, the image will be increasing in alpha.
        Otherwise, it will be decreasing.
        """
        self.image: pygame.Surface = None
        """
        The image shown at the center. This is an changing image
        of a list of images chosen randomly from constants.INTRO_IMAGES
        """
        self.image_pos: tuple[int, int] = None
        """
        The position of the image.
        """
        self.enter_intro_menu: bool = False
        """
        If this flag is set tick() returns an IntroMenuFrame
        instance as the next main window.
        """

        self.entry_delay_clock: Clock = Clock()
        """
        Clock for the entry delay.
        since we might have keys pressed when starting this
        application, they might be registered immediately as inputs.
        Therefore we wait a bit before accepting inputs.
        """
        self.entry_delay: float = 250#ms

        #starting all clocks
        self.headline_clock.start()
        self.image_animation_clock.start()
        self.entry_delay_clock.start()

        self.rerender()

    def handle_headline_animation(self) -> None:
        """
        This handles the headline animation.
        Is called once per tick.
        """
        percentage: float = self.headline_clock.elapsed() / self.headline_animation_duration

        if percentage >= 1.0:
            #render onto the normal surface
            self.headline_label = Label(
                                            frame_dim=self.headline_frame,
                                            font=Fonts.STANDARD_FONT,
                                            label_page=self.headline_text,
                                            background_color=Colors.TRANSPARENT
                                        )
            #restart the clock
            self.headline_clock.start()

        else:

            increase_margin: float = 0.0
            """
            The margins for the headline frame increase/decrease.
            """

            if percentage <= 0.5:

                #increase accordingly
                inc_percentage: float = 2 * percentage
                increase_margin = -(self.headline_increase_percentage * inc_percentage)

            else:

                inc_percentage: float = (percentage - 0.5) * 2
                increase_margin = -self.headline_increase_percentage + self.headline_increase_percentage * inc_percentage

            #now applying the margins and rendering
            increased_headline_frame: pygame.Rect = graphics.apply_margins(self.headline_frame, increase_margin, increase_margin)
            #centering the headline frame
            increased_headline_frame = graphics.get_center_with_rect_as_rect(outer_rect=self.headline_area, inner_rect=increased_headline_frame)

            self.headline_label = Label(
                                            frame_dim=increased_headline_frame,
                                            font=Fonts.STANDARD_FONT,
                                            label_page=self.headline_text,
                                            background_color=Colors.TRANSPARENT
                                        )

    def handle_image_animation(self) -> None:
        """
        Handles the images fading in and out
        """

        percentage: float = self.image_animation_clock.elapsed() / self.image_animation_duration

        if percentage >= 1.0:

            #if we were decreasing in alpha, fade in a new image
            if not self.alpha_increasing:

                self.image, self.image_pos = graphics.img_load_and_position(random.choice(INTRO_IMAGES), self.image_frame)
                self.image.set_alpha(0)

            #change alpha increase/decrease direction
            self.alpha_increasing = not self.alpha_increasing
            #restart the clock
            self.image_animation_clock.start()

        else:

            if self.image is None:
                self.image, self.image_pos = graphics.img_load_and_position(random.choice(INTRO_IMAGES), self.image_frame)

            alpha: int = int( (percentage * 255 if self.alpha_increasing else (1.0 - percentage) * 255) )

            self.image.set_alpha(alpha)


    def rerender(self) -> None:
        """
        Renders the frame as it should be as the beginning.
        This resets all render data.
        """
        self.image = None
        self.image_pos = None

        self.headline_label = None
        self.press_text_label = None

        self.headline_area, self.image_area = graphics.split_rect_vertically(self.frame_dim, [self.headline_height_percentage, self.image_height_percentage])
        self.headline_frame = graphics.apply_margins(self.headline_area, self.headline_frame_hmargin, self.headline_frame_vmargin)
        self.image_frame = graphics.apply_margins(self.image_area, self.image_frame_hmargin, self.image_frame_vmargin)
        #centering
        self.headline_frame = graphics.get_center_with_rect_as_rect(self.headline_area, self.headline_frame)
        self.image_frame = graphics.get_center_with_rect_as_rect(self.image_area, self.image_frame)
        self.press_text_frame = pygame.Rect(self.width // 75, self.height - self.height // 20, self.width // 5, self.height // 20)
        self.press_text_label = Label(
                                        frame_dim=self.press_text_frame,
                                        font=Fonts.STANDARD_FONT,
                                        label_page=graphics.str_to_colored_page("Press enter to continue...", Colors.STANDARD_TEXT_COLOR),
                                        background_color=Colors.TRANSPARENT
                                        )

        self.handle_headline_animation()
        self.handle_image_animation()

        self.reset_exit_flag()
        self.entry_delay_clock.start()


    def bind_events(self) -> None:
        """
        Binds the enter events as triggering a transition into the IntroMenuFrame.
        """

        #adding generic escape exit function
        self.add_default_escape_callback()
        self.add_pygame_key_callback(pygame.K_RETURN, None, False, self.enter_pressed)
        self.add_pygame_key_callback(KeyAlternatives.ENTER_ALTERNATIVE, None, False, self.enter_pressed)

    def enter_pressed(self, event: pygame.event.Event, data: Any):
        """
        If the entry delay has already passed, we set the enter intro menu flag to true.
        """

        if self.entry_delay_clock.elapsed() > self.entry_delay:
            self.enter_intro_menu = True


    def tick(self):
        """
        Basic tick function.
        """
        self.manage_pygame_events()

        if self.exit_flag_raised():
            return None

        self.handle_headline_animation()
        self.handle_image_animation()

        if self.enter_intro_menu:

            imframe = IntroMenuFrame(data=self.data, frame_dim=self.frame_dim.copy(), parent_frame=self, focus_group=self.focus_group)
            self.enter_intro_menu = False
            return imframe

        return self

    def render(self, screen: pygame.Surface) -> None:
        """
        Rendering function, see Frame class.
        """

        screen.fill(Colors.BLACK)

        if self.exit_flag_raised():
            return None

        self.headline_label.tick()
        self.press_text_label.tick()

        if self.headline_label is not None:
            self.headline_label.render(screen)

        if self.image is not None:
            screen.blit(self.image, self.image_pos)

        if self.press_text_label is not None:
            self.press_text_label.render(screen)
