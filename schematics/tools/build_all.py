#!/usr/bin/env python3
"""Builds every schematic (.schem, Sponge v3), validates blockstates against the game jar,
round-trips each file through an independent reader, renders thumbnails and writes catalog.json.

    python3 tools/build_all.py [--jar path/to/VanillaPro.jar] [--no-thumbs]
"""
import argparse
import datetime
import gzip
import hashlib
import json
import os
import re
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import nbt  # noqa: E402
import dsl  # noqa: E402
from dsl import REGISTRY, domain_ok, schema, state_str, varints  # noqa: E402
import schem_read  # noqa: E402
import thumbs  # noqa: E402
import builds_houses, builds_farms, builds_mini, builds_portals, builds_decor  # noqa: E402,F401

ROOT = os.path.dirname(HERE)
DEFAULT_JAR = os.path.normpath(os.path.join(ROOT, "..", "..", "..", "packs", "vanillapro", "VanillaPro.jar"))
MC_VERSION = "26.2"
BASE_URL = "https://raw.githubusercontent.com/LAYT73/ReminedPacks/main/schematics/"
CATEGORIES = [
    {"id": "houses", "name": {"ru": "Дома", "en": "Houses"}},
    {"id": "farms", "name": {"ru": "Фермы", "en": "Farms"}},
    {"id": "mini", "name": {"ru": "Мини-постройки", "en": "Mini builds"}},
    {"id": "portals", "name": {"ru": "Порталы", "en": "Portals"}},
    {"id": "decor", "name": {"ru": "Декор и природа", "en": "Decor & nature"}},
]
MAX_DIM = 32


# --------------------------------------------------------------------------- reference data from the jar
class Ref:
    def __init__(self, jar):
        self.zf = zipfile.ZipFile(jar)
        self.blockstates = {}
        for n in self.zf.namelist():
            if n.startswith("assets/minecraft/blockstates/") and n.endswith(".json"):
                self.blockstates[os.path.basename(n)[:-5]] = json.loads(self.zf.read(n))
        # ground truth: full property-name sets used by the game's own structure files
        self.props = {}
        for n in self.zf.namelist():
            if n.startswith("data/minecraft/structure/") and n.endswith(".nbt"):
                try:
                    root = schem_read.read_nbt(gzip.decompress(self.zf.read(n)))
                except Exception:
                    continue
                pals = [root["palette"]] if "palette" in root else root.get("palettes", [])
                for pal in pals:
                    for e in pal:
                        name = e["Name"].split(":", 1)[1]
                        self.props.setdefault(name, set()).update(e.get("Properties", {}).keys())
        try:
            self.data_version = json.loads(self.zf.read("version.json"))["world_version"]
        except Exception:
            self.data_version = 4903


def parse_state(s):
    m = re.fullmatch(r"minecraft:([a-z0-9_]+)(?:\[(.*)\])?", s)
    if not m:
        raise ValueError(f"malformed state {s!r}")
    props = []
    if m.group(2):
        for kv in m.group(2).split(","):
            k, v = kv.split("=")
            props.append((k, v))
    return m.group(1), props


def _when_props(cond, acc):
    if isinstance(cond, dict):
        for k, v in cond.items():
            if k in ("OR", "AND"):
                for c in v:
                    _when_props(c, acc)
            else:
                acc.setdefault(k, set()).update(str(v).split("|"))


def validate_state(s, ref):
    """Raise ValueError if the canonical state string is not a valid state of the jar's block."""
    name, kv = parse_state(s)
    keys = [k for k, _ in kv]
    if keys != sorted(keys):
        raise ValueError(f"{s}: properties not sorted")
    props = dict(kv)
    if len(props) != len(kv):
        raise ValueError(f"{s}: duplicate property")
    if name == "air":
        if props:
            raise ValueError(s)
        return
    if name not in ref.blockstates:
        raise ValueError(f"{s}: no blockstate file for {name}")
    # full property set: ground truth from structure files, else the DSL schema
    expected = ref.props.get(name)
    if expected is None:
        expected = set(schema(name))
    if set(props) != expected:
        raise ValueError(f"{s}: property set {sorted(props)} != expected {sorted(expected)}")
    if set(props) != set(schema(name)):
        raise ValueError(f"{s}: DSL schema disagrees: {sorted(schema(name))}")
    for k, v in props.items():
        if not domain_ok(k, v, name):
            raise ValueError(f"{s}: bad value for {k}")
    if name.endswith("_leaves") and props["persistent"] != "true":
        raise ValueError(f"{s}: leaves must be persistent")
    bs = ref.blockstates[name]
    if "variants" in bs:
        variants = bs["variants"]
        parsed = []
        for vk in variants:
            parsed.append(dict(p.split("=") for p in vk.split(",")) if vk else {})
        if not parsed or all(not p for p in parsed):
            return  # single model; properties don't affect it
        vnames = set(parsed[0])
        for p in parsed:
            if set(p) != vnames:
                raise ValueError(f"{name}: inconsistent variant keys")
        if not vnames <= set(props):
            raise ValueError(f"{s}: missing variant properties {sorted(vnames - set(props))}")
        sub = {k: props[k] for k in vnames}
        if sub not in parsed:
            raise ValueError(f"{s}: no variant matches {sub}")
    elif "multipart" in bs:
        seen = {}
        for part in bs["multipart"]:
            if "when" in part:
                _when_props(part["when"], seen)
        for k, vals in seen.items():
            if k not in props:
                raise ValueError(f"{s}: multipart property {k} missing")
            v = props[k]
            # a value no part selects on is only fine as the implicit base case
            # ("false"/"none", or a number below every number the parts use, e.g. level=0, flower_amount=1)
            base_ok = v in ("false", "none") or (
                v.isdigit() and all(x.isdigit() for x in vals) and int(v) < min(int(x) for x in vals))
            if v not in vals and not base_ok:
                raise ValueError(f"{s}: value {k}={v} never used by multipart of {name}")
    else:
        raise ValueError(f"{name}: unknown blockstate format")


# --------------------------------------------------------------------------- writing
def schem_bytes(entry, built, data_version):
    W, H, L = built["size"]
    pal = nbt.compound({k: nbt.int_(v) for k, v in built["palette"].items()})
    root = nbt.compound({"Schematic": nbt.compound({
        "Version": nbt.int_(3),
        "DataVersion": nbt.int_(data_version),
        "Width": nbt.short(W), "Height": nbt.short(H), "Length": nbt.short(L),
        "Offset": nbt.int_array([0, 0, 0]),
        "Metadata": nbt.compound({"Name": nbt.string(entry["name"]["en"]), "Author": nbt.string("Remined")}),
        "Blocks": nbt.compound({
            "Palette": pal,
            "Data": nbt.byte_array(varints(built["indices"])),
            "BlockEntities": nbt.list_(nbt.COMPOUND, []),
        }),
    })})
    return nbt.dumps("", root)


def verify_roundtrip(path, built):
    dec = schem_read.decode_schem(path)
    assert dec["size"] == built["size"], (dec["size"], built["size"])
    assert dec["offset"] == [0, 0, 0]
    assert dict(dec["palette"]) == built["palette"], "palette mismatch"
    W, H, L = built["size"]
    nonair = 0
    for y in range(H):
        for z in range(L):
            for x in range(W):
                got = dec["at"](x, y, z)
                want = built["grid"].get((x, y, z), "minecraft:air")
                if got != want:
                    raise AssertionError(f"{path}: ({x},{y},{z}) {got} != {want}")
                if got != "minecraft:air":
                    nonair += 1
    return nonair


def spot_checks(entry_id, path):
    """A few semantic spot checks on the decoded file (independent of the builder)."""
    dec = schem_read.decode_schem(path)
    W, H, L = dec["size"]
    cells = [(x, y, z) for y in range(H) for z in range(L) for x in range(W)]
    states = [dec["at"](*c) for c in cells]
    count = lambda pre: sum(1 for s in states if s.startswith(pre))
    # every bed has a head and a foot, doors come in pairs
    assert count("minecraft:") > 0
    for color in ("red", "blue", "white", "light_blue", "orange"):
        f = sum(1 for s in states if s.startswith(f"minecraft:{color}_bed[") and "part=foot" in s)
        h = sum(1 for s in states if s.startswith(f"minecraft:{color}_bed[") and "part=head" in s)
        assert f == h, (entry_id, color, f, h)
    lo = sum(1 for s in states if "_door[" in s and "half=lower" in s)
    up = sum(1 for s in states if "_door[" in s and "half=upper" in s)
    assert lo == up, (entry_id, "doors", lo, up)
    chl = sum(1 for s in states if s.startswith("minecraft:chest[") and "type=left" in s)
    chr_ = sum(1 for s in states if s.startswith("minecraft:chest[") and "type=right" in s)
    assert chl == chr_, (entry_id, "double chests")
    # double chest geometry: left half sits at CW(facing)-opposite side
    for (x, y, z), s in zip(cells, states):
        if s.startswith("minecraft:chest[") and "type=left" in s:
            f = re.search(r"facing=(\w+)", s).group(1)
            ox, oz = {"south": (-1, 0), "north": (1, 0), "east": (0, -1), "west": (0, 1)}[f]  # towards the right half
            r = dec["at"](x + ox, y, z + oz)
            assert r.startswith("minecraft:chest[") and "type=right" in r and f"facing={f}" in r, (entry_id, x, y, z, r)
    for s in set(states):
        if "_leaves[" in s:
            assert "persistent=true" in s


def check_portal(eid, path):
    """A lightable nether portal needs obsidian on the 14 non-corner frame blocks around a 2x3 hole."""
    dec = schem_read.decode_schem(path)
    W, H, L = dec["size"]
    OB, OK_INNER = "minecraft:obsidian", ("minecraft:air", "minecraft:nether_portal[axis=x]", "minecraft:nether_portal[axis=z]")
    found = 0
    for axis in ("x", "z"):
        for y0 in range(H - 4):
            for a in range((W if axis == "x" else L) - 3):
                for c in range(L if axis == "x" else W):
                    def at(i, j):  # i along the frame, j up
                        x, z = (a + i, c) if axis == "x" else (c, a + i)
                        return dec["at"](x, y0 + j, z)
                    ok = all(at(i, j) == OB for i in (1, 2) for j in (0, 4)) and \
                        all(at(i, j) == OB for i in (0, 3) for j in (1, 2, 3)) and \
                        all(at(i, j) in OK_INNER for i in (1, 2) for j in (1, 2, 3))
                    found += ok
    assert found >= 1, f"{eid}: no valid 4x5 portal frame"
    return found


def ascii_top(built, legend_cap=14):
    W, H, L = built["size"]
    top = {}
    for (x, y, z), s in built["grid"].items():
        if (x, z) not in top or y > top[(x, z)][0]:
            top[(x, z)] = (y, s)
    sym, lines = {}, []
    pool = iter("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    for z in range(L):
        row = ""
        for x in range(W):
            if (x, z) not in top:
                row += "."
                continue
            n = top[(x, z)][1].split("[")[0][10:]
            if n not in sym:
                sym[n] = next(pool)
            row += sym[n]
        lines.append(row)
    return "\n".join(lines), sym


# --------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jar", default=os.environ.get("REMINED_JAR", DEFAULT_JAR))
    ap.add_argument("--no-thumbs", action="store_true")
    ap.add_argument("--flat-thumbs", action="store_true", help="overwrite thumbs/ with flat top-down renders")
    ap.add_argument("--map", action="append", default=[], help="print an ASCII top-down map for this id")
    args = ap.parse_args()

    if not os.path.isfile(args.jar):
        sys.exit(f"jar not found: {args.jar} (pass --jar or set REMINED_JAR)")
    ref = Ref(args.jar)
    print(f"jar: {args.jar}  DataVersion {ref.data_version}  blockstates {len(ref.blockstates)}  "
          f"structure-known blocks {len(ref.props)}")

    pal_tex = thumbs.Palette(ref.zf) if not args.no_thumbs else None
    items, ids, avoided_unused = [], set(), set()
    all_states = set()
    for entry in REGISTRY:
        eid = entry["id"]
        assert eid not in ids, f"duplicate id {eid}"
        ids.add(eid)
        built = entry["fn"]().export()
        W, H, L = built["size"]
        assert max(W, H, L) <= MAX_DIM, (eid, built["size"])
        for st in built["palette"]:
            try:
                validate_state(st, ref)
            except ValueError as e:
                sys.exit(f"INVALID BLOCKSTATE in {eid}: {e}")
            all_states.add(st)
        rel = f"{entry['category']}/{eid}.schem"
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = schem_bytes(entry, built, ref.data_version)
        with open(path, "wb") as fh:
            fh.write(data)
        nonair = verify_roundtrip(path, built)
        spot_checks(eid, path)
        if entry["category"] == "portals":
            check_portal(eid, path)
        item = {
            "id": eid, "category": entry["category"], "name": entry["name"], "description": entry["description"],
            "file": rel, "format": "schem", "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "size": [W, H, L], "blockCount": nonair, "mcVersion": MC_VERSION, "difficulty": entry["difficulty"],
            "tags": entry["tags"], "author": "Remined", "license": "CC0-1.0", "sourceUrl": None,
        }
        thumb_path = os.path.join(ROOT, "thumbs", f"{eid}.png")
        # thumbs/ holds the 3D renders made with the launcher's own renderer (see README). The flat
        # top-down render here is only a placeholder for new entries that have no 3D thumb yet.
        if pal_tex and (args.flat_thumbs or not os.path.exists(thumb_path)):
            os.makedirs(os.path.join(ROOT, "thumbs"), exist_ok=True)
            with open(thumb_path, "wb") as fh:
                fh.write(thumbs.render(built["grid"], built["size"], pal_tex))
        if os.path.exists(thumb_path):
            item["thumb"] = f"thumbs/{eid}.png"
        items.append(item)
        print(f"ok  {entry['category']:8s} {eid:28s} {W:2d}x{H:2d}x{L:2d}  blocks={nonair:5d}  palette={len(built['palette'])}")
        if eid in args.map:
            m, sym = ascii_top(built)
            print(m); print(sym)

    extra = os.path.join(HERE, "extra_items.json")
    if os.path.isfile(extra):  # hand-written third-party entries (author/license/sourceUrl required)
        for it in json.load(open(extra, encoding="utf-8")):
            for k in ("author", "license", "sourceUrl", "sha256", "bytes", "file"):
                assert k in it, f"extra item {it.get('id')}: missing {k}"
            data = open(os.path.join(ROOT, it["file"]), "rb").read()
            assert hashlib.sha256(data).hexdigest() == it["sha256"] and len(data) == it["bytes"], it["id"]
            assert it["id"] not in ids, f"duplicate id {it['id']}"
            ids.add(it["id"])
            items.append(it)
    cats_used = {i["category"] for i in items}
    assert cats_used <= {c["id"] for c in CATEGORIES}
    catalog = {
        "version": 1,
        "updatedAt": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "baseUrl": BASE_URL,
        "categories": CATEGORIES,
        "items": items,
    }
    with open(os.path.join(ROOT, "catalog.json"), "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    # re-check catalog integrity from disk
    for it in items:
        b = open(os.path.join(ROOT, it["file"]), "rb").read()
        assert hashlib.sha256(b).hexdigest() == it["sha256"] and len(b) == it["bytes"]
    print(f"\n{len(items)} schematics, {len(all_states)} distinct validated blockstates -> catalog.json written")


if __name__ == "__main__":
    main()
