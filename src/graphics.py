import pygame
import constants

def render_text(font, fontsize, text, color=constants.Colors.WHITE):

    f = pygame.font.Font(font, fontsize)
    surface = f.render(text, False, color)

    return surface

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
