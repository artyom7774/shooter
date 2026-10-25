from src.enemy import Enemy

from src.variables import *

from src.enemies import *
from src.bosses import *

import random
import math


SPAWNED_ENEMIES = [
    {
        "point": 1,
        "chance": 1,
        "class": EnemyShootingRed,
        "stats": {
            "health": [4, 4],
            "damage": 5,
            "radius": 8,
            "xp": 1
        }
    },
    {
        "point": 2,
        "chance": 1,
        "class": EnemyAttackingRed,
        "stats": {
            "health": [7, 7],
            "damage": 5,
            "radius": 8,
            "xp": 2
        }
    },
    {
        "point": 5,
        "chance": 0.5,
        "class": EnemyShootingAroundRed,
        "stats": {
            "health": [6, 6],
            "damage": 5,
            "radius": 8,
            "xp": 5
        }
    },
    {
        "point": 8,
        "chance": 0.5,
        "class": EnemyShootingTripleRed,
        "stats": {
            "health": [6, 6],
            "damage": 5,
            "radius": 8,
            "xp": 8
        }
    },
    {
        "point": 10,
        "chance": 0.25,
        "class": EnemyAttackingTripleRed,
        "stats": {
            "health": [10, 10],
            "damage": 5,
            "radius": 8,
            "xp": 12
        }
    },
    {
        "point": 30,
        "chance": 0.15,
        "class": EnemyDividedFirstRed,
        "stats": {
            "health": [30, 30],
            "damage": 6,
            "radius": 13,
            "xp": 10
        }
    },
    {
        "point": 8,
        "chance": 0.5,
        "class": EnemyDividedSecondRed,
        "stats": {
            "health": [10, 10],
            "damage": 4,
            "radius": 8,
            "xp": 4
        }
    },
    {
        "point": 3,
        "chance": 1,
        "class": EnemyDividedThirdRed,
        "stats": {
            "health": [3, 3],
            "damage": 2,
            "radius": 6,
            "xp": 1
        }
    },
    {
        "point": 20,
        "chance": 0.25,
        "class": EnemyShootingPotionRed,
        "stats": {
            "health": [8, 8],
            "damage": 5,
            "radius": 8,
            "xp": 20
        }
    },
    {
        "point": 30,
        "chance": 0.2,
        "class": EnemyShootingBlue,
        "stats": {
            "health": [8, 8],
            "damage": 5,
            "radius": 8,
            "xp": 25
        }
    },
    {
        "point": 30,
        "chance": 0.15,
        "class": EnemyAttackingBlue,
        "stats": {
            "health": [13, 13],
            "damage": 5,
            "radius": 8,
            "xp": 25
        }
    },
]

SPAWNED_BOSSES = [
    {
        "point": 50,
        "class": BossShooting,
        "stats": {
            "health": [50, 50],
            "damage": 5,
            "radius": 13,
            "xp": 100
        }
    },
    {
        "point": 200,
        "class": BossShootingTwo,
        "stats": {
            "health": [80, 80],
            "damage": 5,
            "radius": 13,
            "xp": 250
        }
    }
]


class Spawn:
    def __init__(self, game):
        self.game = game

        self.wave = 0
        self.points = 5

        self.timerToNewWave = 0

        self.enemyes = {}

        for enemy in SPAWNED_ENEMIES:
            self.enemyes[enemy["class"]] = enemy

        for enemy in SPAWNED_BOSSES:
            self.enemyes[enemy["class"]] = enemy

    def update(self):
        if self.game.online:
            return

        count = len(list(filter(lambda obj: isinstance(obj, Enemy), self.game.objects)))

        self.timerToNewWave -= 1

        if count == 0 and self.timerToNewWave < 0:
            self.timerToNewWave = TIMER_TO_NEW_WAVE

        if count == 0 and self.timerToNewWave == 0:
            self.next()

    def spawn(self, x, y, enemy):
        self.game.objects.append(enemy["class"](self.game, x, y, Color.ENEMY_COLOR_RED, enemy["stats"]["radius"], 1, math.sqrt(math.log2(self.wave) / 1.618 + 1), [int(enemy["stats"]["health"][0] * (1 + self.wave / ENEMYES_PROGRESSION_MYLTIPLY)), int(enemy["stats"]["health"][1] * (1 + self.wave / ENEMYES_PROGRESSION_MYLTIPLY))], int(enemy["stats"]["damage"] * (1 + self.wave / ENEMYES_PROGRESSION_MYLTIPLY)), enemy["stats"]["xp"]))

    def position(self):
        players = self.game.targets()

        center = random.choice(players)

        x = center.x
        y = center.y

        while math.sqrt((center.x - x) ** 2 + (center.y - y) ** 2) < 250:
            x = random.randint(-2 * self.game.width, 2 * self.game.width) + center.x
            y = random.randint(-2 * self.game.height, 2 * self.game.height) + center.y

        return [x, y]

    def next(self):
        self.wave += 1

        self.game.onNewWave(self.wave)

        points = math.ceil((self.points * WAVE_BOSS_POINTS_CAPACITY if (self.wave % 5 == 0 and self.wave >= 10) else self.points) * random.uniform(*WAVE_RANDOM_POINTS_CAPACITY))
        points = math.ceil(points * self.game.difficulty())

        self.points *= WAVE_NEXT_CAPACITY

        if self.wave % 5 == 0 and self.wave >= 10:
            enemy = random.choice(SPAWNED_BOSSES)

            iter = 0

            while enemy["point"] > points and iter <= 100:
                enemy = random.choice(SPAWNED_BOSSES)

                iter += 1

            self.spawn(*self.position(), enemy)

            points //= 5

        while points > 0:
            enemyes = [e for e in SPAWNED_ENEMIES if e.get("point") <= points]

            if len(enemyes) == 0:
                break

            weights = []

            for enemy in enemyes:
                weights.append(enemy["chance"] * enemy["point"] ** 0.5)

            enemy = random.choices(enemyes, weights=weights, k=1)[0]

            self.spawn(*self.position(), enemy)

            points -= enemy["point"]
