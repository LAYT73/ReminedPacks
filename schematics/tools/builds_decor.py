import math
import random
from dsl import Build, register


def blob(b, cx, cy, cz, rx, ry, rz, leaf, rnd, skip=0.12):
    """Rough ellipsoid of leaves; edge cells are randomly dropped for a natural look."""
    for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for z in range(int(cz - rz) - 1, int(cz + rz) + 2):
                d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2
                if d <= 1.0 and (d < 0.7 or rnd.random() > skip) and b.get(x, y, z) is None:
                    b.set(x, y, z, leaf)


def branch(b, mat, start, direction, length, rise_every=2):
    """Log branch from `start` heading horizontally along direction=(dx,dz), rising every n steps."""
    x, y, z = start
    dx, dz = direction
    axis = "x" if dx else "z"
    tip = start
    for i in range(1, length + 1):
        x += dx; z += dz
        if i % rise_every == 0:
            y += 1
            b.log(x, y, z, mat, "y")
        else:
            b.log(x, y, z, mat, axis)
        tip = (x, y, z)
    return tip


def ground(b, cx, cz, r, rnd, flowers=("dandelion", "poppy", "azure_bluet", "oxeye_daisy"), density=0.22):
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            d = math.hypot(x - cx, z - cz)
            if d <= r + 0.3 and (d < r - 1 or rnd.random() < 0.6):
                b.set(x, 0, z, "grass_block")
    for x in range(cx - r, cx + r + 1):
        for z in range(cz - r, cz + r + 1):
            if b.name_at((x, 0, z)) == "grass_block" and b.get(x, 1, z) is None and (x, z) != (cx, cz):
                q = rnd.random()
                if q < density * 0.55:
                    b.set(x, 1, z, "short_grass")
                elif q < density * 0.75:
                    b.set(x, 1, z, rnd.choice(flowers))
                elif q < density * 0.85:
                    b.tall(x, 1, z, "tall_grass")


@register("decor", "big-oak-tree", "Большой дуб", "Large oak tree",
          "Раскидистый дуб с толстыми ветвями и пышной кроной. Листва не опадает.",
          "A spreading oak with thick branches and a full canopy. The leaves are persistent and never decay.",
          "medium", ["oak", "tree", "nature"])
def oak():
    b = Build("big-oak-tree")
    rnd = random.Random(2)
    C = 8
    ground(b, C, C, 6, rnd)
    b.set(C, 0, C, "dirt")
    b.vlog(C, 1, 11, C, "oak")
    for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if rnd.random() < 0.8:
            b.log(C + dx, 1, C + dz, "oak", "x" if dx else "z")
            b.set(C + dx, 0, C + dz, "dirt")
    tips = [branch(b, "oak", (C, 7, C), (1, 0), 4), branch(b, "oak", (C, 8, C), (-1, 0), 4),
            branch(b, "oak", (C, 9, C), (0, 1), 3), branch(b, "oak", (C, 8, C), (0, -1), 3, 3)]
    L = "oak_leaves"
    blob(b, C, 14, C, 5, 3.2, 5, L, rnd)
    for (tx, ty, tz) in tips:
        blob(b, tx, ty + 1, tz, 3.3, 2.6, 3.3, L, rnd)
    blob(b, C, 10, C, 3.5, 2, 3.5, L, rnd, 0.3)
    return b


@register("decor", "cherry-blossom-tree", "Вишнёвое дерево", "Cherry tree",
          "Розовое дерево с изогнутым стволом и широкой плоской кроной. Под ним лепестки на траве.",
          "A pink tree with a twisting trunk and a wide, flat canopy, with petals scattered on the grass below.",
          "medium", ["cherry", "tree", "nature", "pink"])
def cherry():
    b = Build("cherry-blossom-tree")
    rnd = random.Random(9)
    C = 8
    ground(b, C, C, 6, rnd, flowers=("azure_bluet", "oxeye_daisy", "cornflower"), density=0.1)
    b.set(C, 0, C, "dirt")
    b.vlog(C, 1, 5, C, "cherry")
    t1 = branch(b, "cherry", (C, 5, C), (1, 0), 4)
    t2 = branch(b, "cherry", (C, 5, C), (-1, 0), 3, 1)
    b.vlog(C, 6, 8, C, "cherry")
    t3 = branch(b, "cherry", (C, 7, C), (0, -1), 3)
    t4 = (C, 8, C)
    L = "cherry_leaves"
    for (tx, ty, tz) in (t1, t2, t3, t4):
        blob(b, tx, ty + 1, tz, 4.6, 2.2, 4.6, L, rnd, 0.15)
    blob(b, C, 10, C, 4, 1.8, 4, L, rnd, 0.2)
    # fallen petals on the grass
    for x in range(C - 6, C + 7):
        for z in range(C - 6, C + 7):
            if b.name_at((x, 0, z)) == "grass_block" and b.get(x, 1, z) is None and math.hypot(x - C, z - C) < 6 and rnd.random() < 0.35:
                b.set(x, 1, z, "pink_petals", facing=rnd.choice(["north", "south", "east", "west"]),
                      flower_amount=rnd.randint(1, 4))
    return b


@register("decor", "stone-brick-fountain", "Фонтан из каменных кирпичей", "Stone brick fountain",
          "Восьмиугольный бассейн с водой и центральной чашей. Сверху фонарь, по углам тоже.",
          "An octagonal pool with a central bowl on a pillar. A lantern on top and more at the corners.",
          "medium", ["fountain", "water", "stone-bricks"])
def fountain():
    b = Build("stone-brick-fountain")
    C = 4
    b.fill(0, 0, 0, 8, 0, 8, "stone_bricks")
    for x in range(9):
        for z in range(9):
            dx, dz = abs(x - C), abs(z - C)
            inner = max(dx, dz) <= 3 and dx + dz <= 5
            wall = (not inner) and max(dx, dz) <= 4 and dx + dz <= 7
            if inner:
                b.set(x, 1, z, "water")
            elif wall:
                b.set(x, 1, z, "stone_bricks")
                b.slab(x, 2, z, "stone_brick")
            elif (dx, dz) == (4, 4):
                b.set(x, 0, z, "cobblestone")
    for x, z in ((0, 0), (8, 0), (0, 8), (8, 8)):
        b.set(x, 1, z, "stone_brick_wall"); b.set(x, 2, z, "stone_brick_wall"); b.set(x, 3, z, "lantern")
    # pillar, bowl plate and bowl
    for y in (1, 2):
        b.set(C, y, C, "stone_bricks")
    b.set(C, 3, C, "chiseled_stone_bricks")
    for x in range(C - 2, C + 3):
        for z in range(C - 2, C + 3):
            if (x, z) != (C, C):
                b.set(x, 3, z, "stone_bricks")
            if max(abs(x - C), abs(z - C)) == 2:
                b.set(x, 4, z, "stone_bricks")
            elif (x, z) != (C, C):
                b.set(x, 4, z, "water")
    for y in (4, 5, 6):
        b.set(C, y, C, "stone_brick_wall")
    b.set(C, 7, C, "lantern")
    return b
