import threading
import itertools
import secrets
import time
import math
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.environ["SHOOTER_HEADLESS"] = "1"

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.net.protocol import *

from src.bullets import Bullet
from src.enemy import Enemy
from src.logic import Logic
from src.spawn import Spawn

from src.variables import *


class Config:
    def __init__(self, **kwargs):
        self.tickRate = TICK_RATE
        self.sendRate = SEND_RATE

        self.maxPlayers = MAX_PLAYERS
        self.timeout = PLAYER_TIMEOUT

        self.difficulty = 0.25

        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)


class NullParticles:
    particles = []

    def append(self, particle):
        pass

    def remove(self, particle):
        pass


class RemotePlayer:
    def __init__(self, world, pid, name, color):
        self.world = world

        self.id = pid
        self.name = name
        self.color = color

        self.x = 0.0
        self.y = 0.0
        self.radius = 9

        self.health = [100.0, 100.0]
        self.level = 1
        self.score = 0

        self.hitCD = 0

        self.lastSeen = time.time()

        self.events = []
        self.eventNumber = 0
        self.clientEvent = 0

    def push(self, event):
        self.eventNumber += 1

        self.events.append([self.eventNumber, *event])

        if len(self.events) > MAX_PENDING_EVENTS:
            del self.events[:len(self.events) - MAX_PENDING_EVENTS]

    def getDamage(self, damage, target=None):
        if self.hitCD > 0:
            return

        self.hitCD = PLAYER_GET_DAMAGE_CD

        self.push(["h", round(float(damage), 2), getattr(target, "id", 0) if target is not None else 0])


class HeadlessGame:
    headless = True
    online = False

    net = None
    player = None

    width = 1080
    height = 720

    def __init__(self, world):
        self.world = world

        self.objects = []
        self.particles = NullParticles()

        self.spawn = Spawn(self)

    def targets(self):
        return list(self.world.players.values())

    def nearestPlayer(self, x, y):
        best = None

        distance = 1e18

        for player in self.world.players.values():
            value = (player.x - x) ** 2 + (player.y - y) ** 2

            if value < distance:
                distance = value
                best = player

        return best if best is not None else self.world.nobody

    def difficulty(self):
        return 1 + self.world.config.difficulty * max(0, len(self.world.players) - 1)

    def onNewWave(self, wave):
        self.world.wave = wave

    def onEnemyKilled(self, enemy):
        for player in self.world.players.values():
            player.push(["x", enemy.xp])


class World:
    def __init__(self, config: Config = None):
        self.config = config if config is not None else Config()

        self.lock = threading.RLock()

        self.players = {}

        self.nobody = RemotePlayer(self, "", "", PLAYER_COLORS[0])

        self.tick = 0
        self.wave = 0

        self.game = HeadlessGame(self)
        self.logic = Logic(self.game)

        self.netIds = itertools.count(1)

        self.enemyIndex = {}
        self.snapshot = {"tick": 0, "wave": 0, "enemies": [], "bullets": []}

        self.xpTimer = 0

        self.running = False
        self.thread = None

        self.stepMs = 0.0
        self.started = time.time()

    def reset(self):
        self.game.objects.clear()
        self.game.spawn = Spawn(self.game)

        self.enemyIndex = {}
        self.snapshot = {"tick": self.tick, "wave": 0, "enemies": [], "bullets": []}

        self.wave = 0
        self.xpTimer = 0

    def start(self):
        self.running = True

        self.thread = threading.Thread(target=self.run, name="world", daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def run(self):
        step = 1 / self.config.tickRate
        every = max(1, round(self.config.tickRate / self.config.sendRate))

        next = time.perf_counter()

        while self.running:
            now = time.perf_counter()

            if now - next > 0.5:
                next = now

            steps = 0

            while next <= now and steps < 4:
                started = time.perf_counter()

                with self.lock:
                    self.step()

                    if self.tick % every == 0:
                        self.makeSnapshot()

                spent = (time.perf_counter() - started) * 1000

                self.stepMs += (spent - self.stepMs) * 0.05

                next += step
                steps += 1

            if steps == 4:
                next = now

            delay = next - time.perf_counter()

            if delay > 0:
                time.sleep(min(delay, 0.01))

    def step(self):
        self.tick += 1

        self.removeInactive()

        if not self.players:
            return

        for player in self.players.values():
            player.hitCD -= 1

        for obj in self.game.objects:
            obj.update()

        self.game.spawn.update()

        self.logic.enemyesCollisions()

        self.xpTimer += 1

    def removeInactive(self):
        now = time.time()

        for pid in [pid for pid, player in self.players.items() if now - player.lastSeen > self.config.timeout]:
            self.leave(pid, reason="timeout")

    def broadcast(self, event, skip=None):
        for player in self.players.values():
            if player.id != skip:
                player.push(event)

    def join(self, name):
        with self.lock:
            if len(self.players) >= self.config.maxPlayers:
                return None

            if not self.players:
                self.reset()

            used = {player.color for player in self.players.values()}

            color = next((index for index in range(len(PLAYER_COLORS)) if index not in used), 0)

            name = "".join(ch for ch in str(name) if ch.isprintable()).strip()[:PLAYER_NAME_LENGTH] or "Player"

            pid = secrets.token_hex(6)

            player = RemotePlayer(self, pid, name, color)

            self.players[pid] = player

            return {
                "id": pid,
                "color": color,
                "wave": self.wave,
                "tickRate": self.config.tickRate,
                "sendRate": self.config.sendRate,
                "players": len(self.players),
            }

    def leave(self, pid, reason="left"):
        with self.lock:
            player = self.players.pop(pid, None)

            if player is None:
                return False

            if not self.players:
                self.reset()

            return True

    @staticmethod
    def number(value, default=0.0, limit=1e7):
        try:
            value = float(value)

        except (TypeError, ValueError):
            return default

        if not math.isfinite(value):
            return default

        return max(-limit, min(limit, value))

    def handleUpdate(self, data):
        with self.lock:
            player = self.players.get(str(data.get("id", "")))

            if player is None:
                return 404, {"error": "unknown player"}

            player.lastSeen = time.time()

            self.applyState(player, data.get("st") or {})

            ack = int(self.number(data.get("ack"), 0, 1e12))

            if ack > 0:
                player.events = [event for event in player.events if event[0] > ack]

            events = data.get("ev") or []

            if isinstance(events, list):
                for event in events[:MAX_EVENTS_PER_REQUEST]:
                    self.applyEvent(player, event)

            return 200, self.response(player)

    def applyState(self, player, state):
        if not isinstance(state, dict):
            return

        player.x = self.number(state.get("x"), player.x)
        player.y = self.number(state.get("y"), player.y)

        player.health[0] = self.number(state.get("hp"), player.health[0], 1e9)
        player.health[1] = max(1.0, self.number(state.get("hpm"), player.health[1], 1e9))

        player.level = int(self.number(state.get("lvl"), player.level, 1e6))
        player.score = int(self.number(state.get("score"), player.score, 1e12))

    def applyEvent(self, player, event):
        if not isinstance(event, list) or len(event) < 2:
            return

        number = int(self.number(event[0], 0, 1e12))

        if number <= player.clientEvent:
            return

        player.clientEvent = number

        kind = event[1]

        if kind == "d" and len(event) >= 4:
            self.applyDamage(player, int(self.number(event[2], 0, 1e12)), self.number(event[3], 0))

        elif kind == "s" and len(event) >= 8:
            values = [self.number(value, 0, 1e5) for value in event[2:8]]

            self.broadcast(["s", player.id, *values], skip=player.id)

    def applyDamage(self, player, enemyId, damage):
        enemy = self.enemyIndex.get(enemyId)

        if enemy is None or not 0 < damage <= MAX_HIT_DAMAGE:
            return

        if math.hypot(enemy.x - player.x, enemy.y - player.y) > MAX_HIT_RANGE:
            return

        enemy.getDamage(damage)

    def makeSnapshot(self):
        enemies = []
        bullets = []

        index = {}

        for obj in self.game.objects:
            if isinstance(obj, Enemy):
                kind = ENEMY_INDEX.get(type(obj))

                if kind is None:
                    continue

                if obj.id == 0:
                    obj.id = next(self.netIds)

                index[obj.id] = obj

                enemies.append([obj.id, kind, round(obj.x, 1), round(obj.y, 1), round(max(0, obj.health[0]), 1), round(obj.health[1], 1), obj.radius])

            elif isinstance(obj, Bullet) and obj.type == "enemy":
                if not hasattr(obj, "id"):
                    obj.id = next(self.netIds)

                bullets.append([obj.id, round(obj.x, 1), round(obj.y, 1), obj.radius, obj.width, packColor(obj.color)])

        self.enemyIndex = index

        self.snapshot = {"tick": self.tick, "wave": self.wave, "enemies": enemies, "bullets": bullets}

    def response(self, player):
        snapshot = self.snapshot

        far = VIEW_RADIUS_ENEMIES
        near = VIEW_RADIUS_BULLETS

        px = player.x
        py = player.y

        return {
            "tick": snapshot["tick"],
            "wave": snapshot["wave"],
            "ack": player.clientEvent,
            "ev": player.events[:MAX_EVENTS_PER_REQUEST],
            "pl": [
                [other.id, other.name, other.color, round(other.x, 1), round(other.y, 1), round(other.health[0], 1), round(other.health[1], 1), other.level, other.score]
                for other in self.players.values() if other.id != player.id
            ],
            "en": [row for row in snapshot["enemies"] if abs(row[2] - px) < far and abs(row[3] - py) < far],
            "bu": [row for row in snapshot["bullets"] if abs(row[1] - px) < near and abs(row[2] - py) < near],
        }

    def status(self):
        with self.lock:
            return {
                "game": NAME,
                "version": VERSION,
                "protocol": PROTOCOL_VERSION,
                "uptime": round(time.time() - self.started),
                "wave": self.wave,
                "enemies": len(self.enemyIndex),
                "stepMs": round(self.stepMs, 2),
                "players": [{"name": p.name, "level": p.level, "score": p.score} for p in self.players.values()],
                "maxPlayers": self.config.maxPlayers,
            }
