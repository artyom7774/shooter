from src.bullets import Bullet

from src.enemy import Enemy

from src.variables import *

import pygame
import math


class EnemyShootingBlue(Enemy):
    def __init__(self, game, x, y, color, radius, width, speed, health, damage, xp):
        Enemy.__init__(self, game, x, y, color, radius, width, speed, health, damage, xp)

        self.color = Color.ENEMY_COLOR_BLUE

    def update(self):
        super().update()

        distance = math.sqrt((self.target.x - self.x) ** 2 + (self.target.y - self.y) ** 2)
        angle = math.degrees(math.atan2(self.target.y - self.y, self.target.x - self.x))

        speed = 3 - 400 / distance
        speed = min(5, abs(speed)) * (1 if speed >= 0 else -1)

        self.vectors.append([angle, self.speed * speed, 0, [1, 0]])

        if distance / 500 < 1.2 and self.timer % 20 == 0:
            self.game.objects.append(Bullet(self.game, self.x, self.y, Color.ENEMY_COLOR_BLUE, ENEMY_BULLET_RADIUS, 1, 3, self.target, "enemy", 300, 5, 0))

    def draw(self):
        cx = int(self.x - self.game.camera.x + self.game.width // 2)
        cy = int(self.y - self.game.camera.y + self.game.height // 2)

        angle = math.degrees(math.atan2(self.y - self.target.y, self.x - self.target.x))

        points = []

        for i in range(3):
            cangle = angle + 120 * i

            x = math.cos(math.radians(cangle)) * self.radius
            y = math.sin(math.radians(cangle)) * self.radius

            points.append([cx - x, cy - y])

        pygame.draw.polygon(self.game.screen, self.color, points, 1)
