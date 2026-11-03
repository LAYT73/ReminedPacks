from dsl import Build, register, gable, hip, CW, CCW


@register("houses", "oak-starter-cabin", "Дубовая хижина для старта", "Oak starter cabin",
          "Маленький домик на первые ночи: кровать, сундук, верстак, печка и факелы. Всё из дерева и булыжника.",
          "A tiny first-night home with a bed, chest, crafting table, furnace and torches. Just wood and cobblestone.",
          "easy", ["oak", "starter", "survival"])
def cabin():
    b = Build("oak-starter-cabin")
    b.fill(0, 0, 0, 6, 0, 5, "cobblestone")
    b.fill(1, 0, 1, 5, 0, 4, "oak_planks")
    for y in (1, 2, 3):
        b.shell(0, y, 0, 6, y, 5, "oak_planks")
    for x in (0, 6):
        for z in (0, 5):
            b.vlog(x, 1, 3, z, "oak")
    gable(b, 0, 6, 0, 5, 4, "spruce", axis="x", ov=1, ovx=1, fill=("oak_planks", {}))
    # stoop, door, lamp posts
    b.fill(2, 0, 6, 4, 0, 6, "cobblestone")
    b.door(3, 1, 5, "oak", "north")
    for x in (2, 4):
        b.set(x, 1, 6, "oak_fence")
        b.set(x, 2, 6, "lantern")
    # windows
    b.set(3, 2, 0, "glass_pane")
    b.trapdoor(2, 2, -1, "oak", "north", open=True)
    b.trapdoor(4, 2, -1, "oak", "north", open=True)
    for x in (1, 5):
        b.set(x, 2, 5, "glass_pane")
    for x in (0, 6):
        for z in (2, 3):
            b.set(x, 2, z, "glass_pane")
    # interior
    b.bed(1, 1, 2, "red", "north")
    b.chest(5, 1, 1, "south")
    b.set(4, 1, 1, "crafting_table")
    b.set(5, 1, 2, "furnace", facing="west", lit=True)
    b.set(5, 2, 2, "torch")
    b.wall_torch(2, 2, 4, "north")
    b.wall_torch(4, 2, 4, "north")
    b.fill(3, 1, 2, 4, 1, 3, "red_carpet")
    b.set(1, 1, 4, "barrel", facing="up")
    return b


@register("houses", "spruce-cottage", "Ёлевый коттедж с трубой", "Spruce cottage",
          "Уютный коттедж с каменной трубой, камином и крышей из тёмных ступеней. Внутри стол, кровать и подвесной фонарь.",
          "A cosy cottage with a stone chimney, a hearth and a dark stair roof. Table, bed and a hanging lantern inside.",
          "medium", ["spruce", "cottage", "chimney"])
def cottage():
    b = Build("spruce-cottage")
    b.fill(0, 0, 0, 8, 0, 6, "cobblestone")
    b.fill(1, 0, 1, 7, 0, 5, "spruce_planks")
    b.shell(0, 1, 0, 8, 1, 6, "cobblestone")
    for y in (2, 3):
        b.shell(0, y, 0, 8, y, 6, "spruce_planks")
    for x in (0, 8):
        for z in (0, 6):
            b.vlog(x, 1, 3, z, "spruce")
    for x in (4,):
        b.vlog(x, 2, 3, 0, "spruce"); b.vlog(x, 2, 3, 6, "spruce")
    for z in (3,):
        b.vlog(0, 2, 3, z, "spruce"); b.vlog(8, 2, 3, z, "spruce")
    gable(b, 0, 8, 0, 6, 4, "dark_oak", axis="x", ov=1, ovx=0, fill=("spruce_planks", {}))
    # chimney on the east gable
    for y in range(0, 3):
        b.fill(9, y, 2, 9, y, 4, "cobblestone")
    for y in range(3, 8):
        b.set(9, y, 3, "cobblestone")
    b.set(9, 8, 3, "cobblestone_wall")
    b.set(8, 1, 3, "stone_bricks")
    # door + windows
    b.door(4, 1, 6, "spruce", "north")
    b.set(4, 0, 7, "cobblestone"); b.set(3, 0, 7, "cobblestone"); b.set(5, 0, 7, "cobblestone")
    b.set(3, 1, 7, "spruce_fence"); b.set(5, 1, 7, "spruce_fence")
    b.set(3, 2, 7, "lantern"); b.set(5, 2, 7, "lantern")
    for x in (2, 6):
        b.set(x, 2, 6, "glass_pane")
        b.set(x, 2, 0, "glass_pane")
        b.trapdoor(x - 1, 2, 7, "spruce", "south", open=True)
        b.trapdoor(x + 1, 2, 7, "spruce", "south", open=True)
        b.trapdoor(x - 1, 2, -1, "spruce", "north", open=True)
        b.trapdoor(x + 1, 2, -1, "spruce", "north", open=True)
    b.set(0, 2, 2, "glass_pane"); b.set(0, 2, 4, "glass_pane")
    # interior
    b.bed(1, 1, 2, "blue", "north")
    b.double_chest(3, 1, 1, "south")
    b.set(5, 1, 1, "crafting_table")
    b.set(6, 1, 1, "furnace", facing="south")
    b.set(7, 1, 1, "barrel", facing="up")
    b.set(4, 1, 3, "spruce_fence")
    b.set(4, 2, 3, "spruce_pressure_plate")
    b.stairs(3, 1, 3, "spruce", "west")
    b.stairs(5, 1, 3, "spruce", "east")
    b.set(7, 1, 3, "furnace", facing="west", lit=True)
    b.fill(2, 1, 2, 6, 1, 4, "brown_carpet")
    for y in (4, 5):
        b.set(4, y, 3, "iron_chain", axis="y")
    b.set(4, 3, 3, "lantern", hanging=True)
    b.set(4, 1, 3, "spruce_fence")  # table survives the carpet
    b.fill(2, 1, 2, 3, 1, 2, "brown_carpet")
    return b


@register("houses", "medieval-half-timber", "Фахверковый дом", "Medieval half-timber house",
          "Двухэтажный дом: белая штукатурка, тёмные балки, второй этаж нависает над первым. Лестница внутри.",
          "Two floors of white plaster and dark timber, with a jettied upper storey and a brick-red stair roof. Staircase inside.",
          "hard", ["medieval", "half-timber", "two-floor"])
def halftimber():
    b = Build("medieval-half-timber")
    P, T = "white_terracotta", "stripped_dark_oak_log"
    # ground floor 9x7
    b.fill(0, 0, 0, 8, 0, 6, "stone_bricks")
    b.fill(1, 0, 1, 7, 0, 5, "spruce_planks")
    b.shell(0, 1, 0, 8, 1, 6, "stone_bricks")
    b.shell(0, 2, 0, 8, 2, 6, P)
    for x in (0, 3, 5, 8):
        b.vlog(x, 2, 3, 0, "dark_oak", True); b.vlog(x, 2, 3, 6, "dark_oak", True)
    for z in (0, 3, 6):
        b.vlog(0, 2, 3, z, "dark_oak", True); b.vlog(8, 2, 3, z, "dark_oak", True)
    for x in range(1, 8):
        if x not in (3, 5):
            b.log(x, 3, 0, "dark_oak", "x", True); b.log(x, 3, 6, "dark_oak", "x", True)
    for z in (1, 2, 4, 5):
        b.log(0, 3, z, "dark_oak", "z", True); b.log(8, 3, z, "dark_oak", "z", True)
    # floor 2 (jetty: z -1..7)
    b.fill(0, 4, -1, 8, 4, 7, "spruce_planks")
    for x in range(0, 9):
        b.log(x, 4, -1, "dark_oak", "x", True); b.log(x, 4, 7, "dark_oak", "x", True)
    for z in range(-1, 8):
        b.log(0, 4, z, "dark_oak", "z", True); b.log(8, 4, z, "dark_oak", "z", True)
    for x in (0, 4, 8):
        b.stairs(x, 3, -1, "dark_oak", "south", "top")
        b.stairs(x, 3, 7, "dark_oak", "north", "top")
    # upper walls z -1..7, y5..7
    b.shell(0, 5, -1, 8, 6, 7, P)
    for x in range(0, 9):
        b.log(x, 7, -1, "dark_oak", "x", True); b.log(x, 7, 7, "dark_oak", "x", True)
    for z in range(-1, 8):
        b.log(0, 7, z, "dark_oak", "z", True); b.log(8, 7, z, "dark_oak", "z", True)
    for x in (0, 2, 4, 6, 8):
        b.vlog(x, 5, 6, -1, "dark_oak", True); b.vlog(x, 5, 6, 7, "dark_oak", True)
    for z in (-1, 1, 3, 5, 7):
        b.vlog(0, 5, 6, z, "dark_oak", True); b.vlog(8, 5, 6, z, "dark_oak", True)
    gable(b, 0, 8, -1, 7, 8, "brick", axis="x", ov=1, ovx=1, fill=(P, {}), ridge="bricks")
    # gable timbers
    for u in (0, 8):
        for y in (8, 9, 10):
            b.set(u, y, 3, T, axis="y")
        b.set(u, 8, 0, T, axis="y"); b.set(u, 8, 6, T, axis="y")
        b.set(u, 9, 1, T, axis="y"); b.set(u, 9, 5, T, axis="y")
    # doors, windows
    b.door(4, 1, 6, "spruce", "north")
    b.set(4, 0, 7, "stone_bricks")
    b.set(3, 0, 7, "stone_bricks"); b.set(5, 0, 7, "stone_bricks")
    b.set(3, 1, 7, "dark_oak_fence"); b.set(5, 1, 7, "dark_oak_fence")
    b.set(3, 2, 7, "lantern"); b.set(5, 2, 7, "lantern")
    b.door(4, 1, 0, "spruce", "south")
    for x in (1, 2, 6, 7):
        for z in (0, 6):
            b.set(x, 2, z, "glass_pane")
    for x in (2, 6):
        for z in (-1, 7):
            b.set(x, 6, z, "glass_pane")
    for z in (2, 4):
        b.set(0, 2, z, "glass_pane"); b.set(8, 2, z, "glass_pane")
    for z in (1, 3, 5):
        b.set(0, 6, z, "glass_pane"); b.set(8, 6, z, "glass_pane")
    # staircase to floor 2 along the west wall
    for i, z in enumerate((5, 4, 3, 2)):
        b.stairs(1, 1 + i, z, "spruce", "north")
    for z in (3, 4, 5):
        b.set(1, 4, z, "air")
        b.set(2, 5, z, "dark_oak_fence")
    # ground floor interior
    b.set(7, 1, 1, "crafting_table")
    b.set(7, 1, 2, "furnace", facing="west", lit=True)
    b.set(7, 1, 3, "barrel", facing="west")
    b.double_chest(6, 1, 1, "south")
    b.set(4, 1, 3, "dark_oak_fence"); b.set(4, 2, 3, "dark_oak_pressure_plate")
    b.stairs(3, 1, 3, "spruce", "west"); b.stairs(5, 1, 3, "spruce", "east")
    b.set(4, 3, 3, "lantern", hanging=True)
    b.set(4, 4, 3, "dark_oak_planks")
    b.fill(3, 1, 4, 5, 1, 4, "red_carpet")
    b.wall_torch(3, 2, 5, "north"); b.wall_torch(5, 2, 5, "north")
    # upper floor interior
    b.bed(7, 5, 4, "white", "north")
    b.bed(6, 5, 4, "white", "north")
    b.fill(2, 5, 0, 5, 6, 0, "bookshelf")
    b.set(7, 5, 1, "barrel", facing="up")
    b.set(7, 5, 0, "crafting_table")
    b.fill(3, 5, 2, 5, 5, 3, "red_carpet")
    for y in (8, 9, 10):
        b.set(4, y, 3, "iron_chain", axis="y")
    b.set(4, 11, 3, "bricks")
    b.set(4, 7, 3, "lantern", hanging=True)
    return b


@register("houses", "birch-modern-house", "Современный дом из берёзы и кварца", "Birch modern house",
          "Светлый дом с большими окнами, плоской крышей и террасой. Кварц, берёза и стекло.",
          "A bright house with big windows, a flat roof and a terrace. Quartz, birch and glass.",
          "hard", ["birch", "modern", "quartz", "glass"])
def modern():
    b = Build("birch-modern-house")
    Q, QP = "quartz_block", "quartz_pillar"
    # ground floor x0..8, z0..6
    b.fill(0, 0, 0, 8, 0, 6, "smooth_stone")
    b.fill(1, 0, 1, 7, 0, 5, "birch_planks")
    for y in (1, 2, 3):
        b.shell(0, y, 0, 8, y, 6, "birch_planks")
    for x in (0, 4, 8):
        for z in (0, 6):
            for y in (1, 2, 3):
                b.set(x, y, z, QP, axis="y")
    # glass front (south), windows on the north and west walls
    for x in (1, 2, 3, 5, 6, 7):
        for y in (1, 2, 3):
            b.set(x, y, 6, "glass_pane")
    for x in (2, 6):
        b.set(x, 2, 0, "glass_pane"); b.set(x, 3, 0, "glass_pane")
    for z in (2, 3, 4):
        b.set(0, 2, z, "glass_pane")
    b.door(4, 1, 6, "birch", "north")
    b.set(4, 3, 6, QP, axis="y")
    # ceiling of the ground floor = terrace deck (y4), slab fringe on the west half
    b.fill(0, 4, 0, 8, 4, 6, "smooth_quartz")
    for x in range(-1, 4):
        b.slab(x, 4, -1, "quartz"); b.slab(x, 4, 7, "quartz")
    for z in range(0, 7):
        b.slab(-1, 4, z, "quartz")
    for x in range(-1, 4):
        b.set(x, 5, -1, "birch_fence"); b.set(x, 5, 7, "birch_fence")
    for z in range(0, 7):
        b.set(-1, 5, z, "birch_fence")
    # terrace: planter and a bench
    b.set(0, 5, 0, "moss_block"); b.set(0, 6, 0, "flowering_azalea")
    b.set(0, 5, 6, "moss_block"); b.set(0, 6, 6, "azalea")
    b.stairs(1, 5, 6, "quartz", "north"); b.stairs(2, 5, 6, "quartz", "north")
    b.set(2, 5, 2, "birch_fence"); b.set(2, 6, 2, "birch_pressure_plate")
    b.stairs(1, 5, 2, "birch", "west"); b.stairs(3, 5, 2, "birch", "east")
    # upper box x4..8, z0..6, y5..7
    for y in (5, 6, 7):
        b.shell(4, y, 0, 8, y, 6, Q)
        for x in (4, 8):
            for z in (0, 6):
                b.set(x, y, z, QP, axis="y")
    for x in (5, 6, 7):
        for y in (5, 6):
            b.set(x, y, 6, "glass_pane")
        b.set(x, 6, 0, "glass_pane")
    for z in (2, 3, 4):
        b.set(8, 5, z, "glass_pane"); b.set(8, 6, z, "glass_pane")
    b.fill(4, 8, 0, 8, 8, 6, "smooth_quartz")
    for x in range(3, 10):
        b.slab(x, 8, -1, "smooth_quartz"); b.slab(x, 8, 7, "smooth_quartz")
    for z in range(0, 7):
        b.slab(3, 8, z, "smooth_quartz"); b.slab(9, 8, z, "smooth_quartz")
    # staircase (ascends east along the north wall) through a floor opening
    for i, x in enumerate((3, 4, 5, 6)):
        b.stairs(x, 1 + i, 1, "quartz", "east")
    b.set(4, 4, 1, "air"); b.set(5, 4, 1, "air")
    # ground floor interior
    b.set(7, 1, 1, "crafting_table"); b.set(7, 1, 2, "furnace", facing="west")
    b.set(7, 1, 3, "barrel", facing="west")
    b.double_chest(1, 1, 1, "south")
    b.fill(1, 1, 3, 3, 1, 4, "white_carpet")
    b.set(5, 1, 4, "birch_fence"); b.set(5, 2, 4, "birch_pressure_plate")
    b.stairs(5, 1, 3, "birch", "north"); b.stairs(5, 1, 5, "birch", "south")
    b.set(3, 3, 4, "iron_chain", axis="y"); b.set(3, 2, 4, "lantern", hanging=True)
    # upper room
    b.bed(7, 5, 4, "light_blue", "north")
    b.bed(6, 5, 4, "light_blue", "north")
    b.set(7, 5, 5, "barrel", facing="up"); b.set(5, 5, 5, "crafting_table")
    for x in (6, 7):
        b.set(x, 5, 2, "bookshelf"); b.set(x, 6, 2, "bookshelf")
    b.fill(5, 5, 2, 5, 5, 4, "light_blue_carpet")
    b.set(5, 7, 3, "iron_chain", axis="y"); b.set(5, 6, 3, "lantern", hanging=True)
    return b


@register("houses", "desert-sandstone-house", "Дом из песчаника", "Desert sandstone house",
          "Прохладный дом для пустыни: толстые стены, плоская крыша с навесом и лестница наверх. Внутри всё необходимое.",
          "A cool desert home with thick walls, a flat roof with a shaded corner and a ladder up. Everything you need inside.",
          "medium", ["desert", "sandstone", "flat-roof"])
def desert():
    b = Build("desert-sandstone-house")
    b.fill(0, 0, 0, 8, 0, 6, "sandstone")
    b.fill(1, 0, 1, 7, 0, 5, "cut_sandstone")
    for y in (1, 2, 3):
        b.shell(0, y, 0, 8, y, 6, "sandstone")
    b.shell(0, 4, 0, 8, 4, 6, "cut_sandstone")
    for x in (0, 8):
        for z in (0, 6):
            for y in (1, 2, 3):
                b.set(x, y, z, "cut_sandstone")
    for x in range(1, 8):
        for z in (0, 6):
            if x not in (4,):
                b.set(x, 4, z, "orange_terracotta")
    b.fill(0, 5, 0, 8, 5, 6, "smooth_sandstone")
    # parapet with a gap at the ladder
    for x in range(0, 9):
        for z in range(0, 7):
            if x in (0, 8) or z in (0, 6):
                if (x, z) != (8, 3):
                    b.set(x, 6, z, "sandstone_wall")
    # door, windows, lamps
    b.door(4, 1, 6, "acacia", "north")
    b.set(4, 3, 6, "chiseled_sandstone")
    for x in (3, 5):
        b.set(x, 1, 7, "sandstone_wall"); b.set(x, 2, 7, "lantern")
    b.set(4, 0, 7, "sandstone"); b.set(3, 0, 7, "sandstone"); b.set(5, 0, 7, "sandstone")
    for x in (1, 7):
        b.set(x, 2, 6, "glass_pane"); b.set(x, 3, 6, "glass_pane")
    for x in (2, 6):
        b.set(x, 2, 0, "glass_pane"); b.set(x, 3, 0, "glass_pane")
        b.trapdoor(x - 1, 2, -1, "acacia", "north", open=True); b.trapdoor(x - 1, 3, -1, "acacia", "north", open=True)
        b.trapdoor(x + 1, 2, -1, "acacia", "north", open=True); b.trapdoor(x + 1, 3, -1, "acacia", "north", open=True)
    for z in (2, 4):
        b.set(0, 2, z, "glass_pane"); b.set(0, 3, z, "glass_pane")
    b.set(4, 3, 0, "chiseled_sandstone")
    # ladder to the roof on the east wall
    for y in range(1, 6):
        b.set(9, y, 3, "ladder", facing="east")
    # rooftop pergola
    for x in (5, 7):
        for z in (2, 4):
            b.set(x, 6, z, "acacia_fence"); b.set(x, 7, z, "acacia_fence")
    b.fill(5, 8, 2, 7, 8, 4, "acacia_slab")
    b.fill(5, 6, 3, 7, 6, 3, "orange_carpet")
    b.set(1, 6, 5, "cauldron")
    # interior
    b.bed(1, 1, 2, "orange", "north")
    b.double_chest(3, 1, 1, "south")
    b.set(5, 1, 1, "crafting_table"); b.set(6, 1, 1, "furnace", facing="south")
    b.set(7, 1, 1, "barrel", facing="up")
    b.fill(3, 1, 3, 5, 1, 4, "orange_carpet")
    b.stairs(7, 1, 4, "sandstone", "west"); b.stairs(7, 1, 3, "sandstone", "west")
    b.set(4, 4, 3, "iron_chain", axis="y"); b.set(4, 3, 3, "lantern", hanging=True)
    b.wall_torch(2, 2, 5, "north"); b.wall_torch(6, 2, 5, "north")
    return b


@register("houses", "cherry-tea-house", "Чайный домик из вишни", "Cherry tea house",
          "Небольшой павильон с розовой крышей-пагодой, бумажными окнами и верандой. Внутри низкий столик и подушки.",
          "A small pagoda pavilion with a pink hip roof, paper-screen windows and a veranda. Low table and cushions inside.",
          "medium", ["cherry", "tea", "pagoda"])
def teahouse():
    b = Build("cherry-tea-house")
    b.fill(0, 0, 0, 8, 0, 8, "stone_bricks")
    b.fill(1, 0, 1, 7, 0, 7, "cherry_planks")
    # veranda posts and corner lanterns
    for x in (1, 7):
        for z in (1, 7):
            for y in (1, 2, 3):
                b.set(x, y, z, "cherry_fence")
    for x in (0, 8):
        for z in (0, 8):
            b.set(x, 1, z, "stone_brick_wall"); b.set(x, 2, z, "lantern")
    # walls x2..6, z2..6
    b.shell(2, 1, 2, 6, 1, 6, "cherry_planks")
    for y in (2, 3):
        b.shell(2, y, 2, 6, y, 6, "white_stained_glass_pane")
    for x in (2, 4, 6):
        for z in (2, 6):
            for y in (1, 2, 3):
                b.set(x, y, z, "stripped_cherry_log", axis="y")
    for z in (2, 4, 6):
        for x in (2, 6):
            for y in (1, 2, 3):
                b.set(x, y, z, "stripped_cherry_log", axis="y")
    b.door(4, 1, 6, "cherry", "north")
    b.set(4, 3, 6, "cherry_planks")
    # beam ring
    for x in range(2, 7):
        b.log(x, 4, 2, "cherry", "x", True); b.log(x, 4, 6, "cherry", "x", True)
    for z in range(3, 6):
        b.log(2, 4, z, "cherry", "z", True); b.log(6, 4, z, "cherry", "z", True)
    hip(b, 1, 7, 1, 7, 4, "cherry")
    b.set(4, 8, 4, "cherry_fence"); b.set(4, 9, 4, "lantern")
    b.set(4, 6, 4, "iron_chain", axis="y"); b.set(4, 5, 4, "lantern", hanging=True)
    # interior
    b.slab(4, 1, 4, "cherry")
    b.set(4, 2, 4, "potted_cherry_sapling")
    for p in ((3, 4), (5, 4), (4, 5)):
        b.set(p[0], 1, p[1], "pink_carpet")
    b.set(3, 1, 3, "cauldron"); b.set(4, 1, 3, "barrel", facing="south"); b.set(5, 1, 3, "smoker", facing="south")
    return b

