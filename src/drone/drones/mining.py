from src.drone.drone import Drone

from src.ui import circleSegment

from src.variables import *

import pygame
import random
import math


class MiningDrone(Drone):
    def __init__(self, player, game):
        Drone.__init__(self, game, player.x + random.randint(-100, 100), player.y + random.randint(-100, 100), 5, 1, Color.DRONE_MINING_COLOR)

        self.multiply = player.dronesResourceMultiply
        self.time = 60

        self.droneSpeedUpTimer = [0, 600]

        self.now = None

    def update(self):
        super().update()

        player = math.sqrt((self.game.player.x - self.x) ** 2 + (self.game.player.y - self.y) ** 2)

        if self.now is None and player < 200 and self.game.fpsc % 10 == 0:
            for resource in self.game.resources:
                distance = math.sqrt((resource.x - self.x) ** 2 + (resource.y - self.y) ** 2)

                if distance < 300 and not any([isinstance(drone, MiningDrone) and drone.now == [resource.x, resource.y, resource.name] for drone in self.game.player.drones]):
                    self.now = [resource.x, resource.y, resource.name]

                    self.command = "mining"
                    self.counter = 0

        if self.command == "mining":
            distance = math.sqrt((self.now[0] - self.x) ** 2 + (self.now[1] - self.y) ** 2)
            angle = math.degrees(math.atan2(self.now[1] - self.y, self.now[0] - self.x))

            if distance > 40:
                self.vectors.append([angle, self.speed + distance / 200, 0, [1, 0]])

            if self.counter > 60 * self.time:
                self.game.player.resources[self.now[2]] += self.multiply * (2 if random.randint(0, 100) <= 5 * len(self.game.player.drones) and self.game.data["upgrades"]["chanceDuplicateResource"] else 1)

                idx = -1

                for i in range(len(self.game.resources)):
                    if self.game.resources[i].x == self.now[0] and self.game.resources[i].y == self.now[1] and self.game.resources[i].name == self.now[2]:
                        idx = i

                self.game.resources.pop(idx)

                self.command = "follow"
                self.counter = 0

                self.now = None

            if player <= 100:
                self.droneSpeedUpTimer[0] = min(self.droneSpeedUpTimer[0] + 3, self.droneSpeedUpTimer[1])

            if self.droneSpeedUpTimer[0] >= 1:
                self.droneSpeedUpTimer[0] -= 1

                self.counter += 1

            # print(self.droneSpeedUpTimer)

    def draw(self):
        super().draw()

        cpos = (int(self.x - self.game.camera.x + self.game.width // 2), int(self.y - self.game.camera.y + self.game.height // 2))

        pygame.draw.circle(self.game.screen, Color.DRONE_MINING_COLOR, cpos, 2)

        if self.now and (self.now[0] - self.x) ** 2 + (self.now[1] - self.y) ** 2 < 10000:
            rpos = (int(self.now[0] - self.game.camera.x + self.game.width // 2), int(self.now[1] - self.game.camera.y + self.game.height // 2))

            pygame.draw.line(self.game.screen, Color.DRONE_MINING_COLOR, cpos, rpos, 1)
            pygame.draw.circle(self.game.screen, Color.DRONE_MINING_COLOR, rpos, 2)

        if self.command == "mining":
            circleSegment(self.game.screen, Color.DRONE_MINING_COLOR, cpos, 12, 90 - 360 * self.droneSpeedUpTimer[0] / self.droneSpeedUpTimer[1], 90, 2)
