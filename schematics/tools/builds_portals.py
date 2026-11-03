import random
from dsl import Build, register


def frame(b, x0, y0, z, corners=True, mat="obsidian"):
    """4 wide x 5 tall obsidian frame in the plane z (portal axis x); interior 2x3 stays air.
    Corners are not needed by the game, so callers may override them afterwards."""
    for x in range(x0, x0 + 4):
        for y in range(y0, y0 + 5):
            edge_x = x in (x0, x0 + 3)
            edge_y = y in (y0, y0 + 4)
            if not (edge_x or edge_y):
                b.set(x, y, z, "air")
                continue
            if edge_x and edge_y and not corners:
                continue
            b.set(x, y, z, mat)


@register("portals", "ruined-portal", "Разрушенный портал", "Ruined portal",
          "Старая рама портала на холме из незерака: плачущий обсидиан, золото и вьюны. Рамка рабочая, остаётся зажечь.",
          "An old portal frame on a netherrack mound with crying obsidian, gold and vines. The frame is complete, just light it.",
          "medium", ["nether", "ruined", "obsidian"])
def ruined():
    b = Build("ruined-portal")
    rnd = random.Random(8)
    for x in range(0, 11):
        for z in range(0, 8):
            r = rnd.random()
            b.set(x, 0, z, "netherrack" if r < 0.72 else ("blackstone" if r < 0.88 else "magma_block"))
    frame(b, 3, 1, 3)
    b.set(3, 1, 3, "netherrack"); b.set(6, 1, 3, "crying_obsidian")
    b.set(3, 5, 3, "crying_obsidian"); b.set(6, 5, 3, "gold_block")
    # mound behind and around the frame
    for x in range(1, 10):
        for z in range(0, 8):
            if z == 3 and 3 <= x <= 6:
                continue
            d = abs(x - 4.5) / 4.5 + abs(z - 3) / 4
            if z <= 2 and d < 1.1 and rnd.random() < 0.8:
                b.set(x, 1, z, "netherrack")
                if d < 0.7 and rnd.random() < 0.6:
                    b.set(x, 2, z, "netherrack")
    # broken pillar and fallen blocks
    b.set(1, 1, 4, "crying_obsidian"); b.set(1, 2, 4, "crying_obsidian")
    b.set(9, 1, 5, "crying_obsidian"); b.set(8, 1, 4, "nether_bricks"); b.set(9, 1, 3, "cracked_nether_bricks")
    b.set(2, 1, 6, "gold_block"); b.set(7, 1, 1, "gold_block")
    # vines on the frame
    for x in (4, 5):
        b.set(x, 5, 4, "vine", north=True)
        for y in (4, 3):
            b.set(x, y, 4, "vine", north=True)
    b.set(5, 2, 4, "air")
    for y in (4, 3, 2):
        b.set(2, y, 3, "vine", east=True)
    b.set(7, 4, 3, "vine", west=True); b.set(7, 3, 3, "vine", west=True)
    return b


@register("portals", "blackstone-temple-portal", "Портал-храм из чернокамня", "Blackstone temple portal",
          "Рамка между колоннами из полированного чернокамня и позолоченного чернокамня, с фонарями душ и балкой сверху.",
          "A frame between polished and gilded blackstone pillars, with soul lanterns and a lintel beam above.",
          "hard", ["nether", "blackstone", "temple", "soul-lantern"])
def temple():
    b = Build("blackstone-temple-portal")
    PB = "polished_blackstone_bricks"
    b.fill(0, 0, 0, 11, 0, 8, PB)
    b.fill(1, 0, 1, 10, 0, 7, "blackstone")
    for x in range(0, 12):
        b.set(x, 0, 0, "polished_blackstone")
    # steps to the south
    for x in range(3, 9):
        b.stairs(x, 0, 8, "polished_blackstone_brick", "north")
    frame(b, 4, 1, 3)
    # pillars at x=1 and x=10
    for x in (1, 10):
        for y in range(1, 7):
            b.set(x, y, 3, PB)
        b.set(x, 1, 3, "chiseled_polished_blackstone"); b.set(x, 3, 3, "gilded_blackstone"); b.set(x, 5, 3, "gilded_blackstone")
        b.set(x, 6, 3, "chiseled_polished_blackstone")
    # low side walls
    for x in (2, 3, 8, 9):
        b.set(x, 1, 3, "polished_blackstone_brick_wall"); b.set(x, 2, 3, "polished_blackstone_brick_wall")
    for x in (2, 3, 8, 9):
        b.set(x, 3, 3, "polished_blackstone_brick_wall")
    # lintel beam
    for x in range(1, 11):
        b.set(x, 7, 3, "polished_blackstone_bricks")
    b.stairs(0, 7, 3, "polished_blackstone_brick", "east"); b.stairs(11, 7, 3, "polished_blackstone_brick", "west")
    for x in (3, 8):
        b.set(x, 6, 3, "soul_lantern", hanging=True)
    for x in (4, 7):
        b.set(x, 8, 3, "soul_lantern")
    for x in (1, 10):
        b.set(x, 8, 3, "soul_lantern")
    # soul lanterns on the steps' posts
    for x in (2, 9):
        b.set(x, 1, 6, "polished_blackstone_brick_wall"); b.set(x, 2, 6, "soul_lantern")
    return b


@register("portals", "amethyst-crystal-portal", "Хрустальный портал", "Amethyst crystal portal",
          "Обсидиановая рамка среди аметистовых кристаллов. Основание из кальцита и гладкого базальта.",
          "An obsidian frame among amethyst crystals, on a base of calcite and smooth basalt.",
          "medium", ["amethyst", "crystal", "geode"])
def crystal():
    b = Build("amethyst-crystal-portal")
    rnd = random.Random(14)
    for x in range(0, 11):
        for z in range(0, 8):
            b.set(x, 0, z, "smooth_basalt" if (x in (0, 10) or z in (0, 7)) else "calcite")
    frame(b, 3, 1, 3)
    # crown on top of the frame
    for x in range(3, 7):
        b.set(x, 6, 3, "amethyst_block")
    b.set(4, 7, 3, "budding_amethyst"); b.set(5, 7, 3, "amethyst_block")
    b.set(4, 8, 3, "amethyst_cluster", facing="up"); b.set(5, 8, 3, "large_amethyst_bud", facing="up")
    b.set(3, 7, 3, "medium_amethyst_bud", facing="up"); b.set(6, 7, 3, "small_amethyst_bud", facing="up")

    def crystal_pillar(cx, cz, h, bud=True):
        for y in range(1, h + 1):
            b.set(cx, y, cz, "budding_amethyst" if (y % 2 == 0 and bud) else "amethyst_block")
        b.set(cx, h + 1, cz, "amethyst_cluster", facing="up")
        for dx, dz, f in ((1, 0, "east"), (-1, 0, "west"), (0, 1, "south"), (0, -1, "north")):
            if rnd.random() < 0.8:
                y = rnd.randint(1, h)
                kind = rnd.choice(["small_amethyst_bud", "medium_amethyst_bud", "large_amethyst_bud", "amethyst_cluster"])
                if b.get(cx + dx, y, cz + dz) is None:
                    b.set(cx + dx, y, cz + dz, kind, facing=f)

    for cx, cz, h in ((1, 2, 4), (1, 5, 3), (2, 3, 6), (8, 5, 5), (9, 2, 4), (9, 4, 3), (8, 2, 2)):
        crystal_pillar(cx, cz, h)
    for x, z in ((0, 3), (10, 5), (6, 6), (3, 6)):
        b.set(x, 1, z, "amethyst_block")
        b.set(x, 2, z, "amethyst_cluster", facing="up")
    # support the side crystals so none float
    return b


@register("portals", "overgrown-nature-portal", "Заросший портал", "Overgrown nature portal",
          "Рамка портала, обросшая мхом и азалиями. Вьюны свисают сверху, вокруг мшистый камень и цветы.",
          "A portal frame swallowed by moss and azaleas, with hanging vines, mossy stone and flowers around it.",
          "medium", ["moss", "azalea", "vines", "overgrown"])
def overgrown():
    b = Build("overgrown-nature-portal")
    rnd = random.Random(31)
    for x in range(0, 11):
        for z in range(0, 8):
            r = rnd.random()
            b.set(x, 0, z, "moss_block" if r < 0.55 else ("mossy_cobblestone" if r < 0.7 else ("grass_block" if r < 0.9 else "mossy_stone_bricks")))
    frame(b, 3, 1, 3)
    b.set(3, 1, 3, "mossy_stone_bricks"); b.set(6, 5, 3, "mossy_cobblestone")
    # ruined mossy walls on both sides
    for x, h in ((1, 3), (2, 2), (8, 2), (9, 3), (10, 1)):
        for y in range(1, h + 1):
            b.set(x, y, 3, "mossy_stone_bricks" if (x + y) % 2 else "mossy_cobblestone")
    b.set(2, 3, 3, "mossy_stone_brick_wall"); b.set(8, 3, 3, "mossy_stone_brick_wall")
    # azalea bushes (leaves) and flowers on the moss
    for x, z, y in ((1, 2, 1), (1, 4, 1), (2, 4, 1), (9, 2, 1), (9, 4, 1), (8, 5, 1), (3, 5, 1)):
        b.set(x, y, z, "azalea_leaves" if (x + z) % 2 else "flowering_azalea_leaves")
        if (x + z) % 3 == 0:
            b.set(x, y + 1, z, "azalea_leaves")
    for x, z, n in ((0, 2, "flowering_azalea"), (4, 5, "azalea"), (7, 6, "flowering_azalea"), (2, 6, "azalea"),
                    (10, 5, "azalea"), (6, 5, "flowering_azalea")):
        if b.name_at((x, 0, z)) == "moss_block":
            b.set(x, 1, z, n)
    for x, z in ((5, 5), (1, 6), (9, 6), (4, 2), (6, 2), (0, 5)):
        if b.name_at((x, 0, z)) in ("moss_block", "grass_block"):
            b.set(x, 1, z, rnd.choice(["short_grass", "fern", "azure_bluet", "cornflower"]))
    # hanging vines
    for x in (4, 5):
        for y in (5, 4, 3):
            b.set(x, y, 4, "vine", north=True)
    b.set(3, 5, 4, "vine", north=True)
    for y in (3, 2):
        b.set(7, y, 3, "vine", west=True)
    b.set(7, 4, 3, "vine", west=True)
    # moss on top of the frame and the walls
    for x in (3, 4, 5):
        b.set(x, 6, 3, "moss_block")
    b.set(4, 7, 3, "flowering_azalea"); b.set(3, 7, 3, "azalea")
    b.set(1, 4, 3, "moss_block") ; b.set(1, 5, 3, "azalea")
    return b

