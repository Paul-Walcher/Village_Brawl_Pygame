"""
Global constants
"""
from __future__ import annotations
from typing import Callable, Any

import os
import sys
import pygame

pygame.init()

"""
Types
"""
type color_t = tuple[int, int, int] | tuple[int, int, int, int]

EPSILON = 10E-6
"""
constant for small differences, e.g.
two floats are considered equal when
their difference is less than EPSILON
"""

fequal: Callable[[float, float], bool] = lambda a, b: (abs(a-b) <= EPSILON)
"""
Returns True if the two floats are considered equal.
This is true when abs(a -b) <= EPSILON
"""

WIDTH, HEIGHT = pygame.display.get_desktop_sizes()[0]
"""
Full dimensions of the screen.
"""

FULLSCREEN: pygame.Rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
"""
The pygame.Rect that specifies the fullscreen dimension.
"""

__ADDITIONAL_LOAD_TIME__: float = 500#ms
"""
The additional time that the loading screen will be loading.
"""

BASE_ASSET_PATH: str = "BaseAssets"
STANDARD_IMAGE_PATH: str = os.path.join(BASE_ASSET_PATH, "StandardImages")
CARD_IMAGE_PATH: str = os.path.join(BASE_ASSET_PATH, "CardImages")
ICON_IMAGE_PATH: str = os.path.join(BASE_ASSET_PATH, "Icons")
FONT_PATH: str = os.path.join(BASE_ASSET_PATH, "Fonts")


SIMAGE: Callable[[str], str] = lambda x: os.path.join(STANDARD_IMAGE_PATH, x)
"""
SIMAGE(x.png) gives you the path to the file x.png,
where x.png is stored in STANDARD_IMAGE_PATH.
"""
CIMAGE: Callable[[str], str] = lambda x: os.path.join(CARD_IMAGE_PATH, x)
"""
CIMAGE(x.png) gives you the path to the file x.png,
where x.png is stored in CARD_IMAGE_PATH.
"""
IIMAGE: Callable[[str], str] = lambda x: os.path.join(ICON_IMAGE_PATH, x)
"""
IIMAGE(x.png) gives you the path to the file x.png,
where x.png is stored in ICON_IMAGE_PATH.
"""

INFINITE: int = sys.maxsize
"""
Value considered infinite.
"""

PLAYSETS_FOLDER: str = "playsets"

INTRO_IMAGES: list[str] = [SIMAGE(x) for x in ["Wood.png", "Stone.png", "Pebble.png", "Twig.png"]]
"""
Paths to the images shown on the intro screen.
"""

STANDARD_BACKSIDES: Callable[[str], str] = lambda x: [CIMAGE("standard_backside.png") for i in range(x)]
"""
Function that returns a list of n standard image backsides.
"""

#Icon images
MENU_BUTTON_UNFOCUSED_IMAGE: str = os.path.join(ICON_IMAGE_PATH, "Menu_Button_Unfocused.png")
MENU_BUTTON_FOCUSED_IMAGE: str = os.path.join(ICON_IMAGE_PATH, "Menu_Button_Focused.png")


HASH_VALUE: int = 1
"""
constant internal value for R_ID hash function.
"""

def R_ID() -> int:
    """
    Returns a unique ID.
    """
    global HASH_VALUE

    x: int = HASH_VALUE
    HASH_VALUE += 1

    return hash(str(x))


class Alpha:
    """
    Stores standardized alpha values.
    """

    ZERO = 0

    LEVEL_1 = 30
    LEVEL_2 = 60
    LEVEL_3 = 100

    HALF_FULL = 127

    LEVEL_4 = 160
    LEVEL_5 = 200
    LEVEL_6 = 230

    FULL = 255

class Colors:
    """
    Stored Colors.
    """

    T = lambda c: (*c, 255)
    """
    Gives a color an alpha dimension.
    """

    TRANSPARENT = (0, 0, 0, 0)

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BRIGHT_BLUE = (0, 150, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    DARK_CYAN = (0, 114, 114)
    ULTRA_DARK_CYAN = (0, 38, 38)
    LIGHT_ORANGE = (255, 144, 0)
    GRAY = (127, 127, 127)
    DARK_GRAY = (109, 109, 109)
    DARK_SLATE_GRAY = (47, 79, 79)
    MAGENTA = (255, 0, 255)
    DARK_MAGENTA = (139, 0, 139)
    LILAC = (253, 61, 245)
    ORANGE = (255, 165, 0)

    STANDARD_TEXT_COLOR = WHITE
    MAX_PER_DECK_COLOR = YELLOW
    KEEP_DURATION_COLOR = BLUE


class Fonts:
    """
    saved fonts.
    """

    MINECRAFT = os.path.join(FONT_PATH, "Minecraft.ttf")

    STANDARD_FONT = MINECRAFT

class Fontsizes:

    """
    Standardized fontsizes.
    """

    fscale = lambda x: int(x * HEIGHT * (1/1080))

    TINY = fscale(10)
    SMALL = fscale(20)
    AVERAGE = fscale(50)
    BIG = fscale(80)
    HUGE = fscale(120)

    SMALL_HEADLINE = fscale(140)
    BIG_HEADLINE = fscale(200)

class KeyAlternatives:

    """
    Bindable Keys used as alternatives.
    """

    ENTER_ALTERNATIVE = pygame.K_o
    BACK_KEY = pygame.K_k

    UP_ALTERNATIVE = pygame.K_w
    DOWN_ALTERNATIVE = pygame.K_s
    LEFT_ALTERNATIVE = pygame.K_a
    RIGHT_ALTERNATIVE = pygame.K_d

    SHOW_IMAGE_KEY = pygame.K_LALT
