from src.bosses import *
from src.enemies import *

PROTOCOL_VERSION = 1

DEFAULT_PORT = 3000

TICK_RATE = 60
SEND_RATE = 60

MAX_PLAYERS = 8
PLAYER_TIMEOUT = 10
PLAYER_NAME_LENGTH = 16

VIEW_RADIUS_ENEMIES = 3500
VIEW_RADIUS_BULLETS = 2000

MAX_HIT_DAMAGE = 5000
MAX_HIT_RANGE = 1500
MAX_EVENTS_PER_REQUEST = 400
MAX_PENDING_EVENTS = 300

ENEMY_TYPES = [
    EnemyShootingRed,
    EnemyAttackingRed,
    EnemyShootingAroundRed,
    EnemyShootingTripleRed,
    EnemyAttackingTripleRed,
    EnemyDividedFirstRed,
    EnemyDividedSecondRed,
    EnemyDividedThirdRed,
    EnemyShootingPotionRed,
    EnemyShootingBlue,
    EnemyAttackingBlue,
    BossShooting,
    BossShootingTwo,
]

ENEMY_INDEX = {cls: index for index, cls in enumerate(ENEMY_TYPES)}

PLAYER_COLORS = [
    (245, 245, 245), (110, 200, 255), (255, 200, 90), (120, 255, 140), (240, 110, 210), (255, 130, 90), (170, 140, 255), (90, 230, 210)
] * 10


def packColor(color):
    color = tuple(color)

    if len(color) == 3:
        color = (*color, 255)

    return (color[0] << 24) | (color[1] << 16) | (color[2] << 8) | color[3]


def unpackColor(value):
    r, g, b, a = (value >> 24) & 255, (value >> 16) & 255, (value >> 8) & 255, value & 255

    return (r, g, b) if a == 255 else (r, g, b, a)
