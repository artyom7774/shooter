from src.particle import Particle

from src.entity import Entity

import math


class Drone(Entity):
    def __init__(self, game, x, y, radius, width, color):
        Entity.__init__(self, game, x, y, color, radius, width, 0.5)

        self.command = "follow"
        self.counter = 0

    def update(self):
        super().update()

        self.counter += 1

        player = math.sqrt((self.game.player.x - self.x) ** 2 + (self.game.player.y - self.y) ** 2)
        angle = math.degrees(math.atan2(self.game.player.y - self.y, self.game.player.x - self.x))

        if self.command == "follow":
            if player > 40:
                self.vectors.append([angle, self.speed + player / 200, 0, [1, 0]])

            if player < 30:
                self.vectors.append([angle + 180, self.speed + player / 200, 0, [1, 0]])

    def draw(self):
        super().draw()
