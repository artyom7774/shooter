from src.enemy import Enemy

import random
import math


class EnemyAttackingRed(Enemy):
    def __init__(self, game, x, y, color, radius, width, speed, health, damage, xp):
        Enemy.__init__(self, game, x, y, color, radius, width, speed, health, damage, xp)

    def update(self):
        super().update()

        distance = math.sqrt((self.target.x - self.x) ** 2 + (self.target.y - self.y) ** 2)
        angle = math.degrees(math.atan2(self.target.y - self.y, self.target.x - self.x))

        self.vectors.append([angle, self.speed * min(1, 1 + distance / 200), 1])

        if self.timer % 100 == 0:
            self.vectors.append([angle + random.randint(-5, 5), 15 * self.speed ** 0.3, 0.5])

        if math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2) <= self.radius + self.target.radius:
            self.target.getDamage(self.damage, target=self)
