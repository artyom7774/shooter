from PIL import Image, ImageEnhance

from src.player import Player

from src.net.menu import OnlineMenu

from src.variables import *
from src.ui import *

import random
import pygame
import math


class ChoosingMenu:
    def __init__(self, game):
        self.game = game

        self.choose = None

        if not hasattr(self, "elements"):
            self.elements = []

    def init(self):
        last = []

        self.choose = []
        self.elements = []

        if self.game.player.level == 2 and self.game.data["upgrades"]["weaponsInFirstLevel"]:
            using = []

            for choose in CHOOSES.values():
                if choose.get("another", {}).get("type", "") == "weapon" and choose["open"]:
                    using.append(choose)

            random.shuffle(using)

            minus = 0

            for i in range(min(len(using), 3)):
                answer = using[i]
                last.append(using[i]["code"])

                self.choose.append(answer)
                self.elements.append(ChoosingMenuElement(self.game, i, using[i]))

                minus += 1

        else:
            minus = 0

        for i in range(minus, 3):
            upgrades = {}

            maxWeight = 0

            for code, upgrade in CHOOSES.items():
                if not upgrade["open"]:
                    continue

                if upgrade["max"] == self.game.player.upgrades.get(code, 0):
                    continue

                if "confirm" in upgrade and not eval(upgrade["confirm"]):
                    continue

                if code in last:
                    continue

                upgrades[code] = upgrade
                maxWeight += upgrade["weight"]

            if not upgrades:
                break

            weight = random.randint(0, int(10000 * maxWeight)) / 10000

            nowWeight = 0

            answer = None

            for number, upgrade in enumerate(list(upgrades.values())):
                nowWeight += upgrade["weight"]

                if nowWeight > weight:
                    answer = list(upgrades.values())[number]
                    last.append(upgrade["code"])

                    break

            self.choose.append(answer)
            self.elements.append(ChoosingMenuElement(self.game, i, self.choose[i]))

    def draw(self):
        for element in self.elements:
            element.draw()


class ChoosingMenuElement:
    def __init__(self, game, index, choose):
        self.game = game

        self.index = index

        self.choose = choose

        self.label = Label(self.game,[60 + ((self.game.width - 140) // 3 + 10) * self.index, 60, (self.game.width - 140) // 3, 40], self.choose["name"], font_color=self.choose["color"])
        self.description = TextField(self.game, [63 + ((self.game.width - 140) // 3 + 10) * self.index, 100, (self.game.width - 140) // 3 - 6, 200], self.choose["description"], horizontal="left", vertical="up", font_color=self.choose["color"])
        self.button = Button(self.game, [0, 0, 0, 0], [*self.choose["color"], 120], self.choose["color"], [60 + ((self.game.width - 140) // 3 + 10) * self.index + 10, self.game.height - 60 - 10 - 70, (self.game.width - 140) // 3 - 20, 50], "Choose", self.choose["color"], font_color=self.choose["color"], function=lambda: self.collect())

    def draw(self):
        # pygame.draw.rect(self.game.screen, (0, 0, 0), (60 + ((self.width - 140) // 3 + 10) * self.index, 60, (self.width - 140) // 3, self.height - 120))
        pygame.draw.rect(self.game.screen, self.choose["color"], (60 + ((self.game.width - 140) // 3 + 10) * self.index, 60, (self.game.width - 140) // 3, self.game.height - 140), 2, 3)

        self.label.draw()
        self.description.draw()
        self.button.draw()

    def collect(self):
        exec(self.choose["function"])

        self.game.pause = False
        self.game.menu = "play"

        self.game.player.upgrades[self.choose["code"]] = 1 if self.choose["code"] not in self.game.player.upgrades else self.game.player.upgrades[self.choose["code"]] + 1

        # self.game.render.updateUI()

        self.game.player.getExperience(0)

        self.game.render.healthBar.setValue(self.game.player.health[0] / self.game.player.health[1])


class Garden:
    @staticmethod
    def text(game, slot):
        return f"Garden #{slot}"


class Upgrade:
    def __init__(self, game, upgrade):
        self.game = game

        self.upgrade = upgrade

        self.view = True
        self.open = True

        for first in UPGRADES[self.upgrade["code"]]["dependencies"]:
            if first == "$":
                continue

            if not self.game.data["upgrades"][first]:
                self.open = False

            for second in UPGRADES[first]["dependencies"]:
                if second == "$":
                    continue

                if not self.game.data["upgrades"][second]:
                    self.view = False

        # self.open = not any([not self.game.data["upgrades"][upgrade] for upgrade in self.upgrade["dependencies"] if upgrade != "$"])

        symbol = ("" if self.upgrade.get("image", False) else self.upgrade["symbol"]) if self.open else "?"

        self.size = UPGRADE_CELL_SIZE * self.upgrade.get("size", 1)

        if self.upgrade.get("type", "") == "garden":
            text = TextField(self.game, (0, 0, self.size, self.size), Garden.text(self.game, self.upgrade["garden"]["slot"]), font_color=self.upgrade["color"], vertical="up", horizontal="center")

        else:
            text = TLabel(self.game, (0, 0, self.size, self.size - 3), symbol, font_type="segoeuisymbol", font_size=23, font_color=self.upgrade["color"])

        self.button = Button(self.game, (0, 0, 0, 0), (*self.upgrade["color"], 60), (*self.upgrade["color"], 120), (0, 0, self.size, self.size), text, self.upgrade["color"], function=lambda: self.buy(), anotherFunction=lambda: self.sell(), font_color=self.upgrade["color"])

        self.request = self.upgrade.get("request", "points")

        self.buied = False

        if self.upgrade.get("type", "base") == "many" and self.game.data["upgrades"][self.upgrade["code"]] == self.upgrade["limit"]:
            self.buied = True

        if self.upgrade.get("type", "base") == "base" and self.game.data["upgrades"][self.upgrade["code"]]:
            self.buied = True

        if self.buied:
            self.button.base = (*self.upgrade["color"], 60)
            self.button.mouse = (*self.upgrade["color"], 60)
            self.button.click = (*self.upgrade["color"], 120)

        self.information = TextField(self.game, (5, self.game.height * 2 // 3 + 5 + 2, self.game.width - 10, self.game.height // 3 - 10), f"{self.upgrade['display']} /n {self.upgrade['description']}", vertical="up", horizontal="left")

        self.main = Label(self.game, (0, 0, 300, 150), self.upgrade["display"], font_color=self.upgrade["color"], vertical="up")
        self.cost = Label(self.game, (0, 0, 300, 150), f"Cost: {self.price} {self.request}", font_color=self.upgrade["color"], vertical="down", horizontal="left")

        self.text = TextField(self.game, (0, 0, 300, 150), self.upgrade["description"], font_color=self.upgrade["color"], font_size=18, vertical="up", horizontal="left")

        if self.upgrade.get("type", "base") == "many":
            self.count = Label(self.game, (0, 0, 300, 150), f"{self.game.data['upgrades'][self.upgrade['code']]}/{self.upgrade['limit']}", font_color=self.upgrade["color"], vertical="down", horizontal="right")

        else:
            self.count = None

    @property
    def price(self):
        if self.upgrade.get("type", "base") == "many":
            return self.upgrade["cost"][min(self.game.data["upgrades"][self.upgrade["code"]], self.upgrade["limit"] - 1)]

        return self.upgrade["cost"]

    def draw(self):
        cx = self.upgrade["x"] * UPGRADE_CELL_SIZE - ((self.size - UPGRADE_CELL_SIZE) // 2) - self.game.camera.x + self.game.width // 2 - UPGRADE_CELL_SIZE // 2
        cy = self.upgrade["y"] * UPGRADE_CELL_SIZE - ((self.size - UPGRADE_CELL_SIZE) // 2) - self.game.camera.y + self.game.height // 2 - UPGRADE_CELL_SIZE // 2

        if not self.upgrade.get("type", "") == "garden" or self.open:
            self.button.draw(cx, cy)

        """
        if self.upgrade.get("image", None) is not None:
            img = pygame.image.load(self.upgrade["image"]).convert_alpha()
            img = pygame.transform.scale(img, (32, 32))

            img.fill(Color.UPGRADE_WHITE_COLOR, special_flags=pygame.BLEND_RGB_MAX)

            self.game.screen.blit(img, (cx + 9, cy + 9))
        """

        if self.button.last == 1 and self.open and not self.upgrade.get("type", "") == "garden":
            alphaRect(self.game.screen, (40, 40, 40, 150), (cx - 150 + UPGRADE_CELL_SIZE // 2, cy + 60, 300, 150), 0, 3)
            pygame.draw.rect(self.game.screen, self.upgrade["color"], (cx - 150 + UPGRADE_CELL_SIZE // 2, cy + 60, 300, 150), 2, 3)

            self.main.draw(cx - 150 + UPGRADE_CELL_SIZE // 2, cy + 60 + 5)
            self.text.draw(cx - 150 + UPGRADE_CELL_SIZE // 2, cy + 60 + 23 + 5)
            self.cost.draw(cx - 150 + UPGRADE_CELL_SIZE // 2, cy + 60 - 5)

            if self.count:
                self.count.draw(cx - 150 + UPGRADE_CELL_SIZE // 2, cy + 60 - 5)

        if self.upgrade.get("type", "") == "garden":
            ...

    def buy(self):
        if not self.open:
            return

        if self.game.data[self.request] < self.price:
            return

        if self.upgrade.get("type", "base") == "base" and self.game.data["upgrades"][self.upgrade["code"]]:
            return

        if self.upgrade.get("type", "base") == "many" and self.game.data["upgrades"][self.upgrade["code"]] == self.upgrade["limit"]:
            return

        if self.upgrade["symbol"] == "C" and sum([upgrade["symbol"] == "C" and self.game.data["upgrades"][upgrade["code"]] for upgrade in UPGRADES.values()]):
            return

        if self.upgrade.get("type", "") == "garden":
            return

        self.game.data[self.request] -= self.price

        if self.upgrade.get("type", "base") == "many":
            self.game.data["upgrades"][self.upgrade["code"]] += 1

        else:
            self.game.data["upgrades"][self.upgrade["code"]] = True

        self.game.data.save()

        self.update()

    def sell(self):
        if self.game.data["upgrades"][self.upgrade["code"]] == 0:
            return

        if self.game.data["upgrades"][self.upgrade["code"]] == 1:
            for upgrade in UPGRADES.values():
                if self.game.data["upgrades"][upgrade["code"]]:
                    if upgrade["symbol"] == "I":
                        self.game.data["upgrades"][upgrade["code"]] = False

                        continue

                    if self.upgrade["code"] in upgrade["dependencies"]:
                        return

        if self.upgrade.get("type", "base") == "many":
            self.game.data["upgrades"][self.upgrade["code"]] -= 1

        else:
            self.game.data["upgrades"][self.upgrade["code"]] = False

        self.game.data[self.request] += self.price

        self.game.data.save()

        self.update()

    def update(self):
        self.game.render.upgrades[self.upgrade["code"]] = Upgrade(self.game, UPGRADES[self.upgrade["code"]])

        for code, upgrade in UPGRADES.items():
            if self.upgrade["code"] in upgrade["dependencies"]:
                self.game.render.upgrades[code] = Upgrade(self.game, upgrade)

            for second in upgrade["dependencies"]:
                if second == "$":
                    continue

                self.game.render.upgrades[second] = Upgrade(self.game, UPGRADES[second])

        self.game.render.upgradeMenuUpdate()


class Render:
    def __init__(self, game):
        self.game = game

        self.toMainMenuButton = Button(self.game, (0, 0, 0, 0), (*Color.PLAYER_COLOR, 60), (*Color.PLAYER_COLOR, 120), (0, 0, 250, 50), "Back", Color.PLAYER_COLOR, function=lambda: toMainMenu(self.game), font_color=Color.PLAYER_COLOR)

        # GAME

        self.healthBar = ProgressBar(self.game, 5, 5, 200, 23, Color.BASE_UI_COLOR, Color.HEALTH_BAR_COLOR, Color.BASE_UI_COLOR, 1)
        self.staminaBar = ProgressBar(self.game, 5, self.game.height - 28, 200, 23, Color.BASE_UI_COLOR, Color.STAMINA_BAR_COLOR, Color.BASE_UI_COLOR, 1)
        self.armorBar = ProgressBar(self.game, 5, 33, 200, 23, Color.BASE_UI_COLOR, Color.ARMOR_BAR_COLOR, Color.BASE_UI_COLOR, 1)

        self.xpBar = ProgressBar(self.game, 210, 5, self.game.width - 215, 23, Color.BASE_UI_COLOR, Color.XP_BAR_COLOR, Color.BASE_UI_COLOR, 0)

        self.waveCount = Label(self.game, (5, 30, self.game.width - 10, 30), f"Wave: {self.game.spawn.wave}", horizontal="right", vertical="up")
        self.scoreCount = Label(self.game, (5, 30, self.game.width - 10, 30), f"Points: {self.game.player.score}", horizontal="left", vertical="up")

        self.gameExitButton = Button(self.game, (0, 0, 0, 0), (*Color.PLAYER_COLOR, 60), (*Color.PLAYER_COLOR, 120), (0, 0, 50, 50), TLabel(self.game, (0, 0, 50, 50), "💀", font_type="segoeuisymbol"), Color.PLAYER_COLOR, function=lambda: toMainMenu(self.game), font_color=Color.PLAYER_COLOR)

        self.printPauseLabel = Label(self.game, (0, 0, self.game.width, self.game.height - 6), f"Pause", font_size=28, vertical="down")

        # CHOOSING

        self.choosingMenu = ChoosingMenu(self.game)

        # UPGRADE

        self.upgrades = {}

        self.pointsCount = None
        self.crystalCount = None

        self.mouseClickInfoText = TextField(self.game, (0, 0, self.game.width, self.game.height), "LMB - buy upgrade /n RMB - sell upgrade (no dependencies)", font_color=Color.PLAYER_COLOR, font_size=18, vertical="down", horizontal="left")
        self.anotherInfoText = TextField(self.game, (0, 0, self.game.width, self.game.height), "SHIFT - speed up", font_color=Color.PLAYER_COLOR, font_size=18, vertical="down", horizontal="right")

        self.upgradeMenuInit()

        # MAIN

        self.startGameButton = Button(self.game, (0, 0, 0, 0), (*Color.PLAYER_COLOR, 60), (*Color.PLAYER_COLOR, 120), (self.game.width // 2 - 150, 160, 300, 80), "Play", Color.PLAYER_COLOR, function=lambda: toPlayMode(self.game), font_color=Color.PLAYER_COLOR)
        self.upgradeButton = Button(self.game, (0, 0, 0, 0), (*Color.PLAYER_COLOR, 60), (*Color.PLAYER_COLOR, 120), (self.game.width // 2 - 150, 260, 300, 80), "Upgrades", Color.PLAYER_COLOR, function=lambda: toUpgradeMenu(self.game), font_color=Color.PLAYER_COLOR)
        self.helpButton = Button(self.game, (0, 0, 0, 0), (*Color.PLAYER_COLOR, 60), (*Color.PLAYER_COLOR, 120), (self.game.width // 2 - 150, 360, 300, 80), "Help", Color.PLAYER_COLOR, function=lambda: toHelpMenu(self.game), font_color=Color.PLAYER_COLOR)
        self.statsButton = Button(self.game, (0, 0, 0, 0), (*Color.PLAYER_COLOR, 60), (*Color.PLAYER_COLOR, 120), (self.game.width // 2 - 150, 460, 300, 80), "Stats", Color.PLAYER_COLOR, function=lambda: print(3), font_color=Color.PLAYER_COLOR)
        self.exitButton = Button(self.game, (0, 0, 0, 0), (*Color.PLAYER_COLOR, 60), (*Color.PLAYER_COLOR, 120), (self.game.width // 2 - 150, 460, 300, 80), "Exit", Color.PLAYER_COLOR, function=lambda: self.game.exit(), font_color=Color.PLAYER_COLOR)

        # MODE

        self.modeOfflineButton = Button(self.game, (0, 0, 0, 0), (*Color.PLAYER_COLOR, 60), (*Color.PLAYER_COLOR, 120), (self.game.width // 2 - 150, 160, 300, 80), "Single", Color.PLAYER_COLOR, function=lambda: self.game.startOffline(), font_color=Color.PLAYER_COLOR)
        self.modeOnlineButton = Button(self.game, (0, 0, 0, 0), (*Color.PLAYER_COLOR, 60), (*Color.PLAYER_COLOR, 120), (self.game.width // 2 - 150, 260, 300, 80), "Server", Color.PLAYER_COLOR, function=lambda: self.onlineMenu.open(), font_color=Color.PLAYER_COLOR)
        self.modeBackButton = Button(self.game, (0, 0, 0, 0), (*Color.PLAYER_COLOR, 60), (*Color.PLAYER_COLOR, 120), (self.game.width // 2 - 150, 360, 300, 80), "Back", Color.PLAYER_COLOR, function=lambda: toMainMenu2(self.game), font_color=Color.PLAYER_COLOR)

        self.onlineMenu = OnlineMenu(self.game)

        self.gameNameLabel = Label(self.game, [0, 0, self.game.width, 140], NAME, font_size=80)
        self.gameVersionLabel = Label(self.game, [5, self.game.height - 30, self.game.width, 25], VERSION, font_size=16)

        # HELP

        self.helpSprite = pygame.image.load("files/sprites/help.png").convert()

        self.helpSurface = {}

    def upgradeMenuInit(self):
        for code, upgrade in UPGRADES.items():
            if code not in self.upgrades:
                self.upgrades[code] = Upgrade(self.game, upgrade)

        self.upgradeMenuUpdate()

    def upgradeMenuUpdate(self):
        # if self.game.data["upgrades"]["resources"]:
        #     self.pointsCount = Label(self.game, (0, 0, self.game.width, self.game.height), f"Points: {self.game.data['points']} | {' ' * 9} {' ' * len(str(self.game.data['crystal']))}", vertical="up")
        #     self.crystalCount = Label(self.game, (0, 0, self.game.width, self.game.height), f"{' ' * 7} {' ' * len(str(self.game.data['points']))}   Crystals: {self.game.data['crystal']}", font_color=Color.ITEM_CRYSTAL_COLOR, vertical="up")
        #
        # else:
        #     self.pointsCount = Label(self.game, (0, 0, self.game.width, self.game.height), f"Points: {self.game.data['points']}", vertical="up")

        self.pointsCount = Label(self.game, (0, 0, self.game.width, self.game.height), f"Points: {self.game.data['points']}", horizontal="left", vertical="up")

        if self.game.data["upgrades"]["resources"] or self.game.data["crystal"] > 0:
            self.crystalCount = Label(self.game, (0, 20, self.game.width, self.game.height), f"Crystals: {self.game.data['crystal']}", font_color=Color.ITEM_CRYSTAL_COLOR, horizontal="left", vertical="up")

    def background(self):
        global BACKGROUND

        tileWidth = 5 * NOISE_PARAMS["width"]
        tileHeight = 5 * NOISE_PARAMS["height"]

        if BACKGROUND.get_size() != (tileWidth, tileHeight):
            BACKGROUND = pygame.transform.scale(BACKGROUND, (tileWidth, tileHeight))

        start_x = -tileWidth - (self.game.player.x * 0.3 % tileWidth) - 2000
        start_y = -tileHeight - (self.game.player.y * 0.3 % tileHeight) - 2000

        for x in range(int(start_x), self.game.width + tileWidth, tileWidth):
            for y in range(int(start_y), self.game.height + tileHeight, tileHeight):
                self.game.screen.blit(BACKGROUND, (x, y))

    def play(self):
        self.background()

        for resource in self.game.resources:
            resource.draw()

        for obj in sorted(self.game.objects, key=lambda obj: type(obj) != Player):
            obj.draw()

        for obj in sorted(self.game.objects, key=lambda obj: type(obj) != Player):
            if hasattr(obj, "drawHealthBar"):
                obj.drawHealthBar()

        for particle in self.game.particles.particles[:]:
            particle.draw()

        self.healthBar.draw(f"{math.floor(self.game.player.health[0])}/{math.floor(self.game.player.health[1])}")

        # if self.game.player.staminaIsOpened:
        #     self.staminaBar.draw(f"{round(self.game.player.stamina[0])}/{self.game.player.stamina[1]}")

        if self.game.player.armorIsOpened:
            self.armorBar.draw(f"{math.floor(self.game.player.armor[0])}/{math.floor(self.game.player.armor[1])}")

        self.xpBar.draw(f"Level {self.game.player.level} - {math.floor(self.game.player.xp[0])}/{math.floor(self.game.player.xp[1])}")

        self.waveCount.draw()

        if self.game.player.armorIsOpened:
            self.scoreCount.draw(self.scoreCount.rect[0], self.scoreCount.rect[1] + 28)

        else:
            self.scoreCount.draw()

        self.gameExitButton.draw(self.game.width - 60, self.game.height - 60)

        if self.game.online:
            self.game.world.draw()

        if self.game.pause and self.game.menu == "play":
            self.printPauseLabel.draw()

            alphaTextLine(self.game.screen, Color.PLAYER_COLOR, (
                self.printPauseLabel.rect[2] // 2 - 120,
                self.printPauseLabel.rect[3],
                240,
                1
            ))

    def choosing(self):
        self.play()

        self.choosingMenu.draw()

    def upgrade(self):
        self.background()

        self.pointsCount.draw()

        if self.crystalCount:
            self.crystalCount.draw()

        cx = self.game.camera.x - self.game.width // 2
        cy = self.game.camera.y - self.game.height // 2

        for code, upgrade in UPGRADES.items():
            skip = False

            for element in upgrade["dependencies"]:
                if element == "$":
                    skip = True

                    continue

                if skip:
                    continue

                x1 = upgrade["x"] * UPGRADE_CELL_SIZE
                y1 = upgrade["y"] * UPGRADE_CELL_SIZE

                x2 = UPGRADES[element]["x"] * UPGRADE_CELL_SIZE
                y2 = UPGRADES[element]["y"] * UPGRADE_CELL_SIZE

                c1 = UPGRADES[element]["color"]
                c2 = upgrade["color"]

                if x1 == x2:
                    if y1 > y2:
                        y1, y2 = y2, y1

                    else:
                        c1, c2 = c2, c1

                    prec = (y2 - y1 - UPGRADE_CELL_SIZE) // 2

                    pygame.draw.line(self.game.screen, c1, (x1 - cx, y1 - cy + UPGRADE_CELL_SIZE // 2), (x2 - cx, y2 - cy - UPGRADE_CELL_SIZE // 2 - prec), 2)
                    pygame.draw.line(self.game.screen, c2, (x1 - cx, y1 - cy + UPGRADE_CELL_SIZE // 2 + prec), (x2 - cx, y2 - cy - UPGRADE_CELL_SIZE // 2), 2)

                if y1 == y2:
                    if x1 < x2:
                        x1, x2 = x2, x1
                        c1, c2 = c2, c1

                    prec = (x2 - x1 + UPGRADE_CELL_SIZE) // 2

                    pygame.draw.line(self.game.screen, c1, (x1 - cx - UPGRADE_CELL_SIZE // 2 + prec, y1 - cy), (x2 - cx + UPGRADE_CELL_SIZE // 2, y2 - cy), 2)
                    pygame.draw.line(self.game.screen, c2, (x1 - cx - UPGRADE_CELL_SIZE // 2, y1 - cy), (x2 - cx + UPGRADE_CELL_SIZE // 2 - prec, y2 - cy), 2)

        for upgrade in sorted(list(self.upgrades.values()), key=lambda x: x.button.last):
            upgrade.draw()

        self.mouseClickInfoText.draw()
        self.anotherInfoText.draw()

        self.toMainMenuButton.draw(self.game.width // 2 - 125, self.game.height - 60)

    def help(self):
        surface = pygame.transform.smoothscale_by(self.helpSprite, self.game.height / self.game.bheight / self.game.capacity)

        size = surface.get_size()

        if size not in self.helpSurface:
            self.helpSurface[size] = pygame.image.fromstring(ImageEnhance.Sharpness(Image.frombytes("RGBA", size, pygame.image.tostring(surface, "RGBA"))).enhance(2).tobytes(), size, "RGBA")

        self.game.screen.blit(self.helpSurface[size], ((self.game.width - (self.game.bwidth * self.game.height / self.game.bheight)) // 2, 0))

        self.toMainMenuButton.draw(self.game.width // 2 - 125, self.game.height - 60)

    def main(self):
        self.game.pause = False

        self.background()

        self.startGameButton.draw()
        self.upgradeButton.draw()
        self.helpButton.draw()
        # self.statsButton.draw()
        self.exitButton.draw()

        self.gameNameLabel.draw()
        self.gameVersionLabel.draw()

    def mode(self):
        self.game.pause = False

        self.background()

        self.modeOfflineButton.draw()
        self.modeOnlineButton.draw()
        self.modeBackButton.draw()

        self.gameNameLabel.draw()
        self.gameVersionLabel.draw()

    def online(self):
        self.game.pause = False

        self.background()

        self.onlineMenu.draw()

        self.gameNameLabel.draw()
        self.gameVersionLabel.draw()


def toUpgradeMenu(game):
    game.menu = "upgrade"


def toHelpMenu(game):
    game.menu = "help"


def toMainMenu(game):
    game.player.over()


def toPlayMode(game):
    game.menu = "mode"


def toMainMenu2(game):
    game.menu = "main"
