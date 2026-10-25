from src.bullets import Bullet

from src.enemy import Enemy

from src.variables import *

import random
import math


class BossShootingTwo(Enemy):
    def __init__(self, game, x, y, color, radius, width, speed, health, damage, xp):
        Enemy.__init__(self, game, x, y, color, radius, width, speed, health, damage, xp)

        self.bullets = []

    def update(self):
        super().update()

        distance = math.sqrt((self.game.player.x - self.x) ** 2 + (self.game.player.y - self.y) ** 2)
        angle = math.degrees(math.atan2(self.game.player.y - self.y, self.game.player.x - self.x))

        self.vectors.append([angle, 0.5, 1e9])

        prec = random.randint(-35, 35)

        if self.timer % 120 == 0 and distance / 800 < 1.8:
            for i in range(-30, 30):
                bullet = Bullet(self.game, prec + self.x + 35 + i * 70, self.y - 1000, Color.ENEMY_COLOR_RED, ENEMY_BULLET_RADIUS, 1, 2, None, "enemy", 1000, self.damage, 0, 90)

                self.game.objects.append(bullet)
                self.bullets.append(bullet)

        if (self.timer + 120) % 120 == 0 and distance / 800 < 1.8:
            for i in range(-30, 30):
                bullet = Bullet(self.game, self.x - 1000, prec + self.y + 35 + i * 70, Color.ENEMY_COLOR_RED, ENEMY_BULLET_RADIUS, 1, 2, None, "enemy", 1000, self.damage, 0, 0)

                self.game.objects.append(bullet)
                self.bullets.append(bullet)

        if math.sqrt((self.x - self.game.player.x) ** 2 + (self.y - self.game.player.y) ** 2) <= self.radius + self.game.player.radius:
            self.game.player.getDamage(self.damage, target=self)

    def onDeath(self):
        for bullet in self.bullets:
            bullet.toDestroy = True
