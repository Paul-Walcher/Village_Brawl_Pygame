import pygame

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
import graphics
from constants import Colors, Alpha, Fonts, Fontsizes, KeyAlternatives, WIDTH, HEIGHT
from widgets.textbox import Textbox
from widgets.text_input import TextInput
from clock import Clock
from event_queue_manager import Event

class CardinfoFrame(Frame):

    class EventTypes:

        SLIDING_FINISHED = 0

    def __init__(self, cardinfo, font=Fonts.MINECRAFT,
                alpha=Alpha.LEVEL_5,
                has_focus=True,
                hmargin=0.1, vmargin=0.1,
                chars_per_line=50, lines_per_page=5,
                slide_duration=800,
                data=None, frame_dim=None, parent_frame=None
                ):

        super().__init__(FrameEnums.CARDINFO_FRAME, data, frame_dim, parent_frame)


        self.slide_endpos = None
        self.slide_startpos = None

        self._has_focus = has_focus

        self.cardinfo = cardinfo
        self.alpha = alpha
        self.font = font

        self.hmargin = hmargin
        self.vmargin = vmargin

        self.chars_per_line = chars_per_line
        self.lines_per_page = lines_per_page

        self.bevents = []

        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        self.full_image_shown = False

        self.slide_duration = slide_duration
        self.is_sliding = False
        self.slide_clock = Clock()

        self.bind_events()
        self.rerender()

    def focus(self):
        self._has_focus = True
        self.bind_events()

    def unfocus(self):
        self._has_focus = False
        self.bind_events()

    def bind_events(self):

        for be in self.bevents:
            self.remove_pygame_event_callback(be)

        self.bevents = []

        data = {"frame_ref": self}

        if self._has_focus:

            for key in [pygame.K_RIGHT, KeyAlternatives.RIGHT_ALTERNATIVE]:
                cb = self.add_pygame_key_callback(key, data.copy(),  False, self.next_page)
                self.bevents.append(cb)
            for key in [pygame.K_LEFT, KeyAlternatives.LEFT_ALTERNATIVE]:
                cb = self.add_pygame_key_callback(key, data.copy(),  False, self.prev_page)
                self.bevents.append(cb)

            cb_kd = self.add_pygame_event_callback(pygame.KEYDOWN, data.copy(), False, self.alt_down)
            cb_ku = self.add_pygame_event_callback(pygame.KEYUP, data.copy(), False, self.alt_up)

            self.bevents.append(cb_kd)
            self.bevents.append(cb_ku)

    def next_page(self, event, data):

        ref = data["frame_ref"]
        ref.description_textbox.next_page()

    def prev_page(self, event, data):

        ref = data["frame_ref"]
        ref.description_textbox.prev_page()

    def alt_down(self, event, data):

        if event.key != KeyAlternatives.SHOW_IMAGE_KEY:
            return Frame.CallbackEvent.FAILURE

        ref = data["frame_ref"]
        ref.full_image_shown = True

    def alt_up(self, event, data):

        if event.key != KeyAlternatives.SHOW_IMAGE_KEY:
            return Frame.CallbackEvent.FAILURE

        ref = data["frame_ref"]
        ref.full_image_shown = False

    def slide_to(self, position=(0, 0), duration=800):

        self.is_sliding = True
        self.slide_endpos = position
        self.slide_startpos = (self.x, self.y)
        self.slide_duration = duration

        self.original_headline_pos = self.headline_pos
        self.original_image_pos = self.image_pos
        self.original_description_textbox_pos = (self.description_textbox.x, self.description_textbox.y)
        self.original_full_image_pos = self.full_image_pos

        self.slide_clock.start()


    def rerender(self):

        self.page_parts = self.cardinfo.get_info_page_parts(pygame.Rect(0, 0, self.width, self.height),
                                                        font=self.font,
                                                        hmargin=self.hmargin,
                                                        vmargin=self.vmargin,
                                                        chars_per_line=self.chars_per_line,
                                                        lines_per_page=self.lines_per_page
                                                        )
        self.description_textbox = self.page_parts[2][0]


    def move_slide(self):

        percentage = self.slide_clock.elapsed() / self.slide_duration

        if percentage >= 1:
            self.finalize_slide()
        else:

            x_diff = int((self.slide_endpos[0] - self.slide_startpos[0]) * percentage)
            y_diff = int((self.slide_endpos[1] - self.slide_startpos[1]) * percentage)

            self.move_to(x=self.slide_startpos[0]+x_diff, y=self.slide_startpos[1]+y_diff)

    def finalize_slide(self):

        self.is_sliding = False
        self.event_queue.append(Event(CardinfoFrame.EventTypes.SLIDING_FINISHED, None))

        self.move_to(x=self.slide_endpos[0], y=self.slide_endpos[1])

        self.rerender()



    def tick(self):

        self.manage_pygame_events()
        self.clear_pygame_events()

        if self.exit_flag_raised():
            return None

        self.description_textbox.tick()
        self.widgets_tick()

        if self.is_sliding:
            self.move_slide()

        return self



    def render(self, screen):

        self.surface.fill((*Colors.BLACK, self.alpha))
        self.cardinfo.render_info_page_parts(
                                            self.surface,
                                            self.page_parts,
                                            full_image_shown=self.full_image_shown
                                            )

        screen.blit(self.surface, (self.x, self.y))
