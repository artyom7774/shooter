from src.enemy import Enemy

import random
import copy
import math


class BossAttacking(Enemy):
    def __init__(self, game, x, y, color, radius, width, speed, health, damage, xp, **kwargs):
        Enemy.__init__(self, game, x, y, color, radius, width, speed, health, damage, xp, **kwargs)

        self.precision = random.randint(0, 400)
        self.size = kwargs.get("size", 3 + self.settings.get("essence", 0))

        self.txp = self.xp
        self.xp = 0

    def update(self):
        super().update()

        distance = math.sqrt((self.target.x - self.x) ** 2 + (self.target.y - self.y) ** 2)
        angle = math.degrees(math.atan2(self.target.y - self.y, self.target.x - self.x))

        self.vectors.append([angle, 2 * self.speed * min(1, 1 + distance / 200) / self.size, 1])

        timer = self.timer + self.precision

        if timer % 200 == 0:
            self.vectors.append([angle + random.randint(-5, 5), 15 * self.speed ** 0.3, 0.5])

        if (timer + 40) % 200 == 0:
            self.vectors.append([angle + random.randint(-5, 5), 15 * self.speed ** 0.3, 0.5])

        if (timer + 80) % 200 == 0:
            self.vectors.append([angle + random.randint(-5, 5), 15 * self.speed ** 0.3, 0.5])

        if math.sqrt((self.x - self.target.x) ** 2 + (self.y - self.target.y) ** 2) <= self.radius + self.target.radius:
            self.target.getDamage(self.damage, target=self)

    def onDeath(self):
        if self.size == 1:
            return

        enemy = copy.deepcopy(self.game.spawn.enemyes[BossAttacking])

        enemy["stats"]["radius"] = self.radius - 3

        enemy["stats"]["health"][0] = self.health[1] // 1.5
        enemy["stats"]["health"][1] = self.health[1] // 1.5

        enemy["stats"]["xp"] = self.txp // 4 if self.size == 2 else 0

        enemy["stats"]["another"] = {
            "size": self.size - 1
        }

        for _ in range(2):
            self.game.spawn.spawn(self.x + random.randint(-5, 5), self.y + random.randint(-5, 5), enemy)
