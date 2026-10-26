from src.net.protocol import DEFAULT_PORT

from src.variables import *
from src.ui import *

import pygame
import json


def parseAddress(text):
    text = text.strip()

    host, _, value = text.rpartition(":") if ":" in text else (text, "", "")

    if not host:
        raise ValueError("Enter server address, e.g. 192.168.0.10:3951")

    if " " in host:
        raise ValueError("Address must not contain spaces")

    if value == "":
        return host, DEFAULT_PORT

    if not value.isdigit() or not 1 <= int(value) <= 65535:
        raise ValueError("Port must be a number from 1 to 65535")

    return host, int(value)


class InputField:
    def __init__(self, game, rect, title, text="", limit=40):
        self.game = game

        self.rect = rect
        self.title = title
        self.text = text
        self.limit = limit

        self.active = False

    def type(self, text):
        for char in text:
            if char.isprintable() and char.isascii() and len(self.text) < self.limit:
                self.text += char

    def backspace(self):
        self.text = self.text[:-1]

    def paste(self):
        try:
            pygame.scrap.init()

            data = pygame.scrap.get(pygame.SCRAP_TEXT)

            if data:
                self.type(data.decode("utf-8", "ignore").replace("\x00", "").strip().splitlines()[0])

        except Exception:
            pass

    def draw(self):
        x, y, width, height = self.rect

        mouse = [var // self.game.capacity for var in self.game.mouse]

        if self.game.click[0]:
            self.active = x < mouse[0] < x + width and y < mouse[1] < y + height

        color = Color.PLAYER_COLOR if self.active else (130, 130, 130)

        alphaRect(self.game.screen, (*Color.PLAYER_COLOR, 30 if self.active else 12), (x, y, width, height), border_radius=3)
        alphaRect(self.game.screen, (*color, 255), (x, y, width, height), 2, 3)

        print_text(self.game.screen, x, y - 20, self.title, 16, BASE_FONT, (170, 170, 170))

        text = self.text + ("_" if self.active and (pygame.time.get_ticks() // 500) % 2 == 0 else "")

        print_text(self.game.screen, x + 10, y + (height - 22) // 2 + 2, text, 22, BASE_FONT, Color.PLAYER_COLOR)


class OnlineMenu:
    def __init__(self, game):
        self.game = game

        self.error = ""

        width = 300

        left = game.width // 2 - width // 2

        self.name = InputField(game, (left, 185, width, 50), "Name", game.net.name, 16)
        self.address = InputField(game, (left, 280, width, 50), "Server", f"{game.net.host}:{game.net.port}", 60)

        self.name.active = True

        def button(rect, text, function):
            return Button(game, (0, 0, 0, 0), (*Color.PLAYER_COLOR, 60), (*Color.PLAYER_COLOR, 120), rect, text, Color.PLAYER_COLOR, function=function, font_color=Color.PLAYER_COLOR)

        self.connectButton = button((game.width // 2 - 150, 360, 300, 80), "Connect", self.connect)
        self.backButton = button((game.width // 2 - 150, 460, 300, 80), "Back", self.back)

        self.errorLabel = Label(game, [0, 334, game.width, 24], "", font_size=18, font_color=Color.ENEMY_COLOR_RED)

    def open(self):
        self.error = ""

        self.game.menu = "online"

        pygame.key.start_text_input()

    def back(self):
        self.game.menu = "mode"

    def connect(self):
        try:
            host, port = parseAddress(self.address.text)

        except ValueError as error:
            self.error = str(error)

            return

        self.game.net.name = self.name.text.strip() or "Player"

        self.game.net.host = host
        self.game.net.port = port

        self.game.net.enabled = True

        self.save()

        self.game.startGame()

    def save(self):
        try:
            self.game.settings["online"] = {"enabled": False, "host": self.game.net.host, "port": self.game.net.port, "name": self.game.net.name}

            with open("files/settings.json", "w", encoding="utf-8") as file:
                json.dump(self.game.settings, file, indent=4)

        except OSError:
            pass

    def event(self, event):
        fields = [self.name, self.address]

        if event.type == pygame.TEXTINPUT:
            for field in fields:
                if field.active:
                    field.type(event.text)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.back()

            elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.connect()

            elif event.key == pygame.K_TAB:
                self.name.active, self.address.active = self.address.active, not self.address.active or self.name.active

            elif event.key == pygame.K_BACKSPACE:
                for field in fields:
                    if field.active:
                        field.backspace()

            elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                for field in fields:
                    if field.active:
                        field.paste()

    def draw(self):
        self.name.draw()
        self.address.draw()

        self.errorLabel.text = self.error
        self.errorLabel.draw()

        self.connectButton.draw()
        self.backButton.draw()
