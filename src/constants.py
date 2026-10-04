"""
Global constants
"""
import os
import pygame

BASE_ASSET_PATH = "BaseAssets"
STANDARD_IMAGE_PATH = os.path.join(BASE_ASSET_PATH, "StandardImages")
CARD_IMAGE_PATH = os.path.join(BASE_ASSET_PATH, "CardImages")
FONT_PATH = os.path.join(BASE_ASSET_PATH, "Fonts")

SIMAGE = lambda x: os.path.join(STANDARD_IMAGE_PATH, x)
CIMAGE = lambda x: os.path.join(CARD_IMAGE_PATH, x)

PLAYSETS_FOLDER = "playsets"

INTRO_IMAGES = [SIMAGE(x) for x in ["Wood.png", "Stone.png", "Pebble.png", "Twig.png"]]



class Colors:

    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    LIGHT_ORANGE = (255, 144, 0)

class Fonts:

    MINECRAFT = os.path.join(FONT_PATH, "Minecraft.ttf")

class Fontsizes:

    SMALL = 20
    AVERAGE = 50
    BIG = 80
    HUGE = 120

    BIG_HEADLINE = 200

class KeyAlternatives:

    ENTER_ALTERNATIVE = pygame.K_o

    UP_ALTERNATIVE = pygame.K_w
    DOWN_ALTERNATIVE = pygame.K_s
    LEFT_ALTERNATIVE = pygame.K_a
    RIGHT_ALTERNATIVE = pygame.K_d
