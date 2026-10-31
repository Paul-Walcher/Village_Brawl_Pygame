from __future__ import annotations
from typing import Callable

import pygame
import constants
from constants import fequal, color_t
from collections import deque
import re
"""
This module handles graphical rendering
and graphical calculations.
"""

NL: tuple = (None,)

"""
Type definitions
"""

type text_t = list[str]
"""
Text type. This is what is passed to page_by_chars() to
create pages.
"""
type colored_text_t = list[ tuple[ str, color_t ] ]
"""
Colored text type. This is what is passed to page_by_chars_color() to
create pages.
"""
type page_t = list[str]
"""
Type definition for a uncolored page.
"""
EMPTY_PAGE: Callable[[], page_t] = lambda: []
"""
This generates an empty page.
"""
type colored_page_t = list[list[ tuple[str, color_t] ]]
"""
Type definition for a colored page.
"""
EMPTY_COLORED_PAGE: Callable[[], colored_page_t] = lambda: []
"""
This generates an empty colored page.
"""
type surface_with_position_t = tuple[pygame.Surface, tuple[int, int]]
"""
Type for a (surface, (x, y)=position) tuple.
"""
type rendered_surface_position_tuples_t = list[surface_with_position_t]
"""
A list of rendered (surface, position) tuples
"""

def copy_rendered_surface_position_tuples(rspt: rendered_surface_position_tuples_t) -> rendered_surface_position_tuples_t:
    """
    Creates a copy of the rendered_surface_position_tuples.
    """
    return [(surf.copy(), pos) for surf, pos in rspt]

class _NewPage:
    """Marker requesting a page break after a given number of blank lines."""

    def __init__(self, empty_lines: int = 0):
        if not isinstance(empty_lines, int) or empty_lines < 0:
            raise ValueError("NP(x) requires a non-negative integer")
        self.empty_lines = empty_lines


def NP(x: int = 0):
    """Insert x empty lines, then start a new page."""
    return _NewPage(x)


def _is_newline(item):
    """checks if item is graphics.NL"""
    return isinstance(item, (tuple, list)) and len(item) == 1 and item[0] is None

def render_text(font: pygame.font.Font, fontsize: int, text: str, color: tuple[int, int, int]=constants.Colors.WHITE):
    """
    Gives back a rendered text surface.
    """

    f = pygame.font.Font(font, fontsize)
    surface = f.render(text, False, color)

    return surface

def text_size(font: pygame.font.Font, fontsize: int, text: str) -> tuple[int, int]:
    """
    Returns the (width, height) of text if rendered by font with fontsize.
    """
    f = pygame.font.Font(font, fontsize)
    return f.size(text)



def get_fontsize(font: pygame.font.Font, lines: list[str], frame: pygame.Rect, line_margin: int=5, min_size: int=1, max_size: int=1024) -> int:
    """
    Returns the largest font size for which all lines fit inside frame.

    font      : Pygame font path / filename

    lines     : list of strings representing the current page

    frame     : pygame.Rect

    line_margin: vertical distance added between lines

    min_size: minimal size of the font

    max_size: maximal size of the font
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

def page_by_chars(text: str, line_length: int=40, paragraph_length: int=5, one_page: bool=False) -> list[list[str]]:
    """
    Wrap plain text into pages; accepts NL and NP(x) markers in a list.
    line_length is how many characters are added per line,
    paragraph_length how many lines per page are shown.
    """
    if one_page:
        paragraph_length = constants.INFINITE

    if paragraph_length <= 0:
        raise ValueError("paragraph_length must be positive")

    # Strings retain the original interface. Lists/iterables may contain
    # strings, NL, and NP(x) markers.
    if isinstance(text, str):
        items = []
        for i, line in enumerate(text.splitlines()):
            if i:
                items.append(NL)
            items.append(line)
    else:
        items = list(text)

    pages = []
    current_page = []
    current_line = ""

    def finish_line():
        nonlocal current_line, current_page, pages
        current_page.append(current_line)
        current_line = ""
        if len(current_page) >= paragraph_length:
            pages.append(current_page)
            current_page = []

    def add_text(value):
        nonlocal current_line
        for word in value.split(" "):
            if len(current_line) + len(word) <= line_length:
                current_line += word + " "
            else:
                finish_line()
                current_line = word

    for item in items:
        if isinstance(item, _NewPage):
            if current_line or current_page:
                finish_line()
            for _ in range(item.empty_lines):
                current_page.append("")
                if len(current_page) >= paragraph_length:
                    pages.append(current_page)
                    current_page = []
            if current_page:
                pages.append(current_page)
                current_page = []
            current_line = ""
        elif _is_newline(item):
            finish_line()
        elif isinstance(item, str):
            add_text(item)
        else:
            raise TypeError("Expected text, NL, or NP(x) marker")

    if current_line:
        current_page.append(current_line)
    if current_page:
        pages.append(current_page)

    return pages

def render_page_from_chars(
    font: pygame.font.Font,
    page: list[str],
    frame: pygame.Rect,
    text_color: tuple[int, int, int]=constants.Colors.STANDARD_TEXT_COLOR,
    centered: bool=False,
    vertical_centered: bool=False,
    line_margin: int=5,
    line_margin_as_percentage=None
) -> list[tuple[pygame.Surface, tuple[int, int]]]:
    """
    font: the the page will be rendered in
    page: the list of strings that constitutes the page
    frame: the rect the text will be rendered into
    text_color: color of the text
    centered: if the text should be centered horizontally
    vertical_centered: if the text should be centererd vertically
    line_margin: distance between lines

    returns a list of (surface, position) tuples where position = (x, y)
    """

    if line_margin_as_percentage is not None:
        line_margin = int(frame.height * line_margin_as_percentage)

    fsize = get_fontsize(font, page, frame, line_margin=line_margin)
    trend = []
    cy = 0


    rendered_lines = [
        render_text(font, fsize, line, text_color)
        for line in page
    ]

    # Calculate vertical offset to center all lines within the frame
    total_height = sum(rend.get_height() for rend in rendered_lines)
    total_height += max(0, len(rendered_lines) - 1) * line_margin

    if vertical_centered:
        cy = (frame.height - total_height) // 2

    for rend in rendered_lines:
        pos = (frame.x, frame.y + cy)

        # Horizontal centering (unchanged)
        if centered:
            pos = (
                int(frame.x + (frame.width - rend.get_width()) // 2),
                frame.y + cy
            )

        trend.append((rend, pos))
        cy += rend.get_height() + line_margin

    return trend

def _wrap_colored_chars(chars, line_length: int):
    """Wrap a line of (character, color) pairs, preserving word boundaries."""
    if not chars:
        return [[]]

    wrapped = []
    remaining = list(chars)

    while len(remaining) > line_length:
        # Include one extra character so a space just after the limit
        # can be used as a word boundary.
        window = remaining[:line_length + 1]

        last_break = None
        seen_content = False

        for i, (char, _) in enumerate(window):
            if char.isspace():
                if seen_content:
                    last_break = i
            else:
                seen_content = True

        if last_break is not None:
            # Break at the last available whitespace.
            wrapped.append(remaining[:last_break])
            remaining = remaining[last_break + 1:]

            # Discard leading whitespace on the next line.
            while remaining and remaining[0][0].isspace():
                remaining = remaining[1:]

        else:
            # No word boundary available: split a long word.
            wrapped.append(remaining[:line_length])
            remaining = remaining[line_length:]

    if remaining or not wrapped:
        wrapped.append(remaining)

    return wrapped


def _color_chars_to_runs(chars):
    """Convert (character, color) pairs into (text, color) segments."""
    if not chars:
        return []

    runs = []
    current_color = chars[0][1]
    current_text = []

    for char, color in chars:
        if color != current_color:
            runs.append(("".join(current_text), current_color))
            current_text = []
            current_color = color

        current_text.append(char)

    if current_text:
        runs.append(("".join(current_text), current_color))

    return runs


def page_by_chars_color(
    text: list[tuple[str, tuple[int, int, int]]],
    line_length: int=40,
    paragraph_length: int=5,
    one_page: bool=False
):
    """
    Convert colored text into pages; accepts NL and NP(x) markers.

    Text segments use (text, color). NL starts a new line. NP(x) inserts
    x empty lines before forcing a page break.
    """
    if line_length < 1:
        raise ValueError("line_length must be at least 1")

    if one_page:
        paragraph_length = constants.INFINITE

    if paragraph_length <= 0:
        raise ValueError("paragraph_length must be positive")

    if not text:
        return []

    logical_lines = [[]]
    forced_breaks = set()

    for item in text:
        if isinstance(item, _NewPage):
            for _ in range(item.empty_lines):
                logical_lines.append([])
            forced_breaks.add(len(logical_lines))
            logical_lines.append([])
            continue

        if _is_newline(item):
            logical_lines.append([])
            continue

        if not isinstance(item, (tuple, list)):
            raise TypeError(
                "Each element must be (text, color), NL, or NP(x)"
            )

        if len(item) != 2:
            raise ValueError(
                "Each text segment must be (text, color), or use NL/NP(x)"
            )

        segment_text, color = item
        if not isinstance(segment_text, str):
            raise TypeError("Segment text must be a string")

        logical_lines[-1].extend((char, color) for char in segment_text)

    colored_lines = []
    break_before = set()
    for logical_index, chars in enumerate(logical_lines):
        if logical_index in forced_breaks:
            break_before.add(len(colored_lines))
        for wrapped_line in _wrap_colored_chars(chars, line_length):
            colored_lines.append(_color_chars_to_runs(wrapped_line))

    pages = []
    current_page = []
    for index, line in enumerate(colored_lines):
        if index in break_before and current_page:
            pages.append(current_page)
            current_page = []

        if len(current_page) >= paragraph_length:
            pages.append(current_page)
            current_page = []

        current_page.append(line)

    if current_page:
        pages.append(current_page)

    return pages

def render_page_from_chars_color(
    font,
    page,
    frame,
    text_color=constants.Colors.STANDARD_TEXT_COLOR,
    centered=False,
    vertical_centered=False,
    line_margin=5,
    line_margin_as_percentage=None
):
    """
    Render a page returned by page_by_chars_color().

    Returns a list of (pygame.Surface, position) pairs.
    Each colored text segment is rendered separately.

    See render_page_from_chars.
    """

    if line_margin_as_percentage is not None:
        line_margin = int(frame.height * line_margin_as_percentage)

    if not page:
        return []

    # Build plain strings for get_fontsize().
    plain_page = [
        "".join(segment_text for segment_text, _ in line) or " "
        for line in page
    ]

    fsize = get_fontsize(
        font,
        plain_page,
        frame,
        line_margin=line_margin
    )

    # Used to determine the correct height for empty lines.
    empty_line_surface = render_text(
        font, fsize, " ", text_color
    )

    rendered_lines = []
    line_widths = []
    line_heights = []

    # Render each color segment independently.
    for line in page:
        rendered_segments = []

        for segment_text, color in line:
            if not segment_text:
                continue

            color = text_color if color is None else color

            surface = render_text(
                font,
                fsize,
                segment_text,
                color
            )

            rendered_segments.append(surface)

        rendered_lines.append(rendered_segments)

        line_widths.append(
            sum(surface.get_width() for surface in rendered_segments)
        )

        line_heights.append(
            max(
                (
                    surface.get_height()
                    for surface in rendered_segments
                ),
                default=empty_line_surface.get_height()
            )
        )

    # Calculate the total height for vertical centering.
    total_height = sum(line_heights)
    total_height += max(0, len(page) - 1) * line_margin

    cy = (
        (frame.height - total_height) // 2
        if vertical_centered
        else 0
    )

    trend = []

    for i, rendered_segments in enumerate(rendered_lines):
        line_width = line_widths[i]

        # Center the complete line, not each individual segment.
        cx = (
            frame.x + (frame.width - line_width) // 2
            if centered
            else frame.x
        )

        for surface in rendered_segments:
            trend.append((
                surface,
                (int(cx), int(frame.y + cy))
            ))

            cx += surface.get_width()

        cy += line_heights[i] + line_margin

    return trend


def render_image(img_path: str, dimensions: tuple[float, float]=None, scaling_function=pygame.transform.scale) -> pygame.Surface:
    """
    Renders the image onto a surface, then scales it up or down to dimensions.
    if dimensions is not None.
    """

    img = pygame.image.load(img_path).convert_alpha()
    if dimensions is not None:
        img = scaling_function(img, dimensions)
    return img

def render_image_scale(img_path: str, scale: tuple[float, float], scale_function=pygame.transform.scale) -> pygame.Surface:
    """
    scales the loaded image by scale.
    """

    img = pygame.image.load(img_path).convert_alpha()
    img = scale_function(img,
                (img.get_width() * scale, img.get_height() * scale)
    )
    return img

def scale_surface(img: pygame.Surface, scale: float, scale_function=pygame.transform.scale) ->  pygame.Surface:
    """
    scales the surface by scale.
    """
    return scale_function(img, (int(img.get_width() * scale), int(img.get_height() * scale)))


def center_horizontally(surface: pygame.Surface, frame_rect: pygame.Rect) -> pygame.Rect:
    """
    Returns the x value if surface was to be centered in frame_rect.
    """
    #frame is a pygame.Rect, and defines the area to center in
    width, height = surface.get_size()
    x = (frame_rect.w - width) // 2 + frame_rect.x
    return x

def center_vertically(surface: pygame.Surface, frame_rect: pygame.Rect) -> pygame.Rect:
    """
    Returns the y value if surface was to be centered in frame_rect.
    """
    #frame is a pygame.Rect, and defines the area to center in
    width, height = surface.get_size()
    y = (frame_rect.h - height) // 2 + frame_rect.y
    return y

def center_at(surface: pygame.Surface, pos: tuple[int, int]) -> tuple[int, int]:
    """
    Returns the (x, y) if surface was to be centered at center point pos.
    """

    px, py = pos
    width, height = surface.get_size()

    x = (px - width // 2)
    y = (py - height // 2)

    return (x, y)

def get_center(rect: pygame.Rect) -> tuple[int, int]:
    """
    Returns the center of rect as (x, y)
    """
    x, y, w, h = rect.x, rect.y, rect.w, rect.h

    return (x + w//2, y + h//2)

def get_center_with_surface(surface: pygame.Surface, rect: pygame.Rect) -> tuple[int, int]:
    """
    Returns the position surface needs to be rendered at to be centered at the rects center.
    """

    x, y = get_center(rect)
    w, h = surface.get_size()

    return (x - w//2, y - h//2)

def get_center_with_surface_as_rect(surface: pygame.Surface, rect: pygame.Rect) -> pygame.Rect:
    """
    Returns a frame defining the surfaces position, width and height
    after it was centered in rect.
    """

    x, y = get_center_with_surface(surface, rect)
    return pygame.Rect(x, y, surface.get_width(), surface.get_height())

def get_center_with_rect(outer_rect: pygame.Rect, inner_rect: pygame.Rect) -> tuple[int, int]:
    """
    Returns the position inner_rect needs to be rendered at to be centered at the rects center.
    """

    x, y = get_center(outer_rect)
    w, h = inner_rect.width, inner_rect.height

    return (x - w//2, y - h//2)

def get_center_with_rect_as_rect(outer_rect: pygame.Rect, inner_rect: pygame.Rect) -> pygame.Rect:
    """
    Returns a new rectangle, representing inner rect being centered inside outer_rect.
    """

    x, y = get_center_with_rect(outer_rect, inner_rect)

    return pygame.Rect(x, y, inner_rect.width, inner_rect.height)

def apply_margins(rect: pygame.Rect, h_margin_percentage: float=0.0, v_margin_percentage: float=0.0) -> pygame.Rect:
    """
    Returns rect after applying the margin percentages.

    Negative margins mean expanding the frame by the given percentage,
    positive margins mean decreasing the frame by the given percentage.
    """
    if h_margin_percentage > 1.0 or v_margin_percentage > 1.0:
        raise RuntimeError("Margins can not be greater than 1.0 (Returned frame cant have negative size)")

    margin_rect = pygame.Rect(  int(rect.x + rect.width * h_margin_percentage / 2),
                                int(rect.y + rect.height * v_margin_percentage / 2),
                                int(rect.width * (1.0 - h_margin_percentage)),
                                int(rect.height * (1.0 - v_margin_percentage))
                                )
    return margin_rect

def split_rect_horizontally(rect: pygame.Rect, percentages: list[float]) -> list[pygame.Rect]:
    """
    Splits the given rect into rects where each rect starts where the last ends,
    and has length: int(percentages[rect_index] * rect.width).
    Returns a list of the split rects going to the right.
    Percentages must sum close to 1.0.

    Example:

    rect = pygame.Rect(100, 100, 1000, 300)
    percentages = [0.2, 0.7, 0.1]

    result = split_rect_horizontally(rect, percentages)

    result = [pygame.Rect(100, 100, 200, 300), pygame.Rect(300, 100, 700, 300), pygame.Rect(1000, 100, 100, 300)]
    """
    if not fequal(sum(percentages), 1.0):
        raise RuntimeError("The percentages must sum up to 1 to split the pygame.Rect")

    split_rects = []

    cx = 0
    for p in percentages[:-1]:

        nr = rect.copy()
        nr.x += cx
        nr.width = int(nr.width * p)

        cx += nr.width
        split_rects.append(nr)

    nr = rect.copy()
    nr.x += cx
    nr.width = (rect.width - cx)
    split_rects.append(nr)

    return split_rects

def split_rect_vertically(rect: pygame.Rect, percentages: list[float]) -> list[pygame.Rect]:
    """
    Splits the given rect into rects where each rect starts where the last ends,
    and has height: int(percentages[rect_index] * rect.height).
    Returns a list of the split rects going down.
    Percentages must sum close to 1.0.

    Example:

    rect = pygame.Rect(100, 100, 1000, 300)
    percentages = [0.2, 0.7, 0.1]

    result = split_rect_horizontally(rect, percentages)

    result = [pygame.Rect(100, 100, 1000, 60), pygame.Rect(100, 160, 1000, 210), pygame.Rect(1000, 370, 1000, 30)]
    """
    if not fequal(sum(percentages), 1.0):
        raise RuntimeError("The percentages must sum up to 1 to split the pygame.Rect")

    split_rects = []

    cy = 0
    for p in percentages[:-1]:

        nr = rect.copy()
        nr.y += cy
        nr.height = int(nr.height * p)

        cy += nr.height
        split_rects.append(nr)

    nr = rect.copy()
    nr.y += cy
    nr.height = (rect.height - cy)
    split_rects.append(nr)

    return split_rects

def scale_image_to_frame(img_surf: pygame.Surface, frame: pygame.Rect, smoothscale=False) -> pygame.Surface:
    """
    Returns a version of img_surf that is scaled to fit into frame.
    """

    w, h = frame.width, frame.height
    w2h = img_surf.get_width() / img_surf.get_height()
    sw, sh = 0, 0

    if w2h > 1.0:
        if w <= h:
            sw = w
            sh = int((1.0 / w2h) * w)
        else:
            ph = int((1.0 / w2h) * w)
            if ph > h:
                sh = h
                sw = int(w2h * h)
            else:
                sw = w
                sh = int((1.0 / w2h) * w)
    else:
        if h <= w:
            sh = h
            sw = int(w2h * h)
        else:
            pw = int(w2h * h)
            if pw > w:
                sw = w
                sh = int((1.0 / w2h) * w)
            else:
                sw = int(w2h * h)
                sh = h

    return (pygame.transform.scale(img_surf, (sw, sh)) if not smoothscale else pygame.transform.smoothscale(img_surf, (sw, sh)))

def img_load_and_position(img_path: str, frame: pygame.Rect) -> tuple[pygame.Surface, tuple[int, int]]:
    """
    Given the image path and the frame it should be rendered into,
    this function returns the surface, scaled to fit into the frame and the position
    for which it will be centered at frame. This uses pygame.transform.scale.
    """

    img = render_image(img_path)
    img = scale_image_to_frame(img, frame)
    img_pos = get_center_with_surface(img, frame)

    return (img, img_pos)

def img_load_and_position_smoothscale(img_path: str, frame: pygame.Rect) -> tuple[pygame.Surface, tuple[int, int]]:
    """
    Given the image path and the frame it should be rendered into,
    this function returns the surface, scaled to fit into the frame and the position
    for which it will be centered at frame. This uses pygame.transform.smoothscale.
    """

    img = render_image(img_path)
    img = scale_image_to_frame(img, frame, smoothscale=True)
    img_pos = get_center_with_surface(img, frame)

    return (img, img_pos)
