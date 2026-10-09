# Datapacks

Seis datapacks pensados para jugar con amigos. Funcionan **sin mods**.

> Escritos y probados para **Minecraft 26.3** (formato de datapack 121). En otras versiones hay que cambiar `min_format` y `max_format` de `pack.mcmeta` y puede que haya que adaptar alguna sintaxis (en 26.x, por ejemplo, los predicados de entidad usan `minecraft:entity_type`).

| Carpeta | Qué hace | Cómo se usa |
|---|---|---|
| `pvp_duelos` | Cuando un jugador golpea a otro empieza un duelo de 60 s con título grande y las dos cabezas. Quien cae en el duelo conserva el inventario; las muertes naturales lo sueltan. El daño ajeno al duelo (mobs, lava lejos del rival) cancela la protección. | Automático. `/function pvp_duelos:estado` para comprobarlo. |
| `talar_arboles` | Con un hacha, sin agacharte, al cortar un tronco cae el árbol entero y se replanta. | `/trigger talar` lo activa o desactiva para ti. |
| `minero_vetas` | Con un pico, sin agacharte, al picar una mena se rompe toda la veta (respeta Fortuna y Toque de seda). | `/trigger veta` lo activa o desactiva para ti. |
| `cosecha_facil` | Clic derecho en un cultivo maduro: lo recoge y lo vuelve a plantar. | Automático. |
| `coordenadas_muerte` | Al reaparecer, un mensaje solo para ti con dónde has muerto. | Automático. |
| `casa` | Te lleva a tu cama o ancla de reaparición. No funciona durante un duelo de `pvp_duelos`. | `/trigger casa` |

Un datapack no puede crear comandos con nombre propio como `/casa`; lo más corto posible es `/trigger casa`.

## Instalar

```bash
python scripts/zip_datapacks.py          # crea dist/*.zip
```

Copia los zip que quieras a `<tu instancia>/saves/<tu mundo>/datapacks/` y escribe `/reload` en el juego (hacen falta trucos activados). Cada datapack lleva su propio `LEEME.txt`.
