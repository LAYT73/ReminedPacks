import random
from dsl import Build, register, gable


@register("farms", "crop-field-9x9", "Огород 9×9 с колодцем-водоёмом", "9x9 crop field",
          "Пшеница, морковь и картошка вокруг центрального источника воды. Забор с калиткой, компостер и пугало.",
          "Wheat, carrots and potatoes around a central water source. Fenced, with a gate, a composter and a scarecrow.",
          "easy", ["wheat", "carrot", "potato", "farm", "starter"])
def crop_field():
    b = Build("crop-field-9x9")
    rnd = random.Random(11)
    b.fill(0, 0, 0, 8, 0, 8, "grass_block")
    for x in range(1, 8):
        for z in range(1, 8):
            if (x, z) == (4, 4):
                b.set(x, 0, z, "water")
                continue
            if x == 4 and z >= 5:
                b.set(x, 0, z, "dirt_path")
                continue
            if (x, z) == (2, 2):
                b.set(x, 0, z, "dirt")
                continue
            b.set(x, 0, z, "farmland", moisture=7)
            age = 7 if (x + z) % 3 else rnd.randint(2, 6)
            if z <= 3:
                if x != 4:
                    b.set(x, 1, z, "wheat", age=age)
                else:
                    b.set(x, 1, z, "wheat", age=7)
            elif x < 4:
                b.set(x, 1, z, "potatoes", age=age)
            else:
                b.set(x, 1, z, "carrots", age=age)
    # fence ring with gate
    for x in range(0, 9):
        for z in range(0, 9):
            if x in (0, 8) or z in (0, 8):
                b.set(x, 1, z, "oak_fence")
    b.set(4, 1, 8, "oak_fence_gate", facing="north")
    b.set(0, 1, 4, "composter", level=5)
    for x, z in ((0, 0), (8, 0), (0, 8), (8, 8)):
        b.set(x, 2, z, "torch")
    # scarecrow
    b.set(2, 1, 2, "oak_fence")
    b.set(2, 2, 2, "hay_block", axis="y")
    b.set(1, 2, 2, "oak_fence"); b.set(3, 2, 2, "oak_fence")
    b.set(2, 3, 2, "carved_pumpkin", facing="south")
    return b


@register("farms", "sugar-cane-farm", "Ферма сахарного тростника", "Sugar cane farm",
          "Три водных канала и шесть грядок тростника по обе стороны. Растёт сам, нужно только собирать.",
          "Three water channels with six rows of sugar cane beside them. It grows by itself, you only harvest.",
          "easy", ["sugar-cane", "farm", "water"])
def cane_farm():
    b = Build("sugar-cane-farm")
    rnd = random.Random(5)
    b.fill(0, 0, 0, 10, 0, 8, "stone_bricks")
    for x in range(1, 10):
        for z in range(1, 8):
            if x in (2, 5, 8):
                b.set(x, 0, z, "water")
            else:
                soil = "sand" if x in (1, 4, 7) else "dirt"
                b.set(x, 0, z, soil)
                h = rnd.randint(1, 3)
                for i in range(h):
                    b.set(x, 1 + i, z, "sugar_cane", age=rnd.randint(0, 15) if i == h - 1 else 0)
    for x, z in ((0, 0), (10, 0), (0, 8), (10, 8)):
        b.set(x, 1, z, "oak_fence"); b.set(x, 2, z, "lantern")
    return b


@register("farms", "pumpkin-melon-farm", "Ферма тыкв и арбузов", "Pumpkin & melon farm",
          "Тыквы слева, арбузы справа, посередине канал с водой. Стебли уже повёрнуты к плодам.",
          "Pumpkins on one side, melons on the other, a water channel between. Stems already turn towards their fruit.",
          "medium", ["pumpkin", "melon", "farm"])
def gourd_farm():
    b = Build("pumpkin-melon-farm")
    b.fill(0, 0, 0, 10, 0, 8, "grass_block")
    for z in range(1, 8):
        b.set(5, 0, z, "water")
    for z in (1, 3, 5, 7):
        # pumpkin side (west)
        b.set(1, 1, z, "pumpkin")
        b.set(2, 0, z, "farmland", moisture=7); b.set(2, 1, z, "attached_pumpkin_stem", facing="west")
        b.set(3, 0, z, "farmland", moisture=7); b.set(3, 1, z, "pumpkin_stem", age=(z + 1) // 2 + 2)
        # melon side (east)
        b.set(9, 1, z, "melon")
        b.set(8, 0, z, "farmland", moisture=7); b.set(8, 1, z, "attached_melon_stem", facing="east")
        b.set(7, 0, z, "farmland", moisture=7); b.set(7, 1, z, "melon_stem", age=(z + 1) // 2 + 1)
    for z in (2, 6):
        for x, stem in ((2, "pumpkin_stem"), (3, "pumpkin_stem"), (7, "melon_stem"), (8, "melon_stem")):
            b.set(x, 0, z, "farmland", moisture=7); b.set(x, 1, z, stem, age=(x + z) % 3)
    # little plank bridge over the channel
    b.slab(5, 1, 4, "oak")
    for x in range(0, 11):
        for z in range(0, 9):
            if x in (0, 10) or z in (0, 8):
                b.set(x, 1, z, "oak_fence")
    b.set(5, 1, 8, "oak_fence_gate", facing="north")
    for x, z in ((0, 0), (10, 0), (0, 8), (10, 8)):
        b.set(x, 2, z, "lantern")
    return b


@register("farms", "animal-pen", "Загон для животных", "Animal pen",
          "Забор с калиткой, навес на двух столбах, сено, поилки из котлов и кормушка-компостер.",
          "Fenced pen with a gate, a lean-to shelter, hay bales, cauldron troughs and a composter feeder.",
          "medium", ["animals", "pen", "fence", "hay"])
def animal_pen():
    b = Build("animal-pen")
    rnd = random.Random(3)
    b.fill(0, 0, 0, 10, 0, 8, "grass_block")
    for x in range(1, 10):
        for z in range(1, 8):
            r = rnd.random()
            if r < 0.12:
                b.set(x, 0, z, "coarse_dirt")
            elif r < 0.45 and (x, z) not in ((1, 1),):
                b.set(x, 1, z, "short_grass")
    for x in range(0, 11):
        for z in range(0, 9):
            if x in (0, 10) or z in (0, 8):
                b.set(x, 1, z, "oak_fence")
    b.set(5, 1, 8, "oak_fence_gate", facing="north")
    for x, z in ((0, 0), (10, 0), (0, 8), (10, 8)):
        b.set(x, 2, z, "lantern")
    # path from the gate
    for z in (7, 6, 5, 4):
        b.set(5, 0, z, "dirt_path"); b.set(5, 1, z, "air")
    b.set(4, 0, 4, "dirt_path"); b.set(4, 1, 4, "air"); b.set(3, 0, 4, "dirt_path"); b.set(3, 1, 4, "air")
    b.set(5, 0, 8, "dirt_path")
    # shelter x6..9, z1..3
    b.fill(6, 0, 1, 9, 0, 3, "oak_planks")
    for x, z in ((6, 1), (9, 1), (6, 3), (9, 3)):
        b.vlog(x, 1, 2, z, "oak")
    for x in (7, 8):
        for y in (1, 2):
            b.set(x, y, 1, "oak_planks")
    for y in (1, 2):
        b.set(9, y, 2, "oak_planks")
    for x in (7, 8):
        b.set(x, 1, 2, "air")
    gable(b, 6, 9, 1, 3, 3, "oak", axis="x", ov=1, ovx=1, fill=("oak_planks", {}))
    for x in (7, 8):
        b.set(x, 1, 1, "hay_block", axis="x")
        b.set(x, 1, 2, "hay_block", axis="y") if x == 8 else None
    b.set(8, 2, 2, "hay_block", axis="z")
    b.set(7, 2, 2, "lantern", hanging=True)
    # troughs and feeder
    b.set(2, 1, 5, "water_cauldron", level=3); b.set(3, 1, 5, "water_cauldron", level=3)
    b.set(1, 1, 7, "composter", level=8)
    for z in (1, 2):
        b.set(1, 1, z, "hay_block", axis="y")
    b.set(2, 1, 1, "hay_block", axis="x")
    b.set(1, 2, 1, "hay_block", axis="y")
    b.set(9, 1, 6, "hay_block", axis="z"); b.set(9, 1, 7, "hay_block", axis="z")
    return b


@register("farms", "tree-nursery", "Питомник деревьев", "Tree nursery",
          "Четыре грядки с саженцами: дуб, ель (2×2 на подзоле), тёмный дуб и джунгли. Есть компостер и бочка.",
          "Four beds of saplings: oak, 2x2 spruce on podzol, dark oak and jungle. A composter and a barrel included.",
          "easy", ["trees", "saplings", "podzol", "nursery"])
def nursery():
    b = Build("tree-nursery")
    b.fill(0, 0, 0, 8, 0, 8, "oak_planks")
    # beds
    def bed(x0, z0, soil):
        b.fill(x0, 0, z0, x0 + 2, 0, z0 + 2, soil)
    bed(1, 1, "dirt"); bed(5, 1, "podzol"); bed(1, 5, "podzol"); bed(5, 5, "grass_block")
    for i in range(1, 8):
        b.set(4, 0, i, "dirt_path"); b.set(i, 0, 4, "dirt_path")
    b.set(4, 0, 4, "stone_bricks")
    # oak bed
    for x, z in ((1, 1), (3, 1), (1, 3), (3, 3), (2, 2)):
        b.set(x, 1, z, "oak_sapling" if (x, z) != (2, 2) else "short_grass")
    # spruce 2x2
    for x, z in ((5, 1), (6, 1), (5, 2), (6, 2)):
        b.set(x, 1, z, "spruce_sapling")
    b.set(7, 1, 3, "fern"); b.set(7, 1, 1, "fern")
    # dark oak 2x2 + birch
    for x, z in ((1, 5), (2, 5), (1, 6), (2, 6)):
        b.set(x, 1, z, "dark_oak_sapling")
    b.set(3, 1, 7, "birch_sapling")
    # jungle 2x2 + cherry
    for x, z in ((6, 6), (7, 6), (6, 7), (7, 7)):
        b.set(x, 1, z, "jungle_sapling")
    b.set(5, 1, 5, "cherry_sapling")
    b.set(4, 1, 4, "composter", level=3)
    b.set(4, 1, 0, "barrel", facing="up")
    for x, z in ((0, 0), (8, 0), (0, 8), (8, 8)):
        b.set(x, 1, z, "oak_fence"); b.set(x, 2, z, "lantern")
    return b

