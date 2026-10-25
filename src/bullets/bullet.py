from src.particle import Particle

from src.entity import Entity
from src.enemy import Enemy

from src.variables import *

import random
import math


class Bullet(Entity):
    def __init__(self, game, x, y, color, radius, width, speed, target, type, liveTime, damage, guidance, deviation=0, alreadyDied=True, damageCD=0, onDeath=None, another=None):
        Entity.__init__(self, game, x, y, color, radius, width, speed)

        self.another = another if another else {}

        self.target = target
        self.type = type

        self.liveTime = liveTime
        self.live = 0

        self.guidance = guidance
        self.deviation = deviation

        self.angle = 0

        self.alreadyDied = alreadyDied
        self.damageCD = damageCD
        self.onDeath = onDeath

        self.cd = self.damageCD

        self.damage = damage

        self.toDestroy = False

        self.init()

    def init(self):
        if self.target is not None:
            self.angle = math.degrees(math.atan2(self.target.y - self.y, self.target.x - self.x)) + self.deviation

        else:
            self.angle = self.deviation

    def update(self):
        super().update()

        if self.target is not None:
            px = self.speed * math.cos(math.radians(self.angle))
            py = self.speed * math.sin(math.radians(self.angle))

            if ((self.target.x - self.game.player.x) ** 2 + (self.target.y - self.game.player.y) ** 2) < ((self.x - self.game.player.x) ** 2 + (self.y - self.game.player.y) ** 2):
                self.target = None

            if self.target not in self.game.objects:
                self.target = None

        if self.target is not None:
            self.angle += 40 * ((math.degrees(math.atan2(self.target.y - self.y, self.target.x - self.x)) - self.angle + 180) % 360 - 180) * self.guidance

        self.live += 1

        if self.live >= self.liveTime or self.toDestroy:
            if self.onDeath is not None:
                self.onDeath(self.x, self.y)
            
            if self in self.game.objects:
                self.game.objects.remove(self)

        self.vectors.append([self.angle, self.speed, 1])

        self.cd -= 1

        if self.type == "enemy":
            obj = self.game.player

            if math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2) <= self.radius + obj.radius + (5 if self.type == "player" else 1) and self.cd <= 0:
                self.cd = self.damageCD

                obj.getDamage(self.damage)

                if self in self.game.objects and self.alreadyDied:
                    if self.onDeath is not None:
                        self.onDeath(self.x, self.y)

                    self.game.objects.remove(self)

        if self.type == "player":
            for obj in self.game.objects:
                if self == obj or isinstance(obj, Bullet):
                    continue

                if math.sqrt((self.x - obj.x) ** 2 + (self.y - obj.y) ** 2) <= self.radius + obj.radius + (5 if self.type == "player" else 1):
                    if isinstance(obj, Enemy):
                        obj.getDamage(self.damage)

                        if self in self.game.objects and self.alreadyDied:
                            if self.onDeath is not None:
                                self.onDeath()

                            self.game.objects.remove(self)

                        if self.another.get("type", "") == "base" and self.game.player.upgrades.get("explosiveWeapon", 0):
                            self.explosive(self.game.player.weapons["base"]["another"]["explosiveDamage"] + 1, self.game.player.weapons["base"]["another"]["explosiveDamage"] // 1.5)

                        if self.another.get("type", "") == "shotgun":
                            for _ in range(self.game.player.weapons["shotgun"]["another"]["chapterCount"]):
                                self.game.objects.append(Bullet(self.game, self.x, self.y, Color.PLAYER_COLOR, PLAYER_BULLET_RADIUS - 2, 1, random.uniform(1.5, 2.5) + self.game.data["upgrades"]["pelletSpeed"], None, "player", 15, self.game.player.weaponGetDamage(self.game.player.weapons["shotgun"]) * self.game.player.weapons["shotgun"]["another"]["chapterDamageMultiply"], 0.001, deviation=random.randint(0, 360)))

                        if self.another.get("type", "") == "explosive":
                            self.explosive(4 * self.damage, self.damage)

        # self.game.particles.append(Particle(self.game, self.x, self.y, self.color, 3, priority=0))

    def explosive(self, main, chapter):
        for cobj in self.game.objects:
            if isinstance(cobj, Bullet):
                continue

            if math.sqrt((self.x - cobj.x) ** 2 + (self.y - cobj.y) ** 2) <= 50:
                cobj.getDamage(main)

        self.game.particles.append(Particle(self.game, self.x, self.y, Color.PLAYER_COLOR, 5, -3, 8, priority=1))

        for _ in range(5):
            angle = random.randint(0, 360)

            px = math.cos(angle) * 20
            py = math.sin(angle) * 20

            self.game.particles.append(Particle(self.game, self.x + px, self.y + py, Color.PLAYER_COLOR, 4, -1, 8, priority=1))

            for cobj in self.game.objects:
                if isinstance(cobj, Bullet):
                    continue

                if math.sqrt((self.x + px - cobj.x) ** 2 + (self.y + py - cobj.y) ** 2) <= 20:
                    xp = cobj.xp

                    if cobj.getDamage(chapter) and self.game.data["upgrades"]["explosiveWeaponGetXP"]:
                        self.game.player.getExperience(xp)
