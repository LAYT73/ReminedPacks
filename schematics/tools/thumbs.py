"""Top-down PNG thumbnails using block textures from the game jar (pure Python, no PIL)."""
import re
import struct
import zlib

TEX = "assets/minecraft/textures/block/"
FOLIAGE = (119, 171, 47)
GRASS = (124, 189, 107)
WATER = (63, 118, 228)
BIRCH = (128, 167, 85)
SPRUCE = (97, 153, 97)


def png_decode(data):
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, idat, plte, trns = 8, b"", None, None
    w = h = bd = ct = il = 0
    while pos < len(data):
        n, typ = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if typ == b"IHDR":
            w, h, bd, ct, _, _, il = struct.unpack(">IIBBBBB", body)
        elif typ == b"PLTE":
            plte = body
        elif typ == b"tRNS":
            trns = body
        elif typ == b"IDAT":
            idat += body
    if il or bd not in (1, 2, 4, 8):
        return None
    ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    bpp_bits = ch * bd
    stride = (w * bpp_bits + 7) // 8
    bpp = max(1, bpp_bits // 8)
    raw = zlib.decompress(idat)
    rows, prev, p = [], bytearray(stride), 0
    for _ in range(h):
        f = raw[p]; line = bytearray(raw[p + 1:p + 1 + stride]); p += 1 + stride
        if f == 1:
            for i in range(bpp, stride): line[i] = (line[i] + line[i - bpp]) & 255
        elif f == 2:
            for i in range(stride): line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]; c = prev[i - bpp] if i >= bpp else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c - 0)
                pa = abs(b - c); pb = abs(a - c); pc = abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        rows.append(line); prev = line
    px = []
    for line in rows:
        out = []
        if bd == 8:
            vals = line
        else:
            vals = []
            mask = (1 << bd) - 1
            for byte in line:
                for s in range(8 - bd, -1, -bd):
                    vals.append((byte >> s) & mask)
        for x in range(w):
            if ct == 6: out.append(tuple(vals[x * 4:x * 4 + 4]))
            elif ct == 2: out.append((vals[x * 3], vals[x * 3 + 1], vals[x * 3 + 2], 255))
            elif ct == 0:
                g = vals[x] * (255 // ((1 << bd) - 1)); out.append((g, g, g, 255))
            elif ct == 4: out.append((vals[x * 2],) * 3 + (vals[x * 2 + 1],))
            else:
                i = vals[x]
                a = trns[i] if trns and i < len(trns) else 255
                out.append((plte[i * 3], plte[i * 3 + 1], plte[i * 3 + 2], a))
        px.append(out)
    return px


def png_encode(w, h, rgba_rows):
    raw = b"".join(b"\x00" + bytes(c for px in row for c in px) for row in rgba_rows)
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


class Textures:
    def __init__(self, zf):
        self.zf = zf
        self.names = {n[len(TEX):-4] for n in zf.namelist() if n.startswith(TEX) and n.endswith(".png")}
        self.cache = {}

    def load(self, tex):
        if tex not in self.cache:
            px = png_decode(self.zf.read(TEX + tex + ".png")) if tex in self.names else None
            if px and len(px) > len(px[0]):
                px = px[:len(px[0])]  # animated strip -> first frame
            self.cache[tex] = px
        return self.cache[tex]


def _material(name):
    for suf in ("_stairs", "_slab", "_wall", "_fence_gate", "_fence", "_pressure_plate", "_button"):
        if name.endswith(suf):
            return name[:-len(suf)], True
    return name, False


SPECIAL = {
    "grass_block": ("grass_block_top", GRASS), "short_grass": ("short_grass", GRASS), "fern": ("fern", GRASS),
    "tall_grass": ("tall_grass_top", GRASS), "vine": ("vine", FOLIAGE), "sugar_cane": ("sugar_cane", GRASS),
    "lily_pad": ("lily_pad", FOLIAGE), "farmland": ("farmland_moist", None), "dirt_path": ("dirt_path_top", None),
    "podzol": ("podzol_top", None), "mycelium": ("mycelium_top", None), "pumpkin": ("pumpkin_top", None),
    "melon": ("melon_top", None), "carved_pumpkin": ("pumpkin_top", None), "jack_o_lantern": ("pumpkin_top", None),
    "crafting_table": ("crafting_table_top", None), "furnace": ("furnace_top", None), "smoker": ("smoker_top", None),
    "barrel": ("barrel_top", None), "composter": ("composter_top", None), "cauldron": ("cauldron_top", None),
    "water_cauldron": ("water_still", WATER), "chest": ("oak_planks", None), "bookshelf": ("bookshelf", None),
    "hay_block": ("hay_block_top", None), "campfire": ("campfire_log_lit", None), "lantern": ("lantern", None),
    "soul_lantern": ("soul_lantern", None), "torch": ("torch", None), "iron_chain": ("chain", None),
    "wheat": ("wheat_stage7", None), "carrots": ("carrots_stage3", None), "potatoes": ("potatoes_stage3", None),
    "pumpkin_stem": ("pumpkin_stem", GRASS), "melon_stem": ("melon_stem", GRASS),
    "attached_pumpkin_stem": ("attached_pumpkin_stem", GRASS), "attached_melon_stem": ("attached_melon_stem", GRASS),
    "glass_pane": ("glass", None), "iron_bars": ("iron_bars", None), "quartz_pillar": ("quartz_pillar_top", None),
    "quartz_block": ("quartz_block_top", None), "smooth_quartz": ("quartz_block_bottom", None),
    "sandstone": ("sandstone_top", None), "smooth_sandstone": ("sandstone_top", None),
    "cut_sandstone": ("cut_sandstone", None), "chiseled_sandstone": ("chiseled_sandstone", None),
    "quartz": ("quartz_block_top", None), "smooth_stone": ("smooth_stone", None), "stone_brick": ("stone_bricks", None),
    "brick": ("bricks", None), "nether_brick": ("nether_bricks", None), "mossy_stone_brick": ("mossy_stone_bricks", None),
    "polished_blackstone_brick": ("polished_blackstone_bricks", None), "mossy_cobblestone": ("mossy_cobblestone", None),
    "smooth_quartz_slab": ("quartz_block_bottom", None), "cobblestone": ("cobblestone", None),
    "cherry_leaves": ("cherry_leaves", None), "azalea_leaves": ("azalea_leaves", None),
    "flowering_azalea_leaves": ("flowering_azalea_leaves", None), "azalea": ("azalea_top", None),
    "flowering_azalea": ("flowering_azalea_top", None), "pink_petals": ("pink_petals", None),
    "tinted_glass": ("tinted_glass", None), "nether_portal": ("obsidian", None), "water": ("water_still", WATER),
    "oak_leaves": ("oak_leaves", FOLIAGE), "birch_leaves": ("birch_leaves", BIRCH), "spruce_leaves": ("spruce_leaves", SPRUCE),
    "lilac": ("lilac_top", None), "rose_bush": ("rose_bush_top", None), "potted_poppy": ("poppy", None),
    "potted_dandelion": ("dandelion", None), "potted_cherry_sapling": ("cherry_sapling", None),
    "gilded_blackstone": ("gilded_blackstone", None), "cobblestone_wall": ("cobblestone", None),
}


def candidates(name):
    if name in SPECIAL:
        return [SPECIAL[name]]
    m = re.match(r"(.*)_(bed)$", name)
    if m:
        return [(m.group(1) + "_wool", None)]
    m = re.match(r"(.*)_carpet$", name)
    if m:
        return [(m.group(1) + "_wool", None)]
    if name.endswith("_stained_glass_pane"):
        return [(name[:-5], None)]
    if name.endswith("_door"):
        return [(name + "_top", None)]
    if name.endswith("_trapdoor"):
        return [(name, None)]
    if name.endswith("_sapling") or name.startswith("potted_"):
        return [(name.replace("potted_", ""), None)]
    mat, partial = _material(name)
    base = SPECIAL.get(mat, (mat, None))
    c = [(base[0] + "_top", base[1]), (base[0], base[1]), (base[0] + "_planks", None), (base[0] + "s", None),
         (base[0] + "_block", None), (base[0] + "_log_top", None)]
    if name.endswith(("_log", "_wood")):
        c = [(name + "_top", None), (name.replace("_wood", "_log") + "_top", None), (name, None)]
    return c


class Palette:
    def __init__(self, zf):
        self.t = Textures(zf)
        self.cache = {}

    def tile(self, name):
        """Return (16x16 rgba rows, average rgb)."""
        if name in self.cache:
            return self.cache[name]
        res = None
        for tex, tint in candidates(name):
            px = self.t.load(tex)
            if px:
                tr = [[self._tint(p, tint) for p in row] for row in px]
                res = tr
                break
        if res is None:
            h = sum(ord(c) * (i + 3) for i, c in enumerate(name)) % 120 + 90
            res = [[(h, 90, 200 - h // 2, 255)] * 16 for _ in range(16)]
        tot = [0, 0, 0]; n = 0
        for row in res:
            for r, g, b, a in row:
                if a > 40:
                    tot[0] += r; tot[1] += g; tot[2] += b; n += 1
        avg = tuple(c // max(n, 1) for c in tot) if n else (128, 128, 128)
        self.cache[name] = (res, avg)
        return self.cache[name]

    @staticmethod
    def _tint(p, tint):
        if not tint:
            return p
        return (p[0] * tint[0] // 255, p[1] * tint[1] // 255, p[2] * tint[2] // 255, p[3])


def render(grid, size, palette, px=128):
    W, H, L = size
    top = {}
    for (x, y, z), key in grid.items():
        if (x, z) not in top or y > top[(x, z)][0]:
            top[(x, z)] = (y, key)
    s = max(1, px // max(W, L))
    ow, oh = W * s, L * s
    ox, oy = (px - ow) // 2, (px - oh) // 2
    img = [[(0, 0, 0, 0)] * px for _ in range(px)]
    for (x, z), (y, key) in top.items():
        name = key[len("minecraft:"):].split("[")[0]
        tile, avg = palette.tile(name)
        f = 0.6 + 0.4 * (y / max(H - 1, 1))
        nb = top.get((x, z - 1)); wb = top.get((x - 1, z))
        if nb and nb[0] > y: f *= 0.82
        if wb and wb[0] > y: f *= 0.9
        for dy in range(s):
            for dx in range(s):
                if s >= 4:
                    r, g, b, a = tile[dy * 16 // s][dx * 16 // s]
                    if a < 128:
                        r, g, b = avg
                else:
                    r, g, b = avg
                img[oy + z * s + dy][ox + x * s + dx] = (min(255, int(r * f)), min(255, int(g * f)), min(255, int(b * f)), 255)
    return png_encode(px, px, img)
