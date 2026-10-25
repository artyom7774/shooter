from src.ui import ProgressBar

from src.particle import Particle

from src.entity import Entity

from src.variables import *

import pygame
import random


class Enemy(Entity):
    def __init__(self, game, x, y, color, radius, width, speed, health, damage, xp):
        Entity.__init__(self, game, x, y, color, radius, width, speed)

        self.health = health
        self.damage = damage

        self.xp = xp

        self.healthBar = ProgressBar(self.game, 0, 0, 30, 5, (255, 255, 255), Color.ENEMY_COLOR_RED, (0, 0, 0), 1, 1, 3)

        self.history = {}

        self.id = 0

        self.target = self.game.nearestPlayer(self.x, self.y)

    def getDamage(self, damage, type: int = 0):
        type = random.randint(1, 10 ** 18) if type == 0 else type

        if self.history.get(type, -1) >= 0:
            return False

        self.history[type] = 10

        self.health[0] -= damage

        if self.health[0] <= 0 and self in self.game.objects:
            self.game.onEnemyKilled(self)

            if hasattr(self, "onDeath"):
                self.onDeath()

            self.game.objects.remove(self)

            return True

        self.healthBar.setValue(self.health[0] / self.health[1])

        return False

    def drawHealthBar(self):
        pygame.draw.rect(self.game.screen, self.color, (
            self.x - self.game.camera.x + self.game.width // 2 - 2 - self.radius * (self.health[0] / self.health[1]),
            self.y - self.game.camera.y + self.game.height // 2 - self.radius - 6,
            self.radius * (self.health[0] / self.health[1]) * 2 + 4,
            4
        ), 0, 2)

    def update(self):
        super().update()

        self.target = self.game.nearestPlayer(self.x, self.y)

        for key in self.history:
            self.history[key] -= 1

        if not self.game.headless:
            self.game.particles.append(Particle(self.game, self.x, self.y, self.color, 3, priority=0))

    def draw(self):
        super().draw()
