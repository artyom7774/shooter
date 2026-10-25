from src.ui import alphaCircle

from src.bullets import Bullet, Laser

from src.drone import MiningDrone, AttackDrone

from src.entity import Entity
from src.enemy import Enemy

from src.variables import *
from src.ui import *

import random
import pygame
import math


class Player(Entity):
    def __init__(self, game, x, y, color, radius, width, speed, health):
        Entity.__init__(self, game, x, y, color, radius, width, speed)

        self.speedMultiply = 1

        self.attackSpeedMultiply = 1
        self.attackDamageMultiply = 1

        self.attackRadius = 350

        self.playerGetDamageCD = -100

        self.health = health

        self.experienceMultiply = 1
        self.pointsMultiply = 1

        self.armorGetAttackBonus = False
        self.armorIsOpened = False
        self.armor = None

        self.dronesActive = False
        self.dronesMiningGetForWave = False
        self.dronesResourceMultiply = 1
        self.dronesAttackMultiply = 1
        self.dronesTypes = {"mining": 0, "attack": 0}
        self.drones = []

        self.staminaRegeneration = 0.15
        self.staminaIsOpened = False
        self.stamina = None

        self.bulletsSpeed = 1.5

        self.dashIsOpened = False

        self.dashNow = 0
        self.dashNotTakeDamageCD = 0

        self.score = 0

        self.resources = {
            "crystal": 0
        }

        self.upgrades = {

        }

        self.xp = [0, 10 * PLAYER_XP_REQUEREMENTS_MULTIPLY]
        self.level = 1

        self.usingRevival = False

        self.clazz = None

        self.autoAttackEnabled = True

        self.weaponsActive = 1
        self.weaponsTypesOpened = False
        self.weaponsMaxCount = 1
        self.weapons = {
            "base": {
                "type": "base",
                "symbol": "B",
                "active": True,
                "damage": 5,
                "attackSpeed": 80 - 1,
                "attackSpeedMultiply": 1,
                "attackCD": 0,
                "another": {
                    "explosiveDamage": 2
                }
            },

            "shotgun": {
                "type": "shotgun",
                "symbol": "S",
                "active": False,
                "damage": 7,
                "attackSpeed": 250 - 1,
                "attackSpeedMultiply": 1,
                "attackCD": 0,
                "another": {
                    "chapterDamageMultiply": 0.4,
                    "chapterCount": 8
                }
            },

            "machineGun": {
                "type": "machineGun",
                "symbol": "M",
                "active": False,
                "damage": 2,
                "attackSpeed": 40 - 1,
                "attackSpeedMultiply": 1,
                "attackCD": 0,
                "another": {

                }
            },

            "explosive": {
                "type": "explosive",
                "symbol": "E",
                "active": False,
                "damage": 3,
                "attackSpeed": 300 - 1,
                "attackSpeedMultiply": 1,
                "attackCD": 0,
                "another": {

                }
            },

            "laser": {
                "type": "laser",
                "symbol": "L",
                "active": False,
                "damage": 5,
                "attackSpeed": 300 - 1,
                "attackSpeedMultiply": 1,
                "attackCD": 0,
                "another": {
                    "jumpCount": 2
                }
            }
        }

        self.initUpgrades()

    def initUpgrades(self):
        global UPGRADES

        for code, element in OPENS.items():
            CHOOSES[code]["open"] = element

        for code, upgrade in UPGRADES.items():
            if self.game.data["upgrades"][code]:
                exec(upgrade["function"])

        if self.armorIsOpened:
            self.armor = [10, 10]

        else:
            self.armor = [0, 0]

        if self.staminaIsOpened:
            self.stamina = [0, 100]

        else:
            self.stamina = [0, 0]

        for _ in range(self.dronesTypes["mining"]):
            self.getDrone(MiningDrone(self, self.game))

        for _ in range(self.dronesTypes["attack"]):
            self.getDrone(AttackDrone(self, self.game))

        if self.game.data["upgrades"]["fastWeaponReload"]:
            for weapon in self.weapons.values():
                if weapon["attackSpeed"] >= 120 - 1:
                    weapon["attackSpeed"] *= 0.8

    def getDamage(self, damage, target=None):
        if self.playerGetDamageCD > 0 or self.dashNotTakeDamageCD > 0:
            return

        if target is not None and self.upgrades.get("spikedArmor", 0):
            target.getDamage(4 * min(self.armor[0], damage))

        self.health[0] -= max(0, damage - self.armor[0])
        self.armor[0] -= min(self.armor[0], damage)

        if self.health[0] <= 0:
            if not self.usingRevival and self.game.player.upgrades.get("revival", 0):
                self.usingRevival = True

                self.health[0] = self.health[1]

            else:
                self.over()

        self.playerGetDamageCD = PLAYER_GET_DAMAGE_CD

    def getExperience(self, xp):
        self.xp[0] += xp * self.experienceMultiply

        self.score += math.ceil(PLAYER_POINTS_MULTIPLY * xp * self.pointsMultiply * math.log2(max(1, self.game.spawn.wave)))
        self.game.render.scoreCount.text = f"Points: {self.game.player.score}"

        if self.xp[0] >= self.xp[1]:
            self.level += 1

            self.xp[0] -= self.xp[1]
            self.xp[1] = int(self.xp[1] * 1.4)

            self.game.pauseAfter = 2

            self.game.render.choosingMenu.init()

            if self.game.menu == "play":
                self.game.menu = "choosing"

        self.game.render.xpBar.setValue(math.trunc(self.xp[0]) / self.xp[1])

    def getDrone(self, drone, update: bool = False):
        self.drones.append(drone)

        if update:
            self.dronesTypes["mining"] += 1

        if self.game.data["upgrades"]["dronesStats"]:
            self.experienceMultiply *= 1.01
            self.pointsMultiply *= 1.01

            self.health[1] *= 1.01

        if isinstance(drone, MiningDrone) and self.game.data["upgrades"]["resourceMultiplyByMiningDrones"]:
            self.dronesResourceMultiply *= 1.35

    def over(self):
        self.game.data["points"] += int(self.score)

        for resource, count in self.resources.items():
            self.game.data[resource] += int(count)

        self.score = 0

        self.game.game()

        self.game.menu = "main"

    def dashing(self, x, y):
        if not self.dashIsOpened:
            return

        if x == 0 and y == 0:
            return

        if self.stamina[0] < 40:
            return

        self.stamina[0] -= 40

        angle = math.degrees(math.atan2(y, x))

        self.vectors.append([angle, 16, 1])

        if self.upgrades.get("notTakeDamageWhileDashing", 0):
            self.dashNotTakeDamageCD = PLAYER_DASH_NOT_TAKE_DAMAGE_CD

        self.dashNow = PLAYER_DASH_NOT_TAKE_DAMAGE_CD

    def move(self, angle, capacity: int = 1):
        self.vectors.append([angle, capacity * self.speed * self.speedMultiply * (1.1 if self.game.data["upgrades"]["speedWithStamina"] and self.stamina[0] == self.stamina[1] else 1), 1e9])

    def update(self):
        super().update()

        self.dashNotTakeDamageCD -= 1
        self.dashNow -= 1

        self.playerGetDamageCD -= 1

        self.stamina[0] = min(self.stamina[1], self.stamina[0] + self.staminaRegeneration)

        self.game.render.healthBar.setValue(self.health[0] / self.health[1])

        if self.armorIsOpened:
            self.game.render.armorBar.setValue(self.armor[0] / self.armor[1])

        if self.staminaIsOpened:
            self.game.render.staminaBar.setValue(self.stamina[0] / self.stamina[1])

        for weapon in self.weapons.values():
            weapon["attackCD"] -= 1

        if any([(weapon["active"] and weapon["attackCD"] <= 0) for weapon in self.weapons.values()]):
            if self.autoAttackEnabled and not self.game.press[0]:
                distance = 1e9
                target = None

                for obj in self.game.objects:
                    if not isinstance(obj, Enemy):
                        continue

                    var = math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2)

                    if var < distance:
                        distance = var
                        target = obj

                if target is not None and distance <= self.attackRadius:
                    self.attack(target)

            elif self.game.press[0]:
                self.attack()

        if self.clazz == "warrior" and self.dashNow > 0:
            for obj in self.game.objects:
                if not isinstance(obj, Enemy):
                    continue

                if math.sqrt((obj.x - self.x) ** 2 + (obj.y - self.y) ** 2) < self.radius + obj.radius:
                    obj.getDamage(sum([weapon["active"] * weapon["damage"] for weapon in self.weapons.values()]), 1)

        for drone in self.drones:
            drone.update()

    def attack(self, target = None):
        angle = math.degrees(math.atan2(self.game.mouse[1] - self.game.height // 2, self.game.mouse[0] - self.game.width // 2))

        if self.weapons["base"]["active"] and self.weapons["base"]["attackCD"] <= 0:
            self.game.objects.append(Bullet(self.game, self.x, self.y, Color.PLAYER_COLOR, PLAYER_BULLET_RADIUS, 1, self.bulletsSpeed, target, "player", 300, self.weaponGetDamage(self.weapons["base"]), 0.001, angle if target is None else 0, another={"type": "base"}))

            self.weapons["base"]["attackCD"] = self.weaponGetSpeed(self.weapons["base"])

        if self.weapons["shotgun"]["active"] and self.weapons["shotgun"]["attackCD"] <= 0:
            self.game.objects.append(Bullet(self.game, self.x, self.y, Color.PLAYER_COLOR, PLAYER_BULLET_RADIUS + 2, 1, self.bulletsSpeed, target, "player", 300, self.weaponGetDamage(self.weapons["shotgun"]), 0.001, angle if target is None else 0, another={"type": "shotgun"}))

            self.weapons["shotgun"]["attackCD"] = self.weaponGetSpeed(self.weapons["shotgun"])

        if self.weapons["machineGun"]["active"] and self.weapons["machineGun"]["attackCD"] <= 0:
            self.game.objects.append(Bullet(self.game, self.x, self.y, Color.PLAYER_COLOR, PLAYER_BULLET_RADIUS - 2, 1, self.bulletsSpeed, target, "player", 300, self.weaponGetDamage(self.weapons["machineGun"]), 0.001, angle if target is None else 0, another={"type": "machine-gun"}))

            self.weapons["machineGun"]["attackCD"] = self.weaponGetSpeed(self.weapons["machineGun"])

        if self.weapons["explosive"]["active"] and self.weapons["explosive"]["attackCD"] <= 0:
            self.game.objects.append(Bullet(self.game, self.x, self.y, Color.PLAYER_COLOR, PLAYER_BULLET_RADIUS + 1, 1, 0, None, "player", 1000, self.weaponGetDamage(self.weapons["explosive"]), 0.001, angle if target is None else 0, another={"type": "explosive"}))

            self.weapons["explosive"]["attackCD"] = self.weaponGetSpeed(self.weapons["explosive"])

        if self.weapons["laser"]["active"] and self.weapons["laser"]["attackCD"] <= 0:
            target = None

            for obj in self.game.objects:
                if not isinstance(obj, Enemy):
                    continue

                if math.sqrt((obj.x - self.x) ** 2 + (obj.y - self.y) ** 2) <= 100:
                    target = obj

                    break

            if target:
                self.game.objects.append(Laser(self.game, self.x, self.y, Color.PLAYER_COLOR, 1, "player", target, 100, self.weaponGetDamage(self.weapons["laser"]), self.weapons["laser"]["another"]["jumpCount"], another={"type": "laser"}))

                self.weapons["laser"]["attackCD"] = self.weaponGetSpeed(self.weapons["laser"])

    def weaponGetDamage(self, weapon):
        answer = self.attackDamageMultiply * weapon["damage"]

        if self.armorGetAttackBonus and self.armor[0] > 0:
            answer *= 1.2

        return answer

    def weaponGetSpeed(self, weapon):
        answer = weapon["attackSpeed"] * weapon["attackSpeedMultiply"] * self.attackSpeedMultiply

        if weapon["type"] == "machineGun" and self.game.data["upgrades"]["machineGunMultiplySpeed"]:
            answer *= self.speedMultiply

        if weapon["type"] == "base" and self.upgrades.get("doubleShot", 0):
            answer *= 0.7

        return answer

    def weaponDrawUI(self, pos, weapon):
        x = 10 + 60 * pos
        y = self.game.height - 60

        pygame.draw.rect(self.game.screen, (255, 255, 255), (x, y, 50, 50), 2, 3)

        if not weapon:
            return

        TLabel(self.game, (0, 0, 50, 50), weapon["symbol"], font_color=(255, 255, 255), font_type="segoeuisymbol", font_size=23).draw(x, y)

        if weapon["attackCD"] > 0:
            procent = weapon["attackCD"] / self.weaponGetSpeed(weapon)

            alphaRect(self.game.screen, (255, 255, 255, 60), (x, y + 50 * (1 - procent), 50, 50 - 50 * (1 - procent)), 0, 3)

    def draw(self):
        super().draw()

        px = int(self.x - self.game.camera.x + self.game.width // 2)
        py = int(self.y - self.game.camera.y + self.game.height // 2)

        for obj in self.game.objects:
            if not isinstance(obj, Enemy):
                continue

            cx = int(obj.x - self.game.camera.x + self.game.width // 2)
            cy = int(obj.y - self.game.camera.y + self.game.height // 2)

            angle = math.atan2(cy - py, cx - px)
            lenght = 15

            x = math.cos(angle) * lenght
            y = math.sin(angle) * lenght

            pygame.draw.circle(self.game.screen, Color.PLAYER_COLOR, [px + x, py + y], 2, 5)

            # pygame.draw.line(self.game.screen, Color.ENEMY_COLOR_RED, [px, py], [cx, cy])

        if self.staminaIsOpened:
            alphaCircle(self.game.screen, (*Color.PLAYER_COLOR, 255), (self.game.player.x - self.game.camera.x + self.game.width // 2, self.game.player.y - self.game.camera.y + self.game.height // 2), int(4 * self.stamina[0] / self.stamina[1]))

        # pygame.draw.circle(self.game.screen, Color.ENEMY_COLOR_RED, [px, py], self.attackRadius, 1)

        if self.weaponsTypesOpened:
            nxt = 0

            for weapon in self.weapons.values():
                if weapon["active"]:
                    self.weaponDrawUI(nxt, weapon)

                    nxt += 1

            for pos in range(nxt, self.weaponsMaxCount):
                self.weaponDrawUI(pos, None)

        for drone in self.drones:
            drone.draw()
