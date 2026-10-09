# si el trozo de mundo está cargado y allí ya no hay cama ni ancla, no se viaja
$execute in $(dim) positioned $(x) $(y) $(z) if loaded ~ ~ ~ unless block ~ ~ ~ #minecraft:beds unless block ~ ~ ~ minecraft:respawn_anchor run return run tellraw @s {"text":"Tu cama ya no está en su sitio.","color":"red"}
$execute in $(dim) positioned $(x) $(y) $(z) run tp @s ~0.5 ~0.6 ~0.5
playsound minecraft:entity.enderman.teleport player @s ~ ~ ~ 0.6 1
title @s actionbar {"text":"Has vuelto a casa","color":"green"}
