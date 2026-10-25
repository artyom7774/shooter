from src.particle import Particle

from src.entity import Entity
from src.enemy import Enemy

from src.variables import *

import random
import pygame
import math


class Laser(Entity):
    def __init__(self, game, x, y, color, width, type, target, liveTime, damage, jumps, onDeath=None, another=None):
        Entity.__init__(self, game, x, y, color, 0, width, 0)

        self.another = another if another else {}

        self.type = type

        self.live = 0

        self.onDeath = onDeath

        self.target = target
        # self.pos = (self.target.x - self.game.player.x + self.game.width // 2, self.target.y - self.game.player.y + self.game.height // 2)
        self.pos = (self.target.x, self.target.y)

        self.jumps = jumps

        self.damage = damage

        self.liveTime = liveTime
        self.toDestroy = False

        self.target.getDamage(self.damage)

    def draw(self):
        cpos = (self.x - self.game.camera.x + self.game.width // 2, self.y - self.game.camera.y + self.game.height // 2)
        rpos = (self.pos[0] - self.game.camera.x + self.game.width // 2, self.pos[1] - self.game.camera.y + self.game.height // 2)

        pygame.draw.circle(self.game.screen, self.color, rpos, self.width + 2)
        pygame.draw.line(self.game.screen, self.color, cpos, rpos, self.width)

    def update(self):
        self.live += 1

        if self.jumps:
            target = None
            dist = 1e9

            for obj in self.game.objects:
                if not isinstance(obj, Enemy):
                    continue

                if target == self.target:
                    continue

                if math.sqrt((obj.x - self.x) ** 2 + (obj.y - self.y) ** 2) <= 60 and (obj.x - self.x) ** 2 + (obj.y - self.y) ** 2 < dist:
                    dist = (obj.x - self.x) ** 2 + (obj.y - self.y) ** 2
                    target = obj

                    break

            if target:
                self.game.objects.append(Laser(self.game, self.pos[0], self.pos[1], self.color, self.width, self.type, target, self.liveTime, self.damage, self.jumps - 1, another=self.another))

                self.jumps = 0

        if self.game.player.upgrades.get("laserAttackEveryFrame", 0):
            self.target.getDamage(self.damage / 100)

        if self.live >= self.liveTime or self.toDestroy:
            if self.onDeath is not None:
                self.onDeath(self.x, self.y)

            self.game.objects.remove(self)
