"""Block-by-block structure DSL.

Coordinates: x = east, y = up, z = south.  Every build keeps an in-memory grid
of (name, props); `finalize()` derives all neighbour-dependent properties the way
the game would (stairs shape, fence/wall/pane connections, leaf distance, ...)
and returns canonical blockstate strings.
"""
import re
from collections import deque

DIRS = {"north": (0, 0, -1), "south": (0, 0, 1), "east": (1, 0, 0), "west": (-1, 0, 0)}
OPP = {"north": "south", "south": "north", "east": "west", "west": "east", "up": "down", "down": "up"}
CW = {"north": "east", "east": "south", "south": "west", "west": "north"}
CCW = {v: k for k, v in CW.items()}
AXIS_OF = {"north": "z", "south": "z", "east": "x", "west": "x"}


def add(p, d, n=1):
    v = DIRS[d]
    return (p[0] + v[0] * n, p[1], p[2] + v[2] * n)


# --------------------------------------------------------------------------- schema
# Full property sets of every block that has properties (alphabetical on output).
# Cross-checked against the property sets found in the game's own structure files.
_B = ("false", "true")
RULES = [
    (r".*_stairs", {"facing": "north", "half": "bottom", "shape": "straight", "waterlogged": "false"}),
    (r".*_slab", {"type": "bottom", "waterlogged": "false"}),
    (r".*_(log|wood)|hay_block|quartz_pillar|purpur_pillar|bone_block|basalt|polished_basalt", {"axis": "y"}),
    (r".*_leaves", {"distance": "7", "persistent": "true", "waterlogged": "false"}),
    (r".*_fence", {"east": "false", "north": "false", "south": "false", "waterlogged": "false", "west": "false"}),
    (r".*_fence_gate", {"facing": "north", "in_wall": "false", "open": "false", "powered": "false"}),
    (r".*_wall", {"east": "none", "north": "none", "south": "none", "up": "true", "waterlogged": "false", "west": "none"}),
    (r".*glass_pane|iron_bars", {"east": "false", "north": "false", "south": "false", "waterlogged": "false", "west": "false"}),
    (r".*_door", {"facing": "north", "half": "lower", "hinge": "left", "open": "false", "powered": "false"}),
    (r".*_trapdoor", {"facing": "north", "half": "bottom", "open": "false", "powered": "false", "waterlogged": "false"}),
    (r".*_bed", {"facing": "north", "occupied": "false", "part": "foot"}),
    (r"chest", {"facing": "north", "type": "single", "waterlogged": "false"}),
    (r"barrel", {"facing": "north", "open": "false"}),
    (r"furnace|smoker|blast_furnace", {"facing": "north", "lit": "false"}),
    (r"wall_torch|soul_wall_torch", {"facing": "north"}),
    (r"lantern|soul_lantern", {"hanging": "false", "waterlogged": "false"}),
    (r"campfire|soul_campfire", {"facing": "north", "lit": "true", "signal_fire": "false", "waterlogged": "false"}),
    (r"ladder", {"facing": "north", "waterlogged": "false"}),
    (r"farmland", {"moisture": "0"}),
    (r"wheat|carrots|potatoes", {"age": "0"}),
    (r"beetroots", {"age": "0"}),
    (r"melon_stem|pumpkin_stem", {"age": "0"}),
    (r"attached_melon_stem|attached_pumpkin_stem", {"facing": "north"}),
    (r"composter", {"level": "0"}),
    (r"sugar_cane", {"age": "0"}),
    (r"water", {"level": "0"}),
    (r"(?!potted_).*_sapling", {"stage": "0"}),
    (r"tall_grass|large_fern|lilac|rose_bush|peony|sunflower", {"half": "lower"}),
    (r"grass_block|podzol|mycelium", {"snowy": "false"}),
    (r"vine", {"east": "false", "north": "false", "south": "false", "up": "false", "west": "false"}),
    (r"candle", {"candles": "1", "lit": "false", "waterlogged": "false"}),
    (r"iron_chain", {"axis": "y", "waterlogged": "false"}),
    (r"water_cauldron", {"level": "1"}),
    (r"nether_portal", {"axis": "x"}),
    (r"carved_pumpkin|jack_o_lantern|loom|glazed_terracotta", {"facing": "north"}),
    (r"amethyst_cluster|(large|medium|small)_amethyst_bud", {"facing": "up", "waterlogged": "false"}),
    (r".*_pressure_plate", {"powered": "false"}),
    (r"pink_petals", {"facing": "north", "flower_amount": "1"}),
]
_RULES = [(re.compile(p), d) for p, d in RULES]

DOMAINS = {
    "facing": {"north", "south", "east", "west", "up", "down"},
    "axis": {"x", "y", "z"},
    "half": {"lower", "upper", "top", "bottom"},
    "shape": {"straight", "inner_left", "inner_right", "outer_left", "outer_right"},
    "type": {"bottom", "top", "double", "single", "left", "right"},
    "hinge": {"left", "right"},
    "part": {"foot", "head"},
    "east": {"true", "false", "none", "low", "tall"},
    "north": {"true", "false", "none", "low", "tall"},
    "south": {"true", "false", "none", "low", "tall"},
    "west": {"true", "false", "none", "low", "tall"},
}
INT_PROPS = {"age": 25, "distance": 7, "moisture": 7, "level": 8, "stage": 1, "candles": 4, "flower_amount": 4}
BOOL_PROPS = {"up", "open", "powered", "lit", "waterlogged", "persistent", "in_wall", "occupied",
              "hanging", "signal_fire", "snowy"}


def schema(name):
    for rx, d in _RULES:
        if rx.fullmatch(name):
            return d
    return {}


def domain_ok(prop, val, block=None):
    if prop in INT_PROPS:
        return val.isdigit() and int(val) <= INT_PROPS[prop] and (prop not in ("distance", "candles", "flower_amount") or int(val) >= 1)
    if prop in ("east", "north", "south", "west", "up") and block:
        if block.endswith("_wall"):
            return val in ("none", "low", "tall") if prop != "up" else val in _B
        return val in _B
    if prop in BOOL_PROPS:
        return val in _B
    if prop in DOMAINS:
        return val in DOMAINS[prop]
    return True


# --------------------------------------------------------------------------- classification
NONFULL_RE = re.compile(
    r"(_stairs|_slab|_fence|_fence_gate|_wall|_door|_trapdoor|glass_pane|iron_bars|torch|lantern|ladder|carpet|"
    r"_bed|chest|composter|cauldron|campfire|farmland|dirt_path|_sapling|_leaves|pumpkin|melon|jack_o_lantern|"
    r"candle|vine|_stem|sugar_cane|short_grass|tall_grass|fern|pressure_plate|amethyst_cluster|amethyst_bud|"
    r"flower_pot|potted_|iron_chain|pink_petals|lily_pad|nether_portal|soul_sand|azalea$|dandelion|poppy|"
    r"cornflower|allium|azure_bluet|oxeye_daisy|lily_of_the_valley|blue_orchid|tulip|lilac|rose_bush|peony|"
    r"sunflower|wheat|carrots|potatoes|beetroots|candle|moss_carpet|sweet_berry|bell|end_rod|lightning_rod)")
NONFULL_EXACT = {"air", "water", "lava", "azalea", "flowering_azalea", "chest", "vine"}
LIQUID_OR_AIR = {"air", "water", "lava"}
PLANTS = re.compile(r"(_sapling$|^short_grass$|^fern$|dandelion|poppy|cornflower|allium|azure_bluet|oxeye_daisy|"
                    r"lily_of_the_valley|blue_orchid|_tulip|^azalea$|^flowering_azalea$|pink_petals)")
TALL_PLANTS = {"tall_grass", "large_fern", "lilac", "rose_bush", "peony", "sunflower"}
SOIL = {"dirt", "grass_block", "podzol", "coarse_dirt", "rooted_dirt", "mud", "moss_block", "mycelium", "farmland"}
CANE_SOIL = {"dirt", "grass_block", "podzol", "coarse_dirt", "rooted_dirt", "mud", "sand", "red_sand", "moss_block"}


def is_full(name, props=None):
    if name in ("pumpkin", "melon", "carved_pumpkin", "jack_o_lantern"):
        return False
    if name.endswith("_slab"):
        return bool(props) and props.get("type") == "double"
    if name in NONFULL_EXACT or NONFULL_RE.search(name):
        return False
    return True


def sturdy(name, props, face):
    """Is the face of this block whose outward normal is `face` completely solid?"""
    if name.endswith("_stairs"):
        return props.get("half") == "bottom" and props.get("facing") == face or \
            (props.get("half") == "top" and props.get("facing") == face)
    return is_full(name, props)


# --------------------------------------------------------------------------- build
def _s(v):
    if v is True: return "true"
    if v is False: return "false"
    return str(v)


class Build:
    def __init__(self, name=""):
        self.name = name
        self.g = {}

    # ---- primitives
    def set(self, x, y, z, name, **p):
        name = name.replace("minecraft:", "")
        if name == "air":
            self.g.pop((x, y, z), None)
            return
        sc = schema(name)
        props = {k: _s(v) for k, v in p.items()}
        for k, v in props.items():
            if k not in sc:
                raise ValueError(f"{self.name}: unknown prop {k} for {name}")
            if not domain_ok(k, v, name):
                raise ValueError(f"{self.name}: bad value {k}={v} for {name}")
        self.g[(x, y, z)] = (name, props)

    def get(self, x, y, z):
        return self.g.get((x, y, z))

    def name_at(self, p):
        b = self.g.get(p)
        return b[0] if b else "air"

    def fill(self, x1, y1, z1, x2, y2, z2, name, **p):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                for z in range(min(z1, z2), max(z1, z2) + 1):
                    self.set(x, y, z, name, **p)

    def shell(self, x1, y1, z1, x2, y2, z2, name, **p):
        """Walls only (no floor/ceiling) of a box."""
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                for z in range(z1, z2 + 1):
                    if x in (x1, x2) or z in (z1, z2):
                        self.set(x, y, z, name, **p)

    def ring(self, x1, y, z1, x2, z2, name, **p):
        self.shell(x1, y, z1, x2, y, z2, name, **p)

    # ---- typed helpers
    def stairs(self, x, y, z, mat, facing, half="bottom"):
        self.set(x, y, z, f"{mat}_stairs", facing=facing, half=half)

    def slab(self, x, y, z, mat, type="bottom"):
        self.set(x, y, z, f"{mat}_slab", type=type)

    def log(self, x, y, z, mat, axis="y", stripped=False):
        self.set(x, y, z, f"stripped_{mat}_log" if stripped else f"{mat}_log", axis=axis)

    def vlog(self, x, y1, y2, z, mat, stripped=False):
        for y in range(y1, y2 + 1):
            self.log(x, y, z, mat, "y", stripped)

    def door(self, x, y, z, mat, facing, hinge="left", open=False):
        n = f"{mat}_door"
        self.set(x, y, z, n, facing=facing, half="lower", hinge=hinge, open=open)
        self.set(x, y + 1, z, n, facing=facing, half="upper", hinge=hinge, open=open)

    def trapdoor(self, x, y, z, mat, facing, half="bottom", open=False):
        self.set(x, y, z, f"{mat}_trapdoor", facing=facing, half=half, open=open)

    def bed(self, x, y, z, color, facing):
        """(x,y,z) is the foot; the head lies one block towards `facing`."""
        n = f"{color}_bed"
        self.set(x, y, z, n, facing=facing, part="foot")
        hx, _, hz = add((x, y, z), facing)
        self.set(hx, y, hz, n, facing=facing, part="head")

    def chest(self, x, y, z, facing):
        self.set(x, y, z, "chest", facing=facing)

    def double_chest(self, x, y, z, facing):
        """(x,y,z) is the RIGHT half; the LEFT half is at CCW(facing) from it.
        (facing=south -> left half is on the east side, x+1.)"""
        self.set(x, y, z, "chest", facing=facing, type="right")
        lx, _, lz = add((x, y, z), CCW[facing])
        self.set(lx, y, lz, "chest", facing=facing, type="left")

    def tall(self, x, y, z, name):
        self.set(x, y, z, name, half="lower")
        self.set(x, y + 1, z, name, half="upper")

    def wall_torch(self, x, y, z, facing):
        self.set(x, y, z, "wall_torch", facing=facing)

    def ladder(self, x, y1, y2, z, facing, xx=None):
        for y in range(y1, y2 + 1):
            self.set(x, y, z, "ladder", facing=facing)

    # ---- queries used by finalize
    def _full(self, p):
        b = self.g.get(p)
        return bool(b) and is_full(b[0], b[1])

    def _sturdy(self, p, face):
        b = self.g.get(p)
        return bool(b) and sturdy(b[0], b[1], face)

    # ---- derive neighbour-dependent state
    def finalize(self):
        g = self.g
        out = dict(g)

        def put(p, **kw):
            n, pr = out[p]
            pr = dict(pr)
            pr.update({k: _s(v) for k, v in kw.items()})
            out[p] = (n, pr)

        # leaves distance (BFS from logs)
        dist = {}
        dq = deque()
        for p, (n, _) in g.items():
            if n.endswith("_log") or n.endswith("_wood"):
                dist[p] = 0
                dq.append(p)
        while dq:
            p = dq.popleft()
            if dist[p] >= 6:
                continue
            for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
                q = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
                if q in g and g[q][0].endswith("_leaves") and q not in dist:
                    dist[q] = dist[p] + 1
                    dq.append(q)
        for p, (n, pr) in g.items():
            if n.endswith("_leaves"):
                put(p, distance=dist.get(p, 7), persistent=True)

        def is_stairs(p):
            return p in g and g[p][0].endswith("_stairs")

        def can_take(p, st, face):
            q = add(p, face)
            return not is_stairs(q) or g[q][1]["facing"] != st["facing"] or g[q][1]["half"] != st["half"]

        for p, (n, pr) in g.items():
            if n.endswith("_stairs"):
                f = pr["facing"]
                shape = "straight"
                fr = add(p, f)
                if is_stairs(fr) and g[fr][1]["half"] == pr["half"]:
                    d1 = g[fr][1]["facing"]
                    if AXIS_OF[d1] != AXIS_OF[f] and can_take(p, pr, OPP[d1]):
                        shape = "outer_left" if d1 == CCW[f] else "outer_right"
                if shape == "straight":
                    bk = add(p, OPP[f])
                    if is_stairs(bk) and g[bk][1]["half"] == pr["half"]:
                        d2 = g[bk][1]["facing"]
                        if AXIS_OF[d2] != AXIS_OF[f] and can_take(p, pr, d2):
                            shape = "inner_left" if d2 == CCW[f] else "inner_right"
                put(p, shape=shape)

        def gate_connects(q, d):
            b = g.get(q)
            return bool(b) and b[0].endswith("_fence_gate") and AXIS_OF[b[1]["facing"]] == AXIS_OF[CW[d]]

        def conn_fence(p, d):
            q = add(p, d)
            b = g.get(q)
            if not b:
                return False
            if b[0].endswith("_fence") and "nether_brick" not in b[0]:
                return True
            return gate_connects(q, d) or sturdy(b[0], b[1], OPP[d])

        def conn_pane(p, d):
            q = add(p, d)
            b = g.get(q)
            if not b:
                return False
            if b[0].endswith("glass_pane") or b[0] == "iron_bars" or b[0].endswith("_wall"):
                return True
            return sturdy(b[0], b[1], OPP[d])

        def conn_wall(p, d):
            q = add(p, d)
            b = g.get(q)
            if not b:
                return False
            if b[0].endswith("_wall") or b[0].endswith("glass_pane") or b[0] == "iron_bars":
                return True
            return gate_connects(q, d) or sturdy(b[0], b[1], OPP[d])

        for p, (n, pr) in sorted(g.items(), key=lambda kv: -kv[0][1]):
            if n.endswith("_fence"):
                put(p, **{d: conn_fence(p, d) for d in DIRS})
            elif n.endswith("glass_pane") or n == "iron_bars":
                put(p, **{d: conn_pane(p, d) for d in DIRS})
            elif n.endswith("_fence_gate"):
                f = pr["facing"]
                iw = any(g.get(add(p, s), ("", {}))[0].endswith("_wall") for s in (CW[f], CCW[f]))
                put(p, in_wall=iw)
            elif n.endswith("_wall"):
                above = g.get((p[0], p[1] + 1, p[2]))
                sides = {}
                for d in DIRS:
                    if conn_wall(p, d):
                        tall = False
                        if above:
                            if above[0].endswith("_wall") and conn_wall((p[0], p[1] + 1, p[2]), d):
                                tall = True
                            elif is_full(above[0], above[1]):
                                tall = True
                        sides[d] = "tall" if tall else "low"
                    else:
                        sides[d] = "none"
                conn = [d for d in DIRS if sides[d] != "none"]
                straight = (set(conn) == {"north", "south"} and sides["north"] == sides["south"]) or \
                           (set(conn) == {"east", "west"} and sides["east"] == sides["west"])
                if above and above[0].endswith("_wall"):
                    up = out[(p[0], p[1] + 1, p[2])][1].get("up", "true") == "true" or not straight
                else:
                    up = (not straight) or bool(above)
                put(p, up=up, **sides)
        for p in list(out):
            n, pr = out[p]
            out[p] = (n, {**schema(n), **pr})
        self.out = out
        self._check_support(out)
        return out

    # ---- survival sanity checks
    def _check_support(self, out):
        def nm(p):
            b = out.get(p)
            return b[0] if b else "air"

        def bad(p, msg):
            raise ValueError(f"{self.name}: {nm(p)} at {p}: {msg}")

        for p, (n, pr) in out.items():
            below = (p[0], p[1] - 1, p[2])
            if n == "farmland":
                pass
            elif n in ("wheat", "carrots", "potatoes", "beetroots", "melon_stem", "pumpkin_stem",
                       "attached_melon_stem", "attached_pumpkin_stem"):
                if nm(below) != "farmland":
                    bad(p, "crop needs farmland")
            elif n == "sugar_cane":
                if nm(below) != "sugar_cane":
                    if nm(below) not in CANE_SOIL:
                        bad(p, "cane needs sand/dirt")
                    if not any(nm(add(below, d)) == "water" for d in DIRS):
                        bad(p, "cane base needs adjacent water")
            elif n in TALL_PLANTS:
                if pr["half"] == "lower" and nm(below) not in SOIL:
                    bad(p, "tall plant needs soil")
                if pr["half"] == "upper" and nm(below) != n:
                    bad(p, "upper half without lower")
            elif PLANTS.search(n) and not n.startswith("potted_"):
                if nm(below) not in SOIL:
                    bad(p, "plant needs soil")
            elif n.endswith("_door"):
                if pr["half"] == "lower" and nm(below) in LIQUID_OR_AIR:
                    bad(p, "door floating")
                if pr["half"] == "upper" and nm(below) != n:
                    bad(p, "upper door half without lower")
            elif n in ("torch", "soul_torch"):
                if not (self._o_full(out, below) or nm(below).endswith("_fence")):
                    bad(p, "torch floating")
            elif n in ("wall_torch", "soul_wall_torch", "ladder"):
                back = add(p, OPP[pr["facing"]])
                if not self._o_full(out, back):
                    bad(p, "needs solid block behind")
            elif n in ("lantern", "soul_lantern"):
                if pr["hanging"] == "true":
                    a = (p[0], p[1] + 1, p[2])
                    if nm(a) == "air":
                        bad(p, "hanging lantern without anchor")
                elif nm(below) == "air":
                    bad(p, "lantern floating")
            elif n == "vine":
                a = (p[0], p[1] + 1, p[2])
                ok = nm(a) == "vine" or (pr["up"] == "true" and self._o_full(out, a))
                for d in DIRS:
                    if pr[d] == "true" and self._o_full(out, add(p, d)):
                        ok = True
                if not ok:
                    bad(p, "vine unattached")
            elif n.endswith("_bed"):
                if pr["part"] == "foot":
                    h = add(p, pr["facing"])
                    if nm(h) != n or out[h][1]["part"] != "head":
                        bad(p, "bed without head")
            elif n == "amethyst_cluster" or n.endswith("_amethyst_bud"):
                f = pr["facing"]
                dv = {"up": (0, 1, 0), "down": (0, -1, 0)}.get(f) or DIRS[f]
                base = (p[0] - dv[0], p[1] - dv[1], p[2] - dv[2])
                if nm(base) not in ("amethyst_block", "budding_amethyst"):
                    bad(p, "crystal not attached to amethyst")
            elif n in ("candle",) and nm(below) == "air":
                bad(p, "candle floating")

    @staticmethod
    def _o_full(out, p):
        b = out.get(p)
        return bool(b) and is_full(b[0], b[1])

    # ---- export
    def export(self):
        out = self.finalize()
        xs = [p[0] for p in out]; ys = [p[1] for p in out]; zs = [p[2] for p in out]
        x0, y0, z0 = min(xs), min(ys), min(zs)
        W, H, L = max(xs) - x0 + 1, max(ys) - y0 + 1, max(zs) - z0 + 1
        pal = {"minecraft:air": 0}
        idx = [0] * (W * H * L)
        grid = {}
        for p in sorted(out, key=lambda q: (q[1], q[2], q[0])):
            n, pr = out[p]
            key = state_str(n, pr)
            if key not in pal:
                pal[key] = len(pal)
            x, y, z = p[0] - x0, p[1] - y0, p[2] - z0
            idx[x + z * W + y * W * L] = pal[key]
            grid[(x, y, z)] = key
        return {"size": (W, H, L), "palette": pal, "indices": idx, "grid": grid}


def state_str(name, props):
    full = dict(schema(name))
    full.update(props)
    if not full:
        return f"minecraft:{name}"
    return f"minecraft:{name}[" + ",".join(f"{k}={full[k]}" for k in sorted(full)) + "]"


def varints(values):
    out = bytearray()
    for v in values:
        while True:
            b = v & 0x7F
            v >>= 7
            if v:
                out.append(b | 0x80)
            else:
                out.append(b)
                break
    return bytes(out)


# --------------------------------------------------------------------------- shared shapes
def gable(b, x0, x1, z0, z1, yb, mat, axis="x", ov=1, ovx=1, fill=None, fill_gable=True, ridge=None):
    """Stair gable roof over footprint [x0..x1]x[z0..z1].

    yb = y of the first stair row directly above the wall tops. Ridge runs along
    `axis`. ov = eave overhang across the slope, ovx = overhang past the gable ends.
    fill = (blockname, props) used for the gable-end triangles.
    Odd spans get a full block ridge; even spans end with two facing stairs.
    """
    if axis == "x":
        u0, u1, v0, v1 = x0, x1, z0, z1
        fa, fb = "south", "north"  # facing of min-side / max-side stairs

        def P(u, v, y): return (u, y, v)
    else:
        u0, u1, v0, v1 = z0, z1, x0, x1
        fa, fb = "east", "west"

        def P(u, v, y): return (v, y, u)
    fname, fprops = fill if fill else (f"{mat}_planks", {})
    rb = ridge or f"{mat}_planks"
    k = 0
    while v0 + k <= v1 - k:
        vn, vs = v0 + k, v1 - k
        y = yb + k
        for u in range(u0 - ovx, u1 + ovx + 1):
            if vn == vs:
                b.set(*P(u, vn, y - 1), rb)
            else:
                b.stairs(*P(u, vn, y), mat, fa)
                b.stairs(*P(u, vs, y), mat, fb)
        if vn + 1 == vs - 1:  # odd span: ridge block at same level as top stairs
            for u in range(u0 - ovx, u1 + ovx + 1):
                b.set(*P(u, vn + 1, y), rb)
        if fill_gable:
            for u in (u0, u1):
                for v in range(vn + 1, vs):
                    b.set(*P(u, v, y), fname, **fprops)
        k += 1
    if ov:
        for u in range(u0 - ovx, u1 + ovx + 1):
            b.stairs(*P(u, v0 - 1, yb - 1), mat, fa)
            b.stairs(*P(u, v1 + 1, yb - 1), mat, fb)


def hip(b, x0, x1, z0, z1, y, mat, cap="slab"):
    """Pyramid/hip roof of stair rings. Outer corners get their shape automatically."""
    while True:
        if x1 - x0 < 2 or z1 - z0 < 2:
            for x in range(x0, x1 + 1):
                for z in range(z0, z1 + 1):
                    if cap == "slab":
                        b.slab(x, y, z, mat)
                    else:
                        b.set(x, y, z, f"{mat}_planks")
            return
        for x in range(x0, x1 + 1):
            b.stairs(x, y, z0, mat, "south")
            b.stairs(x, y, z1, mat, "north")
        for z in range(z0 + 1, z1):
            b.stairs(x0, y, z, mat, "east")
            b.stairs(x1, y, z, mat, "west")
        x0 += 1; x1 -= 1; z0 += 1; z1 -= 1; y += 1


# --------------------------------------------------------------------------- registry
REGISTRY = []


def register(category, id, ru, en, desc_ru, desc_en, difficulty, tags):
    def deco(fn):
        REGISTRY.append({"category": category, "id": id, "name": {"ru": ru, "en": en},
                         "description": {"ru": desc_ru, "en": desc_en}, "difficulty": difficulty,
                         "tags": tags, "fn": fn})
        return fn
    return deco
