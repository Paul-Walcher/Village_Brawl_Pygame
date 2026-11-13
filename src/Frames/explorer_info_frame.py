from __future__ import annotations
from typing import Any, Type, Callable, override

import os
import pygame
import threading


from Frames.cardinfo_frame import CardinfoFrame
from constants import PLAYSETS_FOLDER, Colors, Fonts, Fontsizes, KeyAlternatives, Alpha, IIMAGE, STANDARD_BACKSIDES, R_ID,\
                        EXPLORER_STARTING_ICONS_AND_LABELS, color_t, point_t, as_point, Mouse
import graphics
from graphics import page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t
import calculations
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
from Frames.cardinfo_frame import CardinfoFrame
from Frames.widgets.slider import Slider

from context_data import ContextData

class ExplorerInfoFrame(CardinfoFrame):
    """
    Frame that displays a explorers info, but not just the standard info
    but also all starting cards.

    This card inherits from CardinfoFrame
    """

    MENU_FOCUSED: int = R_ID()
    MENU_SLIDING: int = R_ID()

    def __init__(
                self,
                explorer_enum: int,
                modules: Modules,
                frame_dim: pygame.Rect,
                data: Any = None,
                parent_frame: Frame = None,
                focus_group: str = "",
                has_focus: bool = True,
                info_width_percentage: float = 0.5,
                shown_side=None,
                font: pygame.font.Font = Fonts.STANDARD_FONT,
                alpha: int = 170, #the alpha value
                hmargin: float = 0.1,
                vmargin: float = 0.1,
                chars_per_line: int = 50,
                lines_per_page: int = 5,
                slide_duration: float = 400,
                start_position: point_t = None,
                end_position: point_t = None
                ):

        #setting the frame enum
        self.icon_imgs: list[str] = None
        """
        Paths to the icon images for self.slider_menu.
        """
        self.image_labels: list[str] = None
        """
        Labels for the images in self.slider_menu.
        """
        #setting it to the values defined in constants
        self.icon_imgs, self.image_labels = EXPLORER_STARTING_ICONS_AND_LABELS

        self.slider_labels: list[colored_page_t] = None
        """
        The slider labels, these are the image labels rendered as colored pages.
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
        self.standard_info_page_frame: pygame.Rect = None
        """
        Rect for rendering the standard info page.
        """
        self.relative_standard_info_page_frame: pygame.Rect = None
        """
        Relative rect for rendering onto the surface.
        """
        self.divider_frame: pygame.Rect = None
        """
        Frame to divide info_page_frame and slider_frame.
        """
        self.slider_frame: pygame.Rect = None
        """
        Frame for the slider.
        """
        self.relative_slider_frame: pygame.Rect = None
        """
        The relative slider frame for rendering the slider.
        """
        self.slider_border_frame: pygame.Rect = None
        """
        The rect being outlined when self.slider_menu is focused.
        """
        self.relative_slider_border_frame: pygame.Rect = None
        """
        The relative border frame relative to self.info_frame_dim.
        """
        self.slider_menu: LabeledImageSlider = None
        """
        The own slider menu.
        """
        self.current_subframe: Frame = None
        """
        The current subframe
        """
        self.menu_outline_size_p: float = 0.05
        """
        Menu outline for the slider menu
        """
        self.menu_outline_size: int = -1
        """
        The actual menu outline.
        """
        self.menu_outline_color: color_t = Colors.WHITE
        """
        The menu outline color.
        """

        self.explorer_enum: int = explorer_enum
        """
        The explorer enum.
        """
        self.modules: Modules = modules
        """
        The loaded modules for getting the class reference and info.
        """
        self.explorer_ref: Type[Explorer_Template] = self.modules.mappings.explorer_mappings[self.explorer_enum]
        """
        Reference to the explorer class.
        """
        self.explorer_info: ExplorerInfo = self.explorer_ref.info()
        """
        The explorer info.
        """

        CardinfoFrame.__init__(
                                self,
                                cardinfo=self.explorer_info,
                                frame_dim=frame_dim,
                                data=data,
                                parent_frame=parent_frame,
                                focus_group=focus_group,
                                has_focus=has_focus,
                                info_width_percentage=info_width_percentage,
                                shown_side=shown_side,
                                font=font,
                                alpha=alpha, #the alpha value
                                hmargin=hmargin,
                                vmargin=vmargin,
                                chars_per_line=chars_per_line,
                                lines_per_page=lines_per_page,
                                slide_duration=slide_duration,
                                start_position=start_position,
                                end_position=end_position
                                )

        self.frame_enum = FrameEnums.CHOOSE_EXPLORER_FRAME


    @override
    def rerender(self):
        """
        Rerendering.
        """
        sx: int = -1 #starting x
        sy: int = -1 #starting y

        if self.slide_startpos is not None:

            sx, sy = self.slide_startpos

        else:

            #we calculate the slide startpos
            sx = (self.x-self.width if self.shown_side == CardinfoFrame.LEFT_SIDE else self.x + self.width)
            sy = self.y

            self.slide_startpos = pygame.Rect(sx, sy, self.width, self.height)

        #calculating endpos
        if self.slide_endpos is None:
            #creating the generic end position.
            self.slide_endpos = self.frame_dim.copy()

        #setting position to the starting position
        self.x = sx
        self.y = sy

        #recalculates inner frame dimensions
        self.recalculate_inner_frame_dims()

        #creating the info page surface
        self.info_page_surface = pygame.Surface((self.info_frame_dim.width, self.info_frame_dim.height), pygame.SRCALPHA)

        self.page_parts = self.cardinfo.get_info_page_parts(
                                                                self.relative_standard_info_page_frame,
                                                                font=self.font,
                                                                hmargin=0.0,
                                                                vmargin=0.0,
                                                                chars_per_line=self.chars_per_line,
                                                                lines_per_page=self.lines_per_page
                                                                )
        #setting the reference
        self.description_textbox = self.page_parts.textbox

        self.textbox_outline_size = int(min(self.info_frame_dim.width, self.info_frame_dim.height) * self.textbox_outline_size_p)
        self.description_textbox.set_outline_size(0)
        self.description_textbox.set_outline_color(self.textbox_outline_color)

        #text for the labeled image slider rendered as colored pages
        self.slider_labels = [
                                graphics.str_to_colored_page(x, Colors.WHITE) for x in self.image_labels
                                ]

        #creating the slider
        self.slider_menu = LabeledImageSlider(
                                                self.relative_slider_frame,
                                                text_pages=self.slider_labels,
                                                images=self.icon_imgs,
                                                text_location=LabeledImageSlider.BOTTOM,
                                                max_slides=3
                                                )

        self.menu_outline_size: int = int(min(self.slider_border_frame.width, self.slider_border_frame.height) * self.menu_outline_size_p)

        #prerender
        self.prerender()

        self.intro_delay_clock.start()

    @override
    def prerender(self):

        if self.current_subframe is None:
            """
            Prerendering.
            """

            self.surface.fill(Colors.TRANSPARENT)
            self.info_page_surface.fill((*Colors.BLACK, self.alpha))

            self.cardinfo.render_info_page_parts(
                                                self.info_page_surface,
                                                self.page_parts,
                                                full_image_shown=self.full_image_shown
                                                )

            self.slider_menu.render(self.info_page_surface)

            if self.state in [ExplorerInfoFrame.MENU_FOCUSED, ExplorerInfoFrame.MENU_SLIDING]:
                pygame.draw.rect(self.info_page_surface, self.menu_outline_color, self.relative_slider_border_frame, width=self.menu_outline_size)

            self.surface.blit(self.info_page_surface, (self.info_frame_dim.x, self.info_frame_dim.y))

        else:

            self.current_subframe.render(self.surface)

    @override
    def recalculate_inner_frame_dims(self) -> None:
        """
        recalculates the inner frame dims
        """
        #getting the width
        info_page_width: int = int(self.width * self.info_width_percentage)
        #now creating the split and inner frame
        self.info_frame_dim = pygame.Rect(
                                            (self.x if self.shown_side == CardinfoFrame.LEFT_SIDE else self.width - info_page_width),
                                            self.y,
                                            info_page_width,
                                            self.height
                                            )
        #creating the inner frame dim
        self.inner_frame_dim = graphics.apply_margins(self.info_frame_dim, self.hmargin, self.vmargin)

        self.standard_info_page_frame, self.divider_frame, self.slider_border_frame = graphics.split_rect_vertically(self.inner_frame_dim, self.dividing_percentages)

        self.slider_frame = graphics.apply_margins(self.slider_border_frame, 0.1, 0.1)
        #calculating relatives
        #since this is relative x, y changes do not matter
        self.relative_inner_frame_dim = graphics.position_relative(anchor_rect=self.info_frame_dim, make_relative_rect=self.inner_frame_dim)
        #relative info page
        self.relative_standard_info_page_frame = graphics.position_relative(anchor_rect=self.info_frame_dim, make_relative_rect=self.standard_info_page_frame)
        #relative slider frame
        #since this is relative x, y changes do not matter
        self.relative_slider_frame = graphics.position_relative(anchor_rect=self.info_frame_dim, make_relative_rect=self.slider_frame)
        #border frame
        self.relative_slider_border_frame = graphics.position_relative(anchor_rect=self.info_frame_dim, make_relative_rect=self.slider_border_frame)


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

            if type(self.data) == ContextData:
                if self.data.mouse_enabled:

                    self.add_pygame_event_callback(etype=pygame.MOUSEMOTION, data=None, putback=False, func=self.mouse_motion)
                    self.add_pygame_event_callback(etype=pygame.MOUSEBUTTONDOWN, data=None, putback=False, func=self.mouse_button_down)
                    self.add_pygame_event_callback(etype=pygame.MOUSEWHEEL, data=None, putback=False, func=self.mouse_wheel)
                    self.add_pygame_event_callback(etype=pygame.MOUSEBUTTONUP, data=None, putback=False, func=self.mouse_button_up)

    @override
    def mouse_motion(self, event: pygame.event.Event, data: Any) -> None:
        """
        Highlights if hovered.
        """
        if self.state in [ExplorerInfoFrame.SLIDING_IN, ExplorerInfoFrame.SLIDING_OUT, ExplorerInfoFrame.MENU_SLIDING]:
            return

        mpos: point_t = graphics.position_relative_point(anchor_point=as_point(self.inner_frame_dim), make_relative_point=event.pos)

        if self.state not in [ExplorerInfoFrame.SLIDING_IN, ExplorerInfoFrame.SLIDING_OUT, ExplorerInfoFrame.MENU_SLIDING]:

            if self.state != ExplorerInfoFrame.TEXTBOX_FOCUSED and calculations.point_collides(mpos, self.description_textbox.frame_dim):

                self.state = ExplorerInfoFrame.TEXTBOX_FOCUSED
                self.description_textbox.set_outline_size(self.textbox_outline_size_p)

                self.raise_prerender_flag()

            elif self.state != ExplorerInfoFrame.MENU_FOCUSED and calculations.point_collides(mpos, self.relative_slider_border_frame):

                if self.state == ExplorerInfoFrame.TEXTBOX_FOCUSED:
                    self.description_textbox.set_outline_size(0)

                self.state = ExplorerInfoFrame.MENU_FOCUSED
                self.raise_prerender_flag()

    @override
    def mouse_button_down(self, event: pygame.event.Event, data: Any) -> None:
        """
        Interacts with the widgets.
        """
        if self.state in [ExplorerInfoFrame.SLIDING_IN, ExplorerInfoFrame.SLIDING_OUT, ExplorerInfoFrame.MENU_SLIDING]:
            return

        left_tbox: pygame.Rect = None
        right_tbox: pygame.Rect = None

        left_sbox: pygame.Rect = None
        main_sbox: pygame.Rect = None
        right_sbox: pygame.Rect = None

        left_tbox, right_tbox = graphics.split_rect_horizontally(rect=self.description_textbox.frame_dim, percentages=[0.5, 0.5])
        left_sbox, main_sbox, right_sbox = graphics.split_rect_horizontally(rect=self.relative_slider_border_frame, percentages=[0.25, 0.5, 0.25])

        mpos: point_t = graphics.position_relative_point(anchor_point=as_point(self.inner_frame_dim), make_relative_point=event.pos)

        if event.button == Mouse.LEFT_BUTTON:

            if calculations.point_collides(mpos, left_tbox):

                self.description_textbox.prev_page()
                self.raise_prerender_flag()

            elif calculations.point_collides(mpos, right_tbox):

                self.description_textbox.next_page()
                self.raise_prerender_flag()

            elif calculations.point_collides(mpos, left_sbox):

                self.slider_menu.slide_right()
                self.state = ExplorerInfoFrame.MENU_SLIDING

            elif calculations.point_collides(mpos, right_sbox):

                self.slider_menu.slide_left()
                self.state = ExplorerInfoFrame.MENU_SLIDING

            elif calculations.point_collides(mpos, main_sbox):

                self.slider_menu.select()

        elif event.button == Mouse.WHEEL:

            self.full_image_shown = True
            self.raise_prerender_flag()

        elif event.button == Mouse.RIGHT_BUTTON:

            if self._next_frame is None:
                self._next_frame = self.parent_frame

            self.raise_exit_flag()

    @override
    def mouse_button_up(self, event: pygame.event.Event, data: Any) -> None:
        """
        Button up
        """
        if self.state in [ExplorerInfoFrame.SLIDING_IN, ExplorerInfoFrame.SLIDING_OUT, ExplorerInfoFrame.MENU_SLIDING]:
            return

        if event.button == Mouse.WHEEL:

            self.full_image_shown = False
            self.raise_prerender_flag()

    @override
    def mouse_wheel(self, event: pygame.event.Event, data: Any) -> None:
        """
        Scrolling
        """

        if self.state in [ExplorerInfoFrame.SLIDING_IN, ExplorerInfoFrame.SLIDING_OUT, ExplorerInfoFrame.MENU_SLIDING]:
            return

        mpos: int = graphics.position_relative_point(anchor_point=as_point(self.inner_frame_dim), make_relative_point=pygame.mouse.get_pos())

        if calculations.point_collides(mpos, self.relative_standard_info_page_frame):

            if event.precise_y < -0.5:

                self.description_textbox.next_page()
                self.raise_prerender_flag()
                self.intro_delay_clock.start()

            elif event.precise_y > 0.5:

                self.description_textbox.prev_page()
                self.raise_prerender_flag()
                self.intro_delay_clock.start()

        elif calculations.point_collides(mpos, self.relative_slider_border_frame):

            if event.precise_y < -0.5:

                self.slider_menu.slide_right()
                self.state = ExplorerInfoFrame.MENU_SLIDING

            elif event.precise_y > 0.5:

                self.slider_menu.slide_left()
                self.state = ExplorerInfoFrame.MENU_SLIDING


    @override
    def escape_pressed(self, event: pygame.event.Event, data: Any) -> None:

        if self.state == ExplorerInfoFrame.TEXTBOX_FOCUSED:
            self.description_textbox.set_outline_size(0)
            self.state = ExplorerInfoFrame.NOTHING_FOCUSED
            self.raise_prerender_flag()
        elif self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.state = ExplorerInfoFrame.NOTHING_FOCUSED
            self.raise_prerender_flag()
        elif self.state == ExplorerInfoFrame.NOTHING_FOCUSED:
            self._next_frame = self.parent_frame
            self.raise_exit_flag()

    @override
    def left_pressed(self, event: pygame.event.Event, data: Any) -> None:

        if self.state == ExplorerInfoFrame.NOTHING_FOCUSED:
            self.state = ExplorerInfoFrame.TEXTBOX_FOCUSED
            self.description_textbox.set_outline_size(self.textbox_outline_size_p)
            self.raise_prerender_flag()
        elif self.state == ExplorerInfoFrame.TEXTBOX_FOCUSED:
            self.description_textbox.prev_page()
            self.raise_prerender_flag()
        elif self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.slider_menu.slide_right()
            self.state = ExplorerInfoFrame.MENU_SLIDING

        return Frame.EventCallback.SUCCESS

    @override
    def right_pressed(self, event: pygame.event.Event, data: Any) -> None:

        if self.state == ExplorerInfoFrame.NOTHING_FOCUSED:
            self.state = ExplorerInfoFrame.TEXTBOX_FOCUSED
            self.description_textbox.set_outline_size(self.textbox_outline_size_p)
            self.raise_prerender_flag()
        elif self.state == ExplorerInfoFrame.TEXTBOX_FOCUSED:
            self.description_textbox.next_page()
            self.raise_prerender_flag()
        elif self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.slider_menu.slide_left()
            self.state = ExplorerInfoFrame.MENU_SLIDING

        return Frame.EventCallback.SUCCESS

    @override
    def up_pressed(self, event: pygame.event.Event, data: Any) -> None:

        if self.state == ExplorerInfoFrame.NOTHING_FOCUSED or self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.state = ExplorerInfoFrame.TEXTBOX_FOCUSED
            self.description_textbox.set_outline_size(self.textbox_outline_size_p)
            self.raise_prerender_flag()

        return Frame.EventCallback.SUCCESS

    @override
    def down_pressed(self, event: pygame.event.Event, data: Any) -> None:

        if self.state == ExplorerInfoFrame.NOTHING_FOCUSED or self.state == ExplorerInfoFrame.TEXTBOX_FOCUSED:
            self.state = ExplorerInfoFrame.MENU_FOCUSED
            self.description_textbox.set_outline_size(0)
            self.raise_prerender_flag()

        return Frame.EventCallback.SUCCESS

    def enter_pressed(self, event: pygame.event.Event, data: Any) -> None:

        if self.state == ExplorerInfoFrame.MENU_FOCUSED:
            self.slider_menu.select()

        return Frame.EventCallback.SUCCESS


    @override
    def start_sliding_in(self) -> bool:
        """
        Starts sliding in, cant happen when a subframe is active.
        """
        if self.current_subframe is not None:
            return False
        else:
            return CardinfoFrame.start_sliding_in(self)

    @override
    def start_sliding_out(self) -> bool:
        """
        Starts sliding out, cant happen when a subframe is active.
        """
        if self.current_subframe is not None:
            return False
        else:
            return CardinfoFrame.start_sliding_out(self)

    def slider_selection_triggered(self):


        idx: int = self.slider_menu.get_selected_index()[0]

        #takes any index of the Labeled image slider, since both should
        #always be in sync

        if idx == 0:

            self.current_subframe = ShowExplorerStartingCardsFrame(
                                                                    explorer_enum=self.explorer_enum,
                                                                    data=self.data,
                                                                    frame_dim=self.frame_dim.copy(),
                                                                    parent_frame=self,
                                                                    focus_group=self.focus_group,
                                                                    has_focus=True
                                                                    )
        else:

            self.current_subframe = TestFrame(
                                            data=None,
                                            frame_dim=self.frame_dim.copy(),
                                            parent_frame=self,
                                            focus_group=self.focus_group,
                                            has_focus=True
                                        )

        self.push_event(Frame.SubframeCreatedEvent(created_subframe=self.current_subframe, n_subframes_active=1))

    @override
    def tick(self):

        if self.intro_delay_clock.elapsed() > self.intro_delay:
            self.manage_pygame_events()

        if self.exit_flag_raised():
            return self._next_frame

        if self.current_subframe is not None:

            ret = self.current_subframe.tick()

            self.raise_prerender_flag()

            if ret is not self.current_subframe:
                self.push_event(Frame.SubframeDeletedEvent(deleted_subframe=self.current_subframe, n_subframes_active=0))
                self.current_subframe = None
                self.raise_prerender_flag()

        #slider menu
        self.slider_menu.tick()
        self.description_textbox.tick()

        if self.state == ExplorerInfoFrame.SLIDING_IN:
            self.slide_in()
        elif self.state == ExplorerInfoFrame.SLIDING_OUT:
            self.slide_out()

        if self.slider_menu.any_animation_playing():
            self.raise_prerender_flag()


        slider_events = self.slider_menu.poll_events()

        for event in slider_events:

            if event.type == Slider.EventTypes.SELECT_ANIMATION_ENDED:

                self.slider_selection_triggered()

            elif event.type == Slider.EventTypes.SLIDING_ANIMATION_ENDED:

                self.state = ExplorerInfoFrame.MENU_FOCUSED

        if self.prerender_flag_raised():
            self.prerender()
            self.reset_prerender_flag()

        return self
