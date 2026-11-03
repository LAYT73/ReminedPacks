import random
from dsl import Build, register, hip


@register("mini", "village-well", "Колодец с крышей", "Well with roof",
          "Каменный колодец с водой, четырьмя столбами и еловой крышей. Внутри висит фонарь.",
          "A stone well with water, four posts and a spruce roof. A lantern hangs inside.",
          "easy", ["well", "water", "village"])
def well():
    b = Build("village-well")
    b.fill(0, 0, 0, 4, 0, 4, "cobblestone")
    b.fill(1, 0, 1, 3, 0, 3, "stone_bricks")
    b.shell(1, 1, 1, 3, 1, 3, "stone_bricks")
    b.set(2, 1, 2, "water")
    for x, z in ((1, 1), (3, 1), (1, 3), (3, 3)):
        b.set(x, 2, z, "oak_fence"); b.set(x, 3, z, "oak_fence")
    hip(b, 0, 4, 0, 4, 4, "spruce")
    b.set(2, 5, 2, "iron_chain", axis="y"); b.set(2, 4, 2, "iron_chain", axis="y")
    b.set(2, 3, 2, "lantern", hanging=True)
    return b


@register("mini", "market-stall", "Рыночный прилавок", "Market stall",
          "Прилавок с полосатым тентом из шерсти, бочками, тыквами и арбузами. Для деревни или спавна.",
          "A counter with a striped wool awning, barrels, pumpkins and melons. Good for a village or spawn.",
          "easy", ["market", "wool", "barrel", "village"])
def stall():
    b = Build("market-stall")
    b.fill(0, 0, 0, 6, 0, 5, "spruce_planks")
    for x, z in ((1, 1), (5, 1), (1, 4), (5, 4)):
        for y in (1, 2, 3):
            b.set(x, y, z, "spruce_fence")
    for x in range(0, 7):
        col = "red_wool" if x % 2 == 0 else "white_wool"
        for z in range(0, 6):
            b.set(x, 4, z, col)
        if x % 2 == 0:
            b.set(x, 3, 5, col)
    # back shelf and counter
    for x in range(1, 6):
        b.set(x, 1, 1, "spruce_planks")
    b.set(2, 1, 1, "barrel", facing="south"); b.set(3, 1, 1, "chest", facing="south")
    b.set(4, 1, 1, "barrel", facing="south")
    for x in range(1, 6):
        b.set(x, 1, 4, "spruce_planks")
    b.set(2, 2, 4, "pumpkin"); b.set(3, 2, 4, "melon"); b.set(4, 2, 4, "hay_block", axis="x")
    b.set(1, 2, 4, "potted_poppy"); b.set(5, 2, 4, "potted_dandelion")
    b.set(0, 1, 4, "barrel", facing="up"); b.set(0, 1, 3, "barrel", facing="north")
    b.set(0, 2, 4, "barrel", facing="up")
    b.set(6, 1, 4, "barrel", facing="up"); b.set(6, 1, 3, "barrel", facing="east")
    b.set(3, 3, 3, "lantern", hanging=True)
    return b


@register("mini", "street-lamp", "Уличный фонарь", "Street lamp post",
          "Высокий фонарь на каменной колонне с двумя боковыми фонарями. Одинаково хорош для дорог и садов.",
          "A tall lamp on a stone column with two side lanterns. Fine for roads and gardens alike.",
          "easy", ["lamp", "lantern", "street"])
def lamp():
    b = Build("street-lamp")
    b.fill(0, 0, 0, 2, 0, 2, "stone_bricks")
    b.set(1, 1, 1, "stone_bricks")
    for y in range(2, 5):
        b.set(1, y, 1, "stone_brick_wall")
    # Full block at arm height: fences connect to it (they don't connect to walls).
    b.set(1, 5, 1, "chiseled_stone_bricks")
    b.set(0, 5, 1, "dark_oak_fence"); b.set(2, 5, 1, "dark_oak_fence")
    b.set(0, 4, 1, "lantern", hanging=True); b.set(2, 4, 1, "lantern", hanging=True)
    b.set(1, 6, 1, "lantern")
    return b


@register("mini", "park-bench", "Скамейка с клумбами", "Park bench with planters",
          "Скамейка у живой изгороди и две клумбы с цветами по бокам. Тротуар из каменных кирпичей.",
          "A bench against a hedge with a flower planter on each side, on a stone brick pavement.",
          "easy", ["bench", "planter", "park"])
def bench():
    b = Build("park-bench")
    b.fill(0, 0, 0, 10, 0, 2, "stone_bricks")
    def planter(x0, flower, plant_name):
        for x in range(x0, x0 + 3):
            for z in range(0, 3):
                b.set(x, 1, z, "spruce_planks")
        b.set(x0 + 1, 1, 1, "moss_block")
        b.tall(x0 + 1, 2, 1, flower)
    planter(0, "lilac", None)
    planter(8, "rose_bush", None)
    for x in (4, 5, 6):
        b.set(x, 1, 0, "oak_leaves"); b.set(x, 2, 0, "oak_leaves")
        b.slab(x, 1, 1, "spruce")
        b.trapdoor(x, 2, 1, "spruce", "south", open=True)
    b.set(3, 1, 1, "spruce_fence"); b.set(7, 1, 1, "spruce_fence")
    b.set(3, 2, 1, "spruce_pressure_plate"); b.set(7, 2, 1, "spruce_pressure_plate")
    return b


@register("mini", "stone-bridge", "Каменный мостик", "Small stone bridge",
          "Горбатый мостик из каменных кирпичей над маленьким прудом. С перилами и фонарями на концах.",
          "A humpback stone brick bridge over a small pond, with railings and lanterns at the ends.",
          "medium", ["bridge", "stone", "water"])
def bridge():
    b = Build("stone-bridge")
    b.fill(0, 0, 0, 8, 0, 4, "grass_block")
    for x in range(2, 7):
        for z in range(0, 5):
            b.set(x, 0, z, "stone_bricks")
    for x in (3, 4, 5):
        for z in (1, 2, 3):
            b.set(x, 0, z, "water")
    for z in (1, 2, 3):
        b.stairs(1, 1, z, "stone_brick", "east"); b.stairs(7, 1, z, "stone_brick", "west")
        b.set(2, 1, z, "stone_bricks"); b.set(6, 1, z, "stone_bricks")
        b.stairs(3, 2, z, "stone_brick", "east"); b.set(4, 2, z, "stone_bricks"); b.stairs(5, 2, z, "stone_brick", "west")
        b.stairs(3, 1, z, "stone_brick", "west", "top"); b.stairs(5, 1, z, "stone_brick", "east", "top")
    for z in (1, 3):
        b.set(2, 2, z, "stone_brick_wall"); b.set(6, 2, z, "stone_brick_wall")
        b.set(2, 3, z, "lantern"); b.set(6, 3, z, "lantern")
        for x in (3, 4, 5):
            b.set(x, 3, z, "stone_brick_wall")
    return b


@register("mini", "campfire-rest", "Привал у костра", "Campfire rest spot",
          "Костёр в кольце камней, брёвна вместо лавок, фонарь на столбе и бочка с припасами.",
          "A campfire in a ring of stones, log seats, a lantern on a post and a barrel of supplies.",
          "easy", ["campfire", "camp", "lantern", "logs"])
def camp():
    b = Build("campfire-rest")
    rnd = random.Random(21)
    b.fill(0, 0, 0, 6, 0, 6, "grass_block")
    for x in range(2, 5):
        for z in range(2, 5):
            b.set(x, 0, z, "coarse_dirt")
    for x, z in ((1, 1), (5, 1), (1, 5), (5, 5), (0, 3), (6, 3)):
        b.set(x, 0, z, "coarse_dirt")
    b.set(3, 1, 3, "campfire", facing="south", lit=True)
    for p in ((3, 2), (2, 2), (4, 2), (2, 4), (4, 4)):
        b.slab(p[0], 1, p[1], "cobblestone")
    for z in (2, 3, 4):
        b.log(1, 1, z, "oak", "z")
    for z in (2, 3, 4):
        b.log(5, 1, z, "spruce", "z") if z != 3 else b.log(5, 1, z, "oak", "z")
    for x in (2, 3, 4):
        b.log(x, 1, 5, "birch", "x")
    for x, z in ((0, 0), (6, 0), (0, 6), (6, 6), (3, 0), (0, 2), (6, 5)):
        r = rnd.random()
        b.set(x, 1, z, "short_grass" if r < 0.5 else ("fern" if r < 0.75 else "dandelion"))
    # lantern post with arm
    for y in (1, 2, 3):
        b.set(6, y, 1, "spruce_fence")
    b.set(5, 3, 1, "spruce_fence"); b.set(5, 2, 1, "lantern", hanging=True)
    b.set(6, 4, 1, "lantern")
    # supplies
    b.set(6, 1, 4, "barrel", facing="west"); b.set(6, 2, 4, "barrel", facing="up")
    return b

