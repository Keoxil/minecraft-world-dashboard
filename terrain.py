"""Terreno real del Overworld: 4 muestras por chunk (superficie), cacheado por región."""
import json, os, struct, sys, zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt_mini

# clase -> color (para la página); la primera regla que coincide gana
CLASSES = {
    "w": "#2f5f9a",  # agua
    "i": "#a9cfe8",  # hielo
    "n": "#eef4f8",  # nieve
    "s": "#d9c98b",  # arena
    "r": "#b8683e",  # arena roja / terracota
    "g": "#5f8f45",  # hierba
    "l": "#3f6b35",  # hojas
    "t": "#6b4e2e",  # troncos / madera
    "d": "#8b6a46",  # tierra
    "m": "#5b4a3f",  # barro / podzol
    "k": "#7d8084",  # piedra
    "p": "#4a4d55",  # deepslate / basalto
    "v": "#8a8782",  # grava
    "c": "#9a6fb0",  # micelio / cerezo
    "o": "#e0561f",  # lava / magma
    "x": "#6d7177",  # otros
    "N": "#7a2f2f",  # netherrack
    "R": "#a3282e",  # carmesí
    "W": "#1f8a8a",  # distorsionado
    "S": "#6b5240",  # arena de almas
    "B": "#3d3d45",  # basalto / piedra negra
    "G": "#e8c35a",  # piedra luminosa
    "Q": "#e8e0d4",  # cuarzo
}
RULES = [
    ("G", ("glowstone", "shroomlight")),
    ("W", ("warped",)),
    ("R", ("crimson", "nether_wart_block", "weeping")),
    ("S", ("soul_sand", "soul_soil")),
    ("B", ("basalt", "blackstone")),
    ("Q", ("quartz",)),
    ("N", ("netherrack", "nether_gold", "nether_brick")),
    ("w", ("water", "kelp", "seagrass", "bubble_column")),
    ("i", ("ice",)),
    ("n", ("snow", "powder_snow")),
    ("o", ("lava", "magma")),
    ("s", ("sand", "sandstone", "suspicious_sand")),
    ("r", ("red_sand", "terracotta", "red_sandstone")),
    ("m", ("mud", "podzol", "mangrove_roots", "muddy")),
    ("c", ("mycelium", "cherry")),
    ("l", ("leaves", "azalea", "moss", "vine")),
    ("t", ("log", "wood", "planks", "stem")),
    ("g", ("grass", "fern", "flower", "bush", "farmland", "tall", "pumpkin", "melon", "hay")),
    ("d", ("dirt", "path", "coarse", "rooted", "clay")),
    ("v", ("gravel",)),
    ("p", ("deepslate", "basalt", "blackstone", "tuff", "bedrock", "obsidian")),
    ("k", ("stone", "andesite", "granite", "diorite", "calcite", "ore", "cobble", "dripstone", "brick")),
]
BIOME_CLASSES = {
    "a": ("Llanura", "#8db360"), "b": ("Bosque", "#4f7a3a"), "c": ("Bosque oscuro", "#34522b"), "d": ("Abedular", "#7da660"),
    "e": ("Taiga", "#3f6f55"), "f": ("Nevado", "#dfe9ee"), "g": ("Desierto", "#e0cd8b"), "h": ("Badlands", "#c0693c"),
    "i": ("Sabana", "#b8a64a"), "j": ("Jungla", "#2f8a2f"), "k": ("Pantano", "#4a6b4a"), "l": ("Montaña", "#8f9aa3"),
    "m": ("Playa", "#e6dba7"), "n": ("Río", "#4f8fd0"), "o": ("Océano", "#2f5f9a"), "p": ("Océano profundo", "#1c3a6b"),
    "q": ("Cerezos", "#e6a8c4"), "r": ("Champiñón", "#a070b0"), "s": ("Cuevas", "#5a4a6a"), "t": ("Otro", "#777c82"),
    "u": ("Yermos del Nether", "#8a3b2f"), "v": ("Bosque carmesí", "#b02a3a"), "w": ("Bosque distorsionado", "#1fa39a"),
    "y": ("Valle de arena de almas", "#7b6a58"), "z": ("Deltas de basalto", "#55555e"),
}
BIOME_RULES = [
    ("u", ("nether_wastes",)), ("v", ("crimson_forest",)), ("w", ("warped_forest",)),
    ("y", ("soul_sand_valley",)), ("z", ("basalt_deltas",)),
    ("p", ("deep_ocean", "deep_cold", "deep_frozen", "deep_lukewarm")),
    ("o", ("ocean",)), ("n", ("river",)), ("m", ("beach", "shore")),
    ("r", ("mushroom",)), ("q", ("cherry",)), ("s", ("lush_caves", "dripstone", "deep_dark")),
    ("f", ("snowy", "ice_spikes", "frozen", "grove")), ("l", ("peaks", "windswept", "meadow", "stony", "jagged", "hills", "mountain")),
    ("h", ("badlands", "eroded")), ("g", ("desert",)), ("i", ("savanna",)), ("j", ("jungle", "bamboo", "sparse")),
    ("k", ("swamp", "mangrove")), ("e", ("taiga",)), ("c", ("dark_forest",)), ("d", ("birch",)),
    ("b", ("forest", "pale_garden")), ("a", ("plains", "sunflower")),
]
_bcache = {}


def classify_biome(name):
    c = _bcache.get(name)
    if c is None:
        n = name.split(":")[-1]
        c = "t"
        for cls, keys in BIOME_RULES:
            if any(k in n for k in keys):
                c = cls
                break
        _bcache[name] = c
    return c


_cache = {}


def classify(name):
    c = _cache.get(name)
    if c is None:
        n = name.split(":")[-1]
        c = "x"
        for cls, keys in RULES:
            if any(k in n for k in keys):
                c = cls
                break
        _cache[name] = c
    return c


SAMPLES = [(4, 4), (12, 4), (4, 12), (12, 12)]


def _unpack(longs, bits, count):
    per = 64 // bits
    mask = (1 << bits) - 1
    out = []
    for lv in longs:
        v = lv & 0xFFFFFFFFFFFFFFFF
        for _ in range(per):
            out.append(v & mask)
            v >>= bits
            if len(out) == count:
                return out
    return out


def _biome_at(sec, x, y, z):
    bm = sec.get("biomes") or {}
    pal = bm.get("palette") or []
    names = [p if isinstance(p, str) else (p.get("Name") or p.get("id") or p.get("") or "") for p in pal]
    if not names:
        return "."
    if len(names) == 1 or "data" not in bm:
        return classify_biome(names[0])
    bits = max(1, (len(names) - 1).bit_length())
    idx = (((y & 15) >> 2) * 4 + (z >> 2)) * 4 + (x >> 2)
    per = 64 // bits
    lv = bm["data"][idx // per] & 0xFFFFFFFFFFFFFFFF
    pi = (lv >> ((idx % per) * bits)) & ((1 << bits) - 1)
    return classify_biome(names[pi] if pi < len(names) else names[0])


MASK = 0xFFFFFFFFFFFFFFFF


def _block_getter(by_y):
    cache = {}

    def get(x, y, z):
        sy = y >> 4
        sec = by_y.get(sy)
        if sec is None:
            return "minecraft:air"
        ent = cache.get(sy)
        if ent is None:
            bs = sec.get("block_states") or {}
            pal = bs.get("palette") or ["minecraft:air"]
            names = [p if isinstance(p, str) else (p.get("Name") or p.get("id") or p.get("") or "minecraft:air") for p in pal]
            if len(names) == 1 or "data" not in bs:
                ent = (names, None, 0)
            else:
                ent = (names, bs["data"], max(4, (len(names) - 1).bit_length()))
            cache[sy] = ent
        names, data, bits = ent
        if data is None:
            return names[0]
        idx = ((y & 15) * 16 + z) * 16 + x
        per = 64 // bits
        pi = ((data[idx // per] & MASK) >> ((idx % per) * bits)) & ((1 << bits) - 1)
        return names[pi] if pi < len(names) else names[0]
    return get


def chunk_samples_nether(raw):
    """Superficie visible bajo el techo: primer bloque sólido con aire encima, bajando desde y=119."""
    t = nbt_mini.read_nbt(raw)
    secs = t.get("sections") or []
    if not secs:
        return "....", "...."
    by_y = {s["Y"]: s for s in secs}
    get = _block_getter(by_y)
    out, bio = [], []
    for x, z in SAMPLES:
        prev_air, cls = False, None
        for y in range(119, 31, -1):
            b = get(x, y, z)
            air = b.endswith("air")
            if not air and prev_air:
                cls = classify(b)
                break
            prev_air = air
        if cls is None:
            fb = get(x, 64, z)
            cls = "." if fb.endswith("air") else classify(fb)
        out.append(cls)
        sec = by_y.get(4)
        bm = _biome_at(sec, x, 64, z) if sec else "."
        bio.append("." if bm == "a" else bm)   # "llanura" no existe en el Nether: chunk a medio generar
    return "".join(out), "".join(bio)


def chunk_samples(raw):
    t = nbt_mini.read_nbt(raw)
    hm = (t.get("Heightmaps") or {}).get("MOTION_BLOCKING")
    secs = t.get("sections") or []
    if not hm or not secs:
        return "....", "...."
    min_sec = min(s["Y"] for s in secs)
    by_y = {s["Y"]: s for s in secs}
    heights = _unpack(hm, 9, 256)
    out = []
    bio = []
    for x, z in SAMPLES:
        h = heights[z * 16 + x] if len(heights) == 256 else 0
        y = min_sec * 16 + h - 1
        sec = by_y.get(y >> 4)
        if not sec:
            out.append(".")
            bio.append(".")
            continue
        bio.append(_biome_at(sec, x, y, z))
        bs = sec.get("block_states") or {}
        pal = bs.get("palette") or ["minecraft:air"]
        names = [p if isinstance(p, str) else (p.get("Name") or p.get("id") or p.get("") or "minecraft:air") for p in pal]
        if len(names) == 1 or "data" not in bs:
            out.append(classify(names[0]))
            continue
        bits = max(4, (len(names) - 1).bit_length())
        idx = ((y & 15) * 16 + z) * 16 + x
        per = 64 // bits
        lv = bs["data"][idx // per] & 0xFFFFFFFFFFFFFFFF
        pi = (lv >> ((idx % per) * bits)) & ((1 << bits) - 1)
        out.append(classify(names[pi] if pi < len(names) else names[0]))
    return "".join(out), "".join(bio)


def region_terrain(path, nether=False):
    data = open(path, "rb").read()
    blocks, biomes = [], []
    for i in range(1024):
        o = int.from_bytes(data[i * 4:i * 4 + 3], "big")
        if not o:
            blocks.append("...."); biomes.append("....")
            continue
        try:
            ln = struct.unpack(">I", data[o * 4096:o * 4096 + 4])[0]
            comp = data[o * 4096 + 4]
            body = data[o * 4096 + 5:o * 4096 + 4 + ln]
            raw = zlib.decompress(body) if comp == 2 else b""
            b, m = (chunk_samples_nether(raw) if nether else chunk_samples(raw)) if raw else ("....", "....")
        except Exception:
            b, m = "....", "...."
        blocks.append(b); biomes.append(m)
    return "".join(blocks), "".join(biomes)


def work(args):
    key, path, nether = args
    return key, os.path.getmtime(path), region_terrain(path, nether)


if __name__ == "__main__":
    import time
    t = time.time()
    p = sys.argv[1]
    b, m = region_terrain(p)
    from collections import Counter
    print(len(b), round(time.time() - t, 2), "s", Counter(b).most_common(6), Counter(m).most_common(6))
