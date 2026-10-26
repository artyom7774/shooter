from src.drone.drone import Drone

from src.enemy import Enemy

from src.variables import *

import pygame
import random
import math


class AttackDrone(Drone):
    def __init__(self, player, game):
        Drone.__init__(self, game, player.x + random.randint(-100, 100), player.y + random.randint(-100, 100), 5, 1, Color.DRONE_ATTACK_COLOR)

        self.damageCD = 0

        self.now = None

    @property
    def damage(self):
        answer = 1 * self.game.player.dronesAttackMultiply

        if self.game.data["upgrades"]["dronesDependsDamage"]:
            answer *= max(1, sum([weapon["active"] * weapon["damage"] for weapon in self.game.player.weapons.values()]) / 5)

        return answer

    def update(self):
        super().update()

        self.damageCD -= 1

        distance = 1e9
        target = None

        for obj in self.game.objects:
            if not isinstance(obj, Enemy):
                continue

            if distance > math.sqrt((self.game.player.x - obj.x) ** 2 + (self.game.player.y - obj.y) ** 2):
                distance = math.sqrt((self.game.player.x - obj.x) ** 2 + (self.game.player.y - obj.y) ** 2)
                target = obj

        if target is None or math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2) > self.game.player.attackRadius:
            self.command = "follow"

            return

        self.command = "target"

        angle = math.degrees(math.atan2(target.y - self.y, target.x - self.x))

        self.vectors.append([angle, min(1, 1 + distance / 100), 1])

        if self.timer % 25 == 0:
            self.vectors.append([angle + random.randint(-5, 5), 15, 0.5])

        if math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2) <= self.radius + target.radius + 5 and self.damageCD <= 0:
            target.getDamage(self.damage)

            self.damageCD = 10

    def draw(self):
        super().draw()