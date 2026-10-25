from src.bullets import Bullet

from src.enemy import Enemy

from src.variables import *

import math


class BossShooting(Enemy):
    def __init__(self, game, x, y, color, radius, width, speed, health, damage, xp):
        Enemy.__init__(self, game, x, y, color, radius, width, speed, health, damage, xp)

    def update(self):
        super().update()

        distance = math.sqrt((self.game.player.x - self.x) ** 2 + (self.game.player.y - self.y) ** 2)
        angle = math.degrees(math.atan2(self.game.player.y - self.y, self.game.player.x - self.x))

        speed = 2 - 400 / distance
        speed = min(5, abs(speed)) * (1 if speed >= 0 else -1)

        # self.vectors.append([angle, speed / 2, 0, [1, 0]])

        if distance / 800 < 1.2 and self.timer % 9 == 0:
            self.game.objects.append(Bullet(self.game, self.x, self.y, Color.ENEMY_COLOR_RED, ENEMY_BULLET_RADIUS, 1, 2, None, "enemy", 300, 5, 0, self.timer % 360 + 0))
            self.game.objects.append(Bullet(self.game, self.x, self.y, Color.ENEMY_COLOR_RED, ENEMY_BULLET_RADIUS, 1, 2, None, "enemy", 300, 5, 0, self.timer % 360 + 90))
            self.game.objects.append(Bullet(self.game, self.x, self.y, Color.ENEMY_COLOR_RED, ENEMY_BULLET_RADIUS, 1, 2, None, "enemy", 300, 5, 0, self.timer % 360 + 180))
            self.game.objects.append(Bullet(self.game, self.x, self.y, Color.ENEMY_COLOR_RED, ENEMY_BULLET_RADIUS, 1, 2, None, "enemy", 300, 5, 0, self.timer % 360 + 270))

        if math.sqrt((self.x - self.game.player.x) ** 2 + (self.y - self.game.player.y) ** 2) <= self.radius + self.game.player.radius:
            self.game.player.getDamage(self.damage, target=self)
