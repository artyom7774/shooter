from src.net.protocol import *

from src.particle import Particle

from src.ui import print_text, get_text_size, BASE_FONT

from src.bullets import Bullet
from src.entity import Entity

from src.variables import *

import pygame
import random
import types
import math


class Smooth:
    def smoothInit(self, x, y):
        self.tx = x
        self.ty = y

        self.sx = x
        self.sy = y

        self.vx = 0
        self.vy = 0

    def setTarget(self, x, y, frames=3):
        frames = max(1, min(12, frames))

        vx = (x - self.sx) / frames
        vy = (y - self.sy) / frames

        if math.hypot(vx, vy) > 12:
            vx = vy = 0

        self.vx = vx
        self.vy = vy

        self.tx = x
        self.ty = y

        self.sx = x
        self.sy = y

    def smooth(self, k=0.15):
        self.tx += self.vx
        self.ty += self.vy

        self.x += self.vx + (self.tx - self.x) * k
        self.y += self.vy + (self.ty - self.y) * k


class NetDummy(Entity):
    xp = 0

    def getDamage(self, *args, **kwargs):
        return False


class NetBullet(Smooth, NetDummy):
    def __init__(self, game, row):
        NetDummy.__init__(self, game, row[1], row[2], unpackColor(row[5]), row[3], row[4], 0)

        self.id = row[0]

        self.smoothInit(row[1], row[2])

    def update(self):
        self.smooth()


class RemotePlayer(Smooth, NetDummy):
    def __init__(self, game, row):
        NetDummy.__init__(self, game, row[3], row[4], PLAYER_COLORS[row[2] % len(PLAYER_COLORS)], 9, 2, 0)

        self.id = row[0]

        self.name = row[1]

        self.smoothInit(row[3], row[4])

        self.set(row)

    def set(self, row, frames=3):
        self.setTarget(row[3], row[4], frames)

        self.hp = row[5]
        self.hpMax = max(1, row[6])

        self.level = row[7]
        self.score = row[8]

    def update(self):
        self.smooth(0.2)

    def draw(self):
        super().draw()

        cx = int(self.x - self.game.camera.x + self.game.width // 2)
        cy = int(self.y - self.game.camera.y + self.game.height // 2)

        width, height = get_text_size(BASE_FONT, 14, self.name)

        print_text(self.game.screen, cx - width // 2, cy - self.radius - height - 9, self.name, 14, BASE_FONT, self.color)

        pygame.draw.rect(self.game.screen, self.color, (cx - 14, cy - self.radius - 7, int(28 * max(0, min(1, self.hp / self.hpMax))), 3))
        pygame.draw.rect(self.game.screen, self.color, (cx - 14, cy - self.radius - 7, 28, 3), 1)


def puppetUpdate(self):
    self.timer += 1

    self._target = self.game.player

    self.vectors.clear()

    for key in self.history:
        self.history[key] -= 1

    self.smooth()

    self.healthBar.setValue(max(0, self.health[0] / self.health[1]))

    self.game.particles.append(Particle(self.game, self.x, self.y, self.color, 3, priority=0))


def puppetDamage(self, damage, type: int = 0):
    type = random.randint(1, 10 ** 18) if type == 0 else type

    if self.history.get(type, -1) >= 0:
        return False

    self.history[type] = 10

    self.game.net.sendDamage(self.id, damage)

    return False


class World:
    def __init__(self, game):
        self.game = game
        self.net = game.net

        self.enemies = {}
        self.bullets = {}
        self.players = {}

        self.lastEvent = 0
        self.lastWave = 0
        self.lastTick = 0

        self.joined = False

        self.ticks = 0

    def update(self):
        game = self.game
        net = self.net

        self.ticks += 1

        player = game.player

        net.setState({
            "x": round(player.x, 1),
            "y": round(player.y, 1),
            "hp": round(player.health[0], 1),
            "hpm": round(player.health[1], 1),
            "lvl": player.level,
            "score": int(player.score),
        })

        if net.status != "online":
            self.clear()

            return

        if net.joinInfo is not None and not self.joined:
            self.joined = True

            self.lastEvent = 0
            self.lastTick = 0

            player.dashNotTakeDamageCD = max(player.dashNotTakeDamageCD, 120)

        answers = net.takeResponses()

        for answer in answers:
            self.events(answer.get("ev", []))

            if not game.online:
                return

        if answers:
            self.snapshot(answers[-1])

    def clear(self):
        if self.joined:
            self.joined = False

        for group in (self.enemies, self.bullets, self.players):
            for obj in group.values():
                if obj in self.game.objects:
                    self.game.objects.remove(obj)

            group.clear()

    def events(self, events):
        game = self.game

        for event in events:
            number = event[0]

            if number <= self.lastEvent:
                continue

            self.lastEvent = number

            kind = event[1]

            if kind == "h":
                if game.menu != "choosing":
                    game.player.getDamage(event[2], target=self.enemies.get(event[3]))

            elif kind == "x":
                game.player.getExperience(event[2])

            elif kind == "s":
                other = self.players.get(event[2])

                color = other.color if other is not None else Color.PLAYER_COLOR

                game.objects.append(Bullet(game, event[3], event[4], color, event[7], 1, event[6], None, "ghost", int(event[8]), 0, 0.001, deviation=event[5]))

            if not game.online:
                return

        self.net.confirm(self.lastEvent)

    def snapshot(self, answer):
        game = self.game

        wave = answer.get("wave", 0)

        if wave < self.lastWave:
            self.lastWave = wave

        while self.lastWave < wave:
            self.lastWave += 1

            game.onNewWave(self.lastWave)

        game.spawn.wave = wave

        tick = answer.get("tick", 0)

        frames = tick - self.lastTick if self.lastTick else 3

        self.lastTick = tick

        if frames <= 0:
            return

        self.syncPlayers(answer.get("pl", []), frames)
        self.syncEnemies(answer.get("en", []), frames)
        self.syncBullets(answer.get("bu", []), frames)

    def syncPlayers(self, rows, frames=3):
        seen = set()

        for row in rows:
            seen.add(row[0])

            other = self.players.get(row[0])

            if other is None:
                other = RemotePlayer(self.game, row)

                self.players[row[0]] = other
                self.game.objects.append(other)

            else:
                other.set(row, frames)

        for pid in [pid for pid in self.players if pid not in seen]:
            other = self.players.pop(pid)

            if other in self.game.objects:
                self.game.objects.remove(other)

    def syncEnemies(self, rows, frames=3):
        seen = set()

        for row in rows:
            seen.add(row[0])

            puppet = self.enemies.get(row[0])

            fresh = False

            if puppet is None:
                puppet = self.createEnemy(row)

                if puppet is None:
                    continue

                fresh = True

                self.enemies[row[0]] = puppet
                self.game.objects.append(puppet)

            if not fresh:
                puppet.setTarget(row[2], row[3], frames)

            puppet.health[0] = row[4]
            puppet.health[1] = max(1, row[5])

        for eid in [eid for eid in self.enemies if eid not in seen]:
            puppet = self.enemies.pop(eid)

            if puppet in self.game.objects:
                self.game.objects.remove(puppet)

    def createEnemy(self, row):
        if not 0 <= row[1] < len(ENEMY_TYPES):
            return None

        puppet = ENEMY_TYPES[row[1]](self.game, row[2], row[3], Color.ENEMY_COLOR_RED, row[6], 1, 1, [row[4], max(1, row[5])], 0, 0)

        puppet.id = row[0]

        for name in ("smoothInit", "setTarget", "smooth"):
            setattr(puppet, name, types.MethodType(getattr(Smooth, name), puppet))

        puppet.smoothInit(row[2], row[3])

        puppet.update = types.MethodType(puppetUpdate, puppet)
        puppet.getDamage = types.MethodType(puppetDamage, puppet)

        return puppet

    def syncBullets(self, rows, frames=3):
        seen = set()

        for row in rows:
            seen.add(row[0])

            bullet = self.bullets.get(row[0])

            if bullet is None:
                bullet = NetBullet(self.game, row)

                self.bullets[row[0]] = bullet
                self.game.objects.append(bullet)

            else:
                bullet.setTarget(row[1], row[2], frames)

        for bid in [bid for bid in self.bullets if bid not in seen]:
            bullet = self.bullets.pop(bid)

            if bullet in self.game.objects:
                self.game.objects.remove(bullet)

    def draw(self):
        screen = self.game.screen

        y = 62

        for other in sorted(self.players.values(), key=lambda other: other.id):
            text = f"{other.name} Lv {other.level} {max(0, round(100 * other.hp / other.hpMax))}%"

            width, height = get_text_size(BASE_FONT, 16, text)

            print_text(screen, self.game.width - width - 10, y, text, 16, BASE_FONT, other.color)

            y += height + 2

        if self.net.status == "online":
            text = f"online | {self.net.ping} ms | {len(self.players) + 1} players"

            width, height = get_text_size(BASE_FONT, 14, text)

            print_text(screen, self.game.width // 2 - width // 2, self.game.height - height - 6, text, 14, BASE_FONT, (150, 150, 150))

            return

        if self.net.status == "error":
            lines = [f"Can't connect to {self.net.address}", self.net.error]

        else:
            lines = [f"Connecting to {self.net.address}...", self.net.error]

        y = self.game.height // 2 - 30

        for line in lines:
            if not line:
                continue

            width, height = get_text_size(BASE_FONT, 20, line)

            print_text(screen, self.game.width // 2 - width // 2, y, line, 20, BASE_FONT, Color.ENEMY_COLOR_RED if self.net.status == "error" else Color.PLAYER_COLOR)

            y += height + 6
