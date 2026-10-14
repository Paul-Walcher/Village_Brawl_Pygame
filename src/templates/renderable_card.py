import pygame

from constants import Colors, Fonts, fequal
import graphics
from widgets.textbox import Textbox

class Renderable_Card:

    def __init__(self,
                name="",
                name_color=Colors.BLACK,
                description="",
                description_color=None, #if this is given, it is a list of [(text, color), ] for rendering
                card_image_path="",
                standard_image_path="",
                description_line_length=40,
                description_paragraph_length=5,
                card_width_to_height_ratio = 5/7,
                standard_width_to_height_ratio = 1.0
                ):

        self.name = name
        self.name_color = name_color
        self.__description = description
        self.card_image_path = card_image_path
        self.standard_image_path = standard_image_path
        self.__description_color = description_color
        if self.__description_color is None:
            self.__description_color = [(self.__description, Colors.STANDARD_TEXT_COLOR)]
        self.__description_line_length = description_line_length
        self.__description_paragraph_length = description_paragraph_length

        self.description_pages = graphics.page_by_chars(self.__description, self.__description_line_length, self.__description_paragraph_length)
        self.description_pages_color = self.description_color
        if self.description_pages_color is not None:
            self.description_pages_color = graphics.page_by_chars_color(self.__description_color, self.__description_line_length, self.__description_paragraph_length)

        self.n_pages = len(self.description_pages)
        self.n_pages_color = (len(self.description_pages_color) if self.description_pages_color is not None else -1)

        self.card_width_to_height_ratio = card_width_to_height_ratio
        self.standard_width_to_height_ratio = standard_width_to_height_ratio

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, desc):

        self.__description = desc
        if self.__description_color is None:
            self.__description_color = [(self.__description, Colors.STANDARD_TEXT_COLOR)]
        self.description_pages = graphics.page_by_chars(self.__description, self.__description_line_length, self.__description_paragraph_length)

        self.n_pages = len(self.description_pages)
        self.n_pages_color = (len(self.description_pages_color) if self.description_pages_color is not None else -1)

    @property
    def description_color(self):
        return self.__description_color

    @description_color.setter
    def description_color(self, desc):

        self.__description_color = desc
        self.description_pages_color = graphics.page_by_chars_color(self.__description_color, self.__description_line_length, self.__description_paragraph_length)

        self.n_pages = len(self.description_pages)
        self.n_pages_color = (len(self.description_pages_color) if self.description_pages_color is not None else -1)

    @property
    def description_line_length(self):
        return self.__description_line_length

    @description_line_length.setter
    def description_line_length(self, ll):

        self.__description_line_length = ll

        self.description_pages = graphics.page_by_chars(self.__description, self.__description_line_length, self.__description_paragraph_length)
        if self.description_pages_color is not None:
            self.description_pages_color = graphics.page_by_chars_color(self.__description_color, self.__description_line_length, self.__description_paragraph_length)

        self.n_pages = len(self.description_pages)
        self.n_pages_color = (len(self.description_pages_color) if self.description_pages_color is not None else -1)

    @property
    def description_paragraph_length(self):
        return self.__description_paragraph_length

    @description_paragraph_length.setter
    def description_paragraph_length(self, ps):

        self.__description_paragraph_length = ps

        self.description_pages = graphics.page_by_chars(self.__description, self.__description_line_length, self.__description_paragraph_length)
        if self.description_pages_color is not None:
            self.description_pages_color = graphics.page_by_chars_color(self.__description_color, self.__description_line_length, self.__description_paragraph_length)

        self.n_pages = len(self.description_pages)
        self.n_pages_color = (len(self.description_pages_color) if self.description_pages_color is not None else -1)

    def get_name_rendered(self, target_frame_dim, font=Fonts.MINECRAFT, line_margin=5):

        fsize = graphics.get_fontsize(font, [self.name], line_margin)
        surf = graphics.render_text(font, fsize, self.name, self.name_color)
        return surf

    def get_card_image_rendered(self, frame_dim):

        cimage = graphics.render_image(self.card_image_path)

        w, h = 0, 0

        if self.card_width_to_height_ratio > 1.0:
            w = frame_dim.width
            h = w * (1.0 / self.card_width_to_height_ratio)
        else:
            h = frame_dim.height
            w = h * self.card_width_to_height_ratio

        cimage = pygame.transform.smoothscale(cimage, (w, h))
        return cimage

    def get_standard_image_rendered(self, frame_dim):

        cimage = graphics.render_image(self.standard_image_path)

        w, h = 0, 0

        if self.standard_width_to_height_ratio > 1.0:
            w = frame_dim.width
            h = w * (1.0 / self.standard_width_to_height_ratio)
        else:
            h = frame_dim.height
            w = h * self.standard_width_to_height_ratio

        cimage = pygame.transform.smoothscale(cimage, (w, h))
        return cimage

    def get_description_textbox(self, frame_dim, colored=True, font=Fonts.MINECRAFT, text_color=Colors.STANDARD_TEXT_COLOR,line_margin=5, wmargin=5, hmargin=5):

        return Textbox(font, (self.description_color if colored else self.description), frame_dim,
                        line_length=self.description_line_length, paragraph_length=self.description_paragraph_length,
                        wmargin=wmargin, hmargin=hmargin, text_color=text_color, centered=True, text_colored=colored
                        )

    def get_info_page_parts(self, frame_dim,
                                font=Fonts.MINECRAFT,
                                hmargin=0.2, vmargin = 0.2,
                                chars_per_line=50, lines_per_page=5,
                                height_distributions=[0.1, 0.1, 0.35, 0.1, 0.25, 0.1]#equals: headline area, distance, card image area, distance, textbox area, distance
                                ):


        if not fequal(1.0, sum(height_distributions)):
            raise RuntimeError("Height Distributions must add up to 1")

        #returns a part list, should be used by the render_info_page_parts method
        x, y, w, h = frame_dim.x, frame_dim.y, frame_dim.width, frame_dim.height

        render_frame = graphics.apply_margins(pygame.Rect(x, y, w, h), hmargin, vmargin)

        headline_area_height, headline_image_dist, image_area_height, \
        image_description_dist, description_area_height, description_bottom_dist = [int(hp *  h) for hp in height_distributions]


        headline_area = render_frame.copy()
        headline_area.height = headline_area_height

        image_area = render_frame.copy()
        image_area.y = headline_area.y + headline_area_height + headline_image_dist
        image_area.height = image_area_height

        description_area = render_frame.copy()
        description_area.y = image_area.y + image_area_height + image_description_dist
        description_area.height = description_area_height

        headline, headline_pos = None, None
        image, image_pos = None, None
        description_textbox = None

        fullcard_surf, fullcard_surf_pos = None, None
        fullcard, fullcard_pos = None, None

        fsize = graphics.get_fontsize(font, [self.name], headline_area)

        headline = graphics.render_text(font, fsize, self.name, self.name_color)
        headline_pos = graphics.get_center_with_surface(headline, headline_area)

        image = self.get_card_image_rendered(image_area)
        image_pos = graphics.get_center_with_surface(image, image_area)

        fw, fh = 0, 0

        if self.card_width_to_height_ratio < 1.0:

            fh = render_frame.height
            fw = int(fh * self.card_width_to_height_ratio)

        else:

            fw = render_frame.width
            fh = int(fw * (1.0 / self.card_width_to_height_ratio))

        full_image = graphics.render_image(self.card_image_path)
        full_image = pygame.transform.smoothscale(full_image, (fw, fh))

        full_image_pos = graphics.get_center_with_surface(full_image, render_frame)

        true_description_area = graphics.apply_margins(description_area, 0.2, 0.2)
        line_rect = true_description_area.copy()
        line_rect.height //= lines_per_page

        fsize = graphics.get_fontsize(font, ["W" * chars_per_line], line_rect)

        description_textbox = Textbox(
                                            font,
                                            self.description_color,
                                            true_description_area,
                                            outline_size=5,
                                            outline_color=Colors.WHITE,
                                            centered=True,
                                            text_colored=True
                                            )

        description_textbox.show_pagenumber()

        return [(headline, headline_pos), (image, image_pos), (description_textbox, (line_rect.x, line_rect.y)), (full_image, full_image_pos)]

    def render_info_page_parts(self,
                                screen,
                                page_parts,
                                page_index=-1,
                                background_color=Colors.BLACK,
                                outline_size=None,
                                outline_color=None,
                                full_image_shown=False
                                ):

        tbox = page_parts[2][0]
        full_image, full_image_pos = page_parts[3]
        if page_index != -1:
            tbox.skip_to_page(page_index)

        if outline_size is not None:
            tbox.set_outline_size(outline_size)
        if outline_color is not None:
            tbox.set_outline_color(outline_color)

        screen.fill(background_color)

        for surf, pos in page_parts[:2]:
            screen.blit(surf, pos)

        for surf, pos in tbox.get_surfaces_with_position():
            screen.blit(surf, pos)

        if full_image_shown:

            tsurf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            tsurf.fill((*Colors.BLACK, 180))

            tsurf.blit(full_image, (full_image_pos[0], full_image_pos[1]))

            screen.blit(tsurf, (0, 0))
