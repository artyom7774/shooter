import pygame
import random
import math

NOISE_PARAMS = {
    "width": 1024,
    "height": 1024,
    "scale": 60,
    "octaves": 6,
    "persistence": 0.5,
    "lacunarity": 2,
    "bright": 0.2
}


def background():
    import noise

    array = []

    for y in range(NOISE_PARAMS["height"]):
        row = []

        for x in range(NOISE_PARAMS["width"]):
            value = noise.pnoise2(
                x / NOISE_PARAMS["scale"],
                y / NOISE_PARAMS["scale"],
                octaves=NOISE_PARAMS["octaves"],
                persistence=NOISE_PARAMS["persistence"],
                lacunarity=NOISE_PARAMS["lacunarity"],
                repeatx=NOISE_PARAMS["width"],
                repeaty=NOISE_PARAMS["height"],
                base=1
            )

            color = int(min(180, max(0, int((value + 1) * 127.5))) * NOISE_PARAMS["bright"])

            row.append(color)

        array.append(row)

    pixel = pygame.Surface((NOISE_PARAMS["width"], NOISE_PARAMS["height"]))

    for y in range(NOISE_PARAMS["height"]):
        for x in range(NOISE_PARAMS["width"]):
            color = array[y][x]

            pixel.set_at((x, y), (color * 0.4, color * 0.1, color * 0.8))

    temp = pygame.transform.scale(pixel, (NOISE_PARAMS["width"] * 5, NOISE_PARAMS["height"] * 5))

    surface = pygame.surface.Surface((NOISE_PARAMS["width"] * 5, NOISE_PARAMS["height"] * 5), pygame.SRCALPHA)

    surface.blit(temp, (0, 0))

    points = []

    for _ in range(1000):
        while True:
            x = random.randint(0, NOISE_PARAMS["width"] * 5)
            y = random.randint(0, NOISE_PARAMS["height"] * 5)

            for point in points:
                if math.sqrt((point[0] - x) ** 2 + (point[1] - y) ** 2) <= 10:
                    break

            else:
                break

        points.append([x, y])

    for _ in range(200):
        point = random.choice(points)

        for _ in range(random.randint(1, 4)):
            x = 1e9
            y = 1e9

            for _ in range(1000):
                if math.sqrt((point[0] - x) ** 2 + (point[1] - y) ** 2) < 200:
                    break

                x, y = random.choice(points)

            else:
                continue

            pygame.draw.line(surface, (255, 255, 255, 60), (x, y), point)

    for point in points:
        x, y = point

        surface.set_at((x, y), (255, 255, 255))

        if random.randint(1, 2) == 1:
            surface.set_at((x + 1, y), (255, 255, 255))
            surface.set_at((x, y + 1), (255, 255, 255))
            surface.set_at((x - 1, y), (255, 255, 255))
            surface.set_at((x, y - 1), (255, 255, 255))

    # pygame.image.save(surface.subsurface([0, 0, 3840 // 2, 2160 // 2]), "bg.png")

    return surface
