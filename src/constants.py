"""
Global constants
"""
import os
import sys
import pygame

pygame.init()

EPSILON = 10E-6

fequal = lambda a, b: (abs(a-b) <= EPSILON)

WIDTH, HEIGHT = pygame.display.get_desktop_sizes()[0]
FULLSCREEN = pygame.Rect(0, 0, WIDTH, HEIGHT)

__ADDITIONAL_LOAD_TIME__ = 500#ms
BASE_ASSET_PATH = "BaseAssets"
STANDARD_IMAGE_PATH = os.path.join(BASE_ASSET_PATH, "StandardImages")
CARD_IMAGE_PATH = os.path.join(BASE_ASSET_PATH, "CardImages")
ICON_IMAGE_PATH = os.path.join(BASE_ASSET_PATH, "Icons")
FONT_PATH = os.path.join(BASE_ASSET_PATH, "Fonts")

SIMAGE = lambda x: os.path.join(STANDARD_IMAGE_PATH, x)
CIMAGE = lambda x: os.path.join(CARD_IMAGE_PATH, x)
IIMAGE = lambda x: os.path.join(ICON_IMAGE_PATH, x)

INFINITE = sys.maxsize

PLAYSETS_FOLDER = "playsets"

INTRO_IMAGES = [SIMAGE(x) for x in ["Wood.png", "Stone.png", "Pebble.png", "Twig.png"]]
STANDARD_BACKSIDES = lambda x: [CIMAGE("standard_backside.png") for i in range(x)]

#Icon images
MENU_BUTTON_UNFOCUSED_IMAGE = os.path.join(ICON_IMAGE_PATH, "Menu_Button_Unfocused.png")
MENU_BUTTON_FOCUSED_IMAGE = os.path.join(ICON_IMAGE_PATH, "Menu_Button_Focused.png")


HASH_VALUE = 1

def R_ID():
    global HASH_VALUE
    x = HASH_VALUE
    HASH_VALUE += 1
    return hash(str(x))


class Alpha:

    ZERO = 0

    LEVEL_1 = 30
    LEVEL_2 = 60
    LEVEL_3 = 100

    HALF_FULL = 127

    LEVEL_4 = 160
    LEVEL_5 = 200
    LEVEL_6 = 230

    FULL = 255

class FrameDataID:

    GAMEINFO = "Gameinfo"
    MODULES = "Modules"
    STACK = "Stack"
    CURRENT_FRAME = "Current Frame"

class Colors:

    T = lambda c: (*c, 255)

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

    STANDARD_TEXT_COLOR = WHITE
    MAX_PER_DECK_COLOR = YELLOW
    KEEP_DURATION_COLOR = BLUE


class Fonts:

    MINECRAFT = os.path.join(FONT_PATH, "Minecraft.ttf")

class Fontsizes:

    fscale = lambda x: int(x * HEIGHT * (1/1080))

    TINY = fscale(10)
    SMALL = fscale(20)
    AVERAGE = fscale(50)
    BIG = fscale(80)
    HUGE = fscale(120)

    SMALL_HEADLINE = fscale(140)
    BIG_HEADLINE = fscale(200)

class KeyAlternatives:

    ENTER_ALTERNATIVE = pygame.K_o
    BACK_KEY = pygame.K_k

    UP_ALTERNATIVE = pygame.K_w
    DOWN_ALTERNATIVE = pygame.K_s
    LEFT_ALTERNATIVE = pygame.K_a
    RIGHT_ALTERNATIVE = pygame.K_d

    SHOW_IMAGE_KEY = pygame.K_LALT
