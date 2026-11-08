from src.enemies import EnemyAttackingRed, EnemyDividedThirdRed, EnemyShootingRed
from src.enemy import Enemy

from src.variables import *

import random
import copy
import math


class BossSpawning(Enemy):
    def __init__(self, game, x, y, color, radius, width, speed, health, damage, xp, **kwargs):
        Enemy.__init__(self, game, x, y, color, radius, width, speed, health, damage, xp, **kwargs)

        self.count = 0
        self.max = 8

    def update(self):
        super().update()

        distance = math.sqrt((self.target.x - self.x) ** 2 + (self.target.y - self.y) ** 2)
        angle = math.degrees(math.atan2(self.target.y - self.y, self.target.x - self.x))

        speed = 2 - 400 / distance
        speed = min(5, abs(speed)) * (1 if speed >= 0 else -1)

        self.vectors.append([angle, self.speed * speed, 0, [1, 0]])

        if self.timer % (180 - 60 * self.settings.get("essence", 0)) == 0:
            self.spawn()

        if math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2) <= self.radius + self.target.radius:
            self.target.getDamage(self.damage, target=self)

    def spawn(self):
        enemy = random.choice([EnemyAttackingRed, EnemyShootingRed, EnemyDividedThirdRed])
        count = min(self.max - self.count, random.randint(1, 3))

        enemy = copy.deepcopy(self.game.spawn.enemyes[enemy])

        enemy["stats"]["health"][0] //= 2
        enemy["stats"]["health"][1] //= 2

        enemy["stats"]["xp"] //= 4

        for _ in range(count):
            self.game.spawn.spawn(self.x + random.randint(-200, 200), self.y + random.randint(-200, 200), enemy, death=lambda: self.death())

            self.count += 1

    def death(self):
        self.count -= 1
