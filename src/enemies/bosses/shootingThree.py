from src.bullets import Bullet

from src.enemy import Enemy

from src.variables import *

import random
import pygame
import math


class BossShootingThree(Enemy):
    def __init__(self, game, x, y, color, radius, width, speed, health, damage, xp, **kwargs):
        Enemy.__init__(self, game, x, y, color, radius, width, speed, health, damage, xp, **kwargs)

        self.bullets = []

    def update(self):
        super().update()

        distance = math.sqrt((self.target.x - self.x) ** 2 + (self.target.y - self.y) ** 2)
        angle = math.degrees(math.atan2(self.target.y - self.y, self.target.x - self.x))

        speed = 2 - 400 / distance
        speed = min(5, abs(speed)) * (1 if speed >= 0 else -1)

        self.vectors.append([angle, self.speed * speed, 0, [1, 0]])

        lenght = 15 - 5 * self.settings.get("essence", 0)
        precision = random.randint(0, lenght)

        if distance / 800 < 1.2 and self.timer % 60 == 0:
            for step in range(0, 360, lenght):
                self.game.objects.append(Bullet(self.game, self.x, self.y, self.color, ENEMY_BULLET_RADIUS, 1, 2, self.target, "enemy", 600, self.damage, 0, step + precision))

        if math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2) <= self.radius + self.target.radius:
            self.target.getDamage(self.damage, target=self)

    def draw(self):
        cx = int(self.x - self.game.camera.x + self.game.width // 2)
        cy = int(self.y - self.game.camera.y + self.game.height // 2)

        angle = math.degrees(math.atan2(self.y - self.target.y, self.x - self.target.x))

        points = []

        for i in range(4):
            cangle = angle + 90 * i

            x = math.cos(math.radians(cangle)) * self.radius
            y = math.sin(math.radians(cangle)) * self.radius

            points.append([cx - x, cy - y])

        pygame.draw.polygon(self.game.screen, self.color, points, 1)
