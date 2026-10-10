# Minecraft World Dashboard

[Read in English](README.md)

Una página web que enseña las estadísticas del mundo de Minecraft que estés jugando: ranking, podio con skins, mapa de lo explorado (terreno, biomas y tiempo), timelapse, carrera del ranking, historial de logros, Arena PvP y mucho más. Se actualiza sola y **encuentra por su cuenta el mundo que esté abierto en ese momento**, así que sirve para cualquier mundo que juegues o alojes en el futuro.

No necesita mods ni plugins: lee los archivos del propio mundo (estadísticas, logros, regiones, datos de jugador). Solo usa la biblioteca estándar de Python.

**10 idiomas**, elegibles desde un selector en la página: English, Español, 中文, हिन्दी, العربية, Français, Português, Русский, Deutsch y 日本語. Los nombres de los logros salen de las traducciones del propio juego.

## Empezar (lo más fácil)

1. Descarga **`MinecraftWorldDashboard-Setup.exe`** desde [Releases](../../releases/latest) y ejecútalo (no pide permisos de administrador).
2. Abre **Minecraft World Dashboard** desde el escritorio o el menú Inicio.
3. Elige tu mundo (o déjalo en "Automatic") y pulsa **Open my page**.

Eso es todo: no hace falta instalar nada más, ni Python, ni cuentas, ni terminal. La app lee tu mundo, sirve la página y la mantiene al día cada minuto. Activa **Public link** y crea un enlace con Cloudflare (descarga la herramienta ella sola, comprobando su firma oficial): pulsa **Copy** y se lo pasas a tus amigos.

- **¿Varios mundos o launchers?** Elige uno en el desplegable, o déjalo en "Automatic", que sigue siempre al mundo que tengas abierto. **Add folder** cubre ubicaciones raras.
- **Start with Windows** es un interruptor de la app (arranca minimizada).
- Cerrar la ventana deja de compartir; minimízala para mantener la página en línea.
- **Tus datos y ajustes** se guardan en `%LOCALAPPDATA%\MinecraftWorldDashboard`. Para desinstalar, usa Configuración de Windows → Aplicaciones (también borra esos datos).

El enlace cambia cada vez que se reinicia la app. Si quieres uno fijo, usa un [túnel con nombre de Cloudflare](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) (necesita cuenta gratuita).

### ¿Es seguro?

- **El instalador no lo compila una persona, lo compila GitHub** a la vista de todos desde este código ([workflow](.github/workflows/release.yml)). Puedes comprobarlo: `gh attestation verify MinecraftWorldDashboard-Setup.exe --repo <usuario>/minecraft-world-dashboard`, o comparar su SHA-256 con `SHA256.txt`.
- **Windows SmartScreen puede mostrar "Windows protegió su PC"** la primera vez ("editor desconocido"). No es una detección de malware (Windows Defender lo analiza y sale limpio): SmartScreen lo muestra con cualquier descarga que no esté firmada. Pulsa *Más información → Ejecutar de todas formas*. Es inofensivo, pero el proyecto no está firmado. Si no te fías, no lo ejecutes: todo el código está aquí y puedes lanzarlo con `python gui.py`.
- **Solo lee** los archivos de tus mundos; nunca los modifica ni toca contraseñas, cuentas ni el resto del disco.
- **Superficie expuesta mínima:** el servidor escucha solo en `127.0.0.1`, solo responde a GET y solo entrega una lista fija de archivos (la página, sus 3 archivos de datos y los 10 de idioma). No sirve carpetas, no ejecuta nada ni acepta subidas. La página lleva una política CSP estricta y escapa todos los nombres (probado con nombres de jugador maliciosos).
- **Cloudflare:** la herramienta se descarga de GitHub oficial y se verifica con su huella SHA-256 antes de ejecutarse. El túnel es saliente: no se abre ningún puerto en tu router.
- **Privacidad:** quien tenga el enlace ve nombres de jugadores, coordenadas actuales y dónde murieron por última vez. Compártelo solo con tus amigos.

## Uso manual (con Python)

Requiere Python 3.9 o superior y Minecraft Java. Probado en **Windows** con **Minecraft 26.3** y el launcher de Modrinth; en mundos 1.21.1 también lee estadísticas, logros y mapa. El terreno y los biomas necesitan mundos de 1.18 o más nuevos. Linux y macOS están contemplados, pero no probados.

```bash
python gui.py            # la ventana de escritorio (igual que la app instalada)
python start.py          # versión de consola: lee el mundo, sirve la página y crea el enlace
python start.py --help   # todas las opciones
```

O paso a paso:

```bash
python build.py          # lee el mundo abierto y genera los datos en site/
python serve.py          # sirve la página en http://127.0.0.1:8765/
```

Para mantener los datos al día sin `start.py`, ejecuta `build.py` cada minuto (Programador de tareas de Windows, o `cron`: `* * * * * cd /ruta/al/repositorio && python3 build.py`).

## Cómo encuentra el mundo

1. Busca instancias de Minecraft en los launchers habituales: launcher oficial, Modrinth, Prism Launcher, MultiMC, CurseForge (también con Documentos redirigido a OneDrive), GDLauncher y ATLauncher.
2. Elige el mundo que Minecraft tiene abierto en ese momento (en Windows, el que tiene `session.lock` bloqueado).
3. Si no hay ninguno abierto, se queda con el último que se usó.

Cuando cambias de mundo, la página lo nota en unos segundos y se recarga sola. Cada mundo guarda su propio historial en `data/<mundo>/`.

Si tu instancia está en un sitio raro, copia `config.example.json` a `config.json` y rellena `instances` (carpetas que contengan `saves/`) o `world` (para fijar un mundo concreto). Otras opciones: `language` (idioma de los nombres de logros en los datos, por defecto `es_es`), `port`, `terrain` y `terrain_max_regions` (los mundos enormes se saltan la capa de terreno para que la página no pese demasiado).

## Traducciones

Cada idioma es un archivo en `site/lang/`. Para corregir una traducción o añadir un idioma, copia `site/lang/en.js`, traduce los valores (conserva las `{variables}`; `|` separa singular|plural) y añádelo a `LANGS_LIST` en `site/index.html`, a la lista blanca de `serve.py` y a `PAGE_LANGS` en `build.py`.

## Datapacks

En `datapacks/` hay seis datapacks sueltos para jugar con amigos: **PvP Duelos**, **Talar árboles**, **Minero de vetas**, **Cosecha fácil**, **Coordenadas de muerte** y **Casa**. `python scripts/zip_datapacks.py` los empaqueta en `dist/`. Mira `datapacks/README.md`.

## Un secreto

<details>
<summary>Hay un premio escondido en la página (pulsa para ver cómo encontrarlo)</summary>

Se descubre escribiendo **siesta** con el teclado en cualquier parte de la página, con el **código Konami** (↑ ↑ ↓ ↓ ← → ← → B A), o tocando siete veces seguidas el título. No cuenta para ninguna clasificación.
</details>

## Créditos

Las skins y las caras se cargan de [mc-heads.net](https://mc-heads.net) (con [crafatar.com](https://crafatar.com) de reserva) y las fuentes, de Google Fonts, cuando hay conexión. No se incluye ningún recurso de Mojang.

Minecraft es una marca de Mojang AB. Este proyecto no está afiliado ni respaldado por Mojang ni por Microsoft.

## Licencia

[MIT](LICENSE)
