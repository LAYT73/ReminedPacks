"""Minimal gzip NBT writer (big-endian, Java edition)."""
import gzip
import struct

END, BYTE, SHORT, INT, LONG, FLOAT, DOUBLE, BYTE_ARRAY, STRING, LIST, COMPOUND, INT_ARRAY = range(12)


class Tag:
    def __init__(self, kind, value, item_kind=None):
        self.kind, self.value, self.item_kind = kind, value, item_kind


def byte(v): return Tag(BYTE, v)
def short(v): return Tag(SHORT, v)
def int_(v): return Tag(INT, v)
def string(v): return Tag(STRING, v)
def byte_array(v): return Tag(BYTE_ARRAY, bytes(v))
def int_array(v): return Tag(INT_ARRAY, list(v))
def compound(d): return Tag(COMPOUND, d)
def list_(item_kind, items): return Tag(LIST, list(items), item_kind)


def _str(s):
    b = s.encode("utf-8")
    return struct.pack(">H", len(b)) + b


def _payload(t):
    k, v = t.kind, t.value
    if k == BYTE: return struct.pack(">b", v)
    if k == SHORT: return struct.pack(">h", v)
    if k == INT: return struct.pack(">i", v)
    if k == STRING: return _str(v)
    if k == BYTE_ARRAY: return struct.pack(">i", len(v)) + v
    if k == INT_ARRAY: return struct.pack(">i", len(v)) + b"".join(struct.pack(">i", x) for x in v)
    if k == LIST:
        ik = t.item_kind if v else END
        return struct.pack(">bi", ik, len(v)) + b"".join(_payload(x) for x in v)
    if k == COMPOUND:
        out = b""
        for name, child in v.items():
            out += struct.pack(">b", child.kind) + _str(name) + _payload(child)
        return out + b"\x00"
    raise ValueError(k)


def dumps(root_name, root):
    """Serialize and gzip a named root compound."""
    raw = struct.pack(">b", root.kind) + _str(root_name) + _payload(root)
    # mtime=0 keeps output byte-for-byte reproducible
    return gzip.compress(raw, 9, mtime=0)
