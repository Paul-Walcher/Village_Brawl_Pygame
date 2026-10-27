from __future__ import annotations

import pygame

from constants import Colors, Fonts, fequal, color_t
import graphics
from graphics import text_t, colored_text_t ,page_t, colored_page_t, surface_with_position_t, rendered_surface_position_tuples_t
from Frames.widgets.textbox import Textbox

class Renderable_CardInfo:
    """
    This class defines how the info  text for a
    card is is rendered. The info text describes the cards
    functionality.

    This class works by first getting the page parts to render with positions
    as a container class using Renderable_CardInfo.get_info_page_parts,
    then some time later rendering the page parts to the given screen by passing
    the container class to Renderable_CardInfo.render_info_page_parts
    """

    class InfoPagePartContainer:
        """
        Container class for the various items constituating
        the info page.
        """

        def __init__(
                    self,
                    frame_dim: pygame.Rect,
                    headline: rendered_surface_position_tuples_t,
                    image_surface: pygame.Surface,
                    image_pos: tuple[int, int],
                    textbox: Textbox,
                    textbox_pos: tuple[int, int],
                    full_image_surface: pygame.Surface,
                    full_image_pos: tuple[int, int],
                    areas: list[pygame.Rect]
                    ):

            self.frame_dim = frame_dim
            """
            The rectangle defining the pages position, width and length.
            """
            self.headline = headline
            """
            (surface, position) tuples for the headline
            """
            self.image_surface: pygame.Surface = image_surface
            """
            Surface for the image displayed.
            """
            self.image_pos: tuple[int, int] = image_pos
            """
            (x, y) position of the image. This is not relative to
            the frame_dim origin (0, 0), but is (actual_position_inside_frame_dim + frame_dim_origin)
            """
            self.textbox: Textbox = textbox
            """
            The textbox displaying the description text.
            """
            self.textbox_pos: tuple[int, int] = textbox_pos
            """
            (x, y) position of the textbox. This is not relative to
            the frame_dim origin (0, 0), but is (actual_position_inside_frame_dim + frame_dim_origin).
            This is not used for rendering, but can be retreived as info.
            """
            self.full_image_surface: pygame.Surface = full_image_surface
            """
            The full image that will be shown in fullscreen dimensions.
            """
            self.full_image_pos: tuple[int, int] = full_image_pos
            """
            (x, y) of the full image. This is centered inside the fullscreen rectangle.
            """
            self.areas: list[pygame.Rect] = areas
            """
            List of the areas the frame_dim is split up into from top to bottom.
            """

        def get_blit_surface_position_tuples(self) -> tuple[ tuple[ pygame.Surface, tuple[ int, int ] ] ]:
            """
            Returns a list of (surface, position),
            of all the parts that should be rendered this way.
            """

            sp_list =   [
                        *self.headline,
                        (self.image_surface, self.image_pos)
                        ]

            return sp_list


    def __init__(self,
                name: page_t = "",
                name_color: color_t = Colors.BLACK,
                description: str = "",
                colored_description: colored_text_t = None,
                card_image_path: str = "",
                standard_image_path: str = "",
                description_line_length: int = 40,
                description_lines_per_page: int = 5
                ):

        self.name: page_t = name
        """
        Name of the card.
        """
        self.name_color: color_t = name_color
        """
        Color of the headline, which renders the name of this card.
        """
        self._description: str = description
        """
        The description for the card. This will be rendered if
        self._colored_description == None.
        If self._colored_description != None,
        self._colored_description will be rendered instead
        """
        self.card_image_path: str = card_image_path
        """
        Path to the card image.
        """
        self.standard_image_path: str = standard_image_path
        """
        Path to the standard image.
        """
        self._colored_description: colored_text_t = colored_description
        """
        Description of the card in colored form.
        This will always be rendered inside the info page textbox if available.
        """
        if self._colored_description is None or not self._colored_description:
            self._colored_description = [(self._description, Colors.STANDARD_TEXT_COLOR)]

        self._description_line_length: int = description_line_length
        """
        Amount of characters per line in the info page textbox.
        """
        self._description_lines_per_page: int = description_lines_per_page
        """
        Amount of lines per page in the info page text box.
        """
        self._description_pages: list[page_t] = graphics.page_by_chars(self._description, self._description_line_length, self._description_lines_per_page)
        """
        List of pages for the info page textbox.
        """
        self._colored_description_pages: list[colored_page_t] = graphics.page_by_chars_color(self._colored_description, self._description_line_length, self._description_lines_per_page)
        """
        List of colored pages for the info textbox
        """
        self._n_pages: int = len(self._description_pages)
        """
        Number of pages in the standard (not colored) description.
        """
        self._n_pages_color = (len(self._colored_description_pages) if self._colored_description_pages is not None else -1)
        """
        Number of pages in the colored description. Is -1 if self._colored_description_pages is None.
        """

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, desc):
        """
        Updates all internal variables after changing the description.
        """

        old_desc = self._description
        self._description = desc

        if not self._colored_description or self._colored_description is None or (len(self._colored_description) == 1 \
            and self._colored_description[0][0] == old_desc and self._colored_description[0][1] == Colors.STANDARD_TEXT_COLOR):

            self._colored_description = [(self._description, Colors.STANDARD_TEXT_COLOR)]

        self._description_pages = graphics.page_by_chars(self._description, self._description_line_length, self._description_lines_per_page)
        self._colored_description_pages = graphics.page_by_chars_color(self._colored_description, self._description_line_length, self._description_lines_per_page)

        self._n_pages = len(self._description_pages)
        self._n_pages_color = (len(self._colored_description_pages) if self._colored_description_pages is not None else -1)

    @property
    def colored_description(self):
        return self._colored_description

    @colored_description.setter
    def colored_description(self, desc):

        """
        Updates all internal variables after changing the colored description.
        """

        self._colored_description = desc
        self._colored_description_pages = graphics.page_by_chars_color(self._colored_description, self._description_line_length, self._description_lines_per_page)

        self._n_pages = len(self._description_pages)
        self._n_pages_color = (len(self._colored_description_pages) if self._colored_description_pages is not None else -1)

    @property
    def description_line_length(self):
        return self._description_line_length

    @description_line_length.setter
    def description_line_length(self, ll):
        """
        Updates the pages after changing the description line length.
        """

        self._description_line_length = ll

        self._description_pages = graphics.page_by_chars(self._description, self._description_line_length, self._description_lines_per_page)
        if self._colored_description_pages is not None:
            self._colored_description_pages = graphics.page_by_chars_color(self._colored_description, self._description_line_length, self._description_lines_per_page)

        self._n_pages = len(self._description_pages)
        self._n_pages_color = (len(self._colored_description_pages) if self._colored_description_pages is not None else -1)

    @property
    def description_lines_per_page(self):
        return self._description_lines_per_page

    @description_lines_per_page.setter
    def description_lines_per_page(self, ps):

        """
        Updates the pages after changing the description page size.
        """

        self._description_lines_per_page = ps

        self._description_pages = graphics.page_by_chars(self._description, self._description_line_length, self._description_lines_per_page)
        if self._colored_description_pages is not None:
            self._colored_description_pages = graphics.page_by_chars_color(self._colored_description, self._description_line_length, self._description_lines_per_page)

        self._n_pages = len(self._description_pages)
        self._n_pages_color = (len(self._colored_description_pages) if self._colored_description_pages is not None else -1)

    def get_name_rendered(self, target_frame_dim: pygame.Rect, font: pygame.font.Font = Fonts.MINECRAFT, line_margin: int = 5) -> rendered_surface_position_tuples_t:
        """
        Returns a rendered page.
        """
        return graphics.render_page_from_chars(font=font, page=self.name, frame=target_frame_dim, line_margin=line_margin, centered=True, vertical_centered=True)

    def get_card_image_rendered(self, frame_dim: pygame.Rect) -> surface_with_position_t:
        """
        Returns the card image rendered into frame_dim.
        """
        return graphics.img_load_and_position(self.card_image_path, frame_dim)

    def get_standard_image_rendered(self, frame_dim: pygame.Rect) -> surface_with_position_t:
        """
        Returns the standard image rendered into frame_dim.
        """
        return graphics.img_load_and_position(self.standard_image_path, frame_dim)

    def get_description_textbox(self,
                                frame_dim: pygame.Rect,
                                colored: bool = True,
                                font: pygame.font.Font = Fonts.MINECRAFT,
                                text_color: color_t = Colors.STANDARD_TEXT_COLOR,
                                line_margin: int = 5,
                                wmargin: int = 5, hmargin: int = 5
                                ) -> Textbox:
        """
        Creates the textbox for the info frame.
        If colored == True, self.colored_description will be used as the text for the textbox.
        Otherwise self.description will be used.
        wmargin, hmargin specify the margins inside the textbox, between frame and text.
        """

        return Textbox(frame_dim,
                        font,
                        (self._colored_description if colored else self._description),
                        line_length=self._description_line_length,
                        paragraph_length=self._description_lines_per_page,
                        wmargin=wmargin,
                        hmargin=hmargin,
                        text_color=text_color,
                        centered=True,
                        text_colored=colored
                        )

    def get_areas(      self,
                        frame_dim: pygame.Rect,
                        height_distributions: list[float],
                        hmargin: float = 0.2,
                        vmargin: float = 0.2
                        ) -> list[pygame.Rect]:
        """
        Calculates the different areas for the info page.

        Traditionally this does:

        areas = get_areas()

        areas[0] | The area into which the headline will be rendered.
        areas[1] | The first divider area (empty).
        areas[2] | The image area.
        areas[3] | The second divider area.
        areas[4] | The textbox area
        areas[5] | The final divider area
        """


        frame_dim = graphics.apply_margins(frame_dim, hmargin, vmargin)
        x, y, w, h = frame_dim.x, frame_dim.y, frame_dim.width, frame_dim.height
        heights = [int(hp *  h) for hp in height_distributions]

        back = []
        cy = frame_dim.y

        for height in heights:

            back.append(pygame.Rect(x, cy, w, height))

            cy += height

        return back


    def get_info_page_parts(    self,
                                frame_dim: pygame.Rect,
                                font: pygame.font.Font = Fonts.MINECRAFT,
                                hmargin: float = 0.1, vmargin: float = 0.1,
                                chars_per_line: int = 50, lines_per_page: int = 5,
                                height_distributions: list[float] = [0.1, 0.05, 0.45, 0.1, 0.25, 0.05],#equals: headline area, distance, card image area, distance, textbox area, distance
                                rendered_image_path: str = None

                                ) -> InfoPagePartContainer:

        """
        Renders all significant parts for the info page, then returns
        a InfoPagePartContainer object.

        hmargin and vmargin specify the margins applied to frame_dim before rendering.
        """

        if not fequal(1.0, sum(height_distributions)):
            raise RuntimeError("Height Distributions must add up to 1")

        if rendered_image_path is None:
            rendered_image_path = self.card_image_path
        #returns a part list, should be used by the render_info_page_parts method
        x, y, w, h = frame_dim.x, frame_dim.y, frame_dim.width, frame_dim.height

        render_frame = graphics.apply_margins(pygame.Rect(x, y, w, h), hmargin, vmargin)

        headline_area, headline_image_dist_r, image_area,\
        image_description_dist_r, description_area, description_bottom_dist_r = self.get_areas(frame_dim, height_distributions, hmargin=hmargin, vmargin=vmargin)

        headline_image_dist, image_description_dist, description_bottom_dist = headline_image_dist_r.h ,image_description_dist_r.h, description_bottom_dist_r.h

        rwidth = render_frame.width
        rheight = render_frame.height

        headline, headline_pos = None, None
        image, image_pos = None, None
        description_textbox = None

        fullcard_surf, fullcard_surf_pos = None, None
        fullcard, fullcard_pos = None, None

        headline = self.get_name_rendered(headline_area, font=font)

        if rendered_image_path == self.card_image_path:
            image, image_pos = self.get_card_image_rendered(image_area)
        elif rendered_image_path == self.standard_image_path:
            image, image_pos = self.get_standard_image_rendered(image_area)

        full_image, full_image_pos = self.get_card_image_rendered(render_frame)

        true_description_area = graphics.apply_margins(description_area, 0.2, 0.2)
        line_rect = true_description_area.copy()
        line_rect.height //= lines_per_page

        description_textbox = self.get_description_textbox(
                                                            frame_dim=description_area,
                                                            colored=True,
                                                            font=font,
                                                            text_color=Colors.STANDARD_TEXT_COLOR
                                                            )

        description_textbox.show_pagenumber()

        return Renderable_CardInfo.InfoPagePartContainer(
                                                        frame_dim=frame_dim.copy(),
                                                        headline=headline,
                                                        image_surface=image,
                                                        image_pos=image_pos,
                                                        textbox=description_textbox,
                                                        textbox_pos=(line_rect.x, line_rect.y),
                                                        full_image_surface=full_image,
                                                        full_image_pos=full_image_pos,
                                                        areas=self.get_areas(frame_dim, height_distributions, hmargin, vmargin)
                                                    )

    def render_info_page_parts( self,
                                screen: pygame.Surface,
                                info_page_part_container: InfoPagePartContainer,
                                page_index: int = -1,
                                background_color: color_t = Colors.BLACK,
                                textbox_outline_size: int = None,
                                textbox_outline_color: int = None,
                                full_image_shown: bool = False
                                ) -> None:

        """
        Given the surface to render onto and the info_page_part_container, this function
        renders the info page onto screen.
        page_index specifies the page shown inside the textbox, background_color
        the background color of the info frame.
        If full_image_shown == True, the full image will be shown on top of the info page.
        """

        tbox = info_page_part_container.textbox
        full_image, full_image_pos = info_page_part_container.full_image_surface, info_page_part_container.full_image_pos

        if page_index != -1:
            tbox.skip_to_page(page_index)

        if textbox_outline_size is not None:
            tbox.set_outline_size(textbox_outline_size)
        if textbox_outline_color is not None:
            tbox.set_outline_color(textbox_outline_color)

        screen.fill(background_color)

        tbox.render(screen)

        for surf, pos in info_page_part_container.get_blit_surface_position_tuples():
            screen.blit(surf, pos)

        tbox.render(screen)

        if full_image_shown:

            tsurf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            tsurf.fill((*Colors.BLACK, 180))

            tsurf.blit(full_image, (full_image_pos[0], full_image_pos[1]))

            screen.blit(tsurf, (0, 0))
