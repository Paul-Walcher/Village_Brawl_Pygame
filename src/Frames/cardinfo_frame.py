import pygame

from Frames.frame import Frame
from Frames.frame_enums import FrameEnums
import graphics
from constants import Colors, Alpha, Fonts, Fontsizes, KeyAlternatives
from widgets.textbox import Textbox

class CardinfoFrame(Frame):

    def __init__(self, cardinfo, alpha=Alpha.LEVEL_6, font=Fonts.MINECRAFT,
                has_focus=True,
                hmargin=0.2, vmargin = 0.2,
                chars_per_line=50, lines_per_page=5,
                data=None, frame_dim=None, parent_frame=None
                ):

        super().__init__(FrameEnums.CARDINFO_FRAME, data, frame_dim, parent_frame)

        self.cardinfo = cardinfo
        self.alpha = alpha
        self.font = font

        self.hmargin = hmargin
        self.vmargin = vmargin

        self.chars_per_line = chars_per_line
        self.lines_per_page = lines_per_page

        self.__has_focus = has_focus

        self.render_frame = graphics.apply_margins(self.frame_dim, self.hmargin, self.vmargin)

        self.area_distances = 0.1
        self.headline_area_p, self.image_area_p, self.description_area_p = 0.2, 0.4, 0.4

        self.rf_dist_height = int(self.render_frame.height * (1.0 - 2 * self.area_distances))
        self.area_dheight = int(self.render_frame.height * self.area_distances)

        self.headline_area = self.render_frame.copy()
        self.headline_area.height = int(self.headline_area_p * self.rf_dist_height)

        self.image_area = self.render_frame.copy()
        self.image_area.y += self.headline_area.height + self.area_dheight
        self.image_area.height = int(self.image_area_p * self.rf_dist_height)

        self.description_area = self.render_frame.copy()
        self.description_area.y = self.image_area.y + self.image_area.height + self.area_dheight
        self.description_area.height = int(self.description_area_p * self.rf_dist_height)

        self.headline, self.headline_pos = None, None
        self.image, self.image_pos = None, None
        self.description_textbox = None

        self.fullcard, self.fullcard_pos = None, None

        self.bottom_surface = pygame.Surface((self.width, self.height))
        self.bottom_surface.set_alpha(self.alpha)
        self.bottom_surface.fill(Colors.BLACK)

        self.second_bottom_surface = self.bottom_surface.copy()

        self.description_textbox = None

        self.full_image_shown = False

        self.bind_events()
        self.rerender()

    def focus(self):
        self.__has_focus = True
        self.bind_events()

    def unfocus(self):
        self.__has_focus = False
        self.bind_events()

    def bind_events(self):

        self.clear_event_callbacks()

        data = {"frame_ref": self}

        if self.__has_focus:

            for key in [pygame.K_RIGHT, KeyAlternatives.RIGHT_ALTERNATIVE]:
                self.add_pygame_key_callback(key, data.copy(),  False, self.next_page)
            for key in [pygame.K_LEFT, KeyAlternatives.LEFT_ALTERNATIVE]:
                self.add_pygame_key_callback(key, data.copy(),  False, self.prev_page)

            self.add_pygame_event_callback(pygame.KEYDOWN, data.copy(), False, self.alt_down)
            self.add_pygame_event_callback(pygame.KEYUP, data.copy(), False, self.alt_up)


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


    def rerender(self):

        fsize = graphics.get_fontsize(self.font, [self.cardinfo.name], self.headline_area)

        self.headline = graphics.render_text(self.font, fsize, self.cardinfo.name, self.cardinfo.name_color)
        self.headline_pos = graphics.get_center_with_surface(self.headline, self.headline_area)

        #getting the card scale size
        cw, ch = 0, 0
        fw, fh = 0, 0

        if self.cardinfo.width_to_height_ratio < 1.0:

            ch = self.image_area.height
            cw = int(ch * self.cardinfo.width_to_height_ratio)

            fh = self.render_frame.height
            fw = int(fh * self.cardinfo.width_to_height_ratio)

        else:

            cw = self.image_area.width
            ch = int(cw * (1.0 / self.cardinfo.width_to_height_ratio))

            fw = self.render_frame.width
            fh = int(fw * (1.0 / self.cardinfo.width_to_height_ratio))

        self.image = graphics.render_image(self.cardinfo.card_image_path)
        self.image = pygame.transform.smoothscale(self.image, (cw, ch))

        self.image_pos = graphics.get_center_with_surface(self.image, self.image_area)

        self.full_image = graphics.render_image(self.cardinfo.card_image_path)
        self.full_image = pygame.transform.smoothscale(self.full_image, (fw, fh))

        self.full_image_pos = graphics.get_center_with_surface(self.full_image, self.render_frame)

        true_description_area = graphics.apply_margins(self.description_area, 0.5, 0.5)
        line_rect = true_description_area.copy()
        line_rect.height //= self.lines_per_page

        fsize = graphics.get_fontsize(self.font, ["W" * self.chars_per_line], line_rect)

        self.description_textbox = Textbox(
                                            self.font, fsize,
                                            self.cardinfo.description_color,
                                            true_description_area,
                                            outline_size=5,
                                            outline_color=Colors.WHITE,
                                            centered=True,
                                            text_colored=True
                                            )

        self.description_textbox.show_pagenumber()

        self.widgets.append(self.description_textbox)




    def tick(self):

        self.manage_pygame_events()

        if self.exit_flag_raised():
            return None

        self.widgets_tick()

    def render(self, screen):

        screen.blit(self.bottom_surface, (self.x, self.y))

        screen.blit(self.headline, self.headline_pos)
        screen.blit(self.image, self.image_pos)

        self.render_widgets(screen)

        if self.full_image_shown:

            screen.blit(self.second_bottom_surface, (self.x, self.y))
            screen.blit(self.full_image, self.full_image_pos)
