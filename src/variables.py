from src.background import NOISE_PARAMS, background

NAME = "Ascension Protocol"
VERSION = "v1.3.0"


class Color:
    UPGRADE_RED_COLOR = (230, 100, 100)
    UPGRADE_YELLOW_COLOR = (240, 210, 100)
    UPGRADE_BLUE_COLOR = (90, 130, 230)
    UPGRADE_WHITE_COLOR = (245, 245, 245)
    UPGRADE_GREEN_COLOR = (90, 230, 130)
    UPGRADE_PURPLE_COLOR = (240, 100, 210)
    UPGRADE_GRAY_COLOR = (120, 120, 120)

    TREE_WHITE_COLOR = (245, 245, 245)
    TREE_BLUE_COLOR = (70, 185, 200)

    PLAYER_COLOR = (245, 245, 245)

    ENEMY_COLOR_RED = (200, 70, 70)
    ENEMY_COLOR_BLUE = (70, 70, 200)

    TEXT_COLOR = (250, 250, 250)
    BASE_UI_COLOR = (220, 220, 220)

    ITEM_CRYSTAL_COLOR = (70, 185, 200)

    DRONE_MINING_COLOR = (245, 245, 245)
    DRONE_ATTACK_COLOR = (245, 245, 245)

    HEALTH_BAR_COLOR = (235, 40, 40)
    ARMOR_BAR_COLOR = (120, 120, 120)
    XP_BAR_COLOR = (40, 220, 40)
    STAMINA_BAR_COLOR = (40, 220, 40)


BACKGROUND = background()

WAVE_RANDOM_POINTS_CAPACITY = [0.8, 1.2]
WAVE_BOSS_POINTS_CAPACITY = 0.5
WAVE_NEXT_CAPACITY = 1.35

MAX_PARTICLES_COUNT = 10000

ENEMYES_PROGRESSION_MYLTIPLY = 10
ENEMY_BULLET_RADIUS = 4

PLAYER_XP_REQUEREMENTS_MULTIPLY = 2
PLAYER_DASH_NOT_TAKE_DAMAGE_CD = 25
PLAYER_GET_DAMAGE_CD = 10
PLAYER_BULLET_RADIUS = 5

PLAYER_POINTS_MULTIPLY = 1.5

TIMER_TO_NEW_WAVE = 100

SPEED_UP_MODE = False

UPGRADE_CELL_SIZE = 50

CHOOSES = {
    "health": {
        "code": "health",
        "name": "Health",
        "description": "Up health by 50 points",
        "function": "self.game.player.health[1] += 50",
        "color": Color.UPGRADE_RED_COLOR,
        "open": True,
        "weight": 1,
        "max": -1
    },

    "attackSpeed": {
        "code": "attackSpeed",
        "name": "Attack speed",
        "description": "Reduces weapon reload time by 20%",
        "function": "self.game.player.attackSpeedMultiply *= 0.8",
        "color": Color.UPGRADE_YELLOW_COLOR,
        "open": True,
        "weight": 0.3,
        "max": 20
    },

    "speed": {
        "code": "speed",
        "name": "Speed",
        "description": "Up speed by 10%",
        "function": "self.game.player.speed *= 1.1",
        "color": Color.UPGRADE_BLUE_COLOR,
        "open": True,
        "weight": 1,
        "max": 5
    },

    "healing": {
        "code": "healing",
        "name": "Healing",
        "confirm": "self.game.player.health[0] != self.game.player.health[1]",
        "description": "Healing all health",
        "function": "self.game.player.health[0] = self.game.player.health[1]",
        "color": Color.UPGRADE_GREEN_COLOR,
        "open": True,
        "weight": 0.5,
        "max": 1
    },

    "doubleShot": {
        "code": "doubleShot",
        "name": "Double shot",
        "description": "Reduces base weapon reload time by 30%",
        "function": "",
        "color": Color.UPGRADE_WHITE_COLOR,
        "open": False,
        "weight": 0.07,
        "max": 1
    },

    "explosiveWeapon": {
        "code": "explosiveWeapon",
        "name": "Explosive weapon",
        "description": "The base weapon's bullet explodes",
        "function": "",
        "color": Color.UPGRADE_WHITE_COLOR,
        "open": False,
        "weight": 0.07,
        "max": 1
    },

    "bigWeapon": {
        "code": "bigWeapon",
        "name": "Big weapon",
        "description": "The base weapon damage +50%, player speed -80%",
        "function": "self.game.player.speed *= 0.2; self.game.player.attackDamageMultiply *= 1.5",
        "color": Color.UPGRADE_PURPLE_COLOR,
        "open": True,
        "weight": 0.02,
        "max": 1
    },

    "revival": {
        "code": "revival",
        "name": "Revival",
        "description": "Revives a character after death",
        "function": "",
        "color": Color.UPGRADE_WHITE_COLOR,
        "open": False,
        "weight": 0.07,
        "max": 1
    },

    "armor": {
        "code": "armor",
        "name": "Armor",
        "description": "Up armor by 5 points",
        "function": "self.game.player.armor[1] += 5",
        "color": Color.UPGRADE_GRAY_COLOR,
        "open": False,
        "weight": 0.6,
        "max": -1
    },

    "notTakeDamageWhileDashing": {
        "code": "notTakeDamageWhileDashing",
        "name": "No dashing damage",
        "description": "Player not take damage while dashing",
        "function": "",
        "color": Color.UPGRADE_PURPLE_COLOR,
        "open": False,
        "weight": 0.1,
        "max": 1
    },

    "spikedArmor": {
        "code": "spikedArmor",
        "name": "Spiked armor",
        "description": "Enemy who damaged armor get 4x damage",
        "function": "",
        "color": Color.UPGRADE_PURPLE_COLOR,
        "open": False,
        "weight": 0.1,
        "max": 1
    },

    "unlockShotgun": {
        "code": "unlockShotgun",
        "confirm": "self.game.player.weaponsActive < self.game.player.weaponsMaxCount",
        "name": "Unlock shotgun",
        "description": "Unlock shotgun",
        "function": "self.game.player.weaponsActive += 1; self.game.player.weapons['shotgun']['active'] = True",
        "color": Color.UPGRADE_WHITE_COLOR,
        "open": False,
        "weight": 0.05,
        "max": 1,

        "another": {
            "type": "weapon"
        }
    },

    "unlockMachineGun": {
        "code": "unlockMachineGun",
        "confirm": "self.game.player.weaponsActive < self.game.player.weaponsMaxCount",
        "name": "Unlock machine gun",
        "description": "Unlock machine gun",
        "function": "self.game.player.weaponsActive += 1; self.game.player.weapons['machineGun']['active'] = True",
        "color": Color.UPGRADE_WHITE_COLOR,
        "open": False,
        "weight": 0.05,
        "max": 1,

        "another": {
            "type": "weapon"
        }
    },

    "unlockExplosive": {
        "code": "unlockExplosive",
        "confirm": "self.game.player.weaponsActive < self.game.player.weaponsMaxCount",
        "name": "Unlock explosive",
        "description": "Unlock explosive",
        "function": "self.game.player.weaponsActive += 1; self.game.player.weapons['explosive']['active'] = True",
        "color": Color.UPGRADE_WHITE_COLOR,
        "open": False,
        "weight": 0.05,
        "max": 1,

        "another": {
            "type": "weapon"
        }
    },

    "unlockLaser": {
        "code": "unlockLaser",
        "confirm": "self.game.player.weaponsActive < self.game.player.weaponsMaxCount",
        "name": "Unlock laser",
        "description": "Unlock laser",
        "function": "self.game.player.weaponsActive += 1; self.game.player.weapons['laser']['active'] = True",
        "color": Color.UPGRADE_WHITE_COLOR,
        "open": False,
        "weight": 0.05,
        "max": 1,

        "another": {
            "type": "weapon"
        }
    },

    "laserAttackEveryFrame": {
        "code": "laserAttackEveryFrame",
        "confirm": "self.game.player.weapons['laser']['active']",
        "name": "Laser attack every frame",
        "description": "Every frame laser deals 1% of damage",
        "function": "",
        "color": Color.UPGRADE_PURPLE_COLOR,
        "open": False,
        "weight": 0.1,
        "max": 1
    },
}

OPENS = {
    "health": True,
    "attackSpeed": True,
    "speed": True,
    "healing": True,
    "doubleShot": False,
    "explosiveWeapon": False,
    "bigWeapon": True,
    "revival": False,
    "armor": False,
    "notTakeDamageWhileDashing": False,
    "spikedArmor": False,
    "unlockShotgun": False,
    "unlockMachineGun": False,
    "unlockExplosive": False,
    "unlockLaser": False,
    "laserAttackEveryFrame": False
}

"""
UPGRADES = {
    "11": {
        "code": "11",
        "dependencies": ["7"],
        "function": "CHOOSES['spikedArmor']['open'] = 1",
        "display": "Spiked armor",
        "description": "Open upgrade, when attacking an enemy, it deals 4x the damage that was dealt to the player's armor",
        "symbol": "UPG",
        "color": Color.UPGRADE_WHITE_COLOR,
        "have": False,
        "cost": 2000,
        "x": 4,
        "y": -4
    },
    "12": {
        "code": "12",
        "dependencies": ["6"],
        "function": "self.armorGetAttackBonus = True",
        "display": "Armored damage",
        "description": "+20% damage while armor is not empty",
        "symbol": "ATK",
        "color": Color.UPGRADE_WHITE_COLOR,
        "have": False,
        "cost": 1000,
        "x": 4,
        "y": 2
    }
}
"""

UPGRADES = {
    "health": {
        "code": "health",
        "dependencies": [],
        "function": "self.health = [self.health[0] + 100, self.health[1] + 100]",
        "display": "Better health",
        "description": "Up health by 100 points",
        "symbol": "HP",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 100,
        "x": 0,
        "y": 0,
    },

    "bulletsSpeed": {
        "code": "bulletsSpeed",
        "dependencies": ["health"],
        "function": "self.bulletsSpeed *= (1 + self.game.data['upgrades']['bulletsSpeed'] / 10)",
        "display": "Bullets speed",
        "description": "Up bullets speed by 10% per level",
        "symbol": "SPD",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "x": -2,
        "y": 0,

        "type": "many",
        "limit": 5,
        "cost": [100, 200, 500, 1000, 2000],
    },

    "damage": {
        "code": "damage",
        "dependencies": ["health"],
        "function": "self.attackDamageMultiply *= 1.2",
        "display": "Attack damage",
        "description": "Up attack damage by 20%",
        "symbol": "ATK",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 200,
        "x": 2,
        "y": 0
    },

    "speed": {
        "code": "speed",
        "dependencies": ["damage"],
        "function": "self.speedMultiply *= 1.1",
        "display": "Player speed",
        "description": "Up player speed by 10%",
        "symbol": "SPD",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 500,
        "x": 2,
        "y": -2
    },

    "speedWithStamina": {
        "code": "speedWithStamina",
        "dependencies": ["speed", "stamina"],
        "function": "",
        "display": "Speed with stamina",
        "description": "Up player speed by 10% when stamina at 100%",
        "symbol": "SPD",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 1000,
        "x": 6,
        "y": -2
    },

    "revival": {
        "code": "revival",
        "dependencies": ["damage"],
        "function": "CHOOSES['revival']['open'] = True",
        "display": "Revival",
        "description": "Unlock upgrade that revives a character",
        "symbol": "UPG",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 500,
        "x": 4,
        "y": 0
    },

    "moreXP": {
        "code": "moreXP",
        "dependencies": ["damage"],
        "function": "self.experienceMultiply *= 1.2",
        "display": "More XP",
        "description": "Player get +20% XP",
        "symbol": "XP",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 1000,
        "x": 2,
        "y": 2
    },

    "stamina": {
        "code": "stamina",
        "dependencies": ["revival"],
        "function": "self.staminaIsOpened = True",
        "display": "Stamina",
        "description": "Unlock player's stamina Displayed on the player",
        "symbol": "SKL",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 1000,
        "x": 6,
        "y": 0
    },

    "dash": {
        "code": "dash",
        "dependencies": ["speedWithStamina"],
        "function": "self.dashIsOpened = True",
        "display": "Dash",
        "description": "Unlock dash for player (use on space)",
        "symbol": "SKL",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 2000,
        "x": 8,
        "y": -2
    },

    "weapons": {
        "code": "weapons",
        "dependencies": ["stamina"],
        "function": "self.weaponsTypesOpened = True; self.weaponsMaxCount += 1",
        "display": "Weapons",
        "description": "Unlock weapons types, you have 2 unique weapons",
        "symbol": "SKL",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 3000,
        "x": 10,
        "y": 0
    },

    "machineGun": {
        "code": "machineGun",
        "dependencies": ["weapons"],
        "function": "CHOOSES['unlockMachineGun']['open'] = True",
        "display": "Machine gun",
        "description": "Unlock weapon: machine gun",
        "symbol": "WP",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 5000,
        "x": 10,
        "y": -4
    },

    "machineGunMultiplySpeed": {
        "code": "machineGunMultiplySpeed",
        "dependencies": ["speedWithStamina", "machineGun"],
        "function": "",
        "display": "Attack speed multiply",
        "description": "Attack speed of machine gun multiplied by player speed",
        "symbol": "ATK",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 5000,
        "x": 6,
        "y": -4
    },

    "shotgun": {
        "code": "shotgun",
        "dependencies": ["weapons"],
        "function": "CHOOSES['unlockShotgun']['open'] = True",
        "display": "Shotgun",
        "description": "Unlock weapon: shotgun",
        "symbol": "WP",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 2000,
        "x": 10,
        "y": 4
    },

    "doubleShot": {
        "code": "doubleShot",
        "dependencies": ["machineGun"],
        "function": "CHOOSES['doubleShot']['open'] = True",
        "display": "Double shot",
        "description": "Unlock upgrade that reduces base attack speed by 30%",
        "symbol": "UPG",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 5000,
        "x": 12,
        "y": -4
    },

    "explosiveWeapon": {
        "code": "explosiveWeapon",
        "dependencies": ["pelletSpeed"],
        "function": "CHOOSES['explosiveWeapon']['open'] = True",
        "display": "Explosive weapon",
        "description": "Unlock upgrade that get explosive base weapon",
        "symbol": "UPG",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 10000,
        "x": 10,
        "y": 8
    },

    "pelletSpeed": {
        "code": "pelletSpeed",
        "dependencies": ["shotgun"],
        "function": "",
        "display": "Pellet speed",
        "description": "Increase shotgun pellet speed",
        "symbol": "UPG",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 8000,
        "x": 10,
        "y": 6
    },

    "moreWeaponSlots": {
        "code": "moreWeaponSlots",
        "dependencies": ["weapons"],
        "function": "",
        "display": "More weapon slots",
        "description": "Every 10 waves you get weapon slot",
        "symbol": "SKL",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 10000,
        "x": 12,
        "y": 0
    },

    "weaponsInFirstLevel": {
        "code": "weaponsInFirstLevel",
        "dependencies": ["moreWeaponSlots"],
        "function": "",
        "display": "Weapons in first level",
        "description": "After first level you get weapon in chooses",
        "symbol": "SKL",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 5000,
        "x": 12,
        "y": -2
    },

    "explosive": {
        "code": "explosive",
        "dependencies": ["moreWeaponSlots", "moreXP"],
        "function": "CHOOSES['unlockExplosive']['open'] = True",
        "display": "Explosive",
        "description": "Unlock weapon: explosive",
        "symbol": "WP",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 10000,
        "x": 12,
        "y": 2
    },

    "explosiveWeaponGetXP": {
        "code": "explosiveWeaponGetXP",
        "dependencies": ["explosive"],
        "function": "CHOOSES['unlockExplosive']['open'] = True",
        "display": "Explosive weapon get XP",
        "description": "If enemy destroyed by explosive you get more xp",
        "symbol": "XP",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 15000,
        "x": 14,
        "y": 2
    },

    "noDamageWhileDashing": {
        "code": "noDamageWhileDashing",
        "dependencies": ["dash"],
        "function": "CHOOSES['notTakeDamageWhileDashing']['open'] = True",
        "display": "No damage while dashing",
        "description": "Unlock upgrade for player not take damage while dashing",
        "symbol": "UPG",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 3000,
        "x": 8,
        "y": -6
    },

    "drones": {
        "code": "drones",
        "dependencies": ["moreWeaponSlots"],
        "function": "self.dronesActive = True",
        "display": "Drones",
        "description": "Drones can mine resources, attack and etc.",
        "symbol": "SKL",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 10000,
        "x": 14,
        "y": 0
    },

    "miningDrones": {
        "code": "miningDrones",
        "dependencies": ["drones"],
        "function": "self.dronesTypes['mining'] += self.game.data['upgrades']['miningDrones']",
        "display": "Mining drones",
        "description": "You have 1 more mining drone",
        "symbol": "SKL",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "x": 16,
        "y": 0,

        "type": "many",
        "limit": 5,
        "cost": [5000, 10000, 20000, 50000, 100000]
    },

    "resources": {
        "code": "resources",
        "dependencies": [],
        "function": "",
        "display": "Resources",
        "description": "Spawn resources in world, but you can't mine it",
        "symbol": "SKL",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 1000,
        "x": 14,
        "y": -2
    },

    "moreResources": {
        "code": "moreResources",
        "dependencies": ["resources"],
        "function": "",
        "display": "More resources",
        "description": "In game spawne more resources",
        "symbol": "SKL",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 10000,
        "x": 14,
        "y": -4
    },

    "resourceMultiply": {
        "code": "resourceMultiply",
        "dependencies": ["miningDrones"],
        "function": "self.dronesResourceMultiply *= 2",
        "display": "Resource multiply",
        "description": "+100% resource multiply from drones",
        "symbol": "SKL",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "cost": 10,
        "x": 18,
        "y": 0,

        "request": "crystal"
    },

    "miningDronesForWaves": {
        "code": "miningDronesForWaves",
        "dependencies": ["resourceMultiply"],
        "function": "self.dronesMiningGetForWave = True",
        "display": "Mining drones for waves",
        "description": "Every 5 waves you get 1 mining drone",
        "symbol": "SKL",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "cost": 25,
        "x": 18,
        "y": -4,

        "request": "crystal"
    },

    "dronesStats": {
        "code": "dronesStats",
        "dependencies": ["resourceMultiply"],
        "function": "",
        "display": "Drones stats",
        "description": "You get +1% health, xp multiply, points multiply for every player drone",
        "symbol": "SKL",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "cost": 50,
        "x": 20,
        "y": 0,

        "request": "crystal"
    },

    "armor": {
        "code": "armor",
        "dependencies": ["dronesStats"],
        "function": "self.armorIsOpened = True",
        "display": "Armor",
        "description": "Unlock armor for player, armor regenerate every wave",
        "symbol": "SKL",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "cost": 100,
        "x": 20,
        "y": 2,

        "request": "crystal"
    },

    "armorUpgrade": {
        "code": "armorUpgrade",
        "dependencies": ["armor"],
        "function": "CHOOSES['armor']['open'] = 1",
        "display": "Armor upgrade",
        "description": "Unlock an upgrade to improve your armor",
        "symbol": "UPG",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "cost": 200,
        "x": 22,
        "y": 2,

        "request": "crystal"
    },

    "laser": {
        "code": "laser",
        "dependencies": ["armor"],
        "function": "CHOOSES['unlockLaser']['open'] = True",
        "display": "Laser",
        "description": "Unlock weapon: laser",
        "symbol": "WP",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "cost": 250,
        "x": 20,
        "y": 4,

        "request": "crystal"
    },

    "laserAttackEveryTick": {
        "code": "laserAttackEveryTick",
        "dependencies": ["laser"],
        "function": "CHOOSES['laserAttackEveryFrame']['open'] = True",
        "display": "Laser arrack every tick",
        "description": "Unlock upgrade for laser that deal damage every frame",
        "symbol": "UPG",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "cost": 400,
        "x": 20,
        "y": 6,

        "request": "crystal"
    },

    "fastWeaponReload": {
        "code": "fastWeaponReload",
        "dependencies": ["shotgun", "explosive", "laser"],
        "function": "",
        "display": "Fast weapon reload",
        "description": "Weapons that take longer than 2 seconds to reload receive +20% reload speed",
        "symbol": "SKL",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "cost": 500,
        "x": 12,
        "y": 4,

        "request": "crystal"
    },

    "resourceMultiplyByMiningDrones": {
        "code": "resourceMultiplyByMiningDrones",
        "dependencies": ["resourceMultiply"],
        "function": "",
        "display": "Drones multiply resources",
        "description": "+35% resource multiply for every mining drone",
        "symbol": "SKL",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "cost": 50,
        "x": 18,
        "y": 2,

        "request": "crystal"
    },

    "attackDrones": {
        "code": "attackDrones",
        "dependencies": ["dronesStats"],
        "function": "self.dronesTypes['attack'] += self.game.data['upgrades']['attackDrones']",
        "display": "Attack drones",
        "description": "You have 1 more attack drone",
        "symbol": "SKL",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "x": 22,
        "y": 0,

        "type": "many",
        "limit": 2,
        "cost": [200, 1000],
        "request": "crystal"
    },

    "chanceDuplicateResource": {
        "code": "chanceDuplicateResource",
        "dependencies": ["dronesStats", "resources"],
        "function": "",
        "display": "Duplicate resource",
        "description": "You get +5% chance duplicate resource for every drone",
        "symbol": "SKL",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "cost": 100,
        "x": 20,
        "y": -2,

        "request": "crystal"
    },

    "classInfo": {
        "code": "classInfo",
        "dependencies": ["shotgun", "$", "dash"],
        "function": "",
        "display": "Class information",
        "description": "You can choose only one class. Choosing a class gives both positive and negative abilities",
        "symbol": "I",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 0,
        "x": 8,
        "y": 6
    },

    "warrior": {
        "code": "warrior",
        "dependencies": ["shotgun", "dash"],
        "function": "self.clazz = 'warrior'; self.attackSpeedMultiply *= 1.3",
        "display": "Warrior",
        "description": "Open class: warrior /n When you dashing in enemy you deals damage equals sum of all using weapons. Attack speed: -30%",
        "symbol": "C",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 5000,
        "x": 8,
        "y": 4
    },

    "staminaRegeneration": {
        "code": "staminaRegeneration",
        "dependencies": ["warrior"],
        "function": "self.staminaRegeneration *= 3",
        "display": "Stamina regeneration",
        "description": "+200% stamina regeneration",
        "symbol": "SKL",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 10000,
        "x": 6,
        "y": 4
    },

    "engineer": {
        "code": "engineer",
        "dependencies": ["attackDrones"],
        "function": "self.dronesAttackMultiply *= 1.3; self.attackDamageMultiply *= 0.2; self.dronesTypes['attack'] += 1; self.dronesTypes['mining'] += 3;",
        "display": "Engineer",
        "description": "Open class: engineer /n +30% Drones damage /n -80% Attack damage /n +3 Mining drones /n +1 Attack drone",
        "symbol": "C",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "cost": 300,
        "x": 24,
        "y": 0,

        "request": "crystal"
    },

    "dronesDependsDamage": {
        "code": "dronesDependsDamage",
        "dependencies": ["engineer"],
        "function": "",
        "display": "Drones depends damage",
        "description": "Drones damage depends sum of all using weapons",
        "symbol": "SKL",
        "color": Color.TREE_BLUE_COLOR,
        "have": False,
        "cost": 500,
        "x": 26,
        "y": 0,

        "request": "crystal"
    },

    "garden": {
        "code": "garden",
        "dependencies": ["machineGunMultiplySpeed"],
        "function": "",
        "display": "Garden",
        "description": "Open garden",
        "symbol": "SKL",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 1000,
        "x": 6,
        "y": -6
    },

    "gardenSlot0": {
        "code": "gardenSlot0",
        "dependencies": ["garden"],
        "function": "",
        "display": "",
        "description": "",
        "symbol": "",
        "color": Color.TREE_WHITE_COLOR,
        "have": False,
        "cost": 0,
        "size": 3,
        "x": 3,
        "y": -5,

        "type": "garden",

        "garden": {
            "slot": "0",
            "cost": 100
        }
    }
}
