# Minecraft World Dashboard

[Leer en español](README.es.md)

A web page that shows the stats of the Minecraft world you are playing: ranking, podium with skins, a map of what has been explored (terrain, biomes and time), timelapse, ranking race, achievement history, a PvP arena and more. It updates itself and **finds the world that is open at that moment on its own**, so it works for any world you play or host in the future.

No mods or plugins needed: it reads the world's own files (statistics, advancements, regions, player data). It uses only the Python standard library.

**10 languages**, picked from a selector on the page: English, Español, 中文, हिन्दी, العربية, Français, Português, Русский, Deutsch and 日本語. Achievement names even come from the game's own translations.

## Quick start (easiest)

1. Download **`MinecraftWorldDashboard-Setup.exe`** from [Releases](../../releases/latest) and run it (no administrator rights needed).
2. Open **Minecraft World Dashboard** from your desktop or Start menu.
3. Pick your world (or leave it on "Automatic") and click **Open my page**.

That's it: nothing else to install, no Python, no accounts, no terminal. The app reads your world, serves the page and keeps it up to date every minute. Turn on **Public link** and it creates a link with Cloudflare (it downloads that tool by itself, checking its official checksum): press **Copy** and send it to your friends.

- **Several worlds or launchers?** Use the dropdown to choose one, or leave "Automatic", which always follows the world you have open. **Add folder** covers unusual locations.
- **Start with Windows** is a switch in the app (it starts minimized).
- Closing the window stops sharing; minimize it to keep the page online.
- **Your data and settings** live in `%LOCALAPPDATA%\MinecraftWorldDashboard`. To uninstall, use Windows Settings → Apps (this also removes that data).

The link changes every time the app restarts. For a permanent one, use a [named Cloudflare tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) (free account needed).

### Is it safe?

- **The installer is not built by a person, it is built by GitHub**, in the open, from this code ([workflow](.github/workflows/release.yml)). You can verify it: `gh attestation verify MinecraftWorldDashboard-Setup.exe --repo <user>/minecraft-world-dashboard`, or compare its SHA-256 with `SHA256.txt`.
- **Windows SmartScreen may show "Windows protected your PC"** the first time ("unknown publisher"). That is not a malware detection (Windows Defender scans it clean): SmartScreen shows it for any download that is not code-signed. Click *More info → Run anyway*. It is harmless, but the project is not code-signed. If you don't trust it, don't run it: all the code is here and you can run it with `python gui.py`.
- **It only reads** your world files; it never modifies them or touches passwords, accounts or the rest of your disk.
- **Minimal exposure:** the server listens only on `127.0.0.1`, only answers GET, and only serves a fixed list of files (the page, its three data files and the ten language files). It serves no folders, runs nothing and accepts no uploads. The page has a strict Content Security Policy and escapes every name (tested with malicious player names).
- **Cloudflare:** the tool is downloaded from the official GitHub releases and verified against its SHA-256 checksum before it runs. The tunnel is outbound only: no port is opened on your router.
- **Privacy:** anyone with the link can see player names, their current coordinates and where they last died. Share it only with friends.

## Manual use (with Python)

Requires Python 3.9+. Minecraft Java. Tested on **Windows** with **Minecraft 26.3** and the Modrinth launcher; stats, advancements and map also work on 1.21.1. Terrain and biomes need worlds from 1.18 or newer. Linux and macOS are supported in the code but untested.

```bash
python gui.py            # the desktop window (same as the installed app)
python start.py          # console version: reads the world, serves the page, creates the link
python start.py --help   # all options
```

Or step by step:

```bash
python build.py          # reads the open world and writes the data files into site/
python serve.py          # serves the page at http://127.0.0.1:8765/
```

To keep the data fresh without `start.py`, run `build.py` every minute (Windows Task Scheduler, or cron: `* * * * * cd /path/to/repo && python3 build.py`).

## How it finds your world

1. It looks for Minecraft instances in the common launchers: the official launcher, Modrinth, Prism Launcher, MultiMC, CurseForge (including a OneDrive-redirected Documents folder), GDLauncher and ATLauncher.
2. It picks the world Minecraft has open right now (on Windows, the one whose `session.lock` is locked).
3. If none is open, it keeps the last one that was used.

When you switch worlds, the page notices within seconds and reloads by itself. Each world keeps its own history in `data/<world>/`.

For an unusual location, copy `config.example.json` to `config.json` and fill in `instances` (folders that contain `saves/`) or `world` (to pin a specific world). Other options: `language` (language of achievement names in the data, default `es_es`), `port`, `terrain` and `terrain_max_regions` (huge worlds skip the terrain layer so the page stays light).

## Translations

Each language is one file in `site/lang/`. To fix a translation or add a language, copy `site/lang/en.js`, translate the values (keep the `{variables}`; `|` separates singular|plural) and add it to `LANGS_LIST` in `site/index.html`, to the allow-list in `serve.py` and to `PAGE_LANGS` in `build.py`.

## Datapacks

`datapacks/` has six standalone datapacks for playing with friends: **PvP Duels**, **Tree Feller**, **Vein Miner**, **Easy Harvest**, **Death Coordinates** and **Home**. `python scripts/zip_datapacks.py` packs them into `dist/`. See `datapacks/README.md`.

## A secret

<details>
<summary>There is a hidden award on the page (click to see how to find it)</summary>

Type **siesta** on the keyboard anywhere on the page, enter the **Konami code** (↑ ↑ ↓ ↓ ← → ← → B A), or tap the title seven times in a row. It doesn't count towards any ranking.
</details>

## Credits

Skins and faces are loaded from [mc-heads.net](https://mc-heads.net) (with [crafatar.com](https://crafatar.com) as a fallback) and fonts from Google Fonts, when online. No Mojang assets are included.

Minecraft is a trademark of Mojang AB. This project is not affiliated with or endorsed by Mojang or Microsoft.

## License

[MIT](LICENSE)
