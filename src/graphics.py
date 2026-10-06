import pygame
import constants
from collections import deque
import re

def render_text(font, fontsize, text, color=constants.Colors.WHITE):

    f = pygame.font.Font(font, fontsize)
    surface = f.render(text, False, color)

    return surface

def text_size(font, fontsize, text):

    f = pygame.font.Font(font, fontsize)
    return f.size(text)



def get_fontsize(font, lines, frame, line_margin=5, min_size=1, max_size=1024):
    """
    Returns the largest font size for which all lines fit inside frame.

    `font`      : Pygame font path / filename
    `lines`     : list of strings representing the current page
    `frame`     : pygame.Rect
    `line_margin`: vertical distance added between lines
    """

    def fits(fontsize):
        f = pygame.font.Font(font, fontsize)

        total_height = 0

        for i, line in enumerate(lines):
            width, height = f.size(line)

            # Line is too wide
            if width > frame.width:
                return False

            total_height += height

            if i < len(lines) - 1:
                total_height += line_margin

            # Already too tall
            if total_height > frame.height:
                return False

        return True

    # Make sure max_size is actually large enough to contain
    # the failure boundary.
    while fits(max_size):
        max_size *= 2

    # No size fits
    if not fits(min_size):
        return 0

    # Binary search for largest fitting size
    low = min_size
    high = max_size

    while low <= high:
        mid = (low + high) // 2

        if fits(mid):
            low = mid + 1
        else:
            high = mid - 1

    return high

def page_by_chars(text, line_length=40, paragraph_length=5):

    tsplit = [x.split(" ") for x in text.splitlines()]

    pages = []
    cpage = []
    cline = ""


    for textline in tsplit:
        for word in textline:

            if len(cline) + len(word) <= line_length:
                cline += word + " "
            else:
                if len(cpage) < paragraph_length:
                    cpage.append(cline)
                    cline = word
                else:
                    pages.append(cpage)
                    cpage = []
                    cpage.append(cline)
                    cline = word

    if cline:

        if len(cpage) < paragraph_length:
            cpage.append(cline)
            cline = ""
        else:
            pages.append(cpage)
            cpage = []
            cpage.append(cline)
            cline = ""

    if cpage:
        pages.append(cpage)

    return pages

def render_page_from_chars(font, page, frame, text_color=constants.Colors.BLACK, centered=False, line_margin=5):

    fsize = get_fontsize(font, page, frame, line_margin=line_margin)
    trend = []
    cy = 0

    for line in page:

        rend = render_text(font, fsize, line, text_color)
        pos = (frame.x, frame.y + cy)
        if centered:
            pos = (int(frame.x + (frame.width - rend.get_width())//2), frame.y+cy)
        trend.append((rend, pos))
        cy += rend.get_height() + line_margin

    return trend



def render_image(img_path, dimensions=None):

    #dimensions = (width, height)

    img = pygame.image.load(img_path).convert_alpha()
    if dimensions is not None:
        img = pygame.transform.scale(img, dimensions)
    return img

def render_image_scale(img_path, scale):

    #dimensions = (width, height)

    img = pygame.image.load(img_path).convert_alpha()
    img = pygame.transform.scale(img,
                (img.get_width() * scale, img.get_height() * scale)
    )
    return img


def center_horizontally(surface, frame_rect):

    #frame is a pygame.Rect, and defines the area to center in
    width, height = surface.get_size()
    x = (frame_rect.w - width) // 2 + frame_rect.x
    return x

def center_vertically(surface, frame_rect):

    #frame is a pygame.Rect, and defines the area to center in
    width, height = surface.get_size()
    y = (frame_rect.h - height) // 2 + frame_rect.y
    return y

def center_at(surface, pos):

    px, py = pos
    width, height = surface.get_size()

    x = (px - width // 2)
    y = (py - height // 2)

    return (x, y)

def get_center(rect):

    x, y, w, h = rect.x, rect.y, rect.w, rect.h

    return (x + w//2, y + h//2)

def get_center_with_surface(surface, rect):

    x, y = get_center(rect)
    w, h = surface.get_size()

    return (x - w//2, y - h//2)

def get_center_with_rect(outer_rect, inner_rect):

    x, y = get_center(outer_rect)
    w, h = inner_rect.width, inner_rect.height

    return (x - w//2, y - h//2)

def apply_margins(rect, h_margin_percentage=0.0, v_margin_percentage=0.0):

    margin_rect = pygame.Rect(int(rect.width * h_margin_percentage / 2 + rect.x),
                                            int(rect.height * v_margin_percentage / 2 + rect.y),
                                            int(rect.width * (1.0 - h_margin_percentage)),
                                            int(rect.height * (1.0 - v_margin_percentage))
                                        )
    return margin_rect
