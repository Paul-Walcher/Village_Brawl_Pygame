import pygame
import constants

def render_text(font, fontsize, text, color=constants.Colors.WHITE):

    f = pygame.font.Font(font, fontsize)
    surface = f.render(text, False, color)

    return surface

def text_size(font, fontsize, text):

    f = pygame.font.Font(font, fontsize)
    return f.size(text)

def get_fontsize(font, text, frame_dim, max_font=500):
    """
    finds the font that fits into the frame
    """

    last_fontsize = 1
    width, height = frame_dim.width, frame_dim.height

    while (last_fontsize < max_font):

        w, h = text_size(font, last_fontsize + 1, text)
        if w > width or h > height:
            break

        last_fontsize += 1

    return last_fontsize


def to_pages(font, fontsize, frame, text, color=constants.Colors.WHITE, wmargin=0, hmargin=0, line_margin=5):

    f = pygame.font.Font(font, fontsize)
    x, y, width, height = frame.x, frame.y, frame.w, frame.h

    lines = text.splitlines()
    pages = []
    #a page consists of a list of (fontsurface, position)

    cpage = []
    cy = 0

    while lines:

        cline = lines.pop(0)
        split_index = len(cline)

        rsize = f.size(cline[:split_index])
        rw, rh = rsize

        if (cy + rh) > (height - 2*hmargin):
            pages.append(cpage)
            cpage = []
            cy = 0
            continue

        while rw > (width - 2*wmargin)  and split_index > 0:

            split_index -= 1
            rsize = f.size(cline[:split_index])
            rw, rh = rsize

        s1, s2 = cline[:split_index], cline[split_index:]

        frend = f.render(s1, False, color)
        pos = (x + wmargin, y+cy+hmargin)

        cpage.append((frend, pos))
        if len(s2) > 0:
            lines.insert(0, s2)

        cy += rh + line_margin

    return pages

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

def apply_margins(rect, h_margin_percentage=0.0, v_margin_percentage=0.0):

    margin_rect = pygame.Rect(int(rect.width * h_margin_percentage / 2),
                                            int(rect.height * v_margin_percentage / 2),
                                            int(rect.width * (1.0 - h_margin_percentage)),
                                            int(rect.height * (1.0 - v_margin_percentage))
                                        )
    return margin_rect
