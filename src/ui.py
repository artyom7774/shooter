from PIL.ImageFont import FreeTypeFont
from PIL import ImageFont

from src.variables import *

import functools
import pygame
import math
import os

BASE_FONT = "files/fonts/courier.ttf"


def cache(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = args + tuple(kwargs.items())
        if key not in cache:
            cache[key] = func(*args, **kwargs)

        return cache[key]

    return wrapper


@cache
def find_system_font(name: str) -> str:
    return pygame.font.match_font(name)


@cache
def get_font(font_type, font_size) -> "pygame.font.Font":
    if os.path.exists(font_type):
        return pygame.font.Font(font_type, font_size)

    return pygame.font.SysFont(font_type, font_size)


@cache
def get_ttf(font_type: str, font_size: int) -> FreeTypeFont:
    if os.path.exists(font_type):
        return ImageFont.truetype(font_type, font_size)

    if find_system_font(font_type.lower()) is not None:
        ImageFont.truetype(find_system_font(font_type.lower()), font_size)

    print(f"WARNING: {font_type} is not found")

    return ImageFont.load_default()


@cache
def get_text_size(font_type, font_size, text):
    font = get_font(font_type, font_size)

    return font.render(text, True, (0, 0, 0)).get_size()


def print_text(screen, x, y, message, font_size=20, font_type=BASE_FONT, font_color=Color.TEXT_COLOR, alpha=255) -> None:
    font = get_font(font_type, font_size)
    text = font.render(message, True, font_color)
    text.set_alpha(alpha)

    screen.blit(text, (x, y))


@cache
def getAlphaRectSurface(color, w, h, width, border_radius):
    surface = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surface, color, (0, 0, w, h), width, border_radius)

    return surface


def alphaRect(screen, color, rect, width: int = 0, border_radius: int = -1):
    screen.blit(getAlphaRectSurface(color, rect[2], rect[3], width, border_radius), (rect[0], rect[1]))


@cache
def getAlphaCircleSurface(color, radius, width):
    surface = pygame.Surface((2 * radius, 2 * radius), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (radius, radius), radius, width)

    return surface


def alphaCircle(screen, color, pos, radius: int = 0, width: int = 0):
    screen.blit(getAlphaCircleSurface(color, radius, width), (pos[0] - radius, pos[1] - radius))


def circleSegment(screen, color, center, radius, start, end, width=1):
    radius *= 8

    var = min(max(1.0, width * 8), radius * 2)

    size = int(radius * 2 + (var + 2) * 2)
    
    surface = pygame.Surface((size, size), pygame.SRCALPHA)

    steps = max(16, int(abs(end - start) * 1.5))

    outer, inner = [], []
    
    for i in range(steps + 1):
        a = math.radians(start + (end - start) * i / steps)

        outer.append((size / 2 + (radius + var / 2) * math.cos(a), size / 2 - (radius + var / 2) * math.sin(a)))
        inner.append((size / 2 + (radius - var / 2) * math.cos(a), size / 2 - (radius - var / 2) * math.sin(a)))

    pygame.draw.polygon(surface, color, outer + inner[::-1])

    get = max(1, size // 8)
    
    screen.blit(pygame.transform.smoothscale(surface, (get, get)), (center[0] - get // 2, center[1] - get // 2))

@cache
def getAlphaLineSurface(color, first, second, width):
    x1, y1 = first
    x2, y2 = second

    minX = min(x1, x2)
    maxX = max(x1, x2)
    minY = min(y1, y2)
    maxY = max(y1, y2)

    padding = width // 2 + 1

    surface = pygame.Surface((maxX - minX + 2 * padding, maxY - minY + 2 * padding), pygame.SRCALPHA)

    ox = minX - padding
    oy = minY - padding

    pygame.draw.line(surface, color, (x1 - ox, y1 - oy), (x2 - ox, y2 - oy), width)

    return surface


def alphaLine(screen, color, first, second, width: int = 1):
    surface = getAlphaLineSurface(color, first, second, width)

    x1, y1 = first
    x2, y2 = second

    mx = min(x1, x2)
    my = min(y1, y2)

    padding = width // 2 + 1

    pos = (mx - padding, my - padding)

    screen.blit(surface, pos)


def alphaTextLine(screen, color, rect):
    surface = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)

    for i in range(rect[2] // 2):
        pygame.draw.line(surface, (*color, int(255 * (1 - abs(i - rect[2] / 2) / (rect[2] / 2)))), (i, 0), (rect[2] - i, 0))

    screen.blit(surface, (rect[0], rect[1]))


class TLabel:
    def __init__(
            self, game, rect, text, font_size=20, font_type=BASE_FONT, font_color=Color.TEXT_COLOR,
            horizontal: str = "center", vertical: str = "center", alpha: int = 255
    ) -> None:
        self.game = game

        self.rect = rect

        self.text = text

        self.alpha = alpha

        self.font_size = font_size
        self.font_color = font_color
        self.font_type = font_type

        self.horizontal = horizontal
        self.vertical = vertical

        self.ttf = None

        self.tx = 0
        self.ty = 0

        self.ttf = get_ttf(self.font_type, self.font_size)

        self.hstep = self.ttf.getbbox("Ag")[3]

    def update(self) -> None:
        pass

    def draw(self, x: int = None, y: int = None) -> None:
        if x is None:
            x = self.rect[0]

        if y is None:
            y = self.rect[1]

        font = get_font(self.font_type, self.font_size)

        text_surface = font.render(self.text, True, self.font_color)
        text_width, text_height = text_surface.get_size()

        if self.horizontal == "center":
            self.tx = (self.rect[2] - text_width) / 2

        elif self.horizontal == "left":
            self.tx = 4

        elif self.horizontal == "right":
            self.tx = self.rect[2] - text_width - 4

        else:
            raise NameError(f"type {self.horizontal} is not defined")

        if self.vertical == "center":
            py = (self.rect[3] - text_height) / 2

        elif self.vertical == "up":
            py = 2

        elif self.vertical == "down":
            py = self.rect[3] - text_height - 2

        else:
            raise NameError(f"vertical {self.vertical} is not defined")

        print_text(self.game.screen, x + self.tx, y + py, self.text, self.font_size, self.font_type, self.font_color, self.alpha)


class Label:
    def __init__(
            self, game, rect, text, font_size=20, font_type=BASE_FONT, font_color=Color.TEXT_COLOR,
            horizontal: str = "center", vertical: str = "center", alpha: int = 255
    ) -> None:
        self.game = game

        self.rect = rect

        self.text = text

        self.alpha = alpha

        self.font_size = font_size
        self.font_color = font_color
        self.font_type = font_type

        self.horizontal = horizontal
        self.vertical = vertical

        self.tx = 0
        self.ty = 0

    def update(self) -> None:
        pass

    def draw(self, x: int = None, y: int = None) -> None:
        if x is None:
            x = self.rect[0]

        if y is None:
            y = self.rect[1]

        text_width, text_height = get_text_size(self.font_type, self.font_size, self.text)

        if self.horizontal == "center":
            self.tx = (self.rect[2] - text_width) / 2

        elif self.horizontal == "left":
            self.tx = 4

        elif self.horizontal == "right":
            self.tx = self.rect[2] - text_width - 4

        else:
            raise NameError(f"type {self.horizontal} is not defined")

        if self.vertical == "center":
            py = (self.rect[3] - text_height) / 2

        elif self.vertical == "up":
            py = 2

        elif self.vertical == "down":
            py = self.rect[3] - text_height - 2

        else:
            raise NameError(f"vertical {self.vertical} is not defined")

        print_text(self.game.screen, x + self.tx, y + py, self.text, self.font_size, self.font_type, self.font_color, self.alpha)


class TextField:
    def __init__(self, game, rect, text, font_size=20, font_type=BASE_FONT, font_color=Color.TEXT_COLOR, horizontal="center", vertical="center", alpha=255) -> None:
        self.game = game

        self.rect = rect

        self.ax = 0
        self.ay = 0

        self.text = text

        self.font_size = font_size
        self.font_type = font_type
        self.font_color = font_color

        self.horizontal = horizontal
        self.vertical = vertical

        self.alpha = alpha

        self.font = get_font(self.font_type, self.font_size)

        self.text = self.text.split()

        self.out = []

        self.hstep = self.font.size("Ag")[1] + 2
        self.wstep = 0

        while self.font.size((self.wstep + 1) * "_")[0] < self.rect[2]:
            self.wstep += 1

        self.init()

    def init(self) -> None:
        if len(self.text) == 0:
            self.out = []

            return

        l = 0
        r = len(self.text) - 1

        if self.text[0] == "/t":
            self.out = [" " * 3]

        else:
            self.out = [self.text[0]]

        while l < r:
            if len(self.out[len(self.out) - 1]) + len(self.text[l + 1]) + 1 < self.wstep:
                if self.text[l + 1] == "/n":
                    self.out.append("")

                elif self.text[l + 1] == "/t":
                    self.out[len(self.out) - 1] += " " * 4

                elif len(self.out[len(self.out) - 1]) == 0:
                    self.out[len(self.out) - 1] += f"{self.text[l + 1]}"

                else:
                    self.out[len(self.out) - 1] += f" {self.text[l + 1]}"

                l += 1

            else:
                self.out.append("")

        self.ay = self.rect[3] / 2 - (self.font.size("Ag")[1] / 2 * len(self.out))

        var = (len(self.out) - self.rect[3] // self.hstep) * self.hstep

        return var if var > 0 else 0

    def update(self) -> None:
        pass

    def draw(self, x: int = None, y: int = None, ax: int = 0, ay: int = 0) -> None:
        self.init()

        if x is None:
            x = self.rect[0] + ax

        if y is None:
            y = self.rect[1] + ay

        if self.vertical == "center":
            py = (self.rect[3] - len(self.out) * self.hstep) / 2

        elif self.vertical == "up":
            py = 2

        elif self.vertical == "down":
            py = self.rect[3] - len(self.out) * self.hstep - 2

        else:
            raise NameError(f"vertical {self.vertical} is not difined")

        for i, element in enumerate(self.out):
            if self.horizontal == "center":
                text_width, _ = get_text_size(self.font_type, self.font_size, element)
                print_text(self.game.screen, x + (self.rect[2] / 2 - text_width / 2), y + i * self.hstep + py, element, self.font_size, self.font_type, self.font_color, self.alpha)

            elif self.horizontal == "left":
                print_text(self.game.screen, x + 4, y + i * self.hstep + py, element, self.font_size, self.font_type, self.font_color, self.alpha)

            elif self.horizontal == "right":
                text_width, _ = get_text_size(self.font_type, self.font_size, element)
                print_text(self.game.screen, (x + self.rect[2]) - text_width - 4, y + i * self.hstep + py, element, self.font_size, self.font_type, self.font_color, self.alpha)

            else:
                raise NameError(f"horizontal {self.horizontal} is not difined")


class Button:
    def __init__(self, game, base, mouse, click, rect, text=None, frame=None, function=None, font_color=None, anotherFunction=None) -> None:
        self.game = game

        self.base = base
        self.mouse = mouse
        self.click = click

        self.frame = frame

        self.active = None

        self.font_color = font_color if font_color is not None else Color.TEXT_COLOR

        self.rect = rect

        self.text = text if text is not None else Label(game, 0, 0, 0, 0, "")

        self.last = 0

        self.anotherFunction = anotherFunction
        self.function = function

    def update(self) -> None:
        pass

    def draw(self, x: int = None, y: int = None) -> None:
        if x is None:
            x = self.rect[0]

        if y is None:
            y = self.rect[1]

        self.last = 0

        mouse = [var // self.game.capacity for var in self.game.mouse]

        if x < mouse[0] < x + self.rect[2]:
            if y < mouse[1] < y + self.rect[3]:
                if self.game.click[2]:
                    if self.anotherFunction is not None:
                        self.anotherFunction()

                if self.game.click[0]:
                    if self.function is not None:
                        self.function()

                elif pygame.mouse.get_pressed()[0]:
                    self.active = self.click
                    self.last = 2

                else:
                    self.active = self.mouse
                    self.last = 1

            else:
                self.active = self.base

        else:
            self.active = self.base

        try:
            alphaRect(self.game.screen, self.active, [x, y, self.rect[2], self.rect[3]], border_radius=3)

        except:
            pass

        if self.frame is not None:
            alphaRect(self.game.screen, self.frame, [x, y, self.rect[2], self.rect[3]], 2, 3)

        if type(self.text) in (Label, TLabel, TextField):
            self.text.draw(x, y)

        else:
            Label(self.game, (x, y, self.rect[2], self.rect[3]), self.text, font_color=self.font_color).draw()


class ProgressBar:
    def __init__(self, game, x, y, width, height, ramaColor, fillColor, textColor, value, progressWidth=2, radiusWidth=3):
        self.game = game

        self.x = x
        self.y = y

        self.progressWidth = progressWidth
        self.radiusWidth = radiusWidth

        self.width = width
        self.height = height

        self.ramaColor = ramaColor
        self.fillColor = fillColor
        self.textColor = textColor

        self.value = value

    def setValue(self, value):
        self.value = value

    def getValue(self, value):
        self.value = value

    def draw(self, text="", x=0, y=0):
        alphaRect(self.game.screen, self.fillColor, (self.x + x, self.y + y, int(self.width * self.value), self.height), border_radius=self.radiusWidth)
        alphaRect(self.game.screen, self.ramaColor, (self.x + x, self.y + y, self.width, self.height), self.progressWidth, self.radiusWidth)

        Label(self.game, (self.x + x, self.y + y + 2, self.width, self.height), text).draw()
