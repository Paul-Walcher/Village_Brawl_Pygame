from __future__ import annotations
from typing import Any, Type, Callable, override

import os
import pygame
import threading


from Frames.cardinfo_frame import CardinfoFrame
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, Alpha, IIMAGE, STANDARD_BACKSIDES, R_ID
import graphics
from graphics import page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t
from clock import Clock
from modules import Modules
import constants

from templates.explorer_template import Explorer_Template, ExplorerInfo

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
from Frames.empty_frame import EmptyFrame
from Frames.test_frame import TestFrame
from Frames.show_explorer_starting_cards_frame import ShowExplorerStartingCardsFrame
from Frames.widgets.textbox import Textbox
from Frames.widgets.image_slider import ImageSlider
from Frames.widgets.text_slider import TextSlider
from Frames.widgets.labeled_image_slider import LabeledImageSlider

from context_data import ContextData

class ExplorerInfoFrame(Frame):
    """
    Frame that displays a explorers info, but not just the standard info
    but also all starting cards.
    """

    NO_FOCUS: int = R_ID()
    DESCRIPTION_FOCUSED: int = R_ID()
    MENU_FOCUSED: int = R_ID()

    def __init__(
                    self,
                    explorer_enum: int,
                    data: Any = None,
                    frame_dim: pygame.Rect = None,
                    parent_frame: Frame = None,
                    focus_group: str = "",
                    has_focus: bool = True
                ):

        super().__init__(
                            frame_enum=FrameEnums.CHOOSE_EXPLORER_FRAME,
                            data=data,
                            frame_dim=frame_dim,
                            parent_frame=parent_frame,
                            focus_group=focus_group,
                            has_focus=has_focus

                        )

        self.explorer_enum: int = explorer_enum
        """
        The explorer identifier of the explorer this info frame
        displays info about.
        """
        self.modules: Modules = None
        """
        Modules reference.
        """
        if type(self.data) == ContextData:
            self.modules = self.data.modules


        self.explorer_ref: Type(Explorer_Template) = self.modules.mappings.explorer_mappings[self.explorer_enum]
        """
        Reference to the explorer class.
        """
        self.explorer_info: ExplorerInfo = self.explorer_ref.info()
        """
        Information about the explorer.
        """
        self.focused_outline_size_p: float = 0.005
        """
        Size of the outline displayed if the slider is focused.
        Relative to min(self.width, self.height)
        """
        self.focused_outline_size: int = -1
        """
        Actual size of the outline.
        """
        self.textbox_outline_size_p: float = 0.05
        """
        Outline for the textbox
        """

        self.icon_imgs: list[str] = [
                                        IIMAGE("Deck_Icon.png"), IIMAGE("Supporter_Icon.png"),
                                        IIMAGE("Item_Icon.png"), IIMAGE("Blueprint_Icon.png"),
                                        IIMAGE("Pack_Icon.png"), IIMAGE("Villager_Icon.png"),
                                        IIMAGE("Terrain_Icon.png")
                                    ]
        """
        Paths to the icon images for self.slider_menu.
        """
        self.image_labels: list[str] = [
                                        "Cards",
                                        "Supporters",
                                        "Items",
                                        "Blueprints",
                                        "Packs",
                                        "Villagers",
                                        "Terrain"
                                        ]
        """
        Labels for the images in self.slider_menu.
        """
        self.slider_labels: list[colored_page_t] = None
        """
        The slider labels, these are the image labels rendered as colored pages.
        """
        self.full_hmargin: float = 0.2
        """
        horizontal margin for the inner frame.
        """
        self.full_vmargin: float = 0.1
        """
        vertical margin for the inner frame
        """
        self.dividing_percentages: list[float] = [
                                                    0.75, #the info frame
                                                    0.05, #distance to the slider
                                                    0.2   #the slider frame
                                                    ]
        """
        percentages used to split the inner frame into:

        Info Frame (standard info text)
        Distance between Info frame and slider.
        Slider Frame.
        """
        self.inner_frame: pygame.Rect = None
        """
        The inner frame, into which everything will be rendered.
        """
        self.info_page_frame: pygame.Rect = None
        """
        Frame for rendering the standard info.
        """
        self.divider_frame: pygame.Rect = None
        """
        Frame to divide info_page_frame and slider_frame.
        """
        self.slider_frame: pygame.Rect = None
        """
        Frame for the slider.
        """
        self.slider_border_frame: pygame.Rect = None
        """
        The rect being outlined when self.slider_menu is focused.
        """
        self.full_image_shown: bool = False
        """
        Whether the full image is shown or not.
        """
        self.state: int = ExplorerInfoFrame.NO_FOCUS
        """
        Current state.
        """
        self.info_page_parts: ExplorerInfo.InfoPagePartContainer = None
        """
        The info page parts for the standard cardinfo.
        """
        self.textbox: Textbox = None
        """
        Reference to the textbox belonging to the info page parts.
        """
        self.slider_menu: LabeledImageSlider = None
        """
        The own slider menu.
        """
        self.intro_delay: float = 100#ms
        """
        The delay after rerender() has been called.
        """
        self.intro_delay_clock: Clock = Clock()
        """
        clock for the intro delay.
        """
        self.current_subframe: Frame = None
        """
        The current subframe
        """
        self.half_frame: pygame.Rect = None
        """
        The half frame, that shows the information half
        """
        self.half_surface: pygame.Surface = None
        """
        Surface for the half surface.
        """
        #rendering
        self.rerender()

    @override
    def rerender(self):

        self.half_frame = pygame.Rect(self.width // 2, 0, self.width // 2, self.height)
        self.half_surface = pygame.Surface((self.half_frame.width, self.half_frame.height), pygame.SRCALPHA)

        #getting outline size
        self.focused_outline_size = int(min(self.half_frame.width, self.half_frame.height) * self.focused_outline_size_p)

        #getting the explorer ref and info
        self.explorer_ref = self.modules.mappings.explorer_mappings[self.explorer_enum]
        self.explorer_info = self.explorer_ref.info()

        #text for the labeled image slider rendered as colored pages
        self.slider_labels = [
                                graphics.str_to_colored_page(x, Colors.WHITE) for x in self.image_labels
                                ]

        #calculating inner frame
        self.inner_frame = graphics.apply_margins(pygame.Rect(0, 0, self.half_frame.width, self.half_frame.height), self.full_hmargin, self.full_hmargin)
        self.info_page_frame, self.divider_frame, self.slider_frame = graphics.split_rect_vertically(self.inner_frame, self.dividing_percentages)
        self.slider_border_frame = self.slider_frame.copy()

        #centering the slider frame
        self.slider_frame = graphics.apply_margins(self.slider_frame, 0.1, 0.1)
        self.slider_frame = graphics.get_center_with_rect_as_rect(outer_rect=self.slider_border_frame, inner_rect=self.slider_frame)

        #getting the info page parts
        self.info_page_parts = self.explorer_info.get_info_page_parts(
                                                                        frame_dim=self.info_page_frame,
                                                                        hmargin=0.0,
                                                                        vmargin=0.0
                                                                        )
        #getting the textbox reference
        self.textbox = self.info_page_parts.textbox
        self.textbox.set_outline_size(0)

        #creating the slider
        self.slider_menu = LabeledImageSlider(
                                                self.slider_frame,
                                                text_pages=self.slider_labels,
                                                images=self.icon_imgs,
                                                text_location=LabeledImageSlider.BOTTOM,
                                                max_slides=3
                                                )

        #prerender
        self.prerender()

        self.intro_delay_clock.start()

    @override
    def bind_events(self) -> None:

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

            self.add_pygame_key_callback(pygame.K_ESCAPE, None, putback=False, func=self.escape_pressed)
            self.add_pygame_key_callback(KeyAlternatives.BACK_KEY, None, putback=False, func=self.escape_pressed)

            self.add_pygame_event_callback(pygame.KEYDOWN, None, False, self.keydown)
            self.add_pygame_event_callback(pygame.KEYUP, None, False, self.keyup)

    def escape_pressed(self, event: pygame.event.Event, data: Any) -> None:
        """
        Just raises the exit flag, returns None in self.tick().
        """
        self.raise_exit_flag()

    def left_pressed(self, event: pygame.event.Event, data: Any) -> None:

        if self.state == ExplorerInfoFrame.NO_FOCUS:
            self.state = ExplorerInfoFrame.DESCRIPTION_FOCUSED
            self.textbox.set_outline_size(self.textbox_outline_size_p)
            self.prerender()
        elif self.state == ExplorerInfoFrame.DESCRIPTION_FOCUSED:
            self.textbox.prev_page()
            self.prerender()
        elif self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.slider_menu.slide_right()

        return Frame.EventCallback.SUCCESS

    def right_pressed(self, event: pygame.event.Event, data: Any) -> None:

        if self.state == ExplorerInfoFrame.NO_FOCUS:
            self.state = ExplorerInfoFrame.DESCRIPTION_FOCUSED
            self.textbox.set_outline_size(self.textbox_outline_size_p)
            self.prerender()
        elif self.state == ExplorerInfoFrame.DESCRIPTION_FOCUSED:
            self.textbox.next_page()
            self.prerender()
        elif self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.slider_menu.slide_left()

        return Frame.EventCallback.SUCCESS

    def up_pressed(self, event: pygame.event.Event, data: Any) -> None:

        if self.state == ExplorerInfoFrame.NO_FOCUS or self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.state = ExplorerInfoFrame.DESCRIPTION_FOCUSED
            self.textbox.set_outline_size(self.textbox_outline_size_p)
            self.prerender()

        return Frame.EventCallback.SUCCESS

    def down_pressed(self, event: pygame.event.Event, data: Any) -> None:

        if self.state == ExplorerInfoFrame.NO_FOCUS or self.state == ExplorerInfoFrame.DESCRIPTION_FOCUSED:
            self.state = ExplorerInfoFrame.MENU_FOCUSED
            self.textbox.set_outline_size(0)
            self.prerender()

        return Frame.EventCallback.SUCCESS

    def enter_pressed(self, event: pygame.event.Event, data: Any) -> None:

        if self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.slider_menu.select()

        return Frame.EventCallback.SUCCESS

    def keydown(self, event: pygame.event.Event, data: Any) -> None:

        if event.key == KeyAlternatives.SHOW_IMAGE_KEY:
            self.full_image_shown = True
            self.prerender()

    def keyup(self, event: pygame.event.Event, data: Any) -> None:

        if event.key == KeyAlternatives.SHOW_IMAGE_KEY:
            self.full_image_shown = False
            self.prerender()

    @override
    def tick(self):

        if self.intro_delay_clock.elapsed() > self.intro_delay:
            self.manage_pygame_events()

        if self.exit_flag_raised():
            #since this would be called as a subframe, no next frame will be passed.
            return None

        if self.current_subframe is not None:

            ret = self.current_subframe.tick()

            if ret is None:
                self.push_event(Frame.SubframeDeletedEvent(deleted_subframe=self.current_subframe, n_subframes_active=0))
                self.current_subframe = None
                self.prerender()


        #slider menu
        self.slider_menu.tick()

        slider_events = self.slider_menu.poll_events()
        for event in slider_events:

            if event.type == LabeledImageSlider.EventTypes.SELECT_ANIMATION_ENDED:

                if self.parent_frame is not None:

                    if self.slider_menu.get_selected_index() == 0:

                        self.current_subframe = ShowExplorerStartingCardsFrame(
                                                                                explorer_enum=self.explorer_enum,
                                                                                data=self.data,
                                                                                frame_dim=self.parent_frame.frame_dim.copy(),
                                                                                parent_frame=self,
                                                                                focus_group=self.focus_group,
                                                                                has_focus=True
                                                                                )
                    else:

                        self.current_subframe = TestFrame(
                                                        data=None,
                                                        frame_dim=self.parent_frame.frame_dim.copy(),
                                                        parent_frame=self,
                                                        focus_group=self.focus_group,
                                                        has_focus=True
                                                    )


                self.push_event(Frame.SubframeCreatedEvent(created_subframe=self.current_subframe, n_subframes_active=1))

        self.prerender()

        return self

    @override
    def prerender(self):

        self.surface.fill(Colors.TRANSPARENT)

        if self.current_subframe is None:

            background_color = (*Colors.BLACK, 210)
            self.half_surface.fill(background_color)

            tosize = None
            tocolor = None

            if self.state == self.DESCRIPTION_FOCUSED:
                tosize = self.textbox_outline_size_p
                tocolor = Colors.WHITE

            self.explorer_info.render_info_page_parts(
                                                        screen=self.half_surface,
                                                        info_page_part_container=self.info_page_parts,
                                                        background_color=background_color,
                                                        full_image_shown=self.full_image_shown,
                                                        textbox_outline_size=tosize,
                                                        textbox_outline_color=tocolor
                                                        )
            self.slider_menu.render(self.half_surface)

            if self.state == ExplorerInfoFrame.MENU_FOCUSED:
                pygame.draw.rect(self.half_surface, (*Colors.WHITE, 255), self.slider_border_frame, width=self.focused_outline_size)

            self.surface.blit(self.half_surface, (self.half_frame.x, self.half_frame.y))

        else:

            self.current_subframe.render(self.surface)
