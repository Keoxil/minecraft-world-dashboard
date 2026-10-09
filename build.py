"""Lee el mundo de Minecraft que esté abierto y genera data.js, history.js y terrain.js para la página (carpeta site/)."""
import glob, json, os, struct, sys, time, zlib
from datetime import datetime, timezone
from multiprocessing import Pool

import paths
HERE = paths.APP
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbt_mini
import terrain
import discover

DATA_DIR = os.path.join(HERE, "data")     # caché e historial de cada mundo (data/<mundo>/)
SITE_DIR = os.path.join(HERE, "site")     # lo que lee la página
PROFILE = WORLD = WORK = None             # los fija configure()
LANG_CODE = "es_es"
FORCE_TERRAIN = False
P = lambda n: os.path.join(WORK, n)       # archivos de trabajo del mundo actual
S = lambda n: os.path.join(SITE_DIR, n)   # archivos que lee la página
KEY = b"\x04\x00\x0dInhabitedTime"
B36 = "0123456789abcdefghijklmnopqrstuvwxyz"

# métricas que se guardan en el historial (para la carrera del ranking) y que se vigilan para los avisos
RACE_METRICS = ["diamonds", "mobKills", "distKm", "playHours", "blocksMined", "advancements",
                "jumps", "crafted", "damageDealt", "deaths", "playerKills", "pvpDeaths"]

ADV_ES = {
    "story/root": "Minecraft", "story/mine_stone": "Edad de Piedra", "story/upgrade_tools": "Mejorando herramientas",
    "story/smelt_iron": "Adquiriendo hardware", "story/obtain_armor": "Ponte el traje", "story/lava_bucket": "Cosas calientes",
    "story/iron_tools": "¿No es un pico de hierro?", "story/deflect_arrow": "No hoy, gracias", "story/form_obsidian": "Desafío del cubo de hielo",
    "story/mine_diamond": "¡Diamantes!", "story/enter_the_nether": "Debemos ir más profundo", "story/shiny_gear": "Cúbreme de diamantes",
    "story/enchant_item": "Encantador", "story/cure_zombie_villager": "Médico de zombis", "story/follow_ender_eye": "Ojo de espía",
    "story/enter_the_end": "¿El Fin?",
    "nether/root": "Nether", "nether/return_to_sender": "Devolver al remitente", "nether/find_bastion": "Eran otros tiempos",
    "nether/obtain_ancient_debris": "Escombros ocultos en las profundidades", "nether/fast_travel": "Viaje subespacial",
    "nether/find_fortress": "Una terrible fortaleza", "nether/obtain_crying_obsidian": "¿Quién corta cebollas?",
    "nether/distract_piglin": "Oh, brillante", "nether/ride_strider": "Este barco tiene piernas", "nether/uneasy_alliance": "Alianza incómoda",
    "nether/loot_bastion": "Cerditos de guerra", "nether/netherite_armor": "Cúbreme de escombros", "nether/get_wither_skull": "Esqueletos espeluznantes",
    "nether/summon_wither": "Marchitándose", "nether/obtain_blaze_rod": "Hacia el fuego", "nether/explore_nether": "Destinos calientes",
    "nether/create_beacon": "Trae el faro a casa", "nether/brew_potion": "Barman local", "nether/all_potions": "Un cóctel furioso",
    "nether/create_full_beacon": "Faroleador", "nether/charge_respawn_anchor": "No exactamente «inmortal»",
    "end/root": "El Fin", "end/kill_dragon": "Libera el Fin", "end/enter_end_gateway": "Escapada remota", "end/respawn_dragon": "El fin... otra vez",
    "end/dragon_egg": "La próxima generación", "end/elytra": "Cielo sin límites", "end/find_end_city": "La ciudad al final del juego",
    "end/dragon_breath": "Sabor a dragón", "end/levitate": "Gran vista desde aquí",
    "adventure/root": "Aventura", "adventure/voluntary_exile": "Exilio voluntario", "adventure/kill_a_mob": "Cazador de monstruos",
    "adventure/trade": "¡Qué buen negocio!", "adventure/honey_block_slide": "Pegajoso", "adventure/ol_betsy": "Vieja Betsy",
    "adventure/sleep_in_bed": "Dulces sueños", "adventure/shoot_arrow": "Apunta", "adventure/kill_all_mobs": "Monstruos cazados",
    "adventure/totem_of_undying": "Más allá de la muerte", "adventure/summon_iron_golem": "Contratar ayuda",
    "adventure/two_birds_one_arrow": "Dos pájaros de un tiro", "adventure/whos_the_pillager_now": "¿Quién es el saqueador ahora?",
    "adventure/arbalistic": "Arbalístico", "adventure/adventuring_time": "Hora de aventuras", "adventure/very_very_frightening": "Muy, muy aterrador",
    "adventure/sniper_duel": "Duelo de francotiradores", "adventure/bullseye": "Diana", "adventure/avoid_vibration": "Sigilo 100",
    "adventure/fall_from_world_height": "Cuevas y acantilados", "adventure/trim_with_any_armor_pattern": "Creando un nuevo estilo",
    "adventure/salvage_sherd": "Respetando el pasado", "adventure/walk_on_powder_snow_with_leather_boots": "Ligero como un conejo",
    "adventure/spyglass_at_parrot": "¿Es un pájaro?", "adventure/spyglass_at_ghast": "¿Es un globo?", "adventure/spyglass_at_dragon": "¿Es un avión?",
    "adventure/lightning_rod_with_villager_no_fire": "Pararrayos protector", "adventure/hero_of_the_village": "Héroe de la aldea",
    "adventure/play_jukebox_in_meadows": "Sonido de la música", "adventure/trade_at_world_height": "Comerciante de las alturas",
    "husbandry/root": "Granja", "husbandry/safely_harvest_honey": "Sé nuestro invitado", "husbandry/breed_an_animal": "Los padres",
    "husbandry/tame_an_animal": "Mejores amigos para siempre", "husbandry/fishy_business": "Negocio de pescado",
    "husbandry/plant_seed": "Un lugar con semillas", "husbandry/bred_all_animals": "Dos de cada uno",
    "husbandry/complete_catalogue": "Un catálogo completo de gatos", "husbandry/tactical_fishing": "Pesca táctica",
    "husbandry/balanced_diet": "Una dieta equilibrada", "husbandry/obtain_netherite_hoe": "Dedicación seria",
    "husbandry/make_a_sign_glow": "Brilla y resplandece", "husbandry/axolotl_in_a_bucket": "El depredador más adorable",
    "husbandry/wax_on": "Encerar", "husbandry/wax_off": "Quitar cera", "husbandry/tadpole_in_a_bucket": "Cubo de renacuajos",
    "husbandry/allay_deliver_item_to_player": "Tienes un amigo en mí", "husbandry/obtain_sniffer_egg": "Huevo aromático",
    "husbandry/feed_snifflet": "Pequeños olfateadores", "husbandry/plant_any_sniffer_seed": "Plantando el pasado",
    "husbandry/ride_a_boat_with_a_goat": "Lo que flota tu cabra", "husbandry/kill_axolotl_target": "El poder curativo de la amistad",
    "husbandry/silk_touch_nest": "Panal portátil", "husbandry/repair_wolf_armor": "Como nuevo",
}


_LANG_ADV = None


def lang_adv():
    """Nombres oficiales de los logros en español de España (es_es), leídos del archivo de idioma del propio juego."""
    global _LANG_ADV
    if _LANG_ADV is not None:
        return _LANG_ADV
    _LANG_ADV = {}
    try:
        for base in discover.assets_dirs(PROFILE):
            for f in sorted(glob.glob(base + "/indexes/*.json"), key=os.path.getmtime, reverse=True):
                objs = json.load(open(f, encoding="utf-8")).get("objects", {})
                ent = objs.get(f"minecraft/lang/{LANG_CODE}.json")
                if not ent:
                    continue
                h = ent["hash"]
                lang = json.load(open(f"{base}/objects/{h[:2]}/{h}", encoding="utf-8"))
                for k, v in lang.items():
                    if k.startswith("advancements.") and k.endswith(".title"):
                        _LANG_ADV[k[len("advancements."):-len(".title")].replace(".", "/", 1)] = v
                break
            if _LANG_ADV:
                break
    except Exception:
        pass
    return _LANG_ADV


def adv_title(aid):
    key = aid.split(":", 1)[-1]
    lang = lang_adv()
    if key in lang:
        return lang[key]
    if key in ADV_ES:
        return ADV_ES[key]
    return key.split("/")[-1].replace("_", " ").capitalize()


TOOL_SUFFIX = ("_pickaxe", "_axe", "_shovel", "_hoe", "_sword", "_spear")
TOOL_NAMES = {"shears", "fishing_rod", "flint_and_steel", "bow", "crossbow", "trident", "mace", "brush",
              "carrot_on_a_stick", "warped_fungus_on_a_stick"}


def is_tool(item_id):
    n = item_id.split(":")[-1]
    return n in TOOL_NAMES or n.endswith(TOOL_SUFFIX)


def load_json(path, default):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return default


def save_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, path)


def write_js(path, var, obj):
    """Escribe window.<var> = ...; de forma atómica: la página nunca lee un archivo a medias."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(f"window.{var} = " + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";\n")
    for _ in range(10):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(0.1)
    os.replace(tmp, path)


def iso_now():
    # con zona horaria (p. ej. -04:00): cada navegador la muestra en la hora local de quien mira
    return datetime.now().astimezone().isoformat(timespec="seconds")


def tz_iso(epoch, timespec="seconds"):
    return datetime.fromtimestamp(epoch).astimezone().isoformat(timespec=timespec)


def fix_ts(s):
    """Convierte horas guardadas sin zona (hora local de este PC) a horas con zona."""
    try:
        dt = datetime.fromisoformat(s)
    except (TypeError, ValueError):
        return s
    return (dt.astimezone() if dt.tzinfo is None else dt).isoformat(timespec="seconds")


# ---------- regiones: niveles de "tiempo pasado" ----------
def scan_region(path):
    name = os.path.basename(path)[2:-4].split(".")
    rx, rz = int(name[0]), int(name[1])
    data = open(path, "rb").read()
    levels = []
    stamps = [struct.unpack(">I", data[4096 + i * 4:4096 + i * 4 + 4])[0] for i in range(1024)] if len(data) >= 8192 else [0] * 1024
    for i in range(1024):
        o = int.from_bytes(data[i * 4:i * 4 + 3], "big")
        if not o:
            levels.append(".")
            continue
        try:
            ln = struct.unpack(">I", data[o * 4096:o * 4096 + 4])[0]
            comp = data[o * 4096 + 4]
            body = data[o * 4096 + 5:o * 4096 + 4 + ln]
            raw = zlib.decompress(body) if comp == 2 else b""
            j = raw.find(KEY)
            t = struct.unpack(">q", raw[j + len(KEY):j + len(KEY) + 8])[0] if j >= 0 else 0
        except Exception:
            t = 0
        lv = 0 if t <= 0 else min(9, 1 + int(max(0, (t / 20.0) ** 0.5 / 3.2)))
        levels.append(str(lv))
    return rx, rz, "".join(levels), stamps


def scan_dimension(pool, dim):
    files = glob.glob(os.path.join(discover.region_dir(WORLD, dim), "r.*.mca"))
    return pool.map(scan_region, files) if files else []


# ---------- terreno (cacheado por región según fecha del archivo) ----------
def update_terrain(pool):
    cfg = load_json(os.path.join(HERE, "config.json"), {})
    n_over = len(glob.glob(os.path.join(discover.region_dir(WORLD, "overworld"), "r.*.mca")))
    if cfg.get("terrain") is False or n_over > int(cfg.get("terrain_max_regions", 700)):
        # mundo demasiado grande (o desactivado): sin capa de terreno; el mapa de «tiempo pasado» sigue funcionando
        try:
            vacio = open(S("terrain.js"), encoding="utf-8").read(40).startswith("window.TERRAIN = null")
        except OSError:
            vacio = False
        if FORCE_TERRAIN or not vacio:
            write_js(S("terrain.js"), "TERRAIN", None)
        return 0
    cache = load_json(P("terrain_cache2.json"), {})
    todo, meta = [], []
    for dim, nether in (("overworld", False), ("the_nether", True)):
        c = cache.setdefault(dim, {})
        for f in glob.glob(os.path.join(discover.region_dir(WORLD, dim), "r.*.mca")):
            k = os.path.basename(f)[2:-4].replace(".", ",")
            mt = os.path.getmtime(f)
            if k not in c or abs(c[k]["mt"] - mt) > 1:
                todo.append((k, f, nether))
                meta.append(dim)
    if todo or FORCE_TERRAIN:
        for dim, (k, mt, (bl, bi)) in zip(meta, pool.map(terrain.work, todo)):
            cache[dim][k] = {"mt": mt, "s": bl, "b": bi}
        if todo:
            save_json(P("terrain_cache2.json"), cache)

        def part(dim):
            c = cache.get(dim, {})
            return ({k: v["s"] for k, v in c.items() if v["s"].strip(".")}, {k: v["b"] for k, v in c.items() if v["s"].strip(".")})
        ow, ow_b = part("overworld")
        ne, ne_b = part("the_nether")
        out = {"classes": terrain.CLASSES, "biomeClasses": terrain.BIOME_CLASSES, "regions": ow, "biomes": ow_b,
               "nether": {"regions": ne, "biomes": ne_b}}
        write_js(S("terrain.js"), "TERRAIN", out)
    return len(todo)


# ---------- jugadores ----------
def num(d, *path, default=0):
    for k in path:
        d = d.get(k, {}) if isinstance(d, dict) else {}
    return d if isinstance(d, (int, float)) else default


def item_brief(it):
    if not isinstance(it, dict) or not it.get("id"):
        return None
    return {"id": it["id"].split(":")[-1], "n": it.get("count", 1)}


def read_players(names):
    players, achievements = [], []
    for f in discover.stat_files(WORLD):
        uuid = os.path.basename(f)[:-5]
        s = json.load(open(f, encoding="utf-8")).get("stats", {})
        c = s.get("minecraft:custom", {})
        mined = s.get("minecraft:mined", {})
        killed = s.get("minecraft:killed", {})
        crafted = s.get("minecraft:crafted", {})
        picked = s.get("minecraft:picked_up", {})
        used = s.get("minecraft:used", {})
        killed_by = s.get("minecraft:killed_by", {})
        top_killer = max(killed_by.items(), key=lambda kv: kv[1]) if killed_by else None
        walk = sum(c.get(k, 0) for k in ("minecraft:walk_one_cm", "minecraft:sprint_one_cm", "minecraft:crouch_one_cm"))
        fly = sum(c.get(k, 0) for k in ("minecraft:fly_one_cm", "minecraft:aviate_one_cm"))
        swim = c.get("minecraft:swim_one_cm", 0) + c.get("minecraft:walk_on_water_one_cm", 0)
        boat = c.get("minecraft:boat_one_cm", 0) + c.get("minecraft:horse_one_cm", 0) + c.get("minecraft:minecart_one_cm", 0)
        top_mob = max(killed.items(), key=lambda kv: kv[1]) if killed else None
        top_block = max(mined.items(), key=lambda kv: kv[1]) if mined else None
        p = {
            "uuid": uuid,
            "name": names.get(uuid, uuid[:8]),
            "playHours": round(c.get("minecraft:play_time", c.get("minecraft:play_one_minute", 0)) / 72000, 2),
            "deaths": c.get("minecraft:deaths", 0),
            "playerKills": c.get("minecraft:player_kills", 0),
            "mobKills": c.get("minecraft:mob_kills", 0),
            "diamonds": sum(v for k, v in mined.items() if "diamond_ore" in k),
            "blocksMined": int(sum(mined.values())),
            "distKm": round((walk + fly + swim + boat) / 100000, 2),
            "walkKm": round(walk / 100000, 2),
            "jumps": c.get("minecraft:jump", 0),
            "sleeps": c.get("minecraft:sleep_in_bed", 0),   # solo para el huevo de pascua; no cuenta en ninguna clasificación
            "pvpDeaths": killed_by.get("minecraft:player", 0),
            "killedByTop": top_killer[0].split(":")[-1] if top_killer else None,
            "killedByTopN": top_killer[1] if top_killer else 0,
            "shieldBlocked": round(c.get("minecraft:damage_blocked_by_shield", 0) / 10),
            "shots": used.get("minecraft:bow", 0) + used.get("minecraft:crossbow", 0) + used.get("minecraft:trident", 0),
            "damageDealt": round(c.get("minecraft:damage_dealt", 0) / 10),
            "damageTaken": round(c.get("minecraft:damage_taken", 0) / 10),
            "crafted": int(sum(crafted.values())),
            "fish": c.get("minecraft:fish_caught", 0),
            "bred": c.get("minecraft:animals_bred", 0),
            "trades": c.get("minecraft:traded_with_villager", 0),
            "topMob": top_mob[0].split(":")[-1] if top_mob else None,
            "topMobN": top_mob[1] if top_mob else 0,
            "topBlock": top_block[0].split(":")[-1] if top_block else None,
            "topBlockN": int(top_block[1]) if top_block else 0,
            "items": int(sum(picked.values())),
            "emeralds": picked.get("minecraft:emerald", 0) + crafted.get("minecraft:emerald", 0),
            "toolsBroken": sum(v for k, v in s.get("minecraft:broken", {}).items() if is_tool(k)),
        }
        # logros: fecha de cada uno
        af = discover.adv_file(WORLD, uuid)
        adv = 0
        if os.path.exists(af):
            a = json.load(open(af, encoding="utf-8"))
            for k, v in a.items():
                if not isinstance(v, dict) or not v.get("done") or k.startswith("minecraft:recipes/") or k == "DataVersion":
                    continue
                if k.endswith("/root"):
                    continue
                adv += 1
                dates = [d for d in (v.get("criteria") or {}).values() if isinstance(d, str)]
                ts = ""
                if dates:
                    try:
                        ts = max(datetime.strptime(d, "%Y-%m-%d %H:%M:%S %z") for d in dates).astimezone().isoformat(timespec="seconds")
                    except Exception:
                        ts = ""
                achievements.append({"u": uuid, "id": k.split(":", 1)[-1], "t": adv_title(k), "ts": ts})
        p["advancements"] = adv
        # estado actual + equipo
        df = discover.player_file(WORLD, uuid)
        if os.path.exists(df):
            try:
                d = nbt_mini.read_gz(df)
                pos = d.get("Pos", [0, 0, 0])
                p["pos"] = [round(pos[0]), round(pos[1]), round(pos[2])]
                p["dim"] = d.get("Dimension", "minecraft:overworld").split(":")[-1]
                p["health"] = d.get("Health", 20)
                p["level"] = d.get("XpLevel", 0)
                p["food"] = d.get("foodLevel", 20)
                ld = d.get("LastDeathLocation")
                p["lastDeath"] = [round(x) for x in ld["pos"]] if ld else None
                p["lastSeen"] = tz_iso(os.path.getmtime(df), "minutes")
                eq = d.get("equipment") or {}
                hot = [None] * 9
                for it in d.get("Inventory") or []:
                    sl = it.get("Slot")
                    if isinstance(sl, int) and 0 <= sl <= 8:
                        hot[sl] = item_brief(it)
                p["equip"] = {
                    "head": item_brief(eq.get("head")), "chest": item_brief(eq.get("chest")),
                    "legs": item_brief(eq.get("legs")), "feet": item_brief(eq.get("feet")),
                    "off": item_brief(eq.get("offhand")), "hotbar": hot,
                    "selected": d.get("SelectedItemSlot", 0),
                }
            except Exception as e:
                print("NBT fallo", uuid, e)
        players.append(p)
    return players, achievements


def mark_online(players):
    """Conexiones y desconexiones desde el latest.log del juego (hora real, sin depender del autoguardado)."""
    import re
    log = PROFILE + "/logs/latest.log"
    ev = {}
    stopped = False
    try:
        lines = open(log, encoding="utf-8", errors="replace").read().splitlines()
        mt = datetime.fromtimestamp(os.path.getmtime(log))
        day = mt.date()
        # reconstruye la fecha de cada línea retrocediendo desde la última modificación
        parsed = []
        prev_s = None
        for ln in reversed(lines):
            m = re.match(r"\[(\d\d):(\d\d):(\d\d)\] ", ln)
            if not m:
                continue
            sec = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            if prev_s is not None and sec > prev_s:
                day = day.fromordinal(day.toordinal() - 1)
            prev_s = sec
            parsed.append((day, m.group(0)[1:9], ln[m.end():]))
        parsed.reverse()
        for d, hms, msg in parsed:
            m = re.search(r"System chat: (\S+) (joined|left) the game", msg)
            if m:
                ev[m.group(1)] = (m.group(2), f"{d.isoformat()}T{hms}")
            if "Stopping singleplayer server" in msg or "Stopping server" in msg:
                stopped = True
            if "Starting integrated" in msg or "Starting minecraft server" in msg:
                stopped = False
    except OSError:
        pass
    running = discover.java_running()
    for p in players:
        e = ev.get(p["name"])
        p["online"] = bool(e and e[0] == "joined" and running and not stopped)
        p["lastEvent"] = fix_ts(e[1]) if e else None
        p["lastEventKind"] = e[0] if e else None


def log_events(names):
    """Todos los logs (comprimidos y actual): conexiones, desconexiones y muertes, con fecha real."""
    import gzip, re
    ev = []   # (epoch, tipo, jugador, extra)
    files = sorted(glob.glob(PROFILE + "/logs/*.log.gz")) + [PROFILE + "/logs/latest.log"]
    name_set = set(names.values())
    death_re = re.compile(r"\[Server thread/INFO\]: (?:System chat: )?(\S+) (was slain by|was shot by|was killed|was blown up|was fireballed|"
                          r"was pummeled|was impaled|was squashed|was pricked|was stung|was skewered|drowned|fell |hit the ground|burned|"
                          r"went up in flames|tried to swim in lava|starved|suffocated|died|blew up|walked into|withered away|froze to death|"
                          r"experienced kinetic energy|discovered the floor was lava|was struck|was roasted)(.*)$")
    jl_re = re.compile(r"\[Server thread/INFO\]: System chat: (\S+) (joined|left) the game")
    for f in files:
        try:
            op = gzip.open if f.endswith(".gz") else open
            lines = op(f, "rt", encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        base = os.path.basename(f)
        if base.endswith(".log.gz"):
            day = datetime.strptime(base[:10], "%Y-%m-%d").date()
            fwd = True
        else:
            day = datetime.fromtimestamp(os.path.getmtime(f)).date()
            fwd = False
        stamped = []
        prev = None
        seq = lines if fwd else list(reversed(lines))
        for ln in seq:
            m = re.match(r"\[(\d\d):(\d\d):(\d\d)\] ", ln)
            if not m:
                continue
            sec = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            if prev is not None:
                if fwd and sec < prev:
                    day = day.fromordinal(day.toordinal() + 1)
                if not fwd and sec > prev:
                    day = day.fromordinal(day.toordinal() - 1)
            prev = sec
            stamped.append((datetime(day.year, day.month, day.day, sec // 3600, sec % 3600 // 60, sec % 60).timestamp(), ln[m.end():]))
        if not fwd:
            stamped.reverse()
        for t, msg in stamped:
            m = jl_re.search(msg)
            if m:
                ev.append((t, m.group(2), m.group(1), None))
                continue
            m = death_re.search(msg)
            if m and m.group(1) in name_set:
                killer = None
                for nm in name_set:
                    if nm != m.group(1) and (" by " + nm) in msg:
                        killer = nm
                ev.append((t, "death", m.group(1), killer))
    ev.sort(key=lambda e: e[0])
    return ev


# categorías que Minecraft no fechó: se estiman repartiendo el total por tiempo jugado (y se marcan como estimación)
EST_METRICS = ["diamonds", "mobKills", "distKm", "blocksMined", "jumps", "crafted", "damageDealt"]


def reconstruct_frames(players, achievements, names, t_start, t_end, step, now_ts, anchor=None):
    """Fotogramas de la carrera desde la creación del mundo, solo con lo que realmente se puede reconstruir."""
    ev = log_events(names)
    uuid_by_name = {p["name"]: p["uuid"] for p in players}
    sess = {u: [] for u in uuid_by_name.values()}
    open_at = {}
    deaths = {u: [] for u in uuid_by_name.values()}
    kills = {u: [] for u in uuid_by_name.values()}
    pvpd = {u: [] for u in uuid_by_name.values()}
    for t, kind, who, extra in ev:
        u = uuid_by_name.get(who)
        if not u:
            continue
        if kind == "joined":
            open_at[u] = t
        elif kind == "left" and u in open_at:
            sess[u].append((open_at.pop(u), t))
        elif kind == "death":
            deaths[u].append(t)
            if extra and uuid_by_name.get(extra):
                kills[uuid_by_name[extra]].append(t)
                pvpd[u].append(t)
    for u, st in open_at.items():
        sess[u].append((st, now_ts))
    adv_ts = {u: [] for u in uuid_by_name.values()}
    for a in achievements:
        if a["u"] in adv_ts and a["ts"]:
            try:
                adv_ts[a["u"]].append(datetime.fromisoformat(a["ts"]).timestamp())
            except ValueError:
                pass
    def hours_at(u, t):
        return sum(max(0, min(e, t) - st) for st, e in sess[u] if st < t) / 3600.0

    hours_anchor = {u: hours_at(u, t_end) for u in uuid_by_name.values()}
    diamond_ts = {}
    for a in achievements:
        if a["id"] == "story/mine_diamond" and a["ts"]:
            try:
                diamond_ts[a["u"]] = datetime.fromisoformat(a["ts"]).timestamp()
            except ValueError:
                pass
    frames = []
    t = t_start
    while t < t_end:
        row = {}
        for u in uuid_by_name.values():
            hours = sum(max(0, min(e, t) - st) for st, e in sess[u] if st < t) / 3600.0
            vals = []
            for m in RACE_METRICS:
                if m == "advancements":
                    vals.append(sum(1 for x in adv_ts[u] if x <= t))
                elif m == "playHours":
                    vals.append(round(hours, 2))
                elif m == "deaths":
                    vals.append(sum(1 for x in deaths[u] if x <= t))
                elif m == "playerKills":
                    vals.append(sum(1 for x in kills[u] if x <= t))
                elif m == "pvpDeaths":
                    vals.append(sum(1 for x in pvpd[u] if x <= t))
                elif m in EST_METRICS and anchor and anchor.get(u) and hours_anchor[u] > 0:
                    base = (anchor[u][RACE_METRICS.index(m)] or 0)
                    frac = min(1.0, hours_at(u, t) / hours_anchor[u])
                    if m == "diamonds" and not (u in diamond_ts and diamond_ts[u] <= t):
                        frac = 0.0                 # antes de su primer logro de diamantes no tenía ninguno
                    v = base * frac
                    vals.append(round(v, 2) if m == "distKm" else int(v))
                else:
                    vals.append(None)
            row[u] = vals
        frames.append([tz_iso(t), row])
        t += step
    return frames


def configure():
    """Elige el mundo abierto (o el último usado) y prepara las rutas. Devuelve False si no hay ninguno."""
    global PROFILE, WORLD, WORK, LANG_CODE, FORCE_TERRAIN
    cfg = load_json(os.path.join(HERE, "config.json"), {})
    LANG_CODE = cfg.get("language", "es_es")
    sel = discover.pick(cfg, DATA_DIR)
    if not sel:
        print("No encuentro ningún mundo de Minecraft. Indica la carpeta de tu instancia en config.json (mira config.example.json).")
        return False
    PROFILE, WORLD = sel["instance"], sel["world"]
    WORK = os.path.join(DATA_DIR, discover.slug(PROFILE, WORLD))
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(SITE_DIR, exist_ok=True)
    try:
        prev = open(S(".world"), encoding="utf-8").read()
    except OSError:
        prev = ""
    FORCE_TERRAIN = prev != WORLD          # cambio de mundo: hay que reescribir también el terreno
    print(f"Mundo: {os.path.basename(WORLD)}  ({'abierto ahora' if sel['open'] else 'el último que se usó'})  en  {PROFILE}")
    return True


def main():
    t0 = time.time()
    os.makedirs(DATA_DIR, exist_ok=True)
    lock = os.path.join(DATA_DIR, ".build.lock")
    if os.path.exists(lock) and time.time() - os.path.getmtime(lock) < 600:
        print("Otra ejecución en curso; salgo.")
        return
    open(lock, "w").close()
    try:
        if configure():
            _main(t0)
    finally:
        try:
            os.remove(lock)
        except OSError:
            pass


def _main(t0):
    names = discover.read_names(PROFILE, WORLD)

    players, achievements = read_players(names)
    mark_online(players)

    folder = os.path.basename(WORLD)
    try:
        lv = nbt_mini.read_gz(os.path.join(WORLD, "level.dat"))
        dat = lv.get("Data", lv)
        spawn = [dat.get("SpawnX", 0), dat.get("SpawnZ", 0)]
        days = round((dat.get("DayTime") or dat.get("Time") or 0) / 24000, 1)
        world_name = dat.get("LevelName") or folder
    except Exception:
        spawn, days, world_name = None, 0, folder

    with Pool(min(8, os.cpu_count() or 4)) as pool:
        dims, stamps = {}, {}
        for dim in ("overworld", "the_nether", "the_end"):
            res = scan_dimension(pool, dim)
            dims[dim] = {f"{rx},{rz}": lv for rx, rz, lv, st in res}
            stamps[dim] = {f"{rx},{rz}": st for rx, rz, lv, st in res}
        n_terrain = update_terrain(pool)

    explored = {}
    for dim, regs in dims.items():
        explored[dim] = {
            "generated": sum(1 for lv in regs.values() for ch in lv if ch != "."),
            "visited": sum(1 for lv in regs.values() for ch in lv if ch not in ".0"),
        }

    # ---------- estado e historial ----------
    first_run = not os.path.exists(P("history.json"))
    now = iso_now()
    history = load_json(P("history.json"), {"snaps": [], "times": [], "startedAt": now})
    for sn in history["snaps"]:
        sn[0] = fix_ts(sn[0])               # migra las horas antiguas, guardadas sin zona
    history["startedAt"] = fix_ts(history.get("startedAt", now))

    vals = {p["uuid"]: [p.get(m, 0) for m in RACE_METRICS] for p in players}
    if not history["snaps"] or history["snaps"][-1][1] != vals:
        history["snaps"].append([now, vals])
        history["snaps"] = history["snaps"][-3000:]
    save_json(P("history.json"), history)

    # timelapse desde la creación del mundo: marca de guardado de cada chunk la primera vez que se detecta pisado
    now_ts = time.time()
    try:
        created = os.path.getctime(WORLD)
    except OSError:
        created = now_ts
    first = load_json(P("explore_first2.json"), {})
    for dim in ("overworld", "the_nether"):
        fd = first.setdefault(dim, {})
        for key, lv in dims[dim].items():
            arr = fd.get(key) or [0] * 1024
            st = stamps[dim].get(key) or [0] * 1024
            for i, ch in enumerate(lv):
                if ch not in ".0" and not arr[i]:
                    arr[i] = max(int(created), st[i]) if st[i] else int(now_ts)
            if any(arr):
                fd[key] = arr
    save_json(P("explore_first2.json"), first)
    span = max(60, now_ts - created)
    step = max(300, int(span / 1000) + 1)
    n_frames = int(span // step) + 1
    times = [tz_iso(created + i * step) for i in range(n_frames + 1)]
    B36 = "0123456789abcdefghijklmnopqrstuvwxyz"
    tl_regions = {}
    for dim, fd in first.items():
        out_d = {}
        for key, arr in fd.items():
            if any(arr):
                out_d[key] = "".join(
                    (B36[min(1295, (v - int(created)) // step) // 36] + B36[min(1295, (v - int(created)) // step) % 36]) if v else ".."
                    for v in arr)
        tl_regions[dim] = out_d

    # carrera: fotogramas reconstruidos desde la creación + los grabados en tiempo real
    first_real = history["snaps"][0][0] if history["snaps"] else iso_now()
    t_first_real = datetime.fromisoformat(first_real).timestamp()
    anchor_vals = history["snaps"][0][1] if history["snaps"] else {p["uuid"]: [p.get(m, 0) for m in RACE_METRICS] for p in players}
    pre = reconstruct_frames(players, achievements, names, created, t_first_real, 300, now_ts, anchor_vals)

    achievements.sort(key=lambda a: a["ts"], reverse=True)
    hist_out = {
        "metrics": RACE_METRICS,
        "startedAt": history["startedAt"],
        "snaps": history["snaps"],
        "created": tz_iso(created),
        "pre": pre,
        "preMetrics": ["advancements", "playHours", "deaths", "playerKills", "pvpDeaths"],
        "preEstimated": EST_METRICS,
        "tl": {"times": times, "regions": tl_regions},
        "ach": achievements[:400],
    }
    write_js(S("history.js"), "HISTORY", hist_out)

    out = {"world": world_name, "worldId": os.path.basename(WORK), "days": days, "spawn": spawn, "generatedAt": now,
           "players": players, "regions": dims, "explored": explored}
    write_js(S("data.js"), "DATA", out)
    with open(S(".world"), "w", encoding="utf-8") as fh:
        fh.write(WORLD)

    print(f"OK {len(players)} jugadores, {sum(len(v) for v in dims.values())} regiones, terreno {n_terrain} regiones nuevas, "
          f"{len(history['snaps'])} snapshots, {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
