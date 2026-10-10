import gzip, struct
MAX_DEPTH = 128          # real NBT is far shallower; stops "depth bomb" files


def read_nbt(raw):
    pos = 0
    depth = 0
    def u(fmt, n):
        nonlocal pos
        v = struct.unpack_from(">" + fmt, raw, pos)[0]; pos += n; return v
    def string():
        nonlocal pos
        l = u("H", 2); s = raw[pos:pos+l].decode("utf-8", "replace"); pos += l; return s
    def payload(t):
        nonlocal pos, depth
        depth += 1
        if depth > MAX_DEPTH:
            raise ValueError("NBT nested too deeply")
        try:
            return _payload(t)
        finally:
            depth -= 1

    def _payload(t):
        nonlocal pos
        if t == 1: return u("b", 1)
        if t == 2: return u("h", 2)
        if t == 3: return u("i", 4)
        if t == 4: return u("q", 8)
        if t == 5: return u("f", 4)
        if t == 6: return u("d", 8)
        if t == 7:
            n = u("i", 4); v = raw[pos:pos+n]; pos += n; return list(v)
        if t == 8: return string()
        if t == 9:
            it = u("b", 1); n = u("i", 4)
            if n < 0 or n > len(raw) - pos:                           # a list cannot have more items than bytes left
                raise ValueError("bad NBT list length")
            return [payload(it) for _ in range(n)]
        if t == 10:
            d = {}
            while True:
                tt = u("b", 1)
                if tt == 0: return d
                k = string(); d[k] = payload(tt)
        if t == 11:
            n = u("i", 4); v = struct.unpack_from(">%di" % n, raw, pos); pos += 4*n; return list(v)
        if t == 12:
            n = u("i", 4); v = struct.unpack_from(">%dq" % n, raw, pos); pos += 8*n; return list(v)
        raise ValueError("tag %d" % t)
    t = u("b", 1); string()
    return payload(t)
def read_gz(path):
    return read_nbt(gzip.open(path, "rb").read())
