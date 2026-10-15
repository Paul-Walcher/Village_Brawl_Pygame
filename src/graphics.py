import pygame
import constants
from collections import deque
import re

NL = (None,)

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

def page_by_chars(text, line_length=40, paragraph_length=5, one_page=False):


    if one_page:
        paragraph_length = constants.INFINITE

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

def render_page_from_chars(
    font,
    page,
    frame,
    text_color=constants.Colors.STANDARD_TEXT_COLOR,
    centered=False,
    vertical_centered=False,
    line_margin=5
):
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

def _wrap_colored_chars(chars, line_length):
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
    text,
    line_length=40,
    paragraph_length=5,
    one_page=False
):
    """
    Convert colored text into pages.

    Input:
        [
            ("Hello ", RED),
            ("world!", BLUE),
            (None,),
            ("Another line.", GREEN)
        ]

    Output:
        [
            [
                [("Hello ", RED), ("world!", BLUE)],
                [("Another line.", GREEN)]
            ]
        ]

    Structure:
        pages -> lines -> (text, color) segments
    """

    if line_length < 1:
        raise ValueError("line_length must be at least 1")

    if one_page:
        paragraph_length = constants.INFINITE

    if paragraph_length <= 0:
        raise ValueError("paragraph_length must be positive")

    if not text:
        return []

    # First, reconstruct logical lines from all text segments.
    # Colors are assigned per character so even a word can have
    # multiple colors.
    logical_lines = [[]]

    for item in text:
        if not isinstance(item, (tuple, list)):
            raise TypeError(
                "Each text element must be a tuple (text, color) "
                "or a newline marker (None,)"
            )

        if len(item) == 1 and item[0] is None:
            logical_lines.append([])
            continue

        if len(item) != 2:
            raise ValueError(
                "Each text segment must be (text, color), "
                "or a newline marker (None,)"
            )

        segment_text, color = item

        if not isinstance(segment_text, str):
            raise TypeError("Segment text must be a string")

        logical_lines[-1].extend(
            (char, color) for char in segment_text
        )

    # Wrap each logical line, then combine adjacent characters
    # with the same color into rendering-friendly segments.
    colored_lines = []

    for chars in logical_lines:
        wrapped_lines = _wrap_colored_chars(chars, line_length)

        for wrapped_line in wrapped_lines:
            colored_lines.append(
                _color_chars_to_runs(wrapped_line)
            )

    # Divide the lines into pages.
    pages = []
    current_page = []

    for line in colored_lines:
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
    line_margin=5
):
    """
    Render a page returned by page_by_chars_color().

    Returns a list of (pygame.Surface, position) pairs.
    Each colored text segment is rendered separately.
    """

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

def scale_image(img, scale):

    return pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))


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
