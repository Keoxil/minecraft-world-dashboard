scoreboard players set @s pvp_timer 0
scoreboard players set @s pvp_par 0
tag @s remove pvp_combate
title @s actionbar {"text":"⚔ Modo PvP cancelado","color":"gold"}
tellraw @s [{"text":"⚔ Modo PvP cancelado. ","color":"gold","bold":true},{"text":"Has recibido daño que no tiene que ver con tu rival (mobs, lava lejos de él…): ya no conservas el inventario si mueres.","color":"gray","bold":false}]
