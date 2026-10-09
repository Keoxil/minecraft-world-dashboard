# Minecraft World Dashboard

Una página web que enseña las estadísticas del mundo de Minecraft que estés jugando: ranking, podio con skins, mapa de lo explorado (terreno, biomas y tiempo), timelapse, carrera del ranking, historial de logros, Arena PvP y mucho más. Se actualiza sola y **encuentra por su cuenta el mundo que esté abierto en ese momento**, así que sirve para cualquier mundo que juegues o alojes en el futuro.

No necesita mods ni plugins: lee los archivos del propio mundo (estadísticas, logros, regiones, datos de jugador) y los registros del juego. Solo usa la biblioteca estándar de Python.

## Qué enseña

- **Contadores** de arriba con estadísticas elegidas al azar en cada carga.
- **Mapa** con tres capas (terreno, biomas y tiempo pasado en cada chunk), Overworld y Nether, posiciones de los jugadores (conectados o no) y **timelapse** desde la creación del mundo.
- **Clasificación general** con podio y skins, **carrera del ranking**, **clasificaciones por categoría** (incluidas las de "menos es mejor") y una tabla ordenable.
- **Premios**, **historial de logros** con la hora real y nombres oficiales del juego, y **Arena PvP**.
- Tema claro y oscuro, fondo animado y adaptación a móvil.
- Todas las horas llevan zona horaria: cada persona las ve en su hora local.

## Requisitos

- Python 3.9 o superior (sin instalar nada más).
- Minecraft Java. Probado en **Windows** con la versión **26.3** y launcher Modrinth; en mundos 1.21.1 también lee estadísticas, logros y mapa. El terreno y los biomas necesitan mundos de 1.18 o más nuevos.
- Linux y macOS están contemplados, pero no los he probado.

## Empezar (lo más fácil)

1. Instala [Python](https://www.python.org/downloads/) (marca **Add python.exe to PATH**) y descarga este repositorio (botón verde *Code → Download ZIP*).
2. Abre Minecraft con tu mundo.
3. Haz doble clic en **`INICIAR.bat`** (en Linux/macOS: `python3 start.py`).

Eso es todo. Lee tu mundo, abre la página en tu navegador, la mantiene al día cada minuto y crea un **enlace público** (descarga y verifica por su cuenta la herramienta de Cloudflare, sin cuenta ni configuración) que se copia solo al portapapeles. Se lo pasas a tus amigos y ya pueden verla. La primera vez te pregunta si quieres que arranque solo al encender el ordenador. Si no quieres enlace público: `python start.py --sin-enlace`.

El enlace cambia cada vez que se reinicia el programa. Si quieres un enlace fijo, usa un [túnel con nombre de Cloudflare](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/) (necesita cuenta gratuita).

## Uso manual

```bash
python build.py        # lee el mundo abierto y genera los datos en site/
python serve.py        # sirve la página en http://127.0.0.1:8765/
```

Abre <http://127.0.0.1:8765/>. Para que los datos se mantengan al día, ejecuta `build.py` cada minuto:

- **Windows:** `scripts\windows\tarea_programada.bat` crea una tarea programada que lo ejecuta cada minuto sin abrir ninguna ventana (`quitar_tarea.bat` la elimina).
- **Linux / macOS:** una línea de `cron`: `* * * * * cd /ruta/al/repositorio && python3 build.py`

## Cómo encuentra el mundo

1. Busca instancias de Minecraft en los launchers habituales: launcher oficial, Modrinth, Prism/MultiMC y CurseForge.
2. Elige el mundo que Minecraft tiene abierto en ese momento (en Windows, el que tiene `session.lock` bloqueado).
3. Si no hay ninguno abierto, se queda con el último que se usó.

Cuando cambias de mundo, la página lo nota en unos segundos y se recarga sola con el mundo nuevo. Cada mundo guarda su propio historial en `data/<mundo>/`.

Si tu instancia está en un sitio raro, copia `config.example.json` a `config.json` y rellena `instances` (carpetas que contengan `saves/`) o `world` (para fijar un mundo concreto). Otras opciones: `language` (idioma de los nombres de los logros, por defecto `es_es`), `port`, `terrain` y `terrain_max_regions` (los mundos enormes desactivan la capa de terreno para que la página no pese demasiado).

## Compartirla con amigos

`serve.py` solo escucha en tu propio equipo (`127.0.0.1`) y solo sirve `site/index.html` y los cuatro archivos de datos, nada más. Para que otros la vean sin abrir puertos en el router puedes usar un túnel, por ejemplo [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/):

```bash
cloudflared tunnel --url http://127.0.0.1:8765
```

(`scripts\windows\compartir.bat` hace las dos cosas a la vez.)

**Ojo con la privacidad:** la página publica los nombres de los jugadores, sus coordenadas actuales y el sitio donde murieron por última vez. Cualquiera que tenga el enlace lo ve. Compártelo solo con quien quieras que sepa dónde están vuestras bases.

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
