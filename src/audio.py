from src.drone.drones.mining import MiningDrone

import threading
import pygame
import random
import json
import time
import math
import os


class AudioElement:
    @staticmethod
    def drill(game):
        if game.menu == "play":
            distance = 1e9

            for drone in game.player.drones:
                if not isinstance(drone, MiningDrone):
                    continue

                if drone.command == "follow" or math.sqrt((drone.now[0] - drone.x) ** 2 + (drone.now[1] - drone.y) ** 2) > 100:
                    continue

                distance = min(distance, math.sqrt((drone.x - game.player.x) ** 2 + (drone.y - game.player.y) ** 2))

            game.audio.sounds["drill"]["volume"] = 1 / (1 + ((distance + 100) / 140) ** 1.618) / 3

        else:
            game.audio.sounds["drill"]["volume"] = 0

    @staticmethod
    def music(game):
        game.audio.sounds["music"]["volume"] = 1


class Audio:
    functions = ["drill", "music"]

    def __init__(self, game):
        self.game = game

        pygame.mixer.init()

        self.lock = threading.Lock()

        self.settings = json.load(open("files/music/settings.json", "r", encoding="utf-8"))
        self.sounds = {}

        self.master = self.game.settings["audio"]["master"]

        idx = 0

        pygame.mixer.set_num_channels(1024)

        for type in os.listdir("files/music"):
            idx += 2

            if type.endswith(".json"):
                continue

            if os.path.isfile(f"files/music/{type}"):
                self.sounds[type.replace(".mp3", "")] = {
                    "index": idx,
                    "channel": [pygame.mixer.Channel(idx), pygame.mixer.Channel(idx + 1)],
                    "volume": 0,

                    "paths": [f"{type}"],
                    "music": [pygame.mixer.Sound(f"files/music/{type}")],
                    "now": -1
                }

                continue

            self.sounds[type] = {
                "index": idx,
                "channel": [pygame.mixer.Channel(idx), pygame.mixer.Channel(idx + 1)],
                "volume": 0,

                "paths": [f"{type}/{name}" for name in os.listdir(f"files/music/{type}")],
                "music": [pygame.mixer.Sound(f"files/music/{type}/{name}") for name in os.listdir(f"files/music/{type}")],
                "now": -1
            }

            self.sounds[type]["channel"][0].set_endevent(pygame.USEREVENT + idx)
            self.sounds[type]["channel"][1].set_endevent(pygame.USEREVENT + idx)

    def init(self):
        self.play("music")
        self.play("drill")

    def update(self):
        for function in self.functions:
            getattr(AudioElement, function)(self.game)

            self.volume(function)

    def reload(self, type, count, idx, channel):
        time.sleep(self.sounds[type]["music"][idx].get_length() - 0.1)

        self.play(type, None, count, channel)

    def volume(self, type):
        for channel in self.sounds[type]["channel"]:
            channel.set_volume(self.sounds[type]["volume"] * self.settings.get(self.sounds[type]["paths"][self.sounds[type]["now"]], 1) * self.master)

    def play(self, type, idx: int = None, count: int = -1, channel: int = 0):
        with self.lock:
            if count == 0:
                return

            self.sounds[type]["now"] = random.randint(0, len(self.sounds[type]["music"]) - 1) if idx is None else idx

            self.volume(type)

            thr = threading.Thread(target=lambda: self.reload(type, count - 1, self.sounds[type]["now"], 1 - channel))
            thr.daemon = True
            thr.start()

            self.sounds[type]["channel"][channel].play(self.sounds[type]["music"][self.sounds[type]["now"]])
