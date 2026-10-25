import pygame
import math


class Entity:
    def __init__(self, game, x, y, color, radius, width, speed):
        self.game = game

        self.x = x
        self.y = y

        self.color = color
        self.radius = radius
        self.width = width

        self.speed = speed

        self.timer = 0

        self.vectors = []  # [angle, power, decrease, [live_time, 0]*]

    def update(self):
        self.timer += 1

        rem = []

        for i, vector in enumerate(self.vectors):
            px = math.cos(math.radians(vector[0])) * vector[1]
            py = math.sin(math.radians(vector[0])) * vector[1]

            otr1 = vector[1] >= 0

            self.x += px
            self.y += py

            vector[1] -= vector[2]

            otr2 = vector[1] >= 0

            if otr1 != otr2:
                rem.append(i)

                continue

            if len(vector) == 4:
                vector[3][1] += 1

                if vector[3][1] > vector[3][0]:
                    rem.append(i)

        for index in rem[::-1]:
            self.vectors.pop(index)

    def draw(self):
        cx = int(self.x - self.game.camera.x + self.game.width // 2)
        cy = int(self.y - self.game.camera.y + self.game.height // 2)

        if len(self.color) == 3 or self.color[3] == 255:
            pygame.draw.circle(self.game.screen, self.color, (cx, cy), self.radius, self.width)

        else:
            rect = pygame.Rect(cx - self.radius, cy - self.radius, self.radius * 2, self.radius * 2)
            surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

            pygame.draw.circle(surface, self.color, (self.radius, self.radius), self.radius, self.width)

            self.game.screen.blit(surface, rect)
