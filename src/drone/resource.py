from src.entity import Entity

import pygame


class Resource(Entity):
    def __init__(self, game, x, y, name, radius, width, color):
        Entity.__init__(self, game, x, y, color, radius, width, 0)

        self.name = name
