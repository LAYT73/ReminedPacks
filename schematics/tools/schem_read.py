"""Independent .schem (Sponge v2/v3) reader used for round-trip verification."""
import gzip
import struct


def read_nbt(raw):
    p = [0]

    def u(fmt, n):
        v = struct.unpack_from(fmt, raw, p[0]); p[0] += n; return v[0]

    def s():
        n = u(">H", 2); r = raw[p[0]:p[0] + n].decode("utf-8"); p[0] += n; return r

    def pay(k):
        if k == 1: return u(">b", 1)
        if k == 2: return u(">h", 2)
        if k == 3: return u(">i", 4)
        if k == 4: return u(">q", 8)
        if k == 5: return u(">f", 4)
        if k == 6: return u(">d", 8)
        if k == 7:
            n = u(">i", 4); r = raw[p[0]:p[0] + n]; p[0] += n; return r
        if k == 8: return s()
        if k == 9:
            ik = u(">b", 1); n = u(">i", 4); return [pay(ik) for _ in range(n)]
        if k == 10:
            d = {}
            while True:
                t = u(">b", 1)
                if t == 0: return d
                nm = s(); d[nm] = pay(t)
        if k == 11:
            n = u(">i", 4); return [u(">i", 4) for _ in range(n)]
        if k == 12:
            n = u(">i", 4); return [u(">q", 8) for _ in range(n)]
        raise ValueError(k)

    t = u(">b", 1); s()
    return pay(t)


def decode_schem(path):
    root = read_nbt(gzip.open(path).read())
    sc = root["Schematic"]
    assert sc["Version"] == 3, "not Sponge v3"
    W, H, L = sc["Width"], sc["Height"], sc["Length"]
    pal = {v: k for k, v in sc["Blocks"]["Palette"].items()}
    data = sc["Blocks"]["Data"]
    vals, cur, shift = [], 0, 0
    for byte in data:
        cur |= (byte & 0x7F) << shift
        if byte & 0x80:
            shift += 7
        else:
            vals.append(cur); cur = 0; shift = 0
    assert len(vals) == W * H * L, (len(vals), W * H * L)
    def at(x, y, z): return pal[vals[x + z * W + y * W * L]]
    return {"size": (W, H, L), "palette": sc["Blocks"]["Palette"], "data_version": sc["DataVersion"],
            "offset": sc["Offset"], "at": at, "values": vals, "palette_inv": pal}
