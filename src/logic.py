from src.enemy import Enemy

import math


class Logic:
    def __init__(self, game):
        self.game = game

    def play(self):
        if self.game.pause:
            return

        if self.game.online:
            self.game.world.update()

        for obj in self.game.objects:
            obj.update()

        for particle in self.game.particles.particles:
            particle.update()

        self.game.spawn.update()

        if not self.game.online:
            self.enemyesCollisions()

        self.dronesCollisions()

    def enemyesCollisions(self):
        def binaryLeft(objects, x: float) -> int:
            left = 0
            right = len(objects) - 1
            mid = 0

            while left < right:
                mid = (left + right) // 2
                if objects[mid].x < x:
                    left = mid + 1

                else:
                    right = mid

            return left if objects[left].x >= x else 0

        def binaryRight(objects, x: float) -> int:
            left = 0
            right = len(objects) - 1
            mid = 0

            while left < right:
                mid = (left + right + 1) // 2
                if objects[mid].x > x:
                    right = mid - 1

                else:
                    left = mid

            return right if objects[right].x <= x else len(objects) - 1

        enemies = sorted([enemy for enemy in self.game.objects if isinstance(enemy, Enemy)], key=lambda enemy: enemy.x)

        for enemy in enemies:
            l = binaryLeft(enemies, enemy.x - enemy.radius - 5)
            r = binaryRight(enemies, enemy.x + enemy.radius + 5) + 1

            for index in range(l, r):
                dx = enemy.x - enemies[index].x
                dy = enemy.y - enemies[index].y

                distance = dx ** 2 + dy ** 2

                if distance == 0:
                    continue

                if distance < 900:
                    force = (30 - math.sqrt(distance)) / 30 * 1
                    angle = math.atan2(dy, dx)

                    enemies[index].vectors.append([math.degrees(angle) + 180, force, 0.5])
                    enemy.vectors.append([math.degrees(angle), force, 0.5])

    def dronesCollisions(self):
        if self.game.player is None:
            return

        for i in range(len(self.game.player.drones)):
            for j in range(i + 1, len(self.game.player.drones)):
                dx = self.game.player.drones[i].x - self.game.player.drones[j].x
                dy = self.game.player.drones[i].y - self.game.player.drones[j].y

                distance = math.sqrt(dx * dx + dy * dy)

                if distance == 0:
                    continue

                if distance < 20:
                    force = (20 - distance) / 20 * 1
                    angle = math.atan2(dy, dx)

                    self.game.player.drones[i].vectors.append([math.degrees(angle), force, 0.5])
                    self.game.player.drones[j].vectors.append([math.degrees(angle) + 180, force, 0.5])

    def choosing(self):
        self.play()

    def upgrade(self):
        self.game.render.upgradeMenuUpdate()

        for obj in self.game.objects:
            obj.update()

    def main(self):
        pass

    def mode(self):
        pass

    def online(self):
        pass

    def help(self):
        pass
