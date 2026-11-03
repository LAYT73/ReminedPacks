# Remined schematic catalog

Starter library of original `.schem` files (Sponge v3, Minecraft 26.2, DataVersion 4903) for the
launcher's built-in schematic catalog. Everything is built block by block from Python and uses
vanilla blocks only, so the builds can be recreated in survival.

```
schematics/
  catalog.json          index the launcher downloads
  <category>/<id>.schem  houses/ farms/ mini/ portals/ decor/
  thumbs/<id>.png        128 px top-down previews (fallback thumbnails)
  tools/                 generator (nbt.py, dsl.py, build_*.py, build_all.py, thumbs.py, schem_read.py)
```

## Rebuild

```
python3 tools/build_all.py            # writes every .schem, thumbs and catalog.json
python3 tools/build_all.py --map oak-starter-cabin   # also prints an ASCII top-down map
python3 tools/build_all.py --jar /path/to/VanillaPro.jar --no-thumbs
```

Pure standard library. The game jar (default `../../../../packs/vanillapro/VanillaPro.jar` relative to
`tools/`, or `$REMINED_JAR`) is used as ground truth, and the build **fails** if:

- a palette entry is not a valid state of its block: unsorted properties, a missing property, a value
  outside the variant keys / multipart conditions of `assets/minecraft/blockstates/<name>.json`, or a
  property set that differs from the one the game's own structure files use for that block;
- an output file does not decode (with the independent reader in `tools/schem_read.py`) to exactly the
  same size, palette and every block the generator placed;
- a bed has no head, a door is missing a half, a double chest is mismatched, or a portal has no valid
  4x5 obsidian frame.

## Conventions

- Axes: x east, y up, z south. Index = `x + z*Width + y*Width*Length`. `Offset` is `[0,0,0]`.
- Layer `y = 0` is the ground/foundation layer: paste it so it replaces the ground surface. Water is
  placed on top of a solid block wherever the build allows it; pasting on solid ground is assumed.
- Neighbour-dependent properties are computed like the game does: fence/pane/bar/wall connections,
  wall post/height, stair shape (straight/inner/outer), fence gate `in_wall`, leaf `distance`
  (leaves are always `persistent=true`), double chest `type`, doors and beds (both halves),
  tall plants (`half=lower/upper`). The builder also refuses floating torches, ladders, unsupported
  crops, canes without water, unattached vines and crystals.
- No block entities or entities are stored (chests/furnaces/beds are placed empty).

## Catalog entry

```json
{
  "id": "oak-starter-cabin",
  "category": "houses",
  "name": {"ru": "...", "en": "..."},
  "description": {"ru": "...", "en": "..."},
  "file": "houses/oak-starter-cabin.schem",
  "thumb": "thumbs/oak-starter-cabin.png",
  "format": "schem",
  "sha256": "<hex of the file bytes>",
  "bytes": 1234,
  "size": [9, 7, 8],
  "blockCount": 214,
  "mcVersion": "26.2",
  "difficulty": "easy",
  "tags": ["oak", "starter"],
  "author": "Remined",
  "license": "CC0-1.0",
  "sourceUrl": null
}
```

`size` is `[width, height, length]` (x, y, z), `blockCount` counts non-air blocks, `difficulty` is
`easy`, `medium` or `hard`, `thumb` is optional.

## Adding a build of your own

1. Pick the category module in `tools/builds_<category>.py` (or add a new one and import it in
   `build_all.py`).
2. Add a function decorated with `@register(category, id, ru_name, en_name, ru_description,
   en_description, difficulty, tags)` that returns a `Build`. Use `b.set`, `b.fill`, `b.shell`,
   `b.stairs`, `b.door`, `b.bed`, `b.double_chest`, `b.tall`, `gable()` and `hip()`; never write
   connection properties by hand.
3. Run `python3 tools/build_all.py`. Fix anything the validator reports, then commit the new
   `.schem`, thumbnail and `catalog.json`.

New block with properties? Add its full property set to `RULES` in `tools/dsl.py` first. The validator
then checks it against the jar.

## Adding a third-party schematic

Drop an existing file into `<category>/` and add a hand-written item to `catalog.json` (the generator
rewrites `catalog.json` from scratch, so keep third-party items in a `tools/extra_items.json` list of
item objects; `build_all.py` appends it when the file exists). Required, in addition to the fields above:

- `author`: the original author's name or handle;
- `license`: an SPDX id (`CC0-1.0`, `CC-BY-4.0`, `MIT`, ...). Do not add anything without a license
  that allows redistribution;
- `sourceUrl`: where the file came from, e.g. the original post or repository;
- `sha256` and `bytes` of the exact file you ship, `size`/`blockCount` as above.

Compute them with `shasum -a 256 file.schem`, `wc -c file.schem`. Only `.schem` (Sponge v2/v3) is
published here; convert `.litematic` or `.schematic` files first, and run
`tools/schem_read.py`'s decoder over the result to make sure it opens.

## Thumbnails

`thumbs/<id>.png` are 480×300 isometric renders made with the launcher's own block renderer, so they match what players see in the Schematics tab. `build_all.py` keeps existing thumbnails and writes a flat top-down placeholder only for new entries that have none (`--flat-thumbs` overwrites all of them with flat renders).
