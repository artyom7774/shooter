from src.entity import Entity

from src.variables import *


class Particles:
    def __init__(self):
        self.particles = []

    def append(self, particle):
        if len(self.particles) > MAX_PARTICLES_COUNT and particle.priority == 0:
            return

        self.particles.append(particle)

    def remove(self, particle):
        self.particles.remove(particle)


class Particle(Entity):
    def __init__(self, game, x, y, color, radius, decrease=0.02, liveTime=1e9, priority=0):
        Entity.__init__(self, game, x, y, color, radius, 100, 0)

        self.priority = priority

        self.liveTime = liveTime
        self.decrease = decrease

        self.game = game

    def update(self):
        super().update()

        self.radius -= self.decrease
        self.liveTime -= 1

        if self.radius <= 0 or self.liveTime <= 0:
            self.game.particles.remove(self)
