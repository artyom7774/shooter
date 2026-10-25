from src.particle import Particles

from src.drone.resource import Resource

from src.entity import Entity
from src.player import Player

from src.render import Render
from src.audio import Audio
from src.logic import Logic
from src.spawn import Spawn

from src.variables import *
from src.ui import *

import faulthandler
import pygame
import ctypes
import random
import math
import json
import sys
import os

try:
    faulthandler.enable()

except BaseException:
    pass

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(True)

except BaseException:
    pass


class Data:
    path = "data.json"

    def __init__(self):
        self.repair()

        self.data = json.load(open(self.path, "r", encoding="utf-8"))

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def repair(self):
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as file:
                json.dump({}, file, indent=4)

        try:
            with open(self.path, "r", encoding="utf-8") as file:
                data = json.load(file)

        except json.decoder.JSONDecodeError:
            os.remove(self.path)

            self.repair()

        with open(self.path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if "points" not in data:
            data["points"] = 0

        if "crystal" not in data:
            data["crystal"] = 0

        if "upgrades" not in data:
            data["upgrades"] = {}

        if "gargen" not in data:
            data["garden"] = {

            }

        for code, upgrade in UPGRADES.items():
            if code not in data["upgrades"]:
                if UPGRADES[code].get("type", "base") == "many":
                    data["upgrades"][code] = 0

                else:
                    data["upgrades"][code] = False

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def save(self):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(self.data, file, indent=4)


class Game:
    bwidth = 1080
    bheight = 720
    capacity = 1

    def __init__(self):
        self.width = self.bwidth
        self.height = self.bheight

        self.fps = (1000 if SPEED_UP_MODE else 60)

        self.fpsc = 0

        self.screen = pygame.Surface((self.width, self.height))
        self.display = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)

        self.settings = json.load(open("files/settings.json", "r", encoding="utf-8"))
        
        pygame.init()

        self.clock = pygame.time.Clock()

        self.data = Data()
        self.data.repair()

        self.camera = Entity(self, 0, 0, (0, 0, 0), 0, 0, 0)

        self.player = Player(self, 0, 0, Color.PLAYER_COLOR, 9, 2, 3.5, [100, 100])
        self.objects = [self.player]

        self.particles = Particles()

        self.spawn = Spawn(self)

        self.menu = "main"

        self.pauseAfter = -1
        self.pause = False

        pygame.display.set_caption(NAME)

        self.press = pygame.mouse.get_pressed()
        self.mouse = pygame.mouse.get_pos()

        self.click = [0, 0, 0, 0, 0]

        self.render = Render(self)
        self.logic = Logic(self)

        self.audio = Audio(self)
        self.audio.init()

        self.resources = []

        # self.game()

    def resize(self, width, height):
        self.width = width
        self.height = height

        wc = self.width // self.bwidth
        hc = self.height // self.bheight

        self.capacity = max(1, min(wc, hc))

        self.width //= self.capacity
        self.height //= self.capacity

        self.screen = pygame.Surface((self.width, self.height))
        self.display = pygame.display.set_mode((width, height), pygame.RESIZABLE)

        self.render = Render(self)

    def init(self):
        self.player = Player(self, 0, 0, Color.PLAYER_COLOR, 9, 2, 3.5, [100, 100])
        self.objects = [self.player]

        self.generate()

        # self.objects.append(BossShooting(self, 100, 100, Color.ENEMY_COLOR, 20, 1, 2, [200, 200], 5, 5))

    def generate(self):
        self.resources = []

        generates = {
            "position": 4 * 4096,

            "types": {
                "crystal": {
                    "name": "crystal",
                    "open": self.data["upgrades"]["resources"],
                    "color": Color.ITEM_CRYSTAL_COLOR,
                    "radius": 7,
                    "width": 2,

                    "count": 1600
                }
            }
        }

        for name, generate in generates["types"].items():
            if not generate["open"]:
                continue

            for _ in range(generate["count"] * (1 + self.data["upgrades"]["moreResources"])):
                x = random.randint(-generates["position"], generates["position"])
                y = random.randint(-generates["position"], generates["position"])

                self.resources.append(Resource(self, x, y, generate["name"], generate["radius"], generate["width"], generate["color"]))

    def game(self):
        self.init()

        self.menu = "play"

        self.generate()

        self.render = Render(self)

        self.spawn = Spawn(self)
        self.logic = Logic(self)

    def exit(self):
        self.data["points"] += self.player.score
        self.data.save()

        sys.exit()

    def start(self):
        while True:
            self.fpsc += 1

            self.clock.tick(self.fps)

            self.click = [0] * 5

            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()

                if event.type == pygame.VIDEORESIZE:
                    self.resize(event.w, event.h)

                if event.type == pygame.MOUSEBUTTONUP:
                    self.click[event.button - 1] = True

                if event.type == pygame.KEYDOWN:
                    if self.menu == "play" and (event.key == pygame.K_ESCAPE or event.key == pygame.K_p):
                        self.pause = (1 - self.pause)

                    if self.menu == "choosing" and event.key == pygame.K_1:
                        self.render.choosingMenu.elements[0].collect()

                    if self.menu == "choosing" and event.key == pygame.K_2:
                        self.render.choosingMenu.elements[1].collect()

                    if self.menu == "choosing" and event.key == pygame.K_3:
                        self.render.choosingMenu.elements[2].collect()

                    if event.key == pygame.K_SPACE or event.key == pygame.K_z:
                        self.player.dashing(
                            int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                            int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])
                        )

            if self.menu in ("play", "upgrade") and not self.pause:
                for _ in range(5 if keys[pygame.K_LSHIFT] and self.menu == "upgrade" else 1):
                    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                        self.player.move(0)

                    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                        self.player.move(90)

                    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                        self.player.move(180)

                    if keys[pygame.K_w] or keys[pygame.K_UP]:
                        self.player.move(270)

            self.press = pygame.mouse.get_pressed()
            self.mouse = pygame.mouse.get_pos()

            self.screen.fill((11, 2, 23))

            self.audio.update()

            getattr(Logic, self.menu)(self.logic)
            getattr(Render, self.menu)(self.render)

            smoothness = 0.08 + min(0.15, math.sqrt((self.player.x - self.camera.x) ** 2 + (self.player.y - self.camera.y) ** 2) * 0.005)

            self.camera.x += (self.player.x - self.camera.x) * smoothness
            self.camera.y += (self.player.y - self.camera.y) * smoothness

            self.pauseAfter -= 1

            if self.pauseAfter == 0:
                self.pause = True

            prec = (random.randint(-4, 4), random.randint(-4, 4)) if self.player.playerGetDamageCD > 0 and self.menu == "play" else (0, 0)
            self.display.blit(pygame.transform.scale_by(self.screen, self.capacity), prec)

            # pygame.display.set_caption(f"{round(self.clock.get_fps())}")

            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.start()
