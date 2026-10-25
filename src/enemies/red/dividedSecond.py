from src.enemies.red.dividedThird import EnemyDividedThirdRed
from src.enemy import Enemy

import random
import math


class EnemyDividedSecondRed(Enemy):
    def __init__(self, game, x, y, color, radius, width, speed, health, damage, xp):
        Enemy.__init__(self, game, x, y, color, radius, width, speed, health, damage, xp)

    def update(self):
        super().update()

        distance = math.sqrt((self.target.x - self.x) ** 2 + (self.target.y - self.y) ** 2)
        angle = math.degrees(math.atan2(self.target.y - self.y, self.target.x - self.x))

        self.vectors.append([angle, 2 * self.speed, 1e9])

        if math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2) <= self.radius + self.target.radius:
            self.target.getDamage(self.damage, target=self)

    def onDeath(self):
        for _ in range(3):
            self.game.spawn.spawn(self.x + random.randint(-5, 5), self.y + random.randint(-5, 5), self.game.spawn.enemyes[EnemyDividedThirdRed])
